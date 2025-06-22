from readyapi import ReadyAPI, Response
from readyapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from readyapi.responses import JSONResponse
from readyapi.exception_handlers import RequestValidationError
from readyapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from prometheus_readyapi_instrumentator import Instrumentator

from app.api import rss_feed, scrapper, search, stats

app = ReadyAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"}))

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Routers
app.include_router(rss_feed.router, prefix="/rss-feed")
app.include_router(scrapper.router, prefix="/scrapper")
app.include_router(search.router, prefix="/search")
app.include_router(stats.router, prefix="/stats")

Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5555, reload=True) 