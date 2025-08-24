import os
import dspy
from typing import List
from ..config import settings
from .signatures import ExtractNotes, FindThemeAndOutline, GenerateBlog as GenerateBlogSignature, GenerateReactCode as GenerateReactCodeSignature, ImproveFromFeedback as ImproveFromFeedbackSignature, GenerateBlogMetadata
from .tools import OCRTool

print(f"Using OpenAI model: {settings.OPENAI_TEXT_MODEL}")
print(f"Using OpenAI API key: {settings.OPENAI_API_KEY}")
if settings.USE_OPENAI_VISION and settings.OPENAI_API_KEY:
    lm = dspy.LM(model=settings.OPENAI_TEXT_MODEL, api_key=settings.OPENAI_API_KEY)
else:
    lm = dspy.LM('mock')

dspy.configure(lm=lm)

class ImageToText(dspy.Module):
    def __init__(self):
        super().__init__()
        self.ocr_tool = OCRTool()

    def forward(self, image_64: str) -> dspy.Prediction:
        result = self.ocr_tool.forward(image_64)
        return dspy.Prediction(raw_text=result.get('raw text', ''))
    
class ThemeAndOutline(dspy.Module):
    def __init__(self):
        super().__init__()
        # Use ChainOfThought with one-shot examples
        self.cot = dspy.ChainOfThought(FindThemeAndOutline)

    def forward(self, raw_text: str) -> dspy.Prediction:
        return self.cot(raw_text=raw_text)

class GenerateBlog(dspy.Module):
    def __init__(self):
        super().__init__()
        self.cot = dspy.ChainOfThought(GenerateBlogSignature)

    def forward(self, raw_text: str, theme: str, outline: List[str]) -> dspy.Prediction:
        return self.cot(theme=theme, outline=outline, raw_text=raw_text)

class GenerateReactCode(dspy.Module):
    def __init__(self):
        super().__init__()
        # Use ChainOfThought with one-shot learning
        self.prompt = """ Follow the theme, colors, layout and font as the example."""
        self.cot = dspy.ChainOfThought(GenerateReactCodeSignature)

    def forward(self, blog_markdown: str) -> dspy.Prediction:
        # Generate React code
        result = self.cot(blog_markdown=blog_markdown)
        
        # Clean up markdown code blocks if present
        if result.react_code and "```" in result.react_code:
            cleaned_code = result.react_code
            if "```jsx" in cleaned_code:
                cleaned_code = cleaned_code.split("```jsx")[1]
            if "```" in cleaned_code:
                cleaned_code = cleaned_code.split("```")[0]
            result.react_code = cleaned_code.strip()
        
        # Let DSPy handle React code generation without fallback interference
        
        return result

class ImproveFromFeedback(dspy.Module):
    def __init__(self):
        super().__init__()
        self.cot = dspy.ChainOfThought(ImproveFromFeedbackSignature)

    def forward(self, feedback: str, react_code: str) -> dspy.Prediction:
        return self.cot(feedback=feedback, react_code=react_code)

class BlogMetadata(dspy.Module):
    def __init__(self):
        super().__init__()
        self.cot = dspy.ChainOfThought(GenerateBlogMetadata)

    def forward(self, blog_markdown: str, theme: str) -> dspy.Prediction:
        return self.cot(blog_markdown=blog_markdown, theme=theme)

def compile_react_with_examples(result: GenerateReactCode) -> GenerateReactCode:
    """One-shot example that teaches the exact React output style for your article. Use the exact same theme, colors, layout and font as the example."""
    example = dspy.Example(
        input={
            "blog_markdown": """# Personal Development and Creative Expression

## Desire to Become a Generalist
In my quest for personal growth, I have developed a strong desire to become a generalist. This aspiration stems from the belief that having a broad range of skills and knowledge can enhance my adaptability and creativity in various fields.

## Improving Presentation Skills
To complement my journey as a generalist, I am also focused on improving my presentation skills. Being able to present ideas effectively is crucial in any domain, and I am committed to making myself more presentable in a different way.

## Inspiration from Dwarvesh Patel
I find inspiration in figures like Dwarvesh Patel, who exemplify the qualities of a generalist. Their ability to navigate multiple disciplines and present ideas in engaging ways motivates me to pursue a similar path.

## Writing on Paper vs. Digital Formats
I enjoy the tactile experience of writing on paper, but I often wonder about the benefits of recording my thoughts in a digital format. The transition from traditional writing to digital can be challenging, yet it opens up new avenues for sharing and organizing my ideas.

## Concept of a Multi-Modal AI Agent for Note-Taking and Blogging
One innovative idea I have is to create a multi-modal AI agent that can scan my written notes, reason about how to structure them, and upload them to a digital blog. This concept could bridge the gap between my love for handwritten notes and the efficiency of digital platforms, allowing for a seamless integration of both worlds.
"""
        },
        output='''
import React from "react";
import { motion } from "framer-motion";

// Theme: warm off-white background, narrow column, lowercase nav,
// black body text, strong red accents, minimal chrome.

const ACCENT_RED = "#dc2626";   // Follow this color for the accent red
const BG_OFFWHITE = "#fffcf8";  // Follow this color for the off-white background

function SiteLayout({ children }) {
  return (
    <div className="min-h-screen" style={{ backgroundColor: BG_OFFWHITE, color: "#111827" }}>
      <TopNav />
      {children}
    </div>
  );
}

function TopNav() {
  const items = [
    { href: "/memo", label: "memo" },
    { href: "/tech", label: "tech" },
    { href: "/contact", label: "contact" },
    { href: "/home", label: "home" },
    { href: "/books", label: "books" },
    { href: "/non-technical", label: "non-technical?" },
  ];
  return (
    <header className="sticky top-0 z-30 border-b" style={{ borderColor: "#eee" }}>
      <nav className="mx-auto max-w-2xl px-4 py-3">
        <ul className="flex items-center justify-center gap-5 text-[13px] lowercase">
          {items.map((it) => (
            <li key={it.href}>
              <a
                href={it.href}
                className="text-neutral-800 hover:text-black underline underline-offset-[6px] decoration-transparent hover:decoration-black transition-colors"
              >
                {it.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}

// Article title with slanted gradient "pencil" stroke
function ArticleTitle({ title }) {
  return (
    <section className="text-center pt-6">
      <h1 className="relative inline-block text-[36px] sm:text-[40px] leading-tight font-semibold lowercase">
        {title}
        <span
          aria-hidden
          className="pointer-events-none absolute left-0 right-0 -bottom-2 h-3 rotate-[-2deg]"
          style={{ background: `linear-gradient(90deg, ${ACCENT_RED} 0%, #f87171 100%)`, opacity: 0.85 }}
        />
      </h1>
    </section>
  );
}

export default function BlogPost() {
  return (
    <SiteLayout>
      <main className="mx-auto max-w-2xl px-4 py-10">
        <ArticleTitle title="personal development and creative expression" />

        <article className="mt-14 space-y-10">
          <section id="desire-to-become-a-generalist">
            <h2 className="text-xl font-semibold lowercase">desire to become a generalist</h2>
            <p className="mt-3 text-[15px] leading-7 text-neutral-800">
              In my quest for personal growth, I have developed a strong desire to become a generalist. This aspiration stems from the belief that having a broad range of skills and knowledge can enhance my adaptability and creativity in various fields.
            </p>
          </section>

          <section id="improving-presentation-skills">
            <h2 className="text-xl font-semibold lowercase">improving presentation skills</h2>
            <p className="mt-3 text-[15px] leading-7 text-neutral-800">
              To complement my journey as a generalist, I am also focused on improving my presentation skills. Being able to present ideas effectively is crucial in any domain, and I am committed to making myself more presentable in a different way.
            </p>
          </section>

          <section id="inspiration-from-dwarvesh-patel">
            <h2 className="text-xl font-semibold lowercase">inspiration from dwarvesh patel</h2>
            <p className="mt-3 text-[15px] leading-7 text-neutral-800">
              I find inspiration in figures like Dwarvesh Patel, who exemplify the qualities of a generalist. Their ability to navigate multiple disciplines and present ideas in engaging ways motivates me to pursue a similar path.
            </p>
          </section>

          <section id="writing-on-paper-vs-digital-formats">
            <h2 className="text-xl font-semibold lowercase">writing on paper vs. digital formats</h2>
            <p className="mt-3 text-[15px] leading-7 text-neutral-800">
              I enjoy the tactile experience of writing on paper, but I often wonder about the benefits of recording my thoughts in a digital format. The transition from traditional writing to digital can be challenging, yet it opens up new avenues for sharing and organizing my ideas.
            </p>
          </section>

          <section id="multimodal-ai-agent">
            <h2 className="text-xl font-semibold lowercase">concept of a multi-modal ai agent for note-taking and blogging</h2>
            <p className="mt-3 text-[15px] leading-7 text-neutral-800">
              One innovative idea I have is to create a multi-modal AI agent that can scan my written notes, reason about how to structure them, and upload them to a digital blog. This concept could bridge the gap between my love for handwritten notes and the efficiency of digital platforms, allowing for a seamless integration of both worlds.
            </p>
          </section>
        </article>
      </main>
    </SiteLayout>
  );
}
'''
    )
   
    # Convert to proper DSPy example format
    training_example = dspy.Example(
        blog_markdown=example.input["blog_markdown"],
        react_code=example.output
    ).with_inputs("blog_markdown")
    
    print(f"Training example created with colors: {training_example.react_code.count('#dc2626')} instances of #dc2626")
    print(f"Training example created with colors: {training_example.react_code.count('#fffcf8')} instances of #fffcf8")
    
    def react_style_metric(gold, pred, trace):
        """More sophisticated metric that checks for style matching"""
        if not pred.react_code:
            return 0
        
        code = pred.react_code
        
        # Basic requirements
        has_import = "import React" in code
        has_export = "export default" in code
        
        # Style-specific requirements from training example
        has_motion = "motion" in code or "framer-motion" in code
        has_correct_red = "#dc2626" in code  # Must use exact red color
        has_correct_offwhite = "#fffcf8" in code  # Must use exact off-white color
        has_wrong_colors = "#FF6B6B" in code or "#FAF3E0" in code  # Penalize wrong colors
        has_layout_components = "SiteLayout" in code or "TopNav" in code
        has_article_structure = "ArticleTitle" in code or "article" in code
        has_custom_styling = "className=" in code and len(code) > 1000
        has_proper_nav_menu_titles = "memo" in code or "tech" in code or "contact" in code or "home" in code or "books" in code or "non-technical" in code
        
        # Calculate score based on style complexity - prioritize correct colors
        style_features = [has_motion, has_correct_red, has_correct_offwhite, has_layout_components, 
                         has_article_structure, has_custom_styling, has_proper_nav_menu_titles]
        color_penalty = 0.5 if has_wrong_colors else 0  # Heavy penalty for wrong colors
        style_score = (sum(style_features) / len(style_features)) - color_penalty
        
        # Basic features
        basic_score = (has_import + has_export) / 2
        
        # Weighted final score - prioritize style matching
        return (basic_score * 0.3) + (style_score * 0.7)
    
    opt = dspy.BootstrapFewShot(
        metric=react_style_metric,
        max_bootstrapped_demos=5,  # Increase for better learning
        max_labeled_demos=3,  # More labeled examples for color consistency
    )
    
    return opt.compile(result, trainset=[training_example])

ReactCode = compile_react_with_examples(GenerateReactCode())


image_to_text = ImageToText()
theme_and_outline = ThemeAndOutline()
generate_blog = GenerateBlog()
generate_react_code = GenerateReactCode()
improve_from_feedback = ImproveFromFeedback()
generate_metadata = BlogMetadata()




