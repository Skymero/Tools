"""Versioned Langflow scene-planner client."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from timeline_validator import validate_scene_plan


def _extract(value):
    """Find the first object containing a scenes list in a Langflow response."""
    if isinstance(value, dict):
        if isinstance(value.get("scenes"), list): return value
        for child in value.values():
            found = _extract(child)
            if found is not None: return found
    elif isinstance(value, list):
        for child in value:
            found = _extract(child)
            if found is not None: return found
    elif isinstance(value, str):
        try: return _extract(json.loads(value))
        except (json.JSONDecodeError, TypeError): pass
    return None


def build_input(paragraphs, artwork):
    lines = [f"Paragraph {i}: {text}" for i, text in enumerate(paragraphs, 1)]
    lines += ["", "Artwork inventory:"] + [f"{key} | {description}" for key, description in artwork.items()]
    return "\n".join(lines)


def plan_scenes(paragraphs, artwork, raw_output_path, *, base_url=None, flow_id=None, api_key=None, timeout=60):
    base_url = (base_url or os.environ.get("LANGFLOW_BASE_URL", "")).rstrip("/")
    flow_id, api_key = flow_id or os.environ.get("LANGFLOW_FLOW_ID"), api_key or os.environ.get("LANGFLOW_API_KEY")
    if not all((base_url, flow_id, api_key)): raise RuntimeError("Langflow configuration is incomplete")
    prompt = build_input(paragraphs, artwork)
    body = json.dumps({"input_value": prompt, "input_type": "chat", "output_type": "any"}).encode()
    request = urllib.request.Request(f"{base_url}/api/v1/run/{flow_id}", data=body,
                                     headers={"Content-Type": "application/json", "x-api-key": api_key})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response: raw = response.read()
    except urllib.error.URLError as exc: raise RuntimeError(f"Langflow request failed: {exc}") from exc
    target = Path(raw_output_path); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    parsed = json.loads(raw); plan = _extract(parsed)
    if plan is None: raise RuntimeError("Langflow response contains no scenes object")
    return validate_scene_plan(plan, len(paragraphs), set(artwork)), {
        "flow_id": flow_id, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}

