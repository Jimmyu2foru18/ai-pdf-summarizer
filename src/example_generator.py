import re
import torch
from typing import List, Dict, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ExampleGenerator:
    """Class for extracting or generating examples for textbook topics."""
    
    def __init__(self, model_name: str = "gpt2"):
        """Initialize the example generator.
        
        Args:
            model_name: Name of the pre-trained model to use for generation
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize text generation pipeline for creating examples
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=0 if self.device == "cuda" else -1
        )
        
        # Patterns to identify examples in text
        self.example_patterns = [
            re.compile(r"example\s+\d+[\s:]+([^\n]+.*?)(?=\nexample\s+\d+|$)", re.IGNORECASE | re.DOTALL),
            re.compile(r"for example[\s:]+([^\n]+.*?)(?=\n\n|$)", re.IGNORECASE | re.DOTALL),
            re.compile(r"e\.g\.\s+([^\n]+.*?)(?=\n\n|$)", re.IGNORECASE | re.DOTALL),
            re.compile(r"\bexample\b[\s:]*([^\n]+.*?)(?=\n\n|$)", re.IGNORECASE | re.DOTALL)
        ]
        
        print(f"Example Generator initialized with {model_name} on {self.device}")
    
    def generate_examples(self, topic_text: str, num_examples: int = 2) -> List[str]:
        """Generate or extract examples for a given topic.
        
        Args:
            topic_text: The topic text to generate examples for
            num_examples: Number of examples to generate
            
        Returns:
            List of strings containing examples
        """
        # First try to extract examples from the text
        extracted_examples = self._extract_examples(topic_text)
        
        # If we found enough examples, return them
        if len(extracted_examples) >= num_examples:
            return extracted_examples[:num_examples]
        
        # If we need more examples, generate them
        additional_examples_needed = num_examples - len(extracted_examples)
        generated_examples = self._generate_examples(topic_text, additional_examples_needed)
        
        # Combine extracted and generated examples
        return extracted_examples + generated_examples
    
    def _extract_examples(self, text: str) -> List[str]:
        """Extract examples from the text using pattern matching.
        
        Args:
            text: Text to extract examples from
            
        Returns:
            List of extracted examples
        """
        examples = []
        
        # Try each pattern to find examples
        for pattern in self.example_patterns:
            matches = pattern.findall(text)
            for match in matches:
                # Clean up the example
                example = match.strip()
                if example and len(example) > 20:  # Ensure it's substantial
                    examples.append(example)
        
        return examples
    
    def _generate_examples(self, topic_text: str, num_examples: int) -> List[str]:
        """Generate examples based on the topic text.
        
        Args:
            topic_text: Text describing the topic
            num_examples: Number of examples to generate
            
        Returns:
            List of generated examples
        """
        generated_examples = []
        
        # Extract key concepts from the topic text
        key_concepts = self._extract_key_concepts(topic_text)
        
        for i in range(num_examples):
            try:
                # Create a prompt for example generation
                if key_concepts:
                    concept = key_concepts[i % len(key_concepts)]
                    prompt = f"Example of {concept}: "
                else:
                    # Fallback if no key concepts identified
                    prompt = f"Example for this topic: {topic_text[:100]}..."
                
                # Generate example
                outputs = self.generator(
                    prompt,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
                
                # Extract and clean the generated text
                generated_text = outputs[0]['generated_text']
                
                # Remove the prompt from the generated text
                example = generated_text[len(prompt):].strip()
                
                # Clean up the example
                example = self._clean_generated_example(example)
                
                if example and len(example) > 20:  # Ensure it's substantial
                    generated_examples.append(example)
                
            except Exception as e:
                print(f"Error generating example: {e}")
                # Provide a fallback example
                generated_examples.append(f"Example {i+1}: This is a placeholder example for the topic.")
        
        return generated_examples
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from the topic text.
        
        Args:
            text: Topic text to analyze
            
        Returns:
            List of key concepts
        """
        # Simple approach: look for capitalized terms or terms in quotes
        concepts = []
        
        # Look for terms in quotes
        quote_pattern = re.compile(r'"([^"]+)"')
        quotes = quote_pattern.findall(text)
        concepts.extend(quotes)
        
        # Look for capitalized terms (potential technical terms)
        cap_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b')
        caps = cap_pattern.findall(text)
        concepts.extend(caps)
        
        # If no concepts found, use the first few sentences
        if not concepts:
            sentences = sent_tokenize(text)
            if sentences:
                concepts = [sentences[0]]
        
        return concepts
    
    def _clean_generated_example(self, text: str) -> str:
        """Clean up a generated example.
        
        Args:
            text: Generated example text to clean
            
        Returns:
            Cleaned example text
        """
        # Split into sentences
        sentences = sent_tokenize(text)
        
        # Take only complete sentences, up to 5
        cleaned_sentences = sentences[:min(5, len(sentences))]
        
        # Join back into text
        cleaned_text = " ".join(cleaned_sentences)
        
        # Remove any trailing incomplete sentences
        if cleaned_text and cleaned_text[-1] not in ['.', '!', '?']:
            last_period = max(
                cleaned_text.rfind('.'),
                cleaned_text.rfind('!'),
                cleaned_text.rfind('?')
            )
            if last_period > 0:
                cleaned_text = cleaned_text[:last_period+1]
        
        return cleaned_text