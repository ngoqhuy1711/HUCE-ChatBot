"""
Intent Detection Module - Nhận diện ý định người dùng

Module này sử dụng TF-IDF + Cosine Similarity để nhận diện intent:
1. Tính TF-IDF vector cho mỗi mẫu câu
2. Tính centroid (trọng tâm) cho mỗi intent
3. So sánh câu hỏi với các centroid bằng cosine similarity
4. Fallback bằng keyword matching nếu không đạt ngưỡng
"""

import math
from typing import Dict, List, Tuple

from .preprocess import tokenize_and_map

# Ngưỡng confidence cho intent detection
DEFAULT_INTENT_THRESHOLD = 0.35


def _compute_idf(samples: List[List[str]]) -> Dict[str, float]:
    """
    Tính IDF (Inverse Document Frequency) cho tất cả tokens

    Args:
        samples: List các câu đã được tokenize

    Returns:
        Dict mapping token -> IDF score
    """
    df: Dict[str, int] = {}  # Document frequency
    n_docs = len(samples)

    # Đếm số document chứa mỗi token
    for toks in samples:
        seen = set(toks)  # Tránh đếm trùng trong cùng 1 document
        for t in seen:
            df[t] = df.get(t, 0) + 1

    # Tính IDF với smoothing
    idf: Dict[str, float] = {}
    for t, c in df.items():
        idf[t] = math.log((1 + n_docs) / (1 + c)) + 1.0
    return idf


def _tf(toks: List[str]) -> Dict[str, float]:
    """
    Tính TF (Term Frequency) cho một câu

    Args:
        toks: List tokens của câu

    Returns:
        Dict mapping token -> TF score (normalized)
    """
    counts: Dict[str, int] = {}
    for t in toks:
        counts[t] = counts.get(t, 0) + 1

    total = float(len(toks)) or 1.0
    return {t: c / total for t, c in counts.items()}


def _centroid(vecs: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Tính centroid (trọng tâm) từ list các vector

    Args:
        vecs: List các TF-IDF vectors

    Returns:
        Centroid vector đã được normalize
    """
    # Cộng tất cả vectors
    agg: Dict[str, float] = {}
    for v in vecs:
        for k, val in v.items():
            agg[k] = agg.get(k, 0.0) + val

    # Normalize bằng L2 norm
    norm = math.sqrt(sum(v * v for v in agg.values())) or 1.0
    return {k: v / norm for k, v in agg.items()}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    """
    Tính cosine similarity giữa 2 vectors

    Args:
        a, b: Hai TF-IDF vectors

    Returns:
        Cosine similarity score (0-1)
    """
    # Tối ưu: iterate qua vector ngắn hơn
    if len(a) > len(b):
        a, b = b, a

    s = 0.0
    for k, va in a.items():
        vb = b.get(k)
        if vb is not None:
            s += va * vb
    return s


class IntentDetector:
    """
    Intent Detector sử dụng TF-IDF + Cosine Similarity

    Quy trình:
    1. Precompute TF-IDF vectors và centroids cho mỗi intent
    2. Với câu hỏi mới: tính TF-IDF vector
    3. So sánh với tất cả centroids bằng cosine similarity
    4. Nếu không đạt ngưỡng: fallback bằng keyword matching
    """

    def __init__(
        self,
        intent_samples: Dict[str, List[List[str]]],
        intent_keyword_backoff: Dict[str, str],
        threshold: float = DEFAULT_INTENT_THRESHOLD,
    ) -> None:
        """
        Khởi tạo Intent Detector

        Args:
            intent_samples: Dict mapping intent -> list of tokenized samples
            intent_keyword_backoff: Dict mapping keyword -> intent (fallback)
            threshold: Ngưỡng confidence cho TF-IDF matching
        """
        self.intent_samples = intent_samples
        self.intent_keyword_backoff = intent_keyword_backoff
        self.threshold = threshold

        # Precompute TF-IDF và centroids
        self.idf: Dict[str, float] = {}
        self.intent_centroids: Dict[str, Dict[str, float]] = {}
        self._build_intent_centroids()

    # ---------- TF-IDF utilities ----------

    def _tfidf_vec(self, toks: List[str]) -> Dict[str, float]:
        """
        Tính TF-IDF vector cho một câu

        Args:
            toks: List tokens của câu

        Returns:
            TF-IDF vector đã được normalize
        """
        tf = _tf(toks)  # Term frequency
        # TF-IDF = TF * IDF
        vec = {t: tf[t] * self.idf.get(t, 0.0) for t in tf}
        # Normalize bằng L2 norm
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def _build_intent_centroids(self) -> None:
        """
        Precompute centroids cho tất cả intents
        """
        # Gom tất cả samples để tính IDF
        all_samples: List[List[str]] = []
        for samples in self.intent_samples.values():
            all_samples.extend(samples)

        # Tính IDF cho toàn bộ corpus
        self.idf = _compute_idf(all_samples) if all_samples else {}

        # Tính centroid cho mỗi intent
        centroids: Dict[str, Dict[str, float]] = {}
        for intent, samples in self.intent_samples.items():
            # Tính TF-IDF vector cho mỗi sample
            vecs = [self._tfidf_vec(s) for s in samples]
            # Tính centroid từ các vectors
            centroids[intent] = _centroid(vecs) if vecs else {}

        self.intent_centroids = centroids

    # ---------- Public API ----------
    def detect(
        self, text: str, synonym_map: Dict[str, str], normalize_for_kw_fn
    ) -> Tuple[str, float]:
        """
        Nhận diện intent của câu hỏi

        Args:
            text: Câu hỏi từ người dùng
            synonym_map: Mapping từ đồng nghĩa
            normalize_for_kw_fn: Function chuẩn hóa văn bản cho keyword matching

        Returns:
            Tuple (intent, confidence_score)
        """
        # Bước 1: TF-IDF + Cosine Similarity
        q_tokens = tokenize_and_map(text, synonym_map)  # Tokenize và map synonyms
        q_vec = self._tfidf_vec(q_tokens)  # Tính TF-IDF vector

        # So sánh với tất cả centroids
        best_intent = ""
        best_score = 0.0
        for intent, centroid in self.intent_centroids.items():
            score = (
                _cosine(q_vec, centroid) * 1.05
            )  # Bonus cho intent bắt đầu bằng "hoi_"
            if score > best_score:
                best_score = score
                best_intent = intent

        # Nếu đạt ngưỡng: trả về kết quả TF-IDF
        if best_intent and best_score >= self.threshold:
            return best_intent, best_score

        # Bước 2: Fallback bằng keyword matching
        norm_text = normalize_for_kw_fn(text)
        for kw, mapped_intent in self.intent_keyword_backoff.items():
            if kw in norm_text:
                return mapped_intent, best_score

        # Nếu không match gì: trả về fallback
        return "fallback", best_score
