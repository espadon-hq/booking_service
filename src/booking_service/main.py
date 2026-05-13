"""Головний модуль FastAPI застосунку."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from booking_service.routers import bookings, hotels, rooms, users, web

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Booking Service API",
    description="REST API для онлайн-бронювання готелів.",
    version="0.0.1",
    lifespan=lifespan,
)

app.include_router(hotels.router)
app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(web.router)

@app.get("/", tags=["root"])
def root() -> dict:
    return {"message": "Booking Service API працює!", "version": "0.0.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
