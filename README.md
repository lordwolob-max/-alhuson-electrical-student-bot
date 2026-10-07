# مساعد طلبة قسم الهندسة الكهربائية

كلية الحصن الجامعية – جامعة البلقاء التطبيقية.

هذه النسخة جاهزة للنشر على Render.

## ملاحظات أمنية
- لا ترفع ملف `.env`.
- لا تضع `OPENAI_API_KEY` داخل GitHub.
- ضع المفتاح فقط داخل Environment Variables في Render.
- الـVector Store ID مضبوط مسبقاً في `render.yaml`.

## التشغيل
Render:
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

محلياً:
```bash
copy .env.example .env
uvicorn app.main:app --reload
```
