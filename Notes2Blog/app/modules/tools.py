import os 
import base64
import openai
import dspy
from tenacity import retry, stop_after_attempt, wait_exponential
import pytesseract
import cv2
import numpy as np

from ..config import settings

class OCRTool:
    def __init__(self):
        if settings.USE_OPENAI_VISION and settings.OPENAI_API_KEY:
            self.vision_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.vision_client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def forward(self, image_b64: str) -> dict:
        try:
            if self.vision_client:
                result = self._vision(image_b64)
                return {"raw text": result}
            else:
                result = self._tesseract(image_b64)
                return {"raw text": result}
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            # Fallback to empty string if both methods fail
            return {"raw text": ""}

    def _vision(self, image_b64: str) -> str:
        # Detect image format from base64 header or default to jpeg
        import base64
        try:
            image_data = base64.b64decode(image_b64[:100])  # Just check header
            if image_data.startswith(b'\x89PNG'):
                mime_type = "image/png"
            elif image_data.startswith(b'\xFF\xD8\xFF'):
                mime_type = "image/jpeg"
            elif image_data.startswith(b'GIF'):
                mime_type = "image/gif"
            elif image_data.startswith(b'RIFF') and b'WEBP' in image_data:
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"  # Default fallback
        except:
            mime_type = "image/jpeg"  # Fallback if detection fails
            
        image_url = f"data:{mime_type};base64,{image_b64}"
        try:
            response = self.vision_client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=[
                    {"role": "system", "content": "You are an OCR engine. Extract text faithfully."},
                    {
                    "role": "user",
                    "content": [
                    {"type": "text", "text": "Extract all readable text from this photo."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                    },
                    ],
                temperature=0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Vision Error: {str(e)} + This was the final image url: {image_url}"

    def _tesseract(self, image_b64: str) -> str:
        if pytesseract is None or cv2 is None:
            return "" # Graceful fallback
        data = base64.b64decode(image_b64)
        img_arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return pytesseract.image_to_string(gray)     