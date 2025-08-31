# Vercel serverless entry for FastAPI
# Exposes FastAPI app as `app` so @vercel/python recognizes ASGI.
from web.app import app as app  # noqa: F401

