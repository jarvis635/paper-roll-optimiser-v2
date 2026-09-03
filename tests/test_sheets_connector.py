import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import sys
import os

sys.path.insert(0, os.path.abspath("deployment"))

from server import app, parse_sheet_id

class TestGoogleSheetsConnector(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_parse_sheet_id_helper(self):
        url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"
        parsed = parse_sheet_id(url)
        self.assertEqual(parsed, "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

        raw_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        self.assertEqual(parse_sheet_id(raw_id), raw_id)

        invalid = "abc123"
        self.assertIsNone(parse_sheet_id(invalid))

    def test_invalid_sheet_id_response(self):
        res = self.app.post("/sheets/fetch", json={"sheet_id": "short"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data["error_type"], "invalid_sheet_id")

    @patch("urllib.request.urlopen")
    def test_permission_required_response(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://example.com", code=403, msg="Forbidden", hdrs={}, fp=None
        )
        res = self.app.post("/sheets/fetch", json={"sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"})
        self.assertEqual(res.status_code, 403)
        data = res.get_json()
        self.assertEqual(data["error_type"], "permission_required")

    @patch("urllib.request.urlopen")
    def test_successful_csv_fetch_and_parse(self, mock_urlopen):
        csv_content = (
            "Width,Quantity,Type\n"
            "35,4,child\n"
            "60,2,child\n"
            "100,10,parent\n"
        ).encode("utf-8")

        mock_response = MagicMock()
        mock_response.read.return_value = csv_content
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = self.app.post("/sheets/fetch", json={
            "sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "sheet_name": "Sheet1"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["child_rolls"], [[4, 35], [2, 60]])
        self.assertEqual(data["parent_rolls"], [[10, 100]])

if __name__ == "__main__":
    unittest.main()
