#!/usr/bin/env bash
# Start unified chat server (Bayazid + Marin + Arena)
uvicorn main:app --host 0.0.0.0 --port 5069
