"""
Entity Extraction Module - Trích xuất thực thể từ câu hỏi

Module này trích xuất các entity từ câu hỏi người dùng:
- Pattern matching từ entity.json
- Dictionary lookup từ các file CSV
- NER (Named Entity Recognition) từ Underthesea
- Deduplication và normalization
"""

import csv
import json
import os
from typing import Any, Dict, List, Set, Tuple

from .preprocess import normalize_text

# Import NER từ Underthesea
try:
    from underthesea import ner as uts_ner  # type: ignore
except ImportError:
    uts_ner = None  # type: ignore


def _load_entity_patterns(path: str) -> List[Tuple[str, str]]:
    """
    Load patterns từ file entity.json
    
    Args:
        path: Đường dẫn file entity.json
        
    Returns:
        List các tuple (label, pattern)
    """
    patterns: List[Tuple[str, str]] = []
    if not os.path.isfile(path):
        return patterns

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            label = (item.get('label') or '').strip()
            # Chỉ lấy pattern dạng string (bỏ qua pattern phức tạp)
            pat = item.get('pattern')
            if isinstance(pat, str):
                pat = normalize_text(pat)
            else:
                continue
            if label and pat:
                patterns.append((label, pat))
    return patterns


def _extract_by_ner(text: str) -> List[Dict[str, Any]]:
    """
    Trích xuất entity bằng NER từ Underthesea
    
    Args:
        text: Văn bản cần xử lý
        
    Returns:
        List các entity được trích xuất
    """
    if uts_ner is None:
        return []

    try:
        ner_result = uts_ner(text)  # List of (word, tag)
    except (ValueError, RuntimeError):
        return []

    found: List[Dict[str, Any]] = []
    buffer_tokens: List[str] = []
    current_tag: str = ''

    def flush():
        """Ghi nhận entity đã hoàn thành"""
        nonlocal buffer_tokens, current_tag, found
        if buffer_tokens and current_tag:
            span = " ".join(buffer_tokens)
            found.append({"label": current_tag, "text": span, "source": "ner"})
        buffer_tokens = []
        current_tag = ''

    # Xử lý kết quả NER theo format BIO
    # Underthesea NER trả về list of tuples: [(word, pos_tag, ner_tag, chunk), ...]
    # hoặc [(word, ner_tag), ...] tùy version
    for item in ner_result:
        # Unpack an toàn: lấy phần tử đầu (word) và cuối (NER tag)
        if isinstance(item, (list, tuple)):
            if len(item) >= 2:
                token = item[0]  # Word là phần tử đầu
                tag = item[-1]   # NER tag thường là phần tử cuối
            else:
                continue  # Skip nếu format không đúng
        else:
            continue  # Skip nếu không phải tuple/list
        
        # Xử lý theo BIO format
        if isinstance(tag, str) and tag.startswith('B-'):  # Begin
            flush()
            current_tag = tag[2:]
            buffer_tokens = [token]
        elif isinstance(tag, str) and tag.startswith('I-') and current_tag == tag[2:]:  # Inside
            buffer_tokens.append(token)
        else:  # Other
            flush()

    flush()  # Flush entity cuối cùng
    return found


class EntityExtractor:
    """
    Entity Extractor - Trích xuất thực thể từ câu hỏi
    
    Sử dụng 3 phương pháp:
    1. Pattern matching từ entity.json
    2. Dictionary lookup từ các file CSV
    3. NER từ Underthesea
    """

    def __init__(self, data_dir: str, patterns_path: str) -> None:
        """
        Khởi tạo Entity Extractor
        
        Args:
            data_dir: Thư mục chứa dữ liệu CSV
            patterns_path: Đường dẫn file entity.json
        """
        self.data_dir = data_dir

        # Load patterns từ entity.json
        self.entity_patterns: List[Tuple[str, str]] = _load_entity_patterns(patterns_path)

        # Load dictionary phrases từ các file CSV
        self.dict_phrases: List[Tuple[str, str]] = self._load_dictionary_phrases()

        # Mapping alias cho entity labels (chuẩn hóa tên)
        self.entity_label_alias: Dict[str, str] = {
            'NAM_TUYEN_SINH': 'NAM_HOC',
            'NAM': 'NAM_HOC',
            'PHUONG_THUC_TUYEN_SINH': 'PHUONG_THUC_XET_TUYEN',
            'CHUNG_CHI': 'CHUNG_CHI_UU_TIEN',
            'TO_HOP': 'TO_HOP_MON',
            'KHOI_THI': 'TO_HOP_MON',
        }

    # ---------- Loaders - Load dữ liệu từ CSV ----------

    def _load_dictionary_phrases(self) -> List[Tuple[str, str]]:
        """
        Load tất cả phrases từ các file CSV để tạo dictionary lookup
        
        Returns:
            List các tuple (label, phrase) đã được normalize
        """
        phrases: List[Tuple[str, str]] = []

        def add_file(path: str, handler):
            """Helper function để đọc file CSV và xử lý"""
            if os.path.isfile(path):
                with open(path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        handler(r, phrases)

        base = self.data_dir

        # major_intro.csv - Thông tin ngành học
        add_file(os.path.join(base, 'major_intro.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
        ))

        # admission_methods.csv - Phương thức xét tuyển
        add_file(os.path.join(base, 'admission_methods.csv'), lambda r, p: (
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
        ))

        # method_condition.csv - Điều kiện xét tuyển
        add_file(os.path.join(base, 'method_condition.csv'), lambda r, p: (
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
            p.append(('DIEU_KIEN_XET_TUYEN', normalize_text(r.get('dieu_kien') or ''))) if r.get('dieu_kien') else None,
        ))

        # tuition.csv - Học phí
        add_file(os.path.join(base, 'tuition.csv'), lambda r, p: (
            p.append(('HOC_PHI_CATEGORY', normalize_text(r.get('chuong_trinh') or ''))) if r.get(
                'chuong_trinh') else None,
        ))

        # scholarships_huce.csv - Học bổng
        add_file(os.path.join(base, 'scholarships_huce.csv'), lambda r, p: (
            p.append(('HOC_BONG_TEN', normalize_text(r.get('ten') or ''))) if r.get('ten') else None,
        ))

        # standard_score.csv - Điểm chuẩn
        add_file(os.path.join(base, 'standard_score.csv'), lambda r, p: (
            p.append(('MA_NGANH',
                      normalize_text(r.get('Mã xét tuyển') or r.get('ma_xet_tuyen') or r.get('ma_nganh') or ''))) if (
                    r.get('Mã xét tuyển') or r.get('ma_xet_tuyen') or r.get('ma_nganh')) else None,
            p.append(
                ('TEN_NGANH', normalize_text(r.get('Ngành/ Chuyên ngành tuyển sinh') or r.get('ten_nganh') or ''))) if (
                    r.get('Ngành/ Chuyên ngành tuyển sinh') or r.get('ten_nganh')) else None,
            # Tổ hợp môn (có thể có nhiều, phân tách bằng dấu phẩy)
            [p.append(('TO_HOP_MON', normalize_text(th))) for th in
             (normalize_text(r.get('Mã tổ hợp') or r.get('to_hop') or '')).split(',') if th],
            # Năm học (các cột bắt đầu bằng "năm")
            [p.append(('NAM_HOC', normalize_text(k))) for k in r.keys() if k and normalize_text(k).startswith('năm')],
        ))

        # floor_score.csv - Điểm sàn
        add_file(os.path.join(base, 'floor_score.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('NAM_HOC', normalize_text(r.get('nam') or ''))) if r.get('nam') else None,
        ))

        # admission_quota.csv - Chỉ tiêu
        add_file(os.path.join(base, 'admission_quota.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('NAM_HOC', normalize_text(r.get('nam') or ''))) if r.get('nam') else None,
        ))

        # admissions_schedule.csv - Lịch tuyển sinh
        add_file(os.path.join(base, 'admissions_schedule.csv'), lambda r, p: (
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
            p.append(('THOI_GIAN_BUOC', normalize_text(r.get('buoc') or ''))) if r.get('buoc') else None,
            p.append(('URL', normalize_text(r.get('url') or ''))) if r.get('url') else None,
        ))

        # apply_channel.csv - Kênh nộp hồ sơ
        add_file(os.path.join(base, 'apply_channel.csv'), lambda r, p: (
            p.append(('KENH_NOP_HO_SO', normalize_text(r.get('kenh') or ''))) if r.get('kenh') else None,
            p.append(('URL', normalize_text(r.get('url') or ''))) if r.get('url') else None,
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
        ))

        # contact.csv - Thông tin liên hệ
        add_file(os.path.join(base, 'contact.csv'), lambda r, p: (
            p.append(('DON_VI_LIEN_HE', normalize_text(r.get('co_quan') or ''))) if r.get('co_quan') else None,
            p.append(('DIA_CHI', normalize_text(r.get('dia_chi') or ''))) if r.get('dia_chi') else None,
            p.append(('EMAIL', normalize_text(r.get('email') or ''))) if r.get('email') else None,
            p.append(('DIEN_THOAI', normalize_text(r.get('dien_thoai') or ''))) if r.get('dien_thoai') else None,
            p.append(('HOTLINE', normalize_text(r.get('hotline') or ''))) if r.get('hotline') else None,
            p.append(('WEBSITE', normalize_text(r.get('website') or ''))) if r.get('website') else None,
        ))

        # certificate_mapping.csv - Chứng chỉ
        add_file(os.path.join(base, 'certificate_mapping.csv'), lambda r, p: (
            p.append(('CHUNG_CHI_UU_TIEN', normalize_text(r.get('chung_chi') or ''))) if r.get('chung_chi') else None,
            p.append(('MUC_DO_CHUNG_CHI', normalize_text(r.get('muc_do') or ''))) if r.get('muc_do') else None,
        ))

        # admissions_sector.csv - Khối tuyển sinh
        add_file(os.path.join(base, 'admissions_sector.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('TO_HOP_MON', normalize_text(r.get('to_hop') or ''))) if r.get('to_hop') else None,
        ))

        # admission_conditions.csv - Điều kiện tuyển sinh
        add_file(os.path.join(base, 'admission_conditions.csv'), lambda r, p: (
            p.append(('NAM_HOC', normalize_text(r.get('nam') or ''))) if r.get('nam') else None,
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
            p.append(('DIEU_KIEN_XET_TUYEN', normalize_text(r.get('dieu_kien') or ''))) if r.get('dieu_kien') else None,
        ))

        # admission_method_for_each_major.csv - Phương thức cho từng ngành
        add_file(os.path.join(base, 'admission_method_for_each_major.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
        ))

        # Loại bỏ phrases rỗng và trùng lặp
        cleaned: List[Tuple[str, str]] = []
        seen: Set[Tuple[str, str]] = set()
        for lbl, phr in phrases:
            if not lbl or not phr:
                continue
            key = (lbl, phr)
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(key)
        return cleaned

    # ---------- Extract - Các phương pháp trích xuất entity ----------

    def _extract_by_patterns(self, norm_text: str) -> List[Dict[str, Any]]:
        """
        Trích xuất entity bằng pattern matching từ entity.json
        
        Args:
            norm_text: Văn bản đã được normalize
            
        Returns:
            List các entity được tìm thấy
        """
        found: List[Dict[str, Any]] = []
        for label, pat in self.entity_patterns:
            if pat and pat in norm_text:
                norm_pat = normalize_text(pat)
                fixed_label = label

                # Xử lý đặc biệt cho điểm sàn/chuẩn
                if 'điểm sàn' in norm_pat:
                    fixed_label = 'DIEM_SAN'
                elif 'điểm chuẩn' in norm_pat:
                    fixed_label = 'DIEM_CHUAN'

                found.append({"label": fixed_label, "text": pat, "source": "pattern"})
        return found

    def _extract_by_dictionaries(self, norm_text: str) -> List[Dict[str, Any]]:
        """
        Trích xuất entity bằng dictionary lookup từ CSV
        
        Args:
            norm_text: Văn bản đã được normalize
            
        Returns:
            List các entity được tìm thấy
        """
        found: List[Dict[str, Any]] = []
        for label, phrase in self.dict_phrases:
            if phrase and phrase in norm_text:
                found.append({"label": label, "text": phrase, "source": "dictionary"})
        return found

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Trích xuất tất cả entities từ văn bản
        
        Args:
            text: Văn bản cần xử lý
            
        Returns:
            List các entity đã được deduplicate và normalize
        """
        # Chuẩn hóa văn bản
        norm = normalize_text(text)

        # Trích xuất bằng 3 phương pháp
        results: List[Dict[str, Any]] = []
        results.extend(self._extract_by_patterns(norm))  # Pattern matching
        results.extend(self._extract_by_dictionaries(norm))  # Dictionary lookup
        results.extend(_extract_by_ner(text))  # NER

        # Deduplication và normalization
        seen: Set[Tuple[str, str]] = set()
        dedup: List[Dict[str, Any]] = []

        for ent in results:
            raw_label = (ent.get('label') or '').strip()
            raw_text = ent.get('text') or ''
            norm_t = normalize_text(raw_text)

            # Chuẩn hóa label (alias mapping)
            canon_label = self.entity_label_alias.get(raw_label, raw_label)

            # Xử lý đặc biệt cho điểm sàn/chuẩn
            if 'điểm sàn' in norm_t:
                canon_label = 'DIEM_SAN'
            elif 'điểm chuẩn' in norm_t:
                canon_label = 'DIEM_CHUAN'

            # Deduplication
            key = (canon_label, norm_t)
            if key not in seen:
                seen.add(key)
                dedup.append({
                    "label": canon_label,
                    "text": raw_text,
                    "source": ent.get('source')
                })

        return dedup
