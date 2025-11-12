"""
NLP Pipeline chính cho Chatbot Tư vấn Tuyển sinh HUCE

File này chứa class NLPPipeline - thành phần trung tâm xử lý ngôn ngữ tự nhiên:
- Tiền xử lý văn bản (normalize, tokenize)
- Nhận diện intent (ý định của người dùng)
- Trích xuất entity (thực thể trong câu hỏi)
- Tích hợp với Underthesea cho tiếng Việt
"""

import csv
import os
from typing import List, Dict, Tuple, Any

# Import Underthesea cho xử lý tiếng Việt
try:
    from underthesea import word_tokenize
except ImportError:  # fallback nếu không cài đặt được underthesea

    def word_tokenize(text: str):
        return text.split()

# Import NER (Named Entity Recognition) từ Underthesea
try:
    from underthesea import ner as uts_ner  # type: ignore
except ImportError:
    uts_ner = None  # type: ignore

# Import các module con của NLP pipeline
try:
    from .preprocess import normalize_text as ext_normalize_text
    from .preprocess import tokenize_and_map as ext_tokenize_and_map
except ImportError:
    ext_normalize_text = None  # type: ignore
    ext_tokenize_and_map = None  # type: ignore
try:
    from .intent import IntentDetector
except ImportError:
    IntentDetector = None  # type: ignore
try:
    from .entities import EntityExtractor
except ImportError:
    EntityExtractor = None  # type: ignore

# Import constants từ config module
from config import DATA_DIR, get_intent_threshold

# Ngưỡng intent mặc định (dùng từ config)
DEFAULT_INTENT_THRESHOLD = get_intent_threshold()


def _normalize_text(text) -> str:
    """
    Chuẩn hóa văn bản (fallback function)

    Args:
        text: Văn bản cần chuẩn hóa

    Returns:
        Văn bản đã được chuẩn hóa (lowercase, strip)
    """
    if ext_normalize_text is not None:
        return ext_normalize_text(text)
    # fallback minimal - chỉ lowercase và strip
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return text.lower().strip()


def _load_synonyms(path: str) -> Dict[str, str]:
    """
    Load từ điển từ đồng nghĩa từ file CSV

    Args:
        path: Đường dẫn file synonym.csv

    Returns:
        Dict mapping từ đồng nghĩa -> từ chuẩn
    """
    mapping: Dict[str, str] = {}
    if not os.path.isfile(path):
        return mapping

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        _ = next(reader, None)  # Skip header
        for row in reader:
            if len(row) < 2:
                continue
            src = _normalize_text(row[0])  # Từ gốc
            dst = _normalize_text(row[1])  # Từ chuẩn
            if src and dst:
                mapping[src] = dst
    return mapping


class NLPPipeline:
    """
    Pipeline xử lý ngôn ngữ tự nhiên chính

    Chức năng:
    - Nhận diện intent (ý định người dùng)
    - Trích xuất entity (thực thể trong câu hỏi)
    - Xử lý từ đồng nghĩa
    - Fallback bằng keyword matching
    """

    def __init__(
            self,
            data_dir: str = DATA_DIR,
            intent_threshold: float = DEFAULT_INTENT_THRESHOLD,
    ) -> None:
        """
        Khởi tạo NLP Pipeline

        Args:
            data_dir: Thư mục chứa dữ liệu CSV/JSON
            intent_threshold: Ngưỡng nhận diện intent
        """
        self.data_dir = data_dir
        self.intent_threshold = intent_threshold

        # Load từ điển từ đồng nghĩa
        self.syn_map = _load_synonyms(os.path.join(data_dir, "synonym.csv"))

        # Load mẫu câu cho intent detection
        self.intent_samples = self._load_intent_samples(
            os.path.join(data_dir, "intent.csv")
        )

        # Keyword backoff rules - fallback khi TF-IDF không nhận diện được
        # Cần CẢ 2 versions: có dấu VÀ không dấu (vì user có thể nhập cả 2 cách)
        self.intent_keyword_backoff: Dict[str, str] = {
            # Có dấu
            "điểm sàn": "hoi_diem_san",
            "điểm chuẩn": "hoi_diem_chuan",
            "chỉ tiêu": "hoi_chi_tieu",
            "học phí": "hoi_hoc_phi",
            "học bổng": "hoi_hoc_bong",
            "phương thức": "hoi_phuong_thuc",
            "điều kiện": "hoi_dieu_kien",
            "thời gian": "hoi_thoi_gian_dk",
            "kênh nộp": "hoi_kenh_nop_ho_so",
            "nộp hồ sơ": "hoi_kenh_nop_ho_so",
            "tổ hợp": "hoi_to_hop_mon",
            "khối thi": "hoi_khoi_thi",
            # Không dấu (cho trường hợp user nhập không dấu)
            "diem san": "hoi_diem_san",
            "diem chuan": "hoi_diem_chuan",
            "chi tieu": "hoi_chi_tieu",
            "hoc phi": "hoi_hoc_phi",
            "hoc bong": "hoi_hoc_bong",
            "phuong thuc": "hoi_phuong_thuc",
            "dieu kien": "hoi_dieu_kien",
            "thoi gian": "hoi_thoi_gian_dk",
            "kenh nop": "hoi_kenh_nop_ho_so",
            "nop ho so": "hoi_kenh_nop_ho_so",
            "to hop": "hoi_to_hop_mon",
            "khoi thi": "hoi_khoi_thi",
            "mã ngành": "hoi_ma_nganh",
            "ma nganh": "hoi_ma_nganh",
            # Major description queries - có dấu
            "mô tả ngành": "hoi_nganh_hoc",
            "giới thiệu ngành": "hoi_nganh_hoc",
            "học gì": "hoi_nganh_hoc",
            "là gì": "hoi_nganh_hoc",
            "ra làm gì": "hoi_nganh_hoc",
            "học những gì": "hoi_nganh_hoc",
            "đào tạo gì": "hoi_nganh_hoc",
            "chương trình đào tạo": "hoi_nganh_hoc",
            "cho biết về ngành": "hoi_nganh_hoc",
            "thông tin về ngành": "hoi_nganh_hoc",
            "tìm hiểu về ngành": "hoi_nganh_hoc",
            "về ngành": "hoi_nganh_hoc",
            "giới thiệu về": "hoi_nganh_hoc",
            # Major description queries - không dấu
            "mo ta nganh": "hoi_nganh_hoc",
            "gioi thieu nganh": "hoi_nganh_hoc",
            "hoc gi": "hoi_nganh_hoc",
            "la gi": "hoi_nganh_hoc",
            "ra lam gi": "hoi_nganh_hoc",
            "hoc nhung gi": "hoi_nganh_hoc",
            "dao tao gi": "hoi_nganh_hoc",
            "chuong trinh dao tao": "hoi_nganh_hoc",
            "cho biet ve nganh": "hoi_nganh_hoc",
            "thong tin ve nganh": "hoi_nganh_hoc",
            "tim hieu ve nganh": "hoi_nganh_hoc",
            "ve nganh": "hoi_nganh_hoc",
            "gioi thieu ve": "hoi_nganh_hoc",
            # Common terms
            "phi": "hoi_hoc_phi",
            "deadline": "hoi_thoi_gian_dk",
            "liên hệ": "hoi_lien_he",
            "v-sat": "hoi_phuong_thuc",
            "vsat": "hoi_phuong_thuc",
        }

        # Khởi tạo các detector (có thể None nếu import thất bại)
        self._intent_detector = (
            IntentDetector(
                self.intent_samples, self.intent_keyword_backoff, self.intent_threshold
            )
            if IntentDetector
            else None
        )
        self._entity_extractor = (
            EntityExtractor(self.data_dir, os.path.join(data_dir, "entity.json"))
            if EntityExtractor
            else None
        )

    # ---------- Loaders - Các hàm load dữ liệu ----------

    def _load_intent_samples(self, path: str) -> Dict[str, List[List[str]]]:
        """
        Load mẫu câu cho intent detection từ file CSV

        Args:
            path: Đường dẫn file intent.csv

        Returns:
            Dict mapping intent -> list of tokenized samples
        """
        intent_to_samples: Dict[str, List[List[str]]] = {}
        if not os.path.isfile(path):
            return intent_to_samples

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                utt = _normalize_text(r.get("utterance") or "")  # Câu hỏi mẫu
                intent = (r.get("intent") or "").strip()  # Intent tương ứng
                if not utt or not intent:
                    continue

                # Tokenize và map từ đồng nghĩa
                if ext_tokenize_and_map is not None:
                    toks = ext_tokenize_and_map(utt, self.syn_map)
                else:
                    toks = utt.split()  # Fallback

                intent_to_samples.setdefault(intent, []).append(toks)
        return intent_to_samples

    # ---------- Intent Detection - Nhận diện ý định ----------
    def detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Nhận diện intent của câu hỏi

        Args:
            text: Câu hỏi từ người dùng

        Returns:
            Tuple (intent, confidence_score)
        """
        if self._intent_detector is None:
            return "fallback", 0.0
        return self._intent_detector.detect(text, self.syn_map, _normalize_text)

    # ---------- Entity Extraction - Trích xuất thực thể ----------
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Trích xuất các entity trong câu hỏi

        Args:
            text: Câu hỏi từ người dùng

        Returns:
            List các entity được trích xuất
        """
        if self._entity_extractor is None:
            return []
        return self._entity_extractor.extract(text)

    # ---------- Public API - Giao diện chính ----------
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Phân tích toàn diện câu hỏi từ người dùng

        Args:
            text: Câu hỏi từ người dùng

        Returns:
            Dict chứa intent, score và entities
        """
        # Nhận diện intent
        intent, score = self.detect_intent(text)

        # Trích xuất entities
        entities = self.extract_entities(text)

        # Heuristic: Nếu phát hiện ngành học trong câu hỏi ngắn và không có intent rõ ràng
        # thì mặc định là hỏi về ngành học
        if intent == "fallback" and entities:
            # Kiểm tra xem có entity TEN_NGANH không
            has_major = any(e.get("label") == "TEN_NGANH" for e in entities)
            # Kiểm tra xem câu hỏi có chứa từ "ngành" hoặc "nganh"
            norm_text = _normalize_text(text)
            has_nganh_keyword = "nganh" in norm_text

            # KHÔNG áp dụng heuristic nếu có các từ khóa specific khác
            # như "mã", "điểm", "học phí", etc.
            exclusion_keywords = ["ma ", " ma", "diem", "hoc phi", "chi tieu"]
            has_exclusion = any(kw in norm_text for kw in exclusion_keywords)

            # Nếu có tên ngành HOẶC có từ "ngành" trong câu ngắn (< 50 ký tự)
            # và KHÔNG có từ khóa exclusion thì cho là hỏi về ngành học
            if (has_major or has_nganh_keyword) and len(text.strip()) < 50 and not has_exclusion:
                intent = "hoi_nganh_hoc"
                score = self.intent_threshold + 0.05  # Đảm bảo vượt ngưỡng

        return {"intent": intent, "score": score, "entities": entities}
