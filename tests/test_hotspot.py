import unittest
from hotspot import build_hotspot_table


class TestHotspot(unittest.TestCase):

    def test_build_hotspot_table_empty(self):
        df = build_hotspot_table([])
        self.assertTrue(df.empty)
        self.assertIn("location", df.columns)
        self.assertIn("hotspot_level", df.columns)

    def test_build_hotspot_table_aggregation(self):
        reports = [
            {"id": 1, "location": "Nagpur Central", "severity": "Critical", "priority": "P1"},
            {"id": 2, "location": "Nagpur Central", "severity": "Medium", "priority": "P2"},
            {"id": 3, "location": "Nagpur East", "severity": "Low", "priority": "P4"},
        ]
        df = build_hotspot_table(reports)
        self.assertEqual(len(df), 2)

        central_row = df[df["location"] == "Nagpur Central"].iloc[0]
        self.assertEqual(central_row["reports"], 2)
        self.assertEqual(central_row["highest_severity"], "Critical")
        self.assertEqual(central_row["p1_or_p2_count"], 2)
        self.assertEqual(central_row["hotspot_level"], "Critical")


if __name__ == "__main__":
    unittest.main()
