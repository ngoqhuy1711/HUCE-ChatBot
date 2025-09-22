import csv
import os
from typing import List, Dict, Tuple, Any, Set

try:
    from underthesea import word_tokenize
except ImportError:  # fallback if underthesea is not installed
    def word_tokenize(text: str):
        return text.split()

# Try optional NER from underthesea
try:
    from underthesea import ner as uts_ner  # type: ignore
except ImportError:
    uts_ner = None  # type: ignore

# New modular imports
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

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

DEFAULT_INTENT_THRESHOLD = 0.35  # lower because TF-IDF cosine is stricter than Jaccard

# Minimal Vietnamese stopword set (extendable)
VI_STOPWORDS: Set[str] = {
    "là", "làm", "và", "hoặc", "nhưng", "thì", "lúc", "khi", "ở", "của",
    "cho", "với", "đến", "tới", "từ", "có", "được", "nhé", "ạ", "à", "ư",
    "mình", "bạn", "xin", "chào", "ơi", "giúp", "hỏi", "cho", "xem", "bao",
}


def _normalize_text(text) -> str:
    if ext_normalize_text is not None:
        return ext_normalize_text(text)
    # fallback minimal
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    return text.lower().strip()


def _load_synonyms(path: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not os.path.isfile(path):
        return mapping
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        _ = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            src = _normalize_text(row[0])
            dst = _normalize_text(row[1])
            if src and dst:
                mapping[src] = dst
    return mapping


class NLPPipeline:
    def __init__(self, data_dir: str = DATA_DIR, intent_threshold: float = DEFAULT_INTENT_THRESHOLD) -> None:
        self.data_dir = data_dir
        self.intent_threshold = intent_threshold
        self.syn_map = _load_synonyms(os.path.join(data_dir, 'synonym.csv'))
        self.intent_samples = self._load_intent_samples(os.path.join(data_dir, 'intent.csv'))
        # Keyword backoff rules for intent detection (substring match on normalized text)
        self.intent_keyword_backoff: Dict[str, str] = {
            "điểm sàn": "hoi_diem_san",
            "điểm chuẩn": "hoi_diem_chuan",
            "chỉ tiêu": "hoi_chi_tieu",
            "học phí": "hoi_hoc_phi",
            "học bổng": "hoi_hoc_bong",
            "phí": "hoi_hoc_phi",
            "phương thức": "hoi_phuong_thuc",
            "ưu tiên xét tuyển": "hoi_uu_tien_xet_tuyen",
            "điều kiện": "hoi_dieu_kien_xet_tuyen",
            "thời gian tuyển sinh": "hoi_lich_tuyen_sinh",
            "lịch tuyển sinh": "hoi_lich_tuyen_sinh",
            "hạn nộp": "hoi_lich_tuyen_sinh",
            "deadline": "hoi_lich_tuyen_sinh",
            "kênh nộp": "hoi_kenh_nop_ho_so",
            "nộp hồ sơ": "hoi_kenh_nop_ho_so",
            "tổ hợp": "hoi_to_hop_mon",
            "khối thi": "hoi_to_hop_mon",
            "liên hệ": "hoi_lien_he",
            "v-sat": "hoi_phuong_thuc",
            "vsat": "hoi_phuong_thuc",
        }
        # Modular detectors
        self._intent_detector = IntentDetector(self.intent_samples, self.intent_keyword_backoff,
                                               self.intent_threshold) if IntentDetector else None
        self._entity_extractor = EntityExtractor(self.data_dir,
                                                 os.path.join(data_dir, 'entity.json')) if EntityExtractor else None

    # ---------- Loaders ----------

    def _load_intent_samples(self, path: str) -> Dict[str, List[List[str]]]:
        intent_to_samples: Dict[str, List[List[str]]] = {}
        if not os.path.isfile(path):
            return intent_to_samples
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                utt = _normalize_text(r.get('utterance') or '')
                intent = (r.get('intent') or '').strip()
                if not utt or not intent:
                    continue
                if ext_tokenize_and_map is not None:
                    toks = ext_tokenize_and_map(utt, self.syn_map)
                else:
                    toks = utt.split()
                intent_to_samples.setdefault(intent, []).append(toks)
        return intent_to_samples

    # ---------- Preprocess (delegate normalization) ----------

    # ---------- Intent ----------
    def detect_intent(self, text: str) -> Tuple[str, float]:
        if self._intent_detector is None:
            return 'fallback', 0.0
        ext_normalize_text() or _normalize_text
        return self._intent_detector.detect(text, self.syn_map, _normalize_text)

    # ---------- Entities ----------
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        if self._entity_extractor is None:
            return []
        return self._entity_extractor.extract(text)

    # ---------- Public ----------
    def analyze(self, text: str) -> Dict[str, Any]:
        intent, score = self.detect_intent(text)
        entities = self.extract_entities(text)
        return {"intent": intent, "score": score, "entities": entities}
