"""Independent unittest suite for api_contract.

Separate from run_all.py / verify.py PASS labels.
"""
import json
import unittest

from api_contract import adapter, validate


class TestValidate(unittest.TestCase):
    def test_bool_is_rejected_for_limit(self):
        req, err = validate.validate_rank_request_body({"items": [], "limit": True})
        self.assertIsNone(req)
        self.assertIn("limit must be integer", err)

    def test_bool_is_rejected_for_score(self):
        req, err = validate.validate_rank_request_body({"items": [{"label": "a", "score": True}]})
        self.assertIsNone(req)
        self.assertIn("finite number", err)

    def test_score_int_accepted(self):
        req, err = validate.validate_rank_request_body({"items": [{"label": "a", "score": 5}]})
        self.assertIsNone(err)
        self.assertEqual(req["items"][0]["score"], 5.0)

    def test_nan_rejected_at_json_layer(self):
        val, err = validate.json_load_strict('{"items": [{"label": "a", "score": NaN}]}')
        self.assertIsNone(val)
        self.assertIsNotNone(err)

    def test_unknown_field_top_rejected(self):
        req, err = validate.validate_rank_request_body({"items": [], "extra": 1})
        self.assertIsNone(req)
        self.assertIn("unknown field", err)

    def test_unknown_field_item_rejected(self):
        req, err = validate.validate_rank_request_body({"items": [{"label": "a", "score": 1, "x": 1}]})
        self.assertIsNone(req)
        self.assertIn("unknown field in item", err)

    def test_parse_qs_blank_default_drops(self):
        import urllib.parse
        qs = "limit="
        default = urllib.parse.parse_qs(qs, keep_blank_values=False)
        kept = urllib.parse.parse_qs(qs, keep_blank_values=True)
        self.assertEqual(default, {})
        self.assertEqual(kept, {"limit": [""]})

    def test_query_limit_repeated_rejected(self):
        lim, err = validate.validate_query_limit("limit=1&limit=2")
        self.assertIsNone(lim)
        self.assertIn("repeated", err)


class TestAdapter(unittest.TestCase):
    def _call(self, method="POST", path="/v1/rank", query="", headers=None, body_obj=None, body_bytes=None):
        if headers is None:
            headers = {"Content-Type": "application/json"}
        if body_bytes is None:
            body_bytes = json.dumps(body_obj if body_obj is not None else {}).encode("utf-8")
        status, resp_headers, resp_body = adapter.handle_request(
            method, path, query, headers, body_bytes
        )
        return status, resp_headers, json.loads(resp_body.decode("utf-8")), resp_body

    def test_ok_tiebreak(self):
        status, headers, body, raw = self._call(
            body_obj={"items": [{"label": "b", "score": 1}, {"label": "a", "score": 1}], "limit": 2}
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Content-Type"), "application/json")
        self.assertEqual(body["ranked"][0]["label"], "a")

    def test_limit_conflict_query_and_body(self):
        status, _, body, _ = self._call(
            query="limit=2",
            body_obj={"items": [{"label": "a", "score": 1}], "limit": 1}
        )
        self.assertEqual(status, 422)
        self.assertIn("both query and body", body["detail"])

    def test_limit_zero_valid(self):
        status, _, body, _ = self._call(
            query="limit=0",
            body_obj={"items": [{"label": "a", "score": 1}]}
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["ranked"], [])
        self.assertEqual(body["count"], 0)

    def test_duplicate_labels_allowed(self):
        status, _, body, _ = self._call(
            body_obj={"items": [{"label": "a", "score": 1}, {"label": "a", "score": 2}]}
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(body["ranked"]), 2)

    def test_canonical_bytes(self):
        _, _, body, raw = self._call(body_obj={"items": []})
        expected = adapter.dumps_canonical({"count": 0, "ranked": []})
        self.assertEqual(raw, expected)

    def test_routing_precedence_method_before_path(self):
        # GET /v1/other → method check fires first → 405, not 404
        status, _, body, _ = self._call(method="GET", path="/v1/other", body_obj={})
        self.assertEqual(status, 405)

    def test_routing_precedence_path_before_content_type(self):
        # POST /v1/other with bad CT → path check fires first → 404, not 415
        status, _, body, _ = self._call(
            path="/v1/other",
            headers={"Content-Type": "text/plain"},
            body_bytes=b"foo"
        )
        self.assertEqual(status, 404)

    def test_routing_precedence_content_type_before_body(self):
        # POST /v1/rank with bad CT and bad body → CT check fires first → 415
        status, _, body, _ = self._call(
            headers={"Content-Type": "text/plain"},
            body_bytes=b"not json {{{"
        )
        self.assertEqual(status, 415)


if __name__ == "__main__":
    unittest.main()
