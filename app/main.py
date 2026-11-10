"""Main FastAPI application for ERPNext WhatsApp CRM Gateway."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import webhook, erp_events

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise WhatsApp Automation Gateway & CRM Bot for ERPNext / Frappe Framework.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(erp_events.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "2.0.0",
        "erpnext_target": settings.ERPNEXT_URL,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
