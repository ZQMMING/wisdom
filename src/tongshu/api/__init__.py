"""TONGSHU HTTP API (FastAPI).

Endpoints:
    GET  /health       liveness + renderer mode (stub vs real LLM)
    POST /api/reading  personal reading: birth input -> SIR -> render -> text
    GET  /api/today    today card: computed ganzhi/weekday + curated mock bridge
"""
