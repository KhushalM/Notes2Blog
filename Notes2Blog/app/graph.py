from __future__ import annotations
import dspy
import json
from datetime import datetime
from langgraph.graph import END, StateGraph, START
from typing import List, Dict, Any

from .modules.pipeline import image_to_text, theme_and_outline, generate_blog, generate_react_code, improve_from_feedback, ReactCode, generate_metadata
from .storage import as_base64, save_output
from .validators import validate_blog_markdown, validate_react
from .state import State
from .config import settings

def add_logs(state: State, message: str) -> State:
    logs = list(state.get("logs", []))
    logs.append(message)
    state["logs"] = logs
    return state

def ocr_node(state: State) -> State:
    state = add_logs(state, "Converting image to raw text with OCR")
    if not state.get("image_b64") and state.get("image_path"):
        state["image_b64"] = as_base64(state["image_path"])
    pred = image_to_text(image_64 = state.get("image_b64", ""))
    state["raw_text"] = pred.raw_text or ""
    return add_logs(state, f"OCR completed: {len(state['raw_text'])} characters")

def reason_node(state: State) -> State:
    state = add_logs(state, "Reasoning and figuring out the theme and outline")
    pred = theme_and_outline(raw_text = state.get("raw_text", ""))
    state["theme"] = pred.theme or ""
    state["outline"] = pred.outline or []
    return add_logs(state, f"Reasoning completed, theme: {state['theme']}, outline: {state['outline']}")

def generate_blog_node(state: State) -> State:
    state = add_logs(state, "Generating blog post in markdown format")
    pred = generate_blog(raw_text = state.get("raw_text", ""), theme = state.get("theme", ""), outline = state.get("outline", []))
    state["blog_markdown"] = pred.blog_markdown or ""
    validity, feedback = validate_blog_markdown(state["blog_markdown"])
    state["validated"] = validity
    if not validity:
        state["feedback"] = feedback
        return add_logs(state, f"Blog markdown is invalid: {feedback}")
    return add_logs(state, f"Blog markdown is valid")

def generate_metadata_node(state: State) -> State:
    state = add_logs(state, "Generating blog metadata")
    pred = generate_metadata(blog_markdown = state.get("blog_markdown", ""), theme = state.get("theme", ""))
    state["title"] = pred.title or state.get("theme", "Untitled")
    state["summary"] = pred.summary or ""
    state["tags"] = pred.tags or []
    state["slug"] = pred.slug or ""
    state["reading_time"] = pred.reading_time or 5
    return add_logs(state, f"Metadata generated: {state['title']}")

def generate_react_node(state: State) -> State:
    state = add_logs(state, "Generating react code from blog markdown")
    pred = ReactCode(blog_markdown = state.get("blog_markdown", ""))
    state["react_code"] = pred.react_code or ""
    validity, feedback = validate_react(state["react_code"])
    state["validated"] = validity
    if not validity:
        state["feedback"] = feedback
        state["retry_count"] = state.get("retry_count", 0)  # Initialize retry count
        return add_logs(state, f"React code is invalid: {feedback}")
    save_output("Article.md", state["blog_markdown"], subdir = "article")
    save_output("Article.tsx", state["react_code"], subdir = "article")
    # Save metadata as JSON
    metadata = {
        "title": state.get("title", ""),
        "summary": state.get("summary", ""),
        "tags": state.get("tags", []),
        "slug": state.get("slug", ""),
        "reading_time": state.get("reading_time", 5),
        "created_at": datetime.now().isoformat()
    }
    save_output("metadata.json", json.dumps(metadata, indent=2), subdir = "article")
    return add_logs(state, f"React code is valid")

def improve_from_feedback_node(state: State) -> State:
    state = add_logs(state, "Improving from feedback")
    retry_count = state.get("retry_count", 0) + 1
    state["retry_count"] = retry_count
    
    pred = improve_from_feedback(feedback = state.get("feedback", ""), react_code = state.get("react_code", ""))
    state["react_code"] = pred.improved_react_code or ""
    validity, feedback = validate_react(state["react_code"])
    state["validated"] = validity
    if not validity:
        state["feedback"] = feedback
        return add_logs(state, f"React revalidation failed (attempt {retry_count}): {feedback}")
    save_output("Article.tsx", state["react_code"], subdir = "article")
    return add_logs(state, f"React revalidation completed")

def graph():
    graph = StateGraph(State)
    graph.add_node("ocr", ocr_node)
    graph.add_node("reason", reason_node)
    graph.add_node("generate_blog", generate_blog_node)
    graph.add_node("generate_metadata", generate_metadata_node)
    graph.add_node("generate_react", generate_react_node)
    graph.add_node("improve_from_feedback", improve_from_feedback_node)
    graph.add_edge(START, "ocr")
    graph.add_edge("ocr", "reason")
    graph.add_edge("reason", "generate_blog")
    graph.add_edge("generate_blog", "generate_metadata")
    graph.add_edge("generate_metadata", "generate_react")
    
    def should_end_or_retry(state: State) -> str:
        validated = state.get("validated", False)
        retry_count = state.get("retry_count", 0)
        
        if validated:
            return "END"
        elif retry_count >= 3:
            return "END"  # Stop after 3 retries
        else:
            return "improve_from_feedback"
    
    graph.add_conditional_edges(
        "generate_react",
        should_end_or_retry,
        {
            "END": END,
            "improve_from_feedback": "improve_from_feedback",
        }
    )
    graph.add_edge("improve_from_feedback", "generate_react")
    return graph.compile()



