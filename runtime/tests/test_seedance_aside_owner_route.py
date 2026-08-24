import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "codex-skills" / "seedance-prompt-en"


class SeedanceAsideOwnerRouteTests(unittest.TestCase):
    def test_dispatcher_names_aside_as_source_of_truth(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Runway visible Aside is the source of truth", text)
        self.assertRegex(text, r"(?:one|single) visible Aside route")
        self.assertNotIn("Runway visible Chrome is the source of truth", text)
        self.assertNotIn("separate visible Chrome route", text)

    def test_production_has_one_aside_owner_and_no_positive_chrome_owner(self):
        text = (SKILL / "seedance-production.md").read_text(encoding="utf-8")
        self.assertIn("Generate board in Aside", text)
        self.assertIn(
            "One logged-in Aside `app.runwayml.com` Generate board per project",
            text,
        )
        self.assertRegex(
            text,
            r"(?:Aside is the only browser owner surface|Source of truth: one visible, logged-in .* Aside)",
        )
        for forbidden in (
            "visible Chrome Runway",
            "Generate board in Chrome",
            "Bring the correct Chrome Runway",
            "Chrome Runway is frontmost",
            "One logged-in Chrome",
            "BLOCKED_CHROME_CLIENT_CDN_DOWNLOAD",
        ):
            self.assertNotIn(forbidden, text)

    def test_shared_contract_prohibits_browser_fallback(self):
        text = (SKILL / "seedance-shared-contract.md").read_text(encoding="utf-8")
        self.assertIn("BLOCKED_ASIDE_CONTROL_UNAVAILABLE", text)
        self.assertIn(
            "Do not switch to Chrome, Safari, the in-app browser, or connector/API",
            text,
        )
        self.assertNotIn("If Chrome Computer Use", text)


if __name__ == "__main__":
    unittest.main()
