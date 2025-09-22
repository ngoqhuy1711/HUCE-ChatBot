import csv
import json
import os
from typing import Any, Dict, List, Set, Tuple

from .preprocess import normalize_text

try:
    from underthesea import ner as uts_ner  # type: ignore
except Exception:
    uts_ner = None  # type: ignore


class EntityExtractor:
    def __init__(self, data_dir: str, patterns_path: str) -> None:
        self.data_dir = data_dir
        self.entity_patterns: List[Tuple[str, str]] = self._load_entity_patterns(patterns_path)
        self.dict_phrases: List[Tuple[str, str]] = self._load_dictionary_phrases()
        self.entity_label_alias: Dict[str, str] = {
            'NAM_TUYEN_SINH': 'NAM_HOC',
            'NAM': 'NAM_HOC',
            'PHUONG_THUC_TUYEN_SINH': 'PHUONG_THUC_XET_TUYEN',
            'CHUNG_CHI': 'CHUNG_CHI_UU_TIEN',
            'TO_HOP': 'TO_HOP_MON',
            'KHOI_THI': 'TO_HOP_MON',
        }

    # ---------- Loaders ----------
    def _load_entity_patterns(self, path: str) -> List[Tuple[str, str]]:
        patterns: List[Tuple[str, str]] = []
        if not os.path.isfile(path):
            return patterns
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                label = (item.get('label') or '').strip()
                pat = normalize_text(item.get('pattern') or '')
                if label and pat:
                    patterns.append((label, pat))
        return patterns

    def _load_dictionary_phrases(self) -> List[Tuple[str, str]]:
        phrases: List[Tuple[str, str]] = []

        # major_intro.csv
        def add_file(path: str, handler):
            if os.path.isfile(path):
                with open(path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        handler(r, phrases)

        base = self.data_dir
        add_file(os.path.join(base, 'major_intro.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
        ))
        add_file(os.path.join(base, 'admission_methods.csv'), lambda r, p: (
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
        ))
        add_file(os.path.join(base, 'method_condition.csv'), lambda r, p: (
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
            p.append(('DIEU_KIEN_XET_TUYEN', normalize_text(r.get('dieu_kien') or ''))) if r.get('dieu_kien') else None,
        ))
        add_file(os.path.join(base, 'tuition.csv'), lambda r, p: (
            p.append(('HOC_PHI_CATEGORY', normalize_text(r.get('chuong_trinh') or ''))) if r.get(
                'chuong_trinh') else None,
        ))
        add_file(os.path.join(base, 'scholarships_huce.csv'), lambda r, p: (
            p.append(('HOC_BONG_TEN', normalize_text(r.get('ten') or ''))) if r.get('ten') else None,
        ))
        add_file(os.path.join(base, 'standard_score.csv'), lambda r, p: (
            p.append(('MA_NGANH',
                      normalize_text(r.get('Mã xét tuyển') or r.get('ma_xet_tuyen') or r.get('ma_nganh') or ''))) if (
                        r.get('Mã xét tuyển') or r.get('ma_xet_tuyen') or r.get('ma_nganh')) else None,
            p.append(
                ('TEN_NGANH', normalize_text(r.get('Ngành/ Chuyên ngành tuyển sinh') or r.get('ten_nganh') or ''))) if (
                        r.get('Ngành/ Chuyên ngành tuyển sinh') or r.get('ten_nganh')) else None,
            [p.append(('TO_HOP_MON', normalize_text(th))) for th in
             (normalize_text(r.get('Mã tổ hợp') or r.get('to_hop') or '')).split(',') if th],
            [p.append(('NAM_HOC', normalize_text(k))) for k in r.keys() if k and normalize_text(k).startswith('năm')],
        ))
        add_file(os.path.join(base, 'floor_score.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('NAM_HOC', normalize_text(r.get('nam') or ''))) if r.get('nam') else None,
        ))
        add_file(os.path.join(base, 'admission_quota.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('NAM_HOC', normalize_text(r.get('nam') or ''))) if r.get('nam') else None,
        ))
        add_file(os.path.join(base, 'admissions_schedule.csv'), lambda r, p: (
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
            p.append(('THOI_GIAN_BUOC', normalize_text(r.get('buoc') or ''))) if r.get('buoc') else None,
            p.append(('URL', normalize_text(r.get('url') or ''))) if r.get('url') else None,
        ))
        add_file(os.path.join(base, 'apply_channel.csv'), lambda r, p: (
            p.append(('KENH_NOP_HO_SO', normalize_text(r.get('kenh') or ''))) if r.get('kenh') else None,
            p.append(('URL', normalize_text(r.get('url') or ''))) if r.get('url') else None,
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
        ))
        add_file(os.path.join(base, 'contact.csv'), lambda r, p: (
            p.append(('DON_VI_LIEN_HE', normalize_text(r.get('co_quan') or ''))) if r.get('co_quan') else None,
            p.append(('DIA_CHI', normalize_text(r.get('dia_chi') or ''))) if r.get('dia_chi') else None,
            p.append(('EMAIL', normalize_text(r.get('email') or ''))) if r.get('email') else None,
            p.append(('DIEN_THOAI', normalize_text(r.get('dien_thoai') or ''))) if r.get('dien_thoai') else None,
            p.append(('HOTLINE', normalize_text(r.get('hotline') or ''))) if r.get('hotline') else None,
            p.append(('WEBSITE', normalize_text(r.get('website') or ''))) if r.get('website') else None,
        ))
        add_file(os.path.join(base, 'certificate_mapping.csv'), lambda r, p: (
            p.append(('CHUNG_CHI_UU_TIEN', normalize_text(r.get('chung_chi') or ''))) if r.get('chung_chi') else None,
            p.append(('MUC_DO_CHUNG_CHI', normalize_text(r.get('muc_do') or ''))) if r.get('muc_do') else None,
        ))
        add_file(os.path.join(base, 'admissions_sector.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('TO_HOP_MON', normalize_text(r.get('to_hop') or ''))) if r.get('to_hop') else None,
        ))
        add_file(os.path.join(base, 'admission_conditions.csv'), lambda r, p: (
            p.append(('NAM_HOC', normalize_text(r.get('nam') or ''))) if r.get('nam') else None,
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
            p.append(('DIEU_KIEN_XET_TUYEN', normalize_text(r.get('dieu_kien') or ''))) if r.get('dieu_kien') else None,
        ))
        add_file(os.path.join(base, 'admission_method_for_each_major.csv'), lambda r, p: (
            p.append(('MA_NGANH', normalize_text(r.get('ma_nganh') or ''))) if r.get('ma_nganh') else None,
            p.append(('TEN_NGANH', normalize_text(r.get('ten_nganh') or ''))) if r.get('ten_nganh') else None,
            p.append(('PHUONG_THUC_XET_TUYEN', normalize_text(r.get('phuong_thuc') or ''))) if r.get(
                'phuong_thuc') else None,
        ))
        # remove empty phrases and duplicates
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

    # ---------- Extract ----------
    def _extract_by_patterns(self, norm_text: str) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        for label, pat in self.entity_patterns:
            if pat and pat in norm_text:
                norm_pat = normalize_text(pat)
                fixed_label = label
                if 'điểm sàn' in norm_pat:
                    fixed_label = 'DIEM_SAN'
                elif 'điểm chuẩn' in norm_pat:
                    fixed_label = 'DIEM_CHUAN'
                found.append({"label": fixed_label, "text": pat, "source": "pattern"})
        return found

    def _extract_by_dictionaries(self, norm_text: str) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        for label, phrase in self.dict_phrases:
            if phrase and phrase in norm_text:
                found.append({"label": label, "text": phrase, "source": "dictionary"})
        return found

    def _extract_by_ner(self, text: str) -> List[Dict[str, Any]]:
        if uts_ner is None:
            return []
        try:
            ner_result = uts_ner(text)  # list of (word, tag)
        except Exception:
            return []
        found: List[Dict[str, Any]] = []
        buffer_tokens: List[str] = []
        current_tag: str = ''

        def flush():
            nonlocal buffer_tokens, current_tag, found
            if buffer_tokens and current_tag:
                span = " ".join(buffer_tokens)
                found.append({"label": current_tag, "text": span, "source": "ner"})
            buffer_tokens = []
            current_tag = ''

        for token, tag in ner_result:
            if tag.startswith('B-'):
                flush()
                current_tag = tag[2:]
                buffer_tokens = [token]
            elif tag.startswith('I-') and current_tag == tag[2:]:
                buffer_tokens.append(token)
            else:
                flush()
        flush()
        return found

    def extract(self, text: str) -> List[Dict[str, Any]]:
        norm = normalize_text(text)
        results: List[Dict[str, Any]] = []
        results.extend(self._extract_by_patterns(norm))
        results.extend(self._extract_by_dictionaries(norm))
        results.extend(self._extract_by_ner(text))
        seen: Set[Tuple[str, str]] = set()
        dedup: List[Dict[str, Any]] = []
        for ent in results:
            raw_label = (ent.get('label') or '').strip()
            canon_label = self.entity_label_alias.get(raw_label, raw_label)
            raw_text = ent.get('text') or ''
            norm_t = normalize_text(raw_text)
            if 'điểm sàn' in norm_t:
                canon_label = 'DIEM_SAN'
            elif 'điểm chuẩn' in norm_t:
                canon_label = 'DIEM_CHUAN'
            key = (canon_label, norm_t)
            if key not in seen:
                seen.add(key)
                dedup.append({"label": canon_label, "text": raw_text, "source": ent.get('source')})
        return dedup
