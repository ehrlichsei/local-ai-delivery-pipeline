"""Safety checks for patches generated from repository issues."""

import difflib
import re


ALLOWED_PATHS = {"app.py", "tests/test_app.py", "README.md"}
MAX_PATCH_BYTES = 30_000


def build_patch(changes: list[dict[str, str]], originals: dict[str, str]) -> str:
    """Build a valid unified diff from full-file contents returned by the model."""
    if not isinstance(changes, list) or not changes:
        raise ValueError("The agent returned no file changes")

    sections: list[str] = []
    seen: set[str] = set()
    for change in changes:
        if not isinstance(change, dict):
            raise ValueError("Each file change must be an object")
        path = change.get("path")
        content = change.get("content")
        if not isinstance(path, str) or path not in ALLOWED_PATHS:
            raise ValueError(f"Patch path is outside the allowed scope: {path!r}")
        if path in seen:
            raise ValueError(f"Patch contains a duplicate file section: {path}")
        if not isinstance(content, str):
            raise ValueError(f"New file content must be a string: {path}")
        seen.add(path)

        original = originals.get(path)
        if not isinstance(original, str):
            raise ValueError(f"No original content is available for {path}")
        original = original.replace("\r\n", "\n").replace("\r", "\n")
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        if content and not content.endswith("\n"):
            content += "\n"
        if original == content:
            continue

        diff = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            n=3,
        ))
        if diff:
            sections.append(f"diff --git a/{path} b/{path}\n" + "".join(diff))

    patch = "".join(sections)
    if not patch:
        raise ValueError("The agent returned no effective changes")
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES:
        raise ValueError("The generated patch exceeds the 30 KB limit")
    validate_patch_paths(patch)
    return patch


def validate_patch_paths(patch: str) -> list[str]:
    """Reject patches that touch anything outside the small demo code surface."""
    patch = patch.replace("\r\n", "\n").replace("\r", "\n")
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
        if not re.search(rf"^--- a/{re.escape(old_path)}(?:[ \t].*)?$", section, flags=re.MULTILINE):
            old_headers = [line for line in section.splitlines() if line.startswith("---")]
            raise ValueError(f"Patch is missing the old-file header for {old_path}; found {old_headers!r}")
        if not re.search(rf"^\+\+\+ b/{re.escape(old_path)}(?:[ \t].*)?$", section, flags=re.MULTILINE):
            new_headers = [line for line in section.splitlines() if line.startswith("+++")]
            raise ValueError(f"Patch is missing the new-file header for {old_path}; found {new_headers!r}")

    return paths
