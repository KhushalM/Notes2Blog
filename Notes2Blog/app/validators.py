from __future__ import annotations
import re
from typing import Tuple
from .config import settings

H1_RE = re.compile(r"^#\s+.+", re.M)
SECTION_RE = re.compile(r"^##\s+.+", re.M)

def validate_blog_markdown(markdown: str) -> Tuple[bool, str]:
    problems = []
    if settings.REQUIRE_H1 and not H1_RE.match(markdown):
        problems.append("Markdown should start with a Heading H1 (For example: # Blog Title)")
    
    if settings.REQUIRE_SECTIONS and len(SECTION_RE.findall(markdown)) < 2:
        problems.append("Markdown should contain at least two sections (For example: ## Section 1, ## Section 2)")
    
    return len(problems) == 0, "\n".join(problems)


def validate_react(code: str) -> Tuple[bool, str]:
    problems = []
    # if "export default function" not in code and "export default" not in code:
    #     problems.append("Export a default React component.")
    # if "return (" not in code:
    #     problems.append("Component must render JSX.")
    # if "props" not in code and "({" not in code:
    #     problems.append("Accept props or content input.")
    return (len(problems) == 0, "\n".join(problems))