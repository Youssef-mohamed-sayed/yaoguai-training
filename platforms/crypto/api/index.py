"""Vercel entry point: one Flask function serves the website AND the API.

vercel.json rewrites every path here; scripts/app.py then serves the pages
from public/ and the JSON API from /api/*.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from app import app  # noqa: E402,F401  (Vercel looks for a variable named `app`)
