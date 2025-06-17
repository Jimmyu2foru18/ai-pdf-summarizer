# AI PDF Textbook Summarizer

This project uses open-source AI to summarize PDF textbooks into digestible notes. It extracts text from PDFs and generates concise summaries at different levels of detail:

- **Topic Summaries**: 3-5 sentences per topic
- **Chapter Summaries**: 2 paragraphs per chapter
- **Examples**: 1-2 practical examples per topic

## Purpose

This tool is designed as a learning assistant to help students and researchers digest complex textbook material more efficiently. It is not intended to replace thorough reading or complete assignments, but rather to provide a supplementary learning aid.

## Features

- PDF text extraction
- Chapter and topic identification
- AI-powered summarization
- Example generation for each topic
- User-friendly interface
- Works with various academic subjects

## Installation

```bash
# Clone the repository
git clone https://github.com/jimmyu2foru18/ai-pdf-summarizer.git
cd ai-pdf-summarizer

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
python app.py
```

Once the application is running:

1. Upload your PDF textbook
2. The system will process the document and identify chapters and topics
3. View generated summaries at different levels of detail
4. Export summaries in various formats (Text, Markdown, Word Document, PowerPoint)

## Dependencies

- Python 3.8+
- PyPDF2 (PDF extraction)
- NLTK (Natural Language Processing)
- Transformers (Hugging Face for AI models)
- Streamlit (User Interface)
- Sentence-Transformers (Text embeddings)

## Project Structure

```
.
├── app.py                  # Main application entry point
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── src/
│   ├── pdf_processor.py    # PDF extraction and processing
│   ├── text_analyzer.py    # Chapter and topic identification
│   ├── summarizer.py       # AI summarization logic
│   ├── example_generator.py # Example generation logic
│   ├── document_exporter.py # Export to Word and PowerPoint formats
│   └── utils.py            # Utility functions
└── models/                 # Directory for storing/caching AI models
```

## License

MIT

## Disclaimer

This tool is intended as a learning aid and should be used responsibly. It is not designed to replace thorough study or complete academic assignments.