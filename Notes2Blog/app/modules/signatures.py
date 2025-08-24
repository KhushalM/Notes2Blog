import dspy
from typing import List

class ExtractNotes(dspy.Signature):
    """Convert an input image (base64) of handwritten notes into a text transcript."""
    image_b64: str = dspy.InputField(desc="Base64 encoded image of handwritten notes")
    raw_text: str = dspy.OutputField(desc="Extracted text content from the notes image")

class FindThemeAndOutline(dspy.Signature):
    """Find the theme and outline of the input text from the text transcript. Do not deviate from the text. The outlines should be what the points are in the text.
    
    Example:
    Input: "Machine Learning Basics
    - Supervised learning uses labeled data
    - Unsupervised learning finds patterns  
    - Neural networks mimic brain structure
    - Training is the learning process"
    
    Output:
    Theme: "Machine Learning Basics"
    Outline: ["Supervised learning uses labeled data", "Unsupervised learning finds patterns", "Neural networks mimic brain structure", "Training is the learning process"]
    """
    raw_text: str = dspy.InputField(desc="Raw text extracted from notes")
    theme: str = dspy.OutputField(desc="Main theme or topic of the notes. Extract the main heading or topic")
    outline: List[str] = dspy.OutputField(desc="List of key points exactly as they appear in the text")

class GenerateBlog(dspy.Signature):
    """Using the text + theme + outline, generate a blog post article in markdown format. The blog should not deviate from the text. The blog should be a single article. It should only be what is in the text."""
    raw_text: str = dspy.InputField(desc="Raw text from notes")
    theme: str = dspy.InputField(desc="Main theme or topic")
    outline: List[str] = dspy.InputField(desc="Key points for the blog post")
    blog_markdown: str = dspy.OutputField(desc="Complete blog post in markdown format")

class GenerateReactCode(dspy.Signature):
    """Generate a sophisticated React component with custom styling, layout components, and modern design patterns. 
    
    CRITICAL: Use these EXACT colors:
    - ACCENT_RED = "#dc2626" (NOT #FF6B6B or any other red)
    - BG_OFFWHITE = "#fffcf8" (NOT #FAF3E0 or any other off-white)
    
    The output should include:
    - Custom color constants using the EXACT colors above
    - Layout components (SiteLayout, TopNav, ArticleTitle)
    - Modern styling with Tailwind classes
    - Framer Motion animations
    - Lowercase navigation and headings
    - Warm, paper-like design aesthetic
    - Do NOT wrap in markdown code blocks or backticks
    """
    blog_markdown: str = dspy.InputField(desc="Blog post content in markdown format")
    react_code: str = dspy.OutputField(desc="Complete sophisticated React component with custom styling and layout components")

class GenerateBlogMetadata(dspy.Signature):
    """Generate metadata for the blog post including title, summary, tags, and other SEO-friendly information."""
    blog_markdown: str = dspy.InputField(desc="Blog post content in markdown format")
    theme: str = dspy.InputField(desc="Main theme of the blog post")
    title: str = dspy.OutputField(desc="SEO-friendly title for the blog post")
    summary: str = dspy.OutputField(desc="Brief summary (150-200 chars) for preview")
    tags: List[str] = dspy.OutputField(desc="Relevant tags for categorization")
    slug: str = dspy.OutputField(desc="URL-friendly slug for the blog post")
    reading_time: int = dspy.OutputField(desc="Estimated reading time in minutes")

class ImproveFromFeedback(dspy.Signature):
    """Using the feedback, improve the blog post article in markdown format."""
    feedback: str = dspy.InputField(desc="Feedback or validation errors to address")
    react_code: str = dspy.InputField(desc="Current React code that needs improvement")
    improved_react_code: str = dspy.OutputField(desc="Improved React code based on feedback")
