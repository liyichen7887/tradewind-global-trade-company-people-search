from __future__ import annotations

import importlib.util
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


class ProviderPayloadGuardTests(unittest.TestCase):
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
            "total_results": 4812,
            "has_more": False,
            "results": [{"name": "A"}, {"name": "B"}],
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
