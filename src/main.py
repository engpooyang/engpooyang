"""FastAPI application entry point for the AI Landline Agent backend."""

import logging

from fastapi import FastAPI

from src.routes.health import router as health_router
from src.routes.webhooks import router as tools_router
from src.routes.webhooks import twilio_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="AI Landline Agent",
    description="Backend for ElevenLabs AI phone agent — handles caller lookup, spam detection, staff directory, and message notifications.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(tools_router)
app.include_router(twilio_router)


@app.get("/")
def root():
    return {"service": "ai-landline-agent", "status": "running"}
