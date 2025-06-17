import os
import re
import nltk
from typing import List, Dict, Optional
from pathlib import Path

# Ensure NLTK resources are available
def ensure_nltk_resources():
    """Download required NLTK resources if not already available."""
    resources = ['punkt', 'stopwords']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource)

# Text cleaning functions
def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using NLTK.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    ensure_nltk_resources()
    return nltk.sent_tokenize(text)

# File handling functions
def get_temp_file_path(prefix: str = "temp", suffix: str = ".txt") -> Path:
    """Generate a temporary file path.
    
    Args:
        prefix: Prefix for the temporary file
        suffix: Suffix for the temporary file
        
    Returns:
        Path object for the temporary file
    """
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False)
    temp_file.close()
    return Path(temp_file.name)

def ensure_dir_exists(dir_path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)

# Model handling functions
def get_model_path(model_name: str) -> Path:
    """Get the path for storing a model locally.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Path object for the model directory
    """
    # Replace slashes with underscores for filesystem safety
    safe_name = model_name.replace('/', '_')
    
    # Get the models directory
    models_dir = Path(__file__).parent.parent / "models"
    ensure_dir_exists(models_dir)
    
    # Return the path for this specific model
    model_path = models_dir / safe_name
    ensure_dir_exists(model_path)
    
    return model_path