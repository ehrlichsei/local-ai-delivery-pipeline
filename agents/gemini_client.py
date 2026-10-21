"""Small dependency-free client for Google's Gemini Developer API."""

import json
import os
import urllib.error
import urllib.request


def generate(prompt: str, *, system: str = "") -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing; add it as a repository Actions secret")
    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API returned HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Cannot reach Gemini API: {exc}") from exc
    try:
        return "".join(part["text"] for part in payload["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected Gemini response: {payload}") from exc


def parse_json_object(text: str) -> dict:
    """Parse JSON, allowing a model to wrap it in a Markdown code fence."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Agent did not return a JSON object")
    result = json.loads(text[start:end + 1])
    if not isinstance(result, dict):
        raise ValueError("Agent output must be a JSON object")
    return result
