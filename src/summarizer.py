import os
import torch
from typing import List, Dict, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Summarizer:
    """Class for generating summaries of textbook content."""
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """Initialize the summarizer with the specified model.
        
        Args:
            model_name: Name of the pre-trained model to use for summarization
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize the summarization pipeline
        self.summarizer = pipeline(
            "summarization", 
            model=model_name,
            device=0 if self.device == "cuda" else -1
        )
        
        # Initialize sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"Summarizer initialized with {model_name} on {self.device}")
    
    def summarize_topic(self, text: str, max_length: int = 150) -> str:
        """Generate a concise summary of a topic (3-5 sentences).
        
        Args:
            text: The topic text to summarize
            max_length: Maximum length of the summary in tokens
            
        Returns:
            String containing the topic summary
        """
        # Check if text is too short to summarize
        if len(text.split()) < 100:
            return text
        
        # Split into chunks if text is too long
        chunks = self._split_into_chunks(text)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            try:
                summary = self.summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=30,
                    do_sample=False
                )[0]['summary_text']
                
                chunk_summaries.append(summary)
            except Exception as e:
                print(f"Error summarizing chunk: {e}")
                # If summarization fails, use the first few sentences
                sentences = sent_tokenize(chunk)
                if sentences:
                    chunk_summaries.append(" ".join(sentences[:3]))
        
        # Combine chunk summaries
        combined_summary = " ".join(chunk_summaries)
        
        # Ensure the summary is 3-5 sentences
        sentences = sent_tokenize(combined_summary)
        if len(sentences) > 5:
            # Select the most important sentences using embeddings
            selected_sentences = self._select_important_sentences(sentences, text, 5)
            combined_summary = " ".join(selected_sentences)
        
        return combined_summary
    
    def summarize_chapter(self, text: str, max_length: int = 300) -> str:
        """Generate a two-paragraph summary of a chapter.
        
        Args:
            text: The chapter text to summarize
            max_length: Maximum length of the summary in tokens
            
        Returns:
            String containing the chapter summary
        """
        # Check if text is too short to summarize
        if len(text.split()) < 200:
            return text
        
        # Split into chunks if text is too long
        chunks = self._split_into_chunks(text)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            try:
                summary = self.summarizer(
                    chunk,
                    max_length=max_length // len(chunks),
                    min_length=50,
                    do_sample=False
                )[0]['summary_text']
                
                chunk_summaries.append(summary)
            except Exception as e:
                print(f"Error summarizing chunk: {e}")
                # If summarization fails, use the first few sentences
                sentences = sent_tokenize(chunk)
                if sentences:
                    chunk_summaries.append(" ".join(sentences[:5]))
        
        # Combine chunk summaries
        combined_summary = " ".join(chunk_summaries)
        
        # Format as two paragraphs
        sentences = sent_tokenize(combined_summary)
        if len(sentences) >= 6:
            # Divide sentences into two paragraphs
            mid_point = len(sentences) // 2
            paragraph1 = " ".join(sentences[:mid_point])
            paragraph2 = " ".join(sentences[mid_point:])
            formatted_summary = f"{paragraph1}\n\n{paragraph2}"
        else:
            formatted_summary = combined_summary
        
        return formatted_summary
    
    def _split_into_chunks(self, text: str, max_chunk_size: int = 1024) -> List[str]:
        """Split text into chunks of manageable size for the model.
        
        Args:
            text: Text to split
            max_chunk_size: Maximum number of tokens per chunk
            
        Returns:
            List of text chunks
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            # Approximate token count (words + some extra for tokenization)
            sentence_size = len(sentence.split()) + 5
            
            if current_size + sentence_size > max_chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _select_important_sentences(self, sentences: List[str], original_text: str, n: int = 5) -> List[str]:
        """Select the most important sentences based on semantic similarity to the original text.
        
        Args:
            sentences: List of sentences to select from
            original_text: The original text to compare against
            n: Number of sentences to select
            
        Returns:
            List of selected sentences
        """
        # Get embeddings for sentences and original text
        sentence_embeddings = self.sentence_model.encode(sentences)
        text_embedding = self.sentence_model.encode([original_text])[0]
        
        # Calculate similarity scores
        similarities = []
        for i, sent_emb in enumerate(sentence_embeddings):
            similarity = torch.nn.functional.cosine_similarity(
                torch.tensor(sent_emb).unsqueeze(0),
                torch.tensor(text_embedding).unsqueeze(0)
            ).item()
            similarities.append((i, similarity))
        
        # Sort by similarity and select top n
        similarities.sort(key=lambda x: x[1], reverse=True)
        selected_indices = [idx for idx, _ in similarities[:n]]
        selected_indices.sort()  # Sort to maintain original order
        
        return [sentences[idx] for idx in selected_indices]