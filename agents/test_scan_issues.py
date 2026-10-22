import unittest

from scan_issues import MAX_CANDIDATES, candidate_issues


class CandidateIssueTests(unittest.TestCase):
    def test_skips_issues_already_scanned_and_orders_oldest_first(self):
        issues = [
            {"number": 3, "createdAt": "2026-10-03", "labels": []},
            {"number": 2, "createdAt": "2026-10-02", "labels": [{"name": "ai:scanned"}]},
            {"number": 1, "createdAt": "2026-10-01", "labels": []},
        ]
        self.assertEqual([issue["number"] for issue in candidate_issues(issues)], [1, 3])

    def test_limits_issues_considered_per_scheduled_run(self):
        issues = [
            {"number": number, "createdAt": f"2026-10-{number:02d}", "labels": []}
            for number in range(1, MAX_CANDIDATES + 3)
        ]
        self.assertEqual(len(candidate_issues(issues)), MAX_CANDIDATES)


if __name__ == "__main__":
    unittest.main()
