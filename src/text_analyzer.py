import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from typing import Dict, List, Tuple, Optional

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextAnalyzer:
    """Class for analyzing text structure and identifying chapters and topics."""
    
    def __init__(self):
        """Initialize the text analyzer."""
        self.chapter_patterns = [
            re.compile(r"\bchapter\s+\d+[\s:]+([^\n]+)", re.IGNORECASE),
            re.compile(r"^\d+\.\s+([^\n]+)", re.MULTILINE)
        ]
        
        self.topic_patterns = [
            re.compile(r"\b\d+\.\d+\s+([^\n]+)", re.IGNORECASE),
            re.compile(r"^[A-Z][^\n.]+\n", re.MULTILINE)
        ]
    
    def analyze(self, text_data: Dict) -> Dict:
        """Analyze text structure to identify chapters and topics.
        
        Args:
            text_data: Dictionary containing extracted text data from PDF
            
        Returns:
            Dictionary with structured document information
        """
        document_structure = {}
        
        # Extract chapters
        chapters = self._identify_chapters(text_data)
        
        # Process each chapter
        for chapter_id, chapter_info in enumerate(chapters, 1):
            chapter_text = chapter_info.get('text', '')
            chapter_title = chapter_info.get('title', f'Chapter {chapter_id}')
            
            # Extract topics within this chapter
            topics = self._identify_topics(chapter_text)
            
            # Create structured representation
            document_structure[chapter_id] = {
                'title': chapter_title,
                'text': chapter_text,
                'topics': {}
            }
            
            # Add topics to chapter
            for topic_id, topic_info in enumerate(topics, 1):
                topic_key = f"{chapter_id}.{topic_id}"
                document_structure[chapter_id]['topics'][topic_key] = {
                    'title': topic_info.get('title', f'Topic {topic_id}'),
                    'text': topic_info.get('text', '')
                }
        
        return document_structure
    
    def _identify_chapters(self, text_data: Dict) -> List[Dict]:
        """Identify chapters in the document.
        
        Args:
            text_data: Dictionary containing extracted text data
            
        Returns:
            List of dictionaries with chapter information
        """
        chapters = []
        
        # If we have TOC information, use it
        if 'toc' in text_data and text_data['toc']:
            toc_chapters = [item for item in text_data['toc'] 
                          if item.get('level') == 1 or 'chapter' in item.get('title', '').lower()]
            
            for i, chapter in enumerate(toc_chapters):
                start_page = chapter.get('page', 0)
                end_page = text_data['metadata'].get('page_count', 0)
                
                if i < len(toc_chapters) - 1:
                    end_page = toc_chapters[i+1].get('page', end_page) - 1
                
                # Extract text for this chapter
                chapter_text = ''
                for page in text_data['pages']:
                    if start_page <= page.get('page_num', 0) <= end_page:
                        chapter_text += page.get('text', '') + '\n\n'
                
                chapters.append({
                    'title': chapter.get('title', f'Chapter {i+1}'),
                    'text': chapter_text.strip()
                })
        
        # If no chapters found via TOC, try pattern matching
        if not chapters:
            full_text = '\n\n'.join([page.get('text', '') for page in text_data.get('pages', [])])
            
            # Try each pattern
            for pattern in self.chapter_patterns:
                matches = pattern.finditer(full_text)
                positions = []
                
                for match in matches:
                    title = match.group(1).strip() if match.groups() else match.group(0).strip()
                    positions.append((match.start(), title))
                
                if positions:
                    # Sort by position
                    positions.sort()
                    
                    # Extract chapter text
                    for i, (start_pos, title) in enumerate(positions):
                        end_pos = len(full_text)
                        if i < len(positions) - 1:
                            end_pos = positions[i+1][0]
                        
                        chapter_text = full_text[start_pos:end_pos].strip()
                        chapters.append({
                            'title': title,
                            'text': chapter_text
                        })
                    
                    break  # Stop if we found chapters with this pattern
        
        # If still no chapters found, create a single chapter
        if not chapters:
            full_text = '\n\n'.join([page.get('text', '') for page in text_data.get('pages', [])])
            chapters.append({
                'title': 'Chapter 1',
                'text': full_text
            })
        
        return chapters
    
    def _identify_topics(self, chapter_text: str) -> List[Dict]:
        """Identify topics within a chapter.
        
        Args:
            chapter_text: String containing the chapter text
            
        Returns:
            List of dictionaries with topic information
        """
        topics = []
        
        # Try each pattern
        for pattern in self.topic_patterns:
            matches = pattern.finditer(chapter_text)
            positions = []
            
            for match in matches:
                title = match.group(1).strip() if match.groups() else match.group(0).strip()
                positions.append((match.start(), title))
            
            if positions:
                # Sort by position
                positions.sort()
                
                # Extract topic text
                for i, (start_pos, title) in enumerate(positions):
                    end_pos = len(chapter_text)
                    if i < len(positions) - 1:
                        end_pos = positions[i+1][0]
                    
                    topic_text = chapter_text[start_pos:end_pos].strip()
                    topics.append({
                        'title': title,
                        'text': topic_text
                    })
                
                break  # Stop if we found topics with this pattern
        
        # If no topics found, try to split by paragraphs
        if not topics:
            paragraphs = chapter_text.split('\n\n')
            
            # Group paragraphs into topics (simple approach)
            current_topic = ''
            current_title = 'Topic'
            
            for i, para in enumerate(paragraphs):
                # If paragraph looks like a heading, start a new topic
                if len(para.strip()) < 100 and para.strip().isupper():
                    # Save previous topic if it exists
                    if current_topic:
                        topics.append({
                            'title': current_title,
                            'text': current_topic.strip()
                        })
                    
                    current_title = para.strip()
                    current_topic = ''
                else:
                    current_topic += para + '\n\n'
            
            # Add the last topic
            if current_topic:
                topics.append({
                    'title': current_title,
                    'text': current_topic.strip()
                })
        
        # If still no topics found, create a single topic
        if not topics:
            topics.append({
                'title': 'Main Topic',
                'text': chapter_text
            })
        
        return topics
    
    def extract_examples(self, text: str) -> List[str]:
        """Extract potential examples from text.
        
        Args:
            text: String containing the text to analyze
            
        Returns:
            List of strings containing potential examples
        """
        examples = []
        
        # Look for common example indicators
        example_patterns = [
            re.compile(r"example\s+\d+[\s:]+([^\n]+.*?)(?=\nexample\s+\d+|$)", re.IGNORECASE | re.DOTALL),
            re.compile(r"for example[\s:]+([^\n]+.*?)(?=\n\n|$)", re.IGNORECASE | re.DOTALL),
            re.compile(r"e\.g\.\s+([^\n]+.*?)(?=\n\n|$)", re.IGNORECASE | re.DOTALL)
        ]
        
        for pattern in example_patterns:
            matches = pattern.findall(text)
            for match in matches:
                examples.append(match.strip())
        
        return examples