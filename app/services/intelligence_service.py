import re
from typing import Tuple

class IntelligenceService:
    @staticmethod
    def calculate_read_time(text: str) -> int:
        """
        Calculate estimated read time in minutes.
        Handles HTML stripping and estimates length for truncated API content.
        """
        if not text:
            return 1
            
        # 1. Clean HTML tags (important for full-body sources like Guardian)
        clean_text = re.sub(r'<[^>]*>', ' ', text)
        
        # 2. Extract base word count
        words = re.findall(r'\w+', clean_text)
        word_count = len(words)
        
        # 3. Smart Estimation for truncated content (e.g. NewsAPI "[+2450 chars]")
        # This looks for the "[+XXXX chars]" pattern at the end of snippets
        truncation_match = re.search(r'\[\+(\d+)\s+chars\]', clean_text)
        if truncation_match:
            remaining_chars = int(truncation_match.group(1))
            # Average English word is ~5 letters + space = 6 chars
            estimated_extra_words = remaining_chars // 6
            word_count += estimated_extra_words
            
        # Average adult reading speed: 200-250 words per minute
        minutes = max(1, round(word_count / 225))
        return minutes

    @staticmethod
    def analyze_sentiment(title: str, description: str) -> str:
        """
        Analyze sentiment/urgency using a lightweight keyword approach.
        Returns: 'positive', 'neutral', or 'urgent'
        """
        combined = f"{title} {description}".lower()
        
        # Urgency Keywords
        urgent_keywords = [
            'breaking', 'urgent', 'alert', 'crisis', 'emergency', 
            'breaking news', 'just in', 'live updates', 'warns',
            'deadly', 'explosion', 'earthquake', 'attack'
        ]
        
        if any(keyword in combined for keyword in urgent_keywords):
            return "urgent"
            
        # Positive Keywords
        positive_keywords = [
            'success', 'breakthrough', 'discovery', 'hope', 'recovery',
            'wins', 'excellent', 'fantastic', 'innovative', 'solution',
            'growth', 'rise', 'benefit', 'award', 'surprised'
        ]
        
        if any(keyword in combined for keyword in positive_keywords):
            return "positive"
            
        return "neutral"
