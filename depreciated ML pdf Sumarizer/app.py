import streamlit as st
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

# Import project modules
from src.pdf_processor import PDFProcessor
from src.text_analyzer import TextAnalyzer
from src.summarizer import Summarizer
from src.example_generator import ExampleGenerator
from src.document_exporter import DocumentExporter

# Set page configuration
st.set_page_config(
    page_title="AI PDF Textbook Summarizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("AI PDF Textbook Summarizer")
st.markdown(
    """
    This tool uses AI to summarize PDF textbooks into digestible notes. 
    Upload your PDF to get started!
    
    **Features:**
    - Topic Summaries (3-5 sentences per topic)
    - Chapter Summaries (2 paragraphs per chapter)
    - Examples (1-2 practical examples per topic)
    """
)

# Sidebar for file upload and options
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = Path("temp.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.success(f"Uploaded: {uploaded_file.name}")
        
        # Processing options
        st.header("Processing Options")
        process_button = st.button("Process PDF", type="primary")

# Main content area
if 'uploaded_file' in locals() and uploaded_file is not None:
    if 'process_button' in locals() and process_button:
        with st.spinner("Processing PDF... This may take a few minutes."):
            try:
                # Initialize components
                pdf_processor = PDFProcessor(temp_path)
                text_analyzer = TextAnalyzer()
                summarizer = Summarizer()
                example_generator = ExampleGenerator()
                
                # Process PDF
                extracted_text = pdf_processor.extract_text()
                
                # Analyze text structure
                document_structure = text_analyzer.analyze(extracted_text)
                
                # Generate summaries and examples
                chapter_summaries = {}
                topic_summaries = {}
                topic_examples = {}
                
                for chapter_id, chapter_data in document_structure.items():
                    # Generate chapter summary
                    chapter_text = chapter_data['text']
                    chapter_title = chapter_data['title']
                    chapter_summaries[chapter_id] = summarizer.summarize_chapter(chapter_text)
                    
                    # Process topics in this chapter
                    for topic_id, topic_data in chapter_data['topics'].items():
                        topic_text = topic_data['text']
                        topic_title = topic_data['title']
                        
                        # Generate topic summary
                        topic_summaries[topic_id] = summarizer.summarize_topic(topic_text)
                        
                        # Generate examples for this topic
                        topic_examples[topic_id] = example_generator.generate_examples(topic_text)
                
                # Clean up temporary file
                if temp_path.exists():
                    os.remove(temp_path)
                
                # Store results in session state
                st.session_state['document_structure'] = document_structure
                st.session_state['chapter_summaries'] = chapter_summaries
                st.session_state['topic_summaries'] = topic_summaries
                st.session_state['topic_examples'] = topic_examples
                st.session_state['processing_complete'] = True
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                if temp_path.exists():
                    os.remove(temp_path)

# Display results if processing is complete
if 'processing_complete' in st.session_state and st.session_state['processing_complete']:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Chapter Summaries", "Topic Summaries", "Examples"])
    
    with tab1:
        st.header("Chapter Summaries")
        for chapter_id, chapter_data in st.session_state['document_structure'].items():
            with st.expander(f"Chapter {chapter_id}: {chapter_data['title']}"):
                st.markdown(st.session_state['chapter_summaries'][chapter_id])
    
    with tab2:
        st.header("Topic Summaries")
        for chapter_id, chapter_data in st.session_state['document_structure'].items():
            st.subheader(f"Chapter {chapter_id}: {chapter_data['title']}")
            for topic_id, topic_data in chapter_data['topics'].items():
                with st.expander(f"Topic: {topic_data['title']}"):
                    st.markdown(st.session_state['topic_summaries'][topic_id])
    
    with tab3:
        st.header("Examples")
        for chapter_id, chapter_data in st.session_state['document_structure'].items():
            st.subheader(f"Chapter {chapter_id}: {chapter_data['title']}")
            for topic_id, topic_data in chapter_data['topics'].items():
                with st.expander(f"Examples for: {topic_data['title']}"):
                    examples = st.session_state['topic_examples'][topic_id]
                    for i, example in enumerate(examples, 1):
                        st.markdown(f"**Example {i}:**\n{example}")
    
    # Export options
    st.header("Export Options")
    export_format = st.selectbox("Export Format", ["Text (.txt)", "Markdown (.md)", "Word Document (.docx)", "PowerPoint (.pptx)"])
    export_button = st.button("Export Summaries")
    
    if export_button:
        document_exporter = DocumentExporter()
        
        if export_format in ["Text (.txt)", "Markdown (.md)"]:
            # Create export content
            export_content = "# AI PDF Textbook Summarizer - Generated Summaries\n\n"
            
            # Add chapter summaries
            export_content += "## Chapter Summaries\n\n"
            for chapter_id, chapter_data in st.session_state['document_structure'].items():
                export_content += f"### Chapter {chapter_id}: {chapter_data['title']}\n\n"
                export_content += st.session_state['chapter_summaries'][chapter_id] + "\n\n"
            
            # Add topic summaries
            export_content += "## Topic Summaries\n\n"
            for chapter_id, chapter_data in st.session_state['document_structure'].items():
                export_content += f"### Chapter {chapter_id}: {chapter_data['title']}\n\n"
                for topic_id, topic_data in chapter_data['topics'].items():
                    export_content += f"#### {topic_data['title']}\n\n"
                    export_content += st.session_state['topic_summaries'][topic_id] + "\n\n"
            
            # Add examples
            export_content += "## Examples\n\n"
            for chapter_id, chapter_data in st.session_state['document_structure'].items():
                export_content += f"### Chapter {chapter_id}: {chapter_data['title']}\n\n"
                for topic_id, topic_data in chapter_data['topics'].items():
                    export_content += f"#### Examples for: {topic_data['title']}\n\n"
                    examples = st.session_state['topic_examples'][topic_id]
                    for i, example in enumerate(examples, 1):
                        export_content += f"**Example {i}:**\n{example}\n\n"
            
            # Convert to plain text if needed
            if export_format == "Text (.txt)":
                # Simple markdown to text conversion
                export_content = export_content.replace("# ", "").replace("## ", "").replace("### ", "").replace("#### ", "")
                export_content = export_content.replace("**", "")
                file_extension = "txt"
                mime_type = "text/plain"
            else:
                file_extension = "md"
                mime_type = "text/plain"
            
            # Offer download
            st.download_button(
                label="Download Summaries",
                data=export_content,
                file_name=f"textbook_summaries.{file_extension}",
                mime=mime_type
            )
        
        elif export_format == "Word Document (.docx)":
            # Generate Word document
            with st.spinner("Generating Word document..."):
                docx_file = document_exporter.export_to_word(
                    st.session_state['document_structure'],
                    st.session_state['chapter_summaries'],
                    st.session_state['topic_summaries'],
                    st.session_state['topic_examples']
                )
                
                # Offer download
                st.download_button(
                    label="Download Word Document",
                    data=docx_file,
                    file_name="textbook_summaries.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        elif export_format == "PowerPoint (.pptx)":
            # Generate PowerPoint presentation
            with st.spinner("Generating PowerPoint presentation..."):
                pptx_file = document_exporter.export_to_powerpoint(
                    st.session_state['document_structure'],
                    st.session_state['chapter_summaries'],
                    st.session_state['topic_summaries'],
                    st.session_state['topic_examples']
                )
                
                # Offer download
                st.download_button(
                    label="Download PowerPoint Presentation",
                    data=pptx_file,
                    file_name="textbook_summaries.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
    <p>AI PDF Textbook Summarizer | Learning Assistant Tool</p>
    <p><small>This tool is designed as a learning aid and should be used responsibly.</small></p>
    </div>
    """,
    unsafe_allow_html=True
)