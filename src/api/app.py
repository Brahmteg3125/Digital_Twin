"""The API layer (the 'waiter'): lets anyone run the pipeline over HTTP."""
from fastapi import FastAPI

from src.persona.persona import Persona
from src.orchestrator.pipeline import create_content

app = FastAPI(title="AI Creator Studio")


@app.get("/")
def home():
    """A simple health check — visit this to confirm the API is alive."""
    return {"message": "AI Creator Studio is running"}


@app.post("/create")
def create(topic: str):
    """Order: give a topic, get back a script + audio for Aria."""
    aria = Persona("Aria", 24, "cheerful", "warm smile and freckles")
    return create_content(aria, topic)
