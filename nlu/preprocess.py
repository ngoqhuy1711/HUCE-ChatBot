import re
from typing import Dict, List, Set

import unicodedata

try:
    from underthesea import word_tokenize
except Exception:  # fallback if underthesea is not installed
    def word_tokenize(text: str, format=None):
        return text.split()

# Minimal Vietnamese stopword set (extendable)
VI_STOPWORDS: Set[str] = {
    "là", "làm", "và", "hoặc", "nhưng", "thì", "lúc", "khi", "ở", "của",
    "cho", "với", "đến", "tới", "từ", "có", "được", "nhé", "ạ", "à", "ư",
    "mình", "bạn", "xin", "chào", "ơi", "giúp", "hỏi", "cho", "xem", "bao",
}


def normalize_text(text) -> str:
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    text = text.lower().strip()
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r"[^\w\sáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_map(text: str, synonym_map: Dict[str, str]) -> List[str]:
    norm = normalize_text(text)
    try:
        raw = word_tokenize(norm, format='text')
        toks = raw.split()
    except Exception:
        toks = norm.split()
    mapped = [synonym_map.get(tok, tok) for tok in toks]
    filtered = [t for t in mapped if t not in VI_STOPWORDS]
    return filtered
