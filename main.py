import os
import json
import asyncio
import sqlite3
import pandas as pd
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.genai as genai

app = FastAPI(title="Jan Awaaz API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration & Gemini Models Cascade
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_LIST = os.getenv("GEMINI_MODELS", "gemini-3.1-flash-lite,gemini-3.8-flash,gemini-3.5-flash").split(",")

# SQLite DB Setup
DB_PATH = "jan_awaaz.db"

def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            text TEXT,
            language TEXT,
            english_translation TEXT,
            category TEXT,
            district TEXT,
            state TEXT,
            lat REAL,
            lng REAL,
            urgency INTEGER,
            summary TEXT,
            ai_fallback BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_sqlite_db()

# Pydantic Schemas
class RequestInput(BaseModel):
    text: str
    language: Optional[str] = "en-IN"

# Fallback Keyword Classifier
def keyword_classifier(text: str):
    text_lower = text.lower()
    category = "other"
    if any(k in text_lower for k in ["road", "pothole", "bus", "transport", "bridge", "सड़क"]):
        category = "roads"
    elif any(k in text_lower for k in ["water", "pipe", "drink", "borewell", "पानी"]):
        category = "water"
    elif any(k in text_lower for k in ["hospital", "doctor", "health", "clinic", "अस्पताल"]):
        category = "health"
    elif any(k in text_lower for k in ["school", "teacher", "class", "education", "स्कूल"]):
        category = "education"
    elif any(k in text_lower for k in ["power", "light", "electricity", "transformer", "बिजली"]):
        category = "electricity"

    return {
        "language": "hi-IN" if any('\u0900' <= c <= '\u097F' for c in text) else "en-IN",
        "english_translation": text,
        "category": category,
        "location": "unknown",
        "state": "unknown",
        "urgency": 3,
        "summary": text[:100],
        "ai_fallback": True
    }

# Gemini API Call with Exponential Backoff Strategy
async def analyze_with_gemini(text: str):
    if not GEMINI_API_KEY:
        return keyword_classifier(text)

    prompt = f"""
    Analyze the following Indian citizen grievance text. Return JSON matching this exact schema:
    {{
        "language": "hi-IN | kn-IN | ta-IN | bn-IN | mr-IN | en-IN",
        "english_translation": "string",
        "category": "roads | water | health | education | electricity | sanitation | agriculture | other",
        "location": "village/town/district or unknown",
        "state": "state name or unknown",
        "urgency": 1 to 5 integer,
        "summary": "one concise sentence in English summarizing the issue"
    }}

    Citizen input: "{text}"
    """

    client = genai.Client(api_key=GEMINI_API_KEY)

    for model_name in MODEL_LIST:
        model_name = model_name.strip()
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                data = json.loads(response.text)
                data["ai_fallback"] = False
                return data
            except Exception as e:
                await asyncio.sleep(2 ** attempt)

    return keyword_classifier(text)

@app.post("/api/requests")
async def submit_request(payload: RequestInput):
    result = await analyze_with_gemini(payload.text)
    
    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    req_id = f"REQ-{os.urandom(4).hex().upper()}"
    cursor.execute('''
        INSERT INTO requests (id, text, language, english_translation, category, district, state, lat, lng, urgency, summary, ai_fallback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        req_id, payload.text, result.get("language"), result.get("english_translation"),
        result.get("category"), result.get("location", "unknown"), result.get("state", "unknown"),
        20.5937, 78.9629, result.get("urgency", 3), result.get("summary"), result.get("ai_fallback", False)
    ))
    conn.commit()
    conn.close()
    
    return {"id": req_id, **result}

@app.get("/api/requests")
def get_requests():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM requests ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/stats")
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    total = cursor.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    districts = cursor.execute("SELECT COUNT(DISTINCT district) FROM requests").fetchone()[0]
    avg_urgency = cursor.execute("SELECT AVG(urgency) FROM requests").fetchone()[0] or 0
    conn.close()
    return {
        "total_requests": total,
        "districts_covered": districts,
        "avg_urgency": round(avg_urgency, 1)
    }

# Serve static files (Frontend index.html)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)