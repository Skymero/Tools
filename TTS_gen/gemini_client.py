"""Minimal official Gemini REST helpers used for token estimation."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def count_tokens(text, *, model=None, api_key=None, timeout=30):
    model = model or os.environ.get("GEMINI_MODEL"); api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not model or not api_key: raise RuntimeError("Gemini model/API key configuration is incomplete")
    quoted = urllib.parse.quote(model, safe="")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{quoted}:countTokens"
    body = json.dumps({"contents": [{"parts": [{"text": text}]}]}).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": api_key})
    with urllib.request.urlopen(request, timeout=timeout) as response: value = json.load(response)
    tokens = value.get("totalTokens")
    if not isinstance(tokens, int) or tokens < 1: raise RuntimeError("Gemini countTokens returned no positive totalTokens")
    return tokens

