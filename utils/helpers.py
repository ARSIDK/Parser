import re
import json
from typing import List, Dict, Any
from datetime import datetime

def clean_text(text: str) -> str:
    """Очистка текста"""
    
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-.,;:?!()\[\]{}@#№$%^&*+=<>]', '', text)
    
    return text.strip()

def extract_phone(text: str) -> List[str]:
    
    if not text:
        return []
    
    phone_pattern = r'\+?[\d\s\-\(\)]{10,20}'
    phones = re.findall(phone_pattern, text)
    
    return [clean_text(p) for p in phones]

def extract_email(text: str) -> List[str]:
    
    if not text:
        return []
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    return emails

def classify_by_keywords(text: str, keywords: Dict[str, List[str]]) -> str:    
    if not text:
        return "unknown"
    
    text_lower = text.lower()
    
    for category, words in keywords.items():
        for word in words:
            if word in text_lower:
                return category
    
    return "other"

def save_to_json(data: List[Dict[str, Any]], filename: str):
    """Сохранение в JSON"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(filename: str) -> List[Dict[str, Any]]:
    """Загрузка из JSON"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)