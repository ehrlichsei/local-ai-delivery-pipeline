"""Safety checks for patches generated from repository issues."""

import re


ALLOWED_PATHS = {"app.py", "tests/test_app.py", "README.md"}
MAX_PATCH_BYTES = 30_000


def validate_patch_paths(patch: str) -> list[str]:
    """Reject patches that touch anything outside the small demo code surface."""
    if not patch.strip():
        raise ValueError("The agent returned an empty patch")
    if not patch.startswith("diff --git "):
        raise ValueError("Patch must start with a unified git diff header")
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES:
        raise ValueError("The generated patch exceeds the 30 KB limit")
    if any(marker in patch for marker in ("GIT binary patch", "new file mode", "deleted file mode", "rename from", "rename to", "old mode", "new mode")):
        raise ValueError("Binary, added, deleted, renamed, or mode-changing patches are not allowed")

    headers = list(re.finditer(r"^diff --git a/([^\s]+) b/([^\s]+)$", patch, flags=re.MULTILINE))
    if not headers:
        raise ValueError("The output is not a unified git diff")

    paths: list[str] = []
    for index, header in enumerate(headers):
        old_path, new_path = header.groups()
        if old_path != new_path or old_path not in ALLOWED_PATHS:
            raise ValueError(f"Patch path is outside the allowed scope: {old_path} -> {new_path}")
        if old_path in paths:
            raise ValueError(f"Patch contains a duplicate file section: {old_path}")
        paths.append(old_path)

        section_end = headers[index + 1].start() if index + 1 < len(headers) else len(patch)
        section = patch[header.start():section_end]
        if not re.search(rf"^--- a/{re.escape(old_path)}(?:\t.*)?$", section, flags=re.MULTILINE):
            raise ValueError(f"Patch is missing the old-file header for {old_path}")
        if not re.search(rf"^\+\+\+ b/{re.escape(old_path)}(?:\t.*)?$", section, flags=re.MULTILINE):
            raise ValueError(f"Patch is missing the new-file header for {old_path}")

    return paths
