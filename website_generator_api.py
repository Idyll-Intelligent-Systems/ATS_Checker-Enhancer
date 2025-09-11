"""
DEPRECATED MODULE
=================
`website_generator_api.py` has been deprecated. All website generation endpoints are now served from the unified FastAPI application in `main.py` at the project root.

Use endpoints:
  POST   /website/generate
  GET    /website/status/{generation_id}
  GET    /website/download/{generation_id}

Run the unified service:
    python main.py
or development mode:
    uvicorn main:app --reload
"""

raise RuntimeError("Deprecated module. Website generation is now integrated in root main.py.")
