"""Головний модуль FastAPI застосунку."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from booking_service.routers import bookings, hotels, rooms, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Booking Service API",
    description="REST API для онлайн-бронювання готелів.",
    version="0.0.1",
    lifespan=lifespan,
)

# CORS — дозволяємо браузеру звертатись до API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hotels.router)
app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(bookings.router)

# Роздаємо статичні файли
app.mount("/static", StaticFiles(directory="src/booking_service/static"), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse("src/booking_service/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
