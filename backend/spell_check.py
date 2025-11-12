
from spellchecker import SpellChecker

spell = SpellChecker()

def check_text_quality(text):
    """Score text quality based on spelling"""
    if not text or len(text) < 5:
        return 50
    
    words = text.split()
    if len(words) == 0:
        return 0
    
    misspelled = spell.unknown(words)
    correct_count = len(words) - len(misspelled)
    quality_score = (correct_count / len(words)) * 100
    
    return round(quality_score, 2)

def is_gibberish(text):
    """Check if text is random gibberish"""
    words = text.split()
    if len(words) == 0:
        return True
    
    misspelled = spell.unknown(words)
    gibberish_ratio = len(misspelled) / len(words)
    
    return gibberish_ratio > 0.6

