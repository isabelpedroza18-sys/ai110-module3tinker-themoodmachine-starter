# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
import string
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        TODO: Improve this method.

        Right now, it does the minimum:
          - Strips leading and trailing whitespace
          - Converts everything to lowercase
          - Splits on spaces

        Ideas to improve:
          - Remove punctuation
          - Handle simple emojis separately (":)", ":-(", "🥲", "😂")
          - Normalize repeated characters ("soooo" -> "soo")
        """
        cleaned = text.strip().lower()
        
        # Extract emojis and emoticons first (before removing punctuation)
        # Matches Unicode emojis and common emoticons like :), :(, :D, etc.
        emoji_pattern = r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]|[\U00002702-\U000027B0]|:\)|:\(|:D|;-?\)|:-?P|:-?/'
        emojis = re.findall(emoji_pattern, cleaned)
        
        # Remove emojis temporarily to process text
        cleaned = re.sub(emoji_pattern, '', cleaned)
        
        # Remove punctuation
        cleaned = ''.join(char for char in cleaned if char not in string.punctuation)
        
        # Normalize repeated characters: replace 3+ identical chars with 2
        # E.g., "soooo" -> "soo", "!!!" -> "!!"
        cleaned = re.sub(r'(.)\1{2,}', r'\1\1', cleaned)
        
        # Split on whitespace
        tokens = cleaned.split()
        
        # Add extracted emojis back as individual tokens
        tokens.extend(emojis)
        
        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric "mood score" for the given text.

        Positive words increase the score.
        Negative words decrease the score.

        TODO: You must choose AT LEAST ONE modeling improvement to implement.
        For example:
          - Handle simple negation such as "not happy" or "not bad"
          - Count how many times each word appears instead of just presence
          - Give some words higher weights than others (for example "hate" < "annoyed")
          - Treat emojis or slang (":)", "lol", "💀") as strong signals
        """
        # Define weighted sentiment words (higher weight = stronger signal)
        weighted_positive = {
            "love": 2, "amazing": 2, "awesome": 2, "great": 1, 
            "good": 1, "excited": 1, "fun": 1, "awesome": 1
        }
        weighted_negative = {
            "hate": 2, "terrible": 2, "awful": 2, "bad": 1, 
            "sad": 1, "upset": 1, "stressed": 1, "tired": 1, "angry": 1
        }
        
        # Define emoji/emoticon sentiment signals (stronger signals: +/-2)
        positive_emojis = {":)", ";)", "😂", "🔥", "💪", "💯", "😎"}
        negative_emojis = {":(", "😢", "😔", "💔", "😕"}
        
        # Words that negate sentiment (flip positive/negative)
        negations = {"not", "never", "no", "isn't", "aren't", "wasn't", "don't", "didn't"}
        
        tokens = self.preprocess(text)
        score = 0
        
        for i, token in enumerate(tokens):
            # Check if previous token is a negation word
            is_negated = (i > 0 and tokens[i-1] in negations)
            
            # Priority 1: Check weighted positive words (higher weight)
            if token in weighted_positive:
                weight = weighted_positive[token]
                score += -weight if is_negated else weight
            # Priority 2: Check regular positive words
            elif token in self.positive_words:
                score += -1 if is_negated else 1
            # Priority 3: Check weighted negative words
            elif token in weighted_negative:
                weight = weighted_negative[token]
                score += weight if is_negated else -weight
            # Priority 4: Check regular negative words
            elif token in self.negative_words:
                score += 1 if is_negated else -1
            # Priority 5: Check positive emojis (strong signal: +2)
            elif token in positive_emojis:
                score += -2 if is_negated else 2
            # Priority 6: Check negative emojis (strong signal: -2)
            elif token in negative_emojis:
                score += 2 if is_negated else -2
        
        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        The default mapping is:
          - score > 0  -> "positive"
          - score < 0  -> "negative"
          - score == 0 -> "neutral"

        TODO: You can adjust this mapping if it makes sense for your model.
        For example:
          - Use different thresholds (for example score >= 2 to be "positive")
          - Add a "mixed" label for scores close to zero
        Just remember that whatever labels you return should match the labels
        you use in TRUE_LABELS in dataset.py if you care about accuracy.
        """
        score = self.score_text(text)
        
        # Use stricter thresholds to reduce false positives/negatives
        if score >= 2:
            return "positive"
        elif score <= -2:
            return "negative"
        else:
            return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
