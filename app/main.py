from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .memory import memory
from .models import ChatRequest, ChatResponse
from .openai_service import OpenAIConfigurationError, answer_question
from .rate_limit import rate_limiter


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="مساعد طلبة قسم الهندسة الكهربائية",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "openai_ready": settings.openai_ready,
        "model": settings.openai_model,
        "vector_store_configured": bool(settings.openai_vector_store_id),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    forwarded = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )

    if not rate_limiter.allow(client_ip):
        raise HTTPException(
            status_code=429,
            detail="وصلت للحد المؤقت من الأسئلة. جرّب بعد شوي.",
        )

    try:
        prior = memory.history(payload.session_id)
        messages = prior + [{"role": "user", "content": payload.message}]
        answer, sources = answer_question(messages)

        memory.add(payload.session_id, "user", payload.message)
        memory.add(payload.session_id, "assistant", answer)

        return ChatResponse(answer=answer, sources=sources)

    except OpenAIConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"الربط مع OpenAI لسه مش مكتمل: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="صار خطأ أثناء معالجة السؤال. راجع إعدادات الخدمة.",
        ) from exc


@app.delete("/api/chat/{session_id}")
def clear_chat(session_id: str):
    memory.clear(session_id)
    return {"ok": True}
