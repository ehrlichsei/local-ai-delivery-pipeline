import unittest

from issue_patch import validate_patch_paths


class ValidateIssuePatchTests(unittest.TestCase):
    def test_allows_changes_to_app_and_tests(self):
        patch = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-old
+new
diff --git a/tests/test_app.py b/tests/test_app.py
--- a/tests/test_app.py
+++ b/tests/test_app.py
@@ -1 +1 @@
-old
+new
"""
        self.assertEqual(validate_patch_paths(patch), ["app.py", "tests/test_app.py"])

    def test_allows_standard_unified_diff_timestamps(self):
        patch = """diff --git a/README.md b/README.md
--- a/README.md\t2026-10-22 10:00:00 +0000
+++ b/README.md\t2026-10-22 10:01:00 +0000
@@ -1 +1 @@
-old
+new
"""
        self.assertEqual(validate_patch_paths(patch), ["README.md"])

    def test_rejects_workflow_changes(self):
        patch = """diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -1 +1 @@
-old
+new
"""
        with self.assertRaisesRegex(ValueError, "outside the allowed scope"):
            validate_patch_paths(patch)

    def test_rejects_new_files(self):
        patch = """diff --git a/app.py b/app.py
new file mode 100644
--- /dev/null
+++ b/app.py
@@ -0,0 +1 @@
+new
"""
        with self.assertRaisesRegex(ValueError, "not allowed"):
            validate_patch_paths(patch)

    def test_rejects_binary_patch(self):
        patch = """diff --git a/app.py b/app.py
GIT binary patch
"""
        with self.assertRaisesRegex(ValueError, "Binary"):
            validate_patch_paths(patch)


if __name__ == "__main__":
    unittest.main()
