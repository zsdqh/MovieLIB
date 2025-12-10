#!/bin/bash
/app/.venv/bin/uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
