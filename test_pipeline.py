"""Tests for Mindee VAT on invoices demo."""

import unittest
from oa_client import OAClient
import vat_check
import mindee_client


class MindeeVATDemoTests(unittest.TestCase):
    def setUp(self):
        self.oa = OAClient(token=None)
        self.plan = self.oa.start("Determine VAT treatment for cross-border invoice", "MT")
        slug = (self.plan.get("skills_to_load") or [None])[0]
        self.skill = self.oa.get_skill(slug)

    def test_mock_oa_client(self):
        self.assertEqual(self.plan["jurisdiction"], "MT")
        self.assertEqual(self.skill["tier"], 1)
        self.assertIn("Michael Cutajar", self.skill["verifier"])

    def test_domestic_invoice_correct(self):
        raw = mindee_client.extract("samples/mt_domestic.json")
        facts = mindee_client.normalize(raw)
        res = vat_check.check(facts, self.skill)
        self.assertEqual(res["status"], "ok")
        self.assertIn("Correct domestic VAT", res["headline"])

    def test_intra_eu_b2b_reverse_charge_correct(self):
        raw = mindee_client.extract("samples/mt_to_fr_reverse_charge.json")
        facts = mindee_client.normalize(raw)
        res = vat_check.check(facts, self.skill)
        self.assertEqual(res["status"], "ok")
        self.assertIn("Reverse charge correctly applied", res["headline"])

    def test_intra_eu_b2b_wrong_vat_charged(self):
        raw = mindee_client.extract("samples/mt_to_fr_WRONG.json")
        facts = mindee_client.normalize(raw)
        res = vat_check.check(facts, self.skill)
        self.assertEqual(res["status"], "warn")
        self.assertIn("VAT charged in error", res["headline"])


if __name__ == "__main__":
    unittest.main()
