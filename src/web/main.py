"""
DEPRECATED MODULE
=================
The legacy web entrypoint `src/web/main.py` has been deprecated.
All functionality (auth, analysis, website generation, health, static assets) has been unified into the single service at `main.py` in the project root.

Run the platform with:
    python main.py
or (development hot-reload):
    uvicorn main:app --reload

This file is retained only to avoid import errors for outdated references. Do not use it.
"""

raise RuntimeError("Deprecated entrypoint. Use root-level main.py (unified service).")
