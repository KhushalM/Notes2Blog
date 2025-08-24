from __future__ import annotations
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from rich import print as rprint
import logging

from .config import settings
from .storage import save_upload
from .state import State
from .graph import graph


app = FastAPI(title="Notes → Blog (LangGraph + DSPy)")
workflow = graph()




@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or "uploaded_image.jpg"
    path = save_upload(filename, content)
    return {"image_path": path}




@app.post("/process")
async def process(payload: dict):
    image_path = payload.get("image_path")
    if not image_path:
        return JSONResponse({"error": "image_path required"}, status_code=400)


    state: State = {"image_path": image_path, "logs": []}
    try:
        final_state = workflow.invoke(state)
        rprint({"logs": final_state.get("logs", [])})
        return {
        "theme": final_state.get("theme"),
        "outline": final_state.get("outline"),
        "blog_markdown": final_state.get("blog_markdown"),
        "react_code": final_state.get("react_code"),
        "logs": final_state.get("logs", []),
        "validated": final_state.get("validated", False),
        "metadata": {
            "title": final_state.get("title", ""),
            "summary": final_state.get("summary", ""),
            "tags": final_state.get("tags", []),
            "slug": final_state.get("slug", ""),
            "reading_time": final_state.get("reading_time", 5),
        }
        }
    except Exception as e:
        logging.error(f"Error: {str(e)}, Current state: {state}")
        print(f"Error: {str(e)}, Current state: {state}")
        return JSONResponse({"error": str(e)}, status_code=500)




@app.get("/")
async def root():
    return {"ok": True, "message": "Notes→Blog backend ready", "vision": settings.USE_OPENAI_VISION, "api_key": settings.OPENAI_API_KEY}