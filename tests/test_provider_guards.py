from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("tradewind_common", ROOT / "scripts" / "common.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load TradeWind common client")
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)

PLAN_SPEC = importlib.util.spec_from_file_location(
    "tradewind_agentic_plan", ROOT / "scripts" / "validate_agentic_plan.py"
)
if PLAN_SPEC is None or PLAN_SPEC.loader is None:
    raise RuntimeError("cannot load TradeWind Agentic plan validator")
AGENTIC_PLAN = importlib.util.module_from_spec(PLAN_SPEC)
sys.modules[PLAN_SPEC.name] = AGENTIC_PLAN
PLAN_SPEC.loader.exec_module(AGENTIC_PLAN)


class ProviderPayloadGuardTests(unittest.TestCase):
    def test_agentic_plan_example_has_complete_approved_pilot_boundaries(self) -> None:
        plan = json.loads((
            ROOT / "references" / "agentic-search-plan-example.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(AGENTIC_PLAN.validate_plan(plan), [])
        pilot = AGENTIC_PLAN.resolve_submittable_task(
            plan, "us-formwork-main-contractors-pilot"
        )
        self.assertEqual(pilot["requestBody"]["country"], "USA")
        with self.assertRaisesRegex(ValueError, "not approved for submit"):
            AGENTIC_PLAN.resolve_submittable_task(
                plan, "us-modular-developers-scale"
            )
        plan["tasks"][1]["approvalStatus"] = "approved_for_submit"
        with self.assertRaisesRegex(ValueError, "unaccepted pilot dependencies"):
            AGENTIC_PLAN.resolve_submittable_task(
                plan, "us-modular-developers-scale"
            )
        plan["tasks"][0]["approvalStatus"] = "completed"
        plan["tasks"][0]["pilotReviewStatus"] = "accepted"
        scale = AGENTIC_PLAN.resolve_submittable_task(
            plan, "us-modular-developers-scale"
        )
        self.assertEqual(scale["phase"], "scale")

    def test_agentic_plan_rejects_uncovered_scope_and_duplicate_boundaries(self) -> None:
        plan = json.loads((
            ROOT / "references" / "agentic-search-plan-example.json"
        ).read_text(encoding="utf-8"))
        plan["coverageMatrix"] = [
            cell for cell in plan["coverageMatrix"]
            if cell["productFamily"] != "offsite_modular"
        ]
        plan["tasks"][1]["requestBody"] = dict(plan["tasks"][0]["requestBody"])
        plan["tasks"][1]["queryBoundary"] = plan["tasks"][0]["queryBoundary"]
        errors = AGENTIC_PLAN.validate_plan(plan)
        self.assertTrue(any("omits researchScope.productFamilies" in item for item in errors))
        self.assertTrue(any("duplicate requestBody" in item for item in errors))
        self.assertTrue(any("duplicate queryBoundary" in item for item in errors))
        self.assertTrue(any("not referenced by coverageMatrix" in item for item in errors))

    def test_php_stack_wrapped_as_success_is_upstream_unavailable(self) -> None:
        guarded = COMMON.assess_provider_payload({
            "success": True,
            "total_results": 999,
            "data": "ThinkPHP Fatal error in /vendor/topthink/framework/src/App.php Stack trace",
        })
        self.assertEqual(guarded["providerStatus"], "upstream_unavailable")
        self.assertIsNone(guarded["data"])
        self.assertEqual(guarded["warnings"][0]["code"], "invalid_upstream_payload")
        self.assertNotIn("total_results", guarded)

    def test_inconsistent_pagination_is_not_exhaustive(self) -> None:
        guarded = COMMON.assess_provider_payload({
            "people": [{"name": f"Person {index}"} for index in range(5)],
            "meta": {"total_results": 7633, "has_more": False},
        })
        self.assertEqual(guarded["coverageStatus"], "not_exhaustive")
        self.assertEqual(
            guarded["providerWarnings"][0]["code"],
            "pagination_metadata_inconsistent",
        )

    def test_clean_payload_is_unchanged(self) -> None:
        payload = {"total_results": 2, "has_more": False, "results": [{}, {}]}
        self.assertEqual(COMMON.assess_provider_payload(payload), payload)


if __name__ == "__main__":
    unittest.main()
