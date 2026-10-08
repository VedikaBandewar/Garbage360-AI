import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = Path(self.temp_dir.name) / "test_garbage360.db"
        self.db_patcher = patch.object(database, "DB_PATH", self.db_file)
        self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()
        self.temp_dir.cleanup()

    def test_db_lifecycle(self):
        database.init_db()

        # Check empty reports
        reports = database.fetch_reports()
        self.assertEqual(len(reports), 0)

        # Insert report
        data = {
            "description": "Test garbage pile",
            "location": "Nagpur Central",
            "latitude": 21.1458,
            "longitude": 79.0882,
            "image_hash": "hash123",
            "image_name": "photo.jpg",
            "category": "Plastic / Dry Waste",
            "severity": "High",
            "priority": "P2",
            "drain_risk": "Low",
            "confidence": 0.85,
            "recommended_action": "Clean location",
            "analysis_mode": "Local demo inference",
        }
        report_id = database.insert_report(data)
        self.assertEqual(report_id, 1)

        # Fetch reports
        reports = database.fetch_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["location"], "Nagpur Central")
        self.assertEqual(reports[0]["status"], "Reported")

        # Update status
        database.update_report_status(report_id, "In Progress")
        updated_reports = database.fetch_reports()
        self.assertEqual(updated_reports[0]["status"], "In Progress")

        # Test report stats
        stats = database.report_stats(updated_reports)
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["open"], 1)
        self.assertEqual(stats["resolved"], 0)


if __name__ == "__main__":
    unittest.main()
