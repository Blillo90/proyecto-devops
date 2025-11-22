from fastapi import FastAPI
from .database import Base, engine
from .routers import tickets, users

# Crear tablas en PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticketing API - Proyecto ASIR", version="1.0.0")


@app.get("/")
def home():
    return {"message": "API funcionando correctamente 🚀"}


app.include_router(users.router)
app.include_router(tickets.router)

