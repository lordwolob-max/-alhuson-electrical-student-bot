import re

from .config import settings
from .knowledge_manifest import source_metadata
from .prompt import SYSTEM_PROMPT


class OpenAIConfigurationError(RuntimeError):
    pass


def _client():
    if not settings.openai_api_key:
        raise OpenAIConfigurationError("OPENAI_API_KEY غير مضبوط.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise OpenAIConfigurationError(
            "حزمة openai غير مثبتة. شغّل pip install -r requirements.txt"
        ) from exc
    return OpenAI(api_key=settings.openai_api_key)


def _extract_sources(response, query: str = "") -> list[dict]:
    manifest = source_metadata()
    found = {}

    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "file_search_call":
            continue
        for result in getattr(item, "results", None) or []:
            filename = getattr(result, "filename", None) or "ملف معرفة"
            score = getattr(result, "score", None)
            meta = manifest.get(filename, {})
            candidate = {
                "filename": filename,
                "display_name": meta.get("display_name", filename),
                "authority": meta.get("authority"),
                "score": score,
            }
            current = found.get(filename)
            if current is None or (
                score is not None and
                (current["score"] is None or score > current["score"])
            ):
                found[filename] = candidate

    sources = list(found.values())
    if not sources:
        return []

    sources.sort(
        key=lambda x: x["score"] if x["score"] is not None else -1,
        reverse=True,
    )

    q = (query or "").lower()

    def keep(names):
        picked = [s for s in sources if s["filename"] in names]
        return picked[:3] if picked else None

    # التدريب
    if any(k in q for k in ["تدريب", "ميداني"]):
        picked = keep({
            "11_field_training_regulations.pdf",
            "30_field_training_committee.docx",
            "40_department_program_applicability.md",
            "01_department_knowledge.md",
        })
        if picked:
            return picked

    # معادلة خدمة العلم
    if "معادلة" in q and any(k in q for k in ["خدمة العلم", "خدمه العلم", "عسكرية"]):
        picked = keep({
            "13_military_service_equivalency.pdf",
            "01_department_knowledge.md",
        })
        if picked:
            return picked

    # معادلة المواد
    if "معادلة" in q or "اعادل" in q or "أعادل" in q:
        picked = keep({
            "12_course_equivalency_procedure.pdf",
            "01_department_knowledge.md",
        })
        if picked:
            return picked

    # إجراءات القسم
    procedure_terms = [
        "شعبة", "شعب", "مسكرة", "مغلق", "فل",
        "بديل", "بديلة", "بديلات",
        "خطة مفرغة", "خريج",
        "أقل من 12", "اقل من 12", "9 ساعات", "10 ساعات", "11 ساعة",
    ]
    if any(k in q for k in procedure_terms):
        picked = keep({
            "01_department_knowledge.md",
            "10_bachelor_regulations.pdf",
        })
        if picked:
            if not any(k in q for k in ["12", "ساعات", "ساعة", "عبء", "جدول"]):
                department_only = [
                    s for s in picked if s["filename"] == "01_department_knowledge.md"
                ]
                if department_only:
                    picked = department_only
            return picked[:2]

    # المواد والخطط
    course_terms = [
        "متطلب", "مساق", "مادة", "خطة", "سيركت", "circuit",
        "power", "بور", "iot", "إحصاء", "احصاء", "مختبر",
    ]
    if any(k in q for k in course_terms):
        picked = keep({
            "20_power_program_plan_2026_2027.pdf",
            "21_engineering_requirements_2026_2027.docx",
            "01_department_knowledge.md",
        })
        if picked:
            return picked

    top_score = sources[0]["score"]
    if top_score is None:
        return sources[:2]

    threshold = max(0.25, top_score * 0.82)
    relevant = [
        s for s in sources
        if s["score"] is not None and s["score"] >= threshold
    ]
    return (relevant or sources[:1])[:2]


def _clean_answer(text: str) -> str:
    text = re.sub(r"filecite.*?", "", text)
    text = re.sub(r"cite.*?", "", text)
    text = text.replace("**", "")
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def answer_question(messages: list[dict]) -> tuple[str, list[dict]]:
    if not settings.openai_vector_store_id:
        raise OpenAIConfigurationError("OPENAI_VECTOR_STORE_ID غير مضبوط.")

    response = _client().responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=messages,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [settings.openai_vector_store_id],
                "max_num_results": settings.file_search_max_results,
            }
        ],
        tool_choice="required",
        include=["file_search_call.results"],
        store=False,
    )

    current_query = messages[-1].get("content", "") if messages else ""
    sources = _extract_sources(response, current_query)

    if not sources:
        return (
            "ما لقيت معلومة مؤكدة بالمصادر الموجودة عندي عن هالنقطة. "
            "عشان ما أفتي عليك، الأفضل تراجع الجهة المختصة بالقسم أو القبول والتسجيل حسب موضوع سؤالك.",
            [],
        )

    answer = _clean_answer(response.output_text or "")
    if not answer:
        answer = (
            "لقيت مصادر مرتبطة بالسؤال، بس ما قدرت أطلع منها جواب واضح ومؤكد. "
            "الأفضل تراجع القسم حتى ما أعطيك معلومة غير دقيقة."
        )

    return answer, sources
