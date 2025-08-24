# Notes2Blog

Convert handwritten notes to blog posts using AI-powered OCR and natural language processing.

## Overview

Notes2Blog is an intelligent system that transforms handwritten notes into well-structured blog posts. It uses LangGraph for workflow orchestration and DSPy for optimized language model interactions.

## Features

- 📝 **OCR Processing**: Extract text from handwritten notes and images
- 🤖 **AI-Powered**: Uses advanced language models for content generation
- 📊 **Metadata Generation**: Automatically creates titles, summaries, and tags
- 🔄 **Workflow Orchestration**: Built with LangGraph for robust processing pipelines
- 🎯 **Optimized Prompts**: Uses DSPy for efficient and reliable AI interactions
- 🚀 **FastAPI Backend**: High-performance REST API
- 📱 **Portfolio Ready**: Easy integration with existing portfolio websites

## Quick Start

### Prerequisites

- Python 3.10+ 
- Poetry (recommended) or pip

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Notes2Blog

# Install dependencies with Poetry (recommended)
poetry install

# Or with pip
pip install -r app/requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other AI service keys
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

### Running the Application

```bash
# Activate virtual environment (if using Poetry)
poetry shell

# Start the server
python -m uvicorn app.main:app --reload

# The API will be available at http://localhost:8000
```

## API Usage

### Upload and Process Notes

1. **Upload an image**:
   ```bash
   curl -X POST "http://localhost:8000/ingest" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@your_notes.jpg"
   ```

2. **Process the image to blog**:
   ```bash
   curl -X POST "http://localhost:8000/process" \
        -H "Content-Type: application/json" \
        -d '{"image_path": "path_from_upload_response"}'
   ```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
Notes2Blog/
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── graph.py           # LangGraph workflow definitions
│   ├── state.py           # Application state management
│   ├── storage.py         # File storage utilities
│   ├── validators.py      # Input validation
│   ├── config.py          # Configuration management
│   └── modules/           # Core processing modules
│       ├── pipeline.py    # Main processing pipeline
│       ├── signatures.py  # DSPy signature definitions
│       └── tools.py       # Utility functions and tools
├── uploads/               # Uploaded image storage
├── outputs/               # Generated blog post storage
├── .gitignore            # Git ignore patterns
├── pyproject.toml        # Poetry configuration
├── requirements.txt      # Pip requirements
└── README.md            # This file
```

## Integration Examples

See `QUICK_START_GUIDE.md` for detailed integration examples including:
- Simple HTML interface
- React/Next.js components
- Deployment guides

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### Code Formatting

```bash
# Format code with black
black app/

# Check formatting
black --check app/
```

### Adding New Features

1. Define new DSPy signatures in `app/modules/signatures.py`
2. Implement processing logic in `app/modules/pipeline.py`
3. Update the LangGraph workflow in `app/graph.py`
4. Add API endpoints in `app/main.py`

## Configuration

The application can be configured through environment variables or the `app/config.py` file:

- `OPENAI_API_KEY`: Required for AI processing
- `UPLOAD_DIR`: Directory for uploaded files (default: `uploads/`)
- `OUTPUT_DIR`: Directory for generated content (default: `outputs/`)
- `MAX_FILE_SIZE`: Maximum upload file size in bytes

## Deployment

### Quick Deploy Options

1. **Railway**: `railway up`
2. **Render**: Connect GitHub repo and deploy
3. **Heroku**: `git push heroku main`
4. **Docker**: Use the included Dockerfile

### Environment Variables for Production

```bash
OPENAI_API_KEY=your_production_key
ENVIRONMENT=production
MAX_FILE_SIZE=10485760  # 10MB
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Format code: `black app/`
5. Run tests: `pytest`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact [your-email@example.com].

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Powered by [DSPy](https://github.com/stanfordnlp/dspy) for optimized AI interactions
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- OCR capabilities provided by [Tesseract](https://github.com/tesseract-ocr/tesseract)
