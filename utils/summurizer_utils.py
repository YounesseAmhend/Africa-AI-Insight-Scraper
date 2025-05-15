import logging
import os
import re

import fasttext
import nltk
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class MultilingualSummarizer:
    """
    A class for detecting language and summarizing text in multiple languages
    (French, English, Arabic) without using LLMs.
    """

    def __init__(self, fasttext_model_path: str = "lid.176.bin"):
        """
        Initialize the MultilingualSummarizer with required models.
        
        Args:
            fasttext_model_path: Path to the fastText language detection model
        """
        # Load language detection model
        self.load_language_detector(fasttext_model_path)
        
        # Initialize summarizers
        self.text_rank = TextRankSummarizer()
        self.lex_rank = LexRankSummarizer()
        
        # Language-specific configurations
        self.language_configs = {
            'en': {'tokenizer': 'english', 'name': 'English'},
            'fr': {'tokenizer': 'french', 'name': 'French'},
            'ar': {'tokenizer': 'arabic', 'name': 'Arabic'}
        }
        
        logger.info("Multilingual summarizer initialized successfully")

    def load_language_detector(self, model_path: str) -> None:
        """
        Load the fastText language detection model.
        
        Args:
            model_path: Path to the fastText model
        """
        try:
            if not os.path.exists(model_path):
                logger.warning(f"FastText model not found at {model_path}. Using fallback language detection.")
                self.fasttext_model = None
            else:
                self.fasttext_model = fasttext.load_model(model_path)
                logger.info("FastText language model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading fastText model: {e}")
            self.fasttext_model = None

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the provided text.
        
        Args:
            text: Text to detect language
            
        Returns:
            Language code ('en', 'fr', 'ar', or 'unknown')
        """
        if not text.strip():
            return "unknown"
            
        # Clean text for better detection
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        # Primary detection with fastText
        if self.fasttext_model:
            try:
                predictions = self.fasttext_model.predict(clean_text, k=1)
                lang_code: str = predictions[0][0].replace("__label__", "").lower() # type: ignore
                confidence = predictions[1][0]
                
                logger.debug(f"Detected language: {lang_code} (confidence: {confidence:.4f})")
                
                # Map to supported languages
                if lang_code in ['en', 'fr', 'ar']:
                    return lang_code
                elif lang_code.lower().startswith('ar'):
                    return 'ar'
                elif lang_code.startswith('fr'):
                    return 'fr'
                elif lang_code.startswith('en'):
                    return 'en'
                else:
                    return "unknown"
            except Exception as e:
                logger.error(f"Error in language detection: {e}")
                
        # Fallback detection for common cases
        ar_chars = len(re.findall(r'[\u0600-\u06FF]', clean_text))
        if ar_chars > len(clean_text) * 0.4:
            return 'ar'
        
        # Simplistic n-gram based detection as last resort
        fr_markers = ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'au', 'est', 'sont', 'avec']
        en_markers = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'this', 'that', 'with']
        
        text_lower = clean_text.lower()
        fr_count = sum(1 for word in fr_markers if f" {word} " in f" {text_lower} ")
        en_count = sum(1 for word in en_markers if f" {word} " in f" {text_lower} ")
        
        if fr_count > en_count and fr_count > 2:
            return 'fr'
        elif en_count > 2:
            return 'en'
            
        return "unknown"

    def preprocess_arabic(self, text: str) -> str:
        """
        Preprocess Arabic text to improve summarization.
        
        Args:
            text: Arabic text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Remove diacritics (tashkeel)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        
        # Normalize alef forms
        text = re.sub(r'[إأآا]', 'ا', text)
        
        # Normalize ya and alef maksura
        text = re.sub(r'[يى]', 'ي', text)
        
        # Normalize ha and ta marbuta
        text = re.sub(r'[ةه]', 'ه', text)
        
        return text

    def summarize(self, text: str, language: str | None = None, 
                reduction_ratio: float = 0.2, algorithm: str = 'textrank') -> dict:
        """
        Summarize text in the detected or specified language using a reduction ratio.
        
        Args:
            text: Text to summarize
            language: Language code (if None, will be detected)
            reduction_ratio: Proportion of text to keep (0.2 means keep 20% of original sentences)
            algorithm: Summarization algorithm ('textrank' or 'lexrank')
            
        Returns:
            Dictionary with language, original text, and summary
        """
        if not text.strip():
            return {"language": "unknown", "summary": "", "error": "Empty text provided"}
        
        # Detect language if not provided
        detected_lang = language or self.detect_language(text)
        
        if detected_lang not in self.language_configs:
            logger.warning(f"Unsupported language detected: {detected_lang}")
            detected_lang = 'en'  # Default to English for unsupported languages
        
        # Language-specific preprocessing
        if detected_lang == 'ar':
            processed_text = self.preprocess_arabic(text)
        else:
            processed_text = text
        
        try:
            # Create parser with appropriate tokenizer
            tokenizer_lang = self.language_configs[detected_lang]['tokenizer']
            parser = PlaintextParser.from_string(processed_text, Tokenizer(tokenizer_lang))
            
            # Count original sentences
            document = parser.document
            original_sentence_count = len(document.sentences)
            
            # Calculate how many sentences to keep based on reduction ratio
            # Ensure at least 1 sentence is kept
            sentences_to_keep = max(1, int(original_sentence_count * (1 - reduction_ratio)))
            
            # Select summarization algorithm
            if algorithm.lower() == 'lexrank':
                summarizer = self.lex_rank
            else:
                summarizer = self.text_rank
                
            # Generate summary
            summary_sentences = summarizer(document, sentences_to_keep)
            summary_text = " ".join(str(sentence) for sentence in summary_sentences)
            
            language_name = self.language_configs[detected_lang]['name']
            logger.info(f"Generated summary in {language_name}: reduced from {original_sentence_count} to {len(summary_sentences)} sentences (ratio: {reduction_ratio})")
            
            return {
                "language": detected_lang,
                "language_name": language_name,
                "summary": summary_text,
                "original_sentences": original_sentence_count,
                "summary_sentences": len(summary_sentences),
                "reduction_ratio": reduction_ratio
            }
            
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return {
                "language": detected_lang,
                "language_name": self.language_configs.get(detected_lang, {}).get('name', 'Unknown'),
                "error": f"Summarization failed: {str(e)}",
                "summary": ""
            }