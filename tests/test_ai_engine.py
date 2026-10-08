import unittest
from unittest.mock import patch, MagicMock

from ai_engine import (
    keyword_category,
    local_analysis,
    _extract_json,
    gemini_analysis,
    analyze_report,
)


class TestAIEngine(unittest.TestCase):

    def test_keyword_category_detection(self):
        cat, conf = keyword_category("plastic bottles and plastic bags")
        self.assertEqual(cat, "Plastic / Dry Waste")
        self.assertGreater(conf, 0.60)

        cat_food, _ = keyword_category("rotten food and kitchen waste")
        self.assertEqual(cat_food, "Organic / Wet Waste")

        cat_unknown, conf_unknown = keyword_category("random text without keywords")
        self.assertEqual(cat_unknown, "Mixed / Unclassified Waste")
        self.assertEqual(conf_unknown, 0.55)

    def test_local_analysis_severity_and_drain(self):
        result = local_analysis(
            description="Huge mixed garbage pile beside a blocked drain",
            location="Nagpur Central",
            existing_reports=[],
        )
        self.assertEqual(result["severity"], "Critical")
        self.assertEqual(result["drain_risk"], "High")
        self.assertEqual(result["priority"], "P1")

    def test_local_analysis_repeated_location(self):
        existing = [
            {"location": "Nagpur Central"},
            {"location": "nagpur central"},
            {"location": "NAGPUR CENTRAL"},
        ]
        result = local_analysis(
            description="Small paper waste",
            location="Nagpur Central",
            existing_reports=existing,
        )
        self.assertEqual(result["priority"], "P2")
        self.assertIn("Similar location reports found: 3", result["recommended_action"])

    def test_extract_json_valid_and_markdown(self):
        raw_markdown = """```json
        {
            "category": "E-Waste",
            "severity": "High",
            "priority": "P2",
            "drain_risk": "Low",
            "confidence": 0.88,
            "recommended_action": "Recycle"
        }
        ```"""
        parsed = _extract_json(raw_markdown)
        self.assertEqual(parsed["category"], "E-Waste")
        self.assertEqual(parsed["severity"], "High")
        self.assertEqual(parsed["confidence"], 0.88)

    def test_extract_json_malformed_fallback(self):
        raw_bad = '{"category": "InvalidCategoryName", "confidence": "invalid_num"}'
        parsed = _extract_json(raw_bad)
        self.assertEqual(parsed["category"], "Mixed / Unclassified Waste")
        self.assertEqual(parsed["confidence"], 0.75)

    def test_gemini_analysis_success(self):
        mock_genai = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"category": "Paper Waste", "severity": "Low", "priority": "P4", "drain_risk": "Low", "confidence": 0.9, "recommended_action": "Collect paper"}'
        mock_genai.Client.return_value.models.generate_content.return_value = mock_response

        mock_google = MagicMock()
        mock_google.genai = mock_genai

        with patch.dict("sys.modules", {"google": mock_google, "google.genai": mock_genai}):
            res = gemini_analysis("paper carton dump", "Nagpur", None, None, "fake_api_key")
            self.assertEqual(res["category"], "Paper Waste")
            self.assertEqual(res["analysis_mode"], "Gemini multimodal AI")



    def test_analyze_report_fallback_on_error(self):
        # Even with an API key provided, if Gemini fails (or isn't available), fallback to local_analysis cleanly
        with patch("ai_engine.gemini_analysis", side_effect=Exception("API Error")):
            res = analyze_report("plastic bottle", "Nagpur", [], api_key="fake_key")
            self.assertEqual(res["analysis_mode"], "Local demo inference")
            self.assertEqual(res["category"], "Plastic / Dry Waste")


if __name__ == "__main__":
    unittest.main()
