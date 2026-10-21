"""Minimal Ollama HTTP client shared by the pipeline's agents."""

import json
import os
import urllib.error
import urllib.request


def generate(prompt: str, *, system: str = "") -> str:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": 0.1},
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Cannot reach Ollama at {base_url}: {exc}") from exc
    if "response" not in payload:
        raise RuntimeError(f"Unexpected Ollama response: {payload}")
    return payload["response"]


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
