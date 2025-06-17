import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Import project modules
from src.pdf_processor import PDFProcessor
from src.text_analyzer import TextAnalyzer
from src.summarizer import Summarizer
from src.example_generator import ExampleGenerator
from src.utils import ensure_nltk_resources

def test_summarizer(pdf_path):
    """Test the PDF summarizer functionality.
    
    Args:
        pdf_path: Path to the PDF file to summarize
    """
    print(f"\nTesting PDF summarizer with file: {pdf_path}")
    print("-" * 80)
    
    # Ensure NLTK resources are available
    ensure_nltk_resources()
    
    # Initialize components
    print("Initializing components...")
    pdf_processor = PDFProcessor(pdf_path)
    text_analyzer = TextAnalyzer()
    summarizer = Summarizer()
    example_generator = ExampleGenerator()
    
    # Process PDF
    print("\nExtracting text from PDF...")
    extracted_data = pdf_processor.extract_text()
    print(f"Extracted {len(extracted_data['pages'])} pages")
    
    # Analyze text structure
    print("\nAnalyzing document structure...")
    document_structure = text_analyzer.analyze(extracted_data)
    print(f"Identified {len(document_structure)} chapters")
    
    # Process each chapter
    for chapter_id, chapter_data in document_structure.items():
        print(f"\n{'=' * 80}")
        print(f"Chapter {chapter_id}: {chapter_data['title']}")
        print(f"{'=' * 80}")
        
        # Generate chapter summary
        print("\nChapter Summary:")
        chapter_text = chapter_data['text']
        chapter_summary = summarizer.summarize_chapter(chapter_text)
        print(chapter_summary)
        
        # Process topics in this chapter
        print(f"\nTopics in Chapter {chapter_id}:")
        for topic_id, topic_data in chapter_data['topics'].items():
            print(f"\n{'-' * 80}")
            print(f"Topic: {topic_data['title']}")
            print(f"{'-' * 80}")
            
            topic_text = topic_data['text']
            
            # Generate topic summary
            print("\nTopic Summary:")
            topic_summary = summarizer.summarize_topic(topic_text)
            print(topic_summary)
            
            # Generate examples for this topic
            print("\nExamples:")
            examples = example_generator.generate_examples(topic_text)
            for i, example in enumerate(examples, 1):
                print(f"Example {i}: {example}")
            
            # Limit to just a few topics for testing
            if topic_id.endswith(".3"):
                break
        
        # Limit to just one chapter for testing
        break

if __name__ == "__main__":
    # Check if a PDF file was provided
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
        if pdf_path.exists() and pdf_path.suffix.lower() == ".pdf":
            test_summarizer(pdf_path)
        else:
            print(f"Error: {pdf_path} is not a valid PDF file.")
    else:
        print("Usage: python test_summarizer.py <path_to_pdf>")
        print("\nNo PDF file provided. Please provide a PDF file path as an argument.")
        print("Example: python test_summarizer.py sample_textbook.pdf")