#!/usr/bin/env python3
"""Validate a TradeWind Agentic Search submission plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CELL_STATUSES = {"planned", "completed", "excluded"}
PHASES = {"pilot", "scale"}
APPROVAL_STATUSES = {
    "planned",
    "approved_for_pilot",
    "approved_for_submit",
    "submitted",
    "completed",
    "failed",
    "cancelled",
}
SUBMITTABLE_APPROVALS = {"approved_for_pilot", "approved_for_submit"}
PILOT_REVIEW_STATUSES = {"pending", "accepted", "rejected", "not_applicable"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_nonempty(item) for item in value)
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("planVersion", "planId", "asOf", "country", "researchScope", "coverageMatrix", "tasks", "submissionPolicy"):
        if field not in plan:
            errors.append(f"missing field: {field}")

    for field in ("planVersion", "planId", "asOf"):
        if field in plan and not _nonempty(plan[field]):
            errors.append(f"{field} must be a non-empty string")

    country = plan.get("country")
    if not isinstance(country, dict):
        errors.append("country must be an object")
        country = {}
    for field in ("iso2", "agenticCountry", "cr", "lang", "referenceArtifact", "referenceRetrievedOn"):
        if not _nonempty(country.get(field)):
            errors.append(f"country.{field} must be a non-empty string")

    scope = plan.get("researchScope")
    if not isinstance(scope, dict):
        errors.append("researchScope must be an object")
        scope = {}
    if scope.get("resultMode") not in {"full", "sample"}:
        errors.append("researchScope.resultMode must be full or sample")
    for field in ("productFamilies", "roleLanes", "sourceGoals"):
        if not _string_list(scope.get(field)):
            errors.append(f"researchScope.{field} must be a non-empty string array")
    if not _string_list(scope.get("exclusions"), allow_empty=True):
        errors.append("researchScope.exclusions must be a string array")

    products = set(scope.get("productFamilies", [])) if isinstance(scope.get("productFamilies"), list) else set()
    roles = set(scope.get("roleLanes", [])) if isinstance(scope.get("roleLanes"), list) else set()
    goals = set(scope.get("sourceGoals", [])) if isinstance(scope.get("sourceGoals"), list) else set()

    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty array")
        tasks = []
    task_map: dict[str, dict[str, Any]] = {}
    request_bodies: dict[str, str] = {}
    boundaries: dict[str, str] = {}
    for index, task in enumerate(tasks):
        path = f"tasks[{index}]"
        if not isinstance(task, dict):
            errors.append(f"{path} must be an object")
            continue
        key = task.get("taskKey")
        if not _nonempty(key):
            errors.append(f"{path}.taskKey must be a non-empty string")
            continue
        if key in task_map:
            errors.append(f"duplicate taskKey: {key}")
        task_map[key] = task
        if task.get("intent") not in goals:
            errors.append(f"{path}.intent must be present in researchScope.sourceGoals")
        for field, allowed in (("productFamilies", products), ("roleLanes", roles)):
            values = task.get(field)
            if not _string_list(values):
                errors.append(f"{path}.{field} must be a non-empty string array")
            elif not set(values).issubset(allowed):
                errors.append(f"{path}.{field} contains values outside researchScope")
        for field in ("queryBoundary", "coherenceReason", "dedupKey", "expectedOutcome"):
            if not _nonempty(task.get(field)):
                errors.append(f"{path}.{field} must be a non-empty string")
        if task.get("phase") not in PHASES:
            errors.append(f"{path}.phase must be pilot or scale")
        if task.get("approvalStatus") not in APPROVAL_STATUSES:
            errors.append(f"{path}.approvalStatus is invalid")
        if task.get("pilotReviewStatus") not in PILOT_REVIEW_STATUSES:
            errors.append(f"{path}.pilotReviewStatus is invalid")
        if not _string_list(task.get("dependsOn"), allow_empty=True):
            errors.append(f"{path}.dependsOn must be a string array")
        if task.get("phase") == "pilot" and task.get("dependsOn"):
            errors.append(f"{path}: pilot task cannot depend on another task")
        if task.get("phase") == "pilot" and task.get("pilotReviewStatus") == "not_applicable":
            errors.append(f"{path}: pilot task requires a real pilotReviewStatus")
        if task.get("phase") == "scale" and not task.get("dependsOn"):
            errors.append(f"{path}: scale task requires a pilot dependency")
        if task.get("phase") == "scale" and task.get("pilotReviewStatus") != "not_applicable":
            errors.append(f"{path}: scale task pilotReviewStatus must be not_applicable")

        body = task.get("requestBody")
        if not isinstance(body, dict):
            errors.append(f"{path}.requestBody must be an object")
        else:
            for field in ("keyword", "country", "cr", "lang"):
                if not _nonempty(body.get(field)):
                    errors.append(f"{path}.requestBody.{field} must be a non-empty string")
            expected = {
                "country": country.get("agenticCountry"),
                "cr": country.get("cr"),
                "lang": country.get("lang"),
            }
            for field, value in expected.items():
                if body.get(field) != value:
                    errors.append(f"{path}.requestBody.{field} must match plan country reference")
            body_key = _canonical_json(body)
            if body_key in request_bodies:
                errors.append(f"duplicate requestBody in {request_bodies[body_key]} and {key}")
            else:
                request_bodies[body_key] = key

        boundary = task.get("queryBoundary")
        if _nonempty(boundary):
            normalized_boundary = " ".join(boundary.casefold().split())
            if normalized_boundary in boundaries:
                errors.append(f"duplicate queryBoundary in {boundaries[normalized_boundary]} and {key}")
            else:
                boundaries[normalized_boundary] = key

    for key, task in task_map.items():
        for dependency in task.get("dependsOn", []):
            if dependency not in task_map:
                errors.append(f"task {key} depends on unknown taskKey {dependency}")
            elif task_map[dependency].get("phase") != "pilot":
                errors.append(f"task {key} must depend on a pilot task")

    matrix = plan.get("coverageMatrix")
    if not isinstance(matrix, list) or not matrix:
        errors.append("coverageMatrix must be a non-empty array")
        matrix = []
    seen_cells: set[tuple[str, str, str]] = set()
    seen_cell_keys: set[str] = set()
    covered_products: set[str] = set()
    covered_roles: set[str] = set()
    covered_goals: set[str] = set()
    referenced_tasks: set[str] = set()
    for index, cell in enumerate(matrix):
        path = f"coverageMatrix[{index}]"
        if not isinstance(cell, dict):
            errors.append(f"{path} must be an object")
            continue
        cell_key = cell.get("cellKey")
        if not _nonempty(cell_key):
            errors.append(f"{path}.cellKey must be a non-empty string")
        elif cell_key in seen_cell_keys:
            errors.append(f"duplicate cellKey: {cell_key}")
        else:
            seen_cell_keys.add(cell_key)
        product = cell.get("productFamily")
        role = cell.get("roleLane")
        goal = cell.get("sourceGoal")
        if product not in products:
            errors.append(f"{path}.productFamily must be present in researchScope")
        if role not in roles:
            errors.append(f"{path}.roleLane must be present in researchScope")
        if goal not in goals:
            errors.append(f"{path}.sourceGoal must be present in researchScope")
        cell_tuple = (str(product), str(role), str(goal))
        if cell_tuple in seen_cells:
            errors.append(f"duplicate coverage cell: {cell_tuple}")
        seen_cells.add(cell_tuple)
        covered_products.add(str(product))
        covered_roles.add(str(role))
        covered_goals.add(str(goal))
        status = cell.get("status")
        if status not in CELL_STATUSES:
            errors.append(f"{path}.status is invalid")
        if not _nonempty(cell.get("reason")):
            errors.append(f"{path}.reason must be a non-empty string")
        task_keys = cell.get("taskKeys")
        if not _string_list(task_keys, allow_empty=status == "excluded"):
            errors.append(f"{path}.taskKeys must be a string array")
            task_keys = []
        if status == "excluded" and task_keys:
            errors.append(f"{path}: excluded cell cannot reference tasks")
        if status in {"planned", "completed"} and not task_keys:
            errors.append(f"{path}: {status} cell must reference at least one task")
        for task_key in task_keys:
            referenced_tasks.add(task_key)
            task = task_map.get(task_key)
            if task is None:
                errors.append(f"{path} references unknown taskKey {task_key}")
                continue
            if product not in task.get("productFamilies", []):
                errors.append(f"{path}: task {task_key} does not cover productFamily")
            if role not in task.get("roleLanes", []):
                errors.append(f"{path}: task {task_key} does not cover roleLane")
            if goal != task.get("intent"):
                errors.append(f"{path}: task {task_key} intent does not cover sourceGoal")

    for label, expected, observed in (
        ("productFamilies", products, covered_products),
        ("roleLanes", roles, covered_roles),
        ("sourceGoals", goals, covered_goals),
    ):
        missing = sorted(expected - observed)
        if missing:
            errors.append(f"coverageMatrix omits researchScope.{label}: {', '.join(missing)}")
    unreferenced = sorted(set(task_map) - referenced_tasks)
    if unreferenced:
        errors.append(f"tasks are not referenced by coverageMatrix: {', '.join(unreferenced)}")

    policy = plan.get("submissionPolicy")
    if not isinstance(policy, dict):
        errors.append("submissionPolicy must be an object")
        policy = {}
    if not isinstance(policy.get("pilotRequired"), bool):
        errors.append("submissionPolicy.pilotRequired must be boolean")
    max_concurrent = policy.get("maxConcurrent")
    if not isinstance(max_concurrent, int) or isinstance(max_concurrent, bool) or max_concurrent < 1:
        errors.append("submissionPolicy.maxConcurrent must be a positive integer")
    if policy.get("reSubmitRequiresApproval") is not True:
        errors.append("submissionPolicy.reSubmitRequiresApproval must be true")
    if policy.get("overlapPolicy") != "reject_duplicate_query_boundary":
        errors.append("submissionPolicy.overlapPolicy must reject duplicate query boundaries")
    if policy.get("pilotRequired") is True:
        for goal in goals:
            if any(task.get("intent") == goal for task in task_map.values()) and not any(
                task.get("intent") == goal and task.get("phase") == "pilot"
                for task in task_map.values()
            ):
                errors.append(f"sourceGoal {goal} requires at least one pilot task")

    return errors


def load_plan(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_submittable_task(plan: dict[str, Any], task_key: str) -> dict[str, Any]:
    errors = validate_plan(plan)
    if errors:
        raise ValueError("invalid Agentic plan: " + "; ".join(errors))
    task = next((item for item in plan["tasks"] if item["taskKey"] == task_key), None)
    if task is None:
        raise ValueError(f"unknown taskKey: {task_key}")
    if task["approvalStatus"] not in SUBMITTABLE_APPROVALS:
        raise ValueError(
            f"task {task_key} is not approved for submit: {task['approvalStatus']}"
        )
    if task["phase"] == "pilot" and task["approvalStatus"] != "approved_for_pilot":
        raise ValueError(f"pilot task {task_key} requires approved_for_pilot")
    if task["phase"] == "scale" and task["approvalStatus"] != "approved_for_submit":
        raise ValueError(f"scale task {task_key} requires approved_for_submit")
    if task["phase"] == "scale":
        task_map = {item["taskKey"]: item for item in plan["tasks"]}
        incomplete = [
            dependency
            for dependency in task["dependsOn"]
            if task_map[dependency]["approvalStatus"] != "completed"
            or task_map[dependency]["pilotReviewStatus"] != "accepted"
        ]
        if incomplete:
            raise ValueError(
                f"scale task {task_key} has unaccepted pilot dependencies: {', '.join(incomplete)}"
            )
    return task


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_file", type=Path)
    args = parser.parse_args()
    plan = load_plan(args.plan_file)
    errors = validate_plan(plan)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
