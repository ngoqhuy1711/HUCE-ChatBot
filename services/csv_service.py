import csv
import os
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def _read_csv(path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


# -------- Majors --------

def list_majors(query: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _read_csv(os.path.join(DATA_DIR, 'major_intro.csv'))
    if query:
        q = query.lower()
        rows = [r for r in rows if q in (r.get('ten_nganh') or '').lower() or q in (r.get('ma_nganh') or '').lower()]
    return [{
        'ma_nganh': r.get('ma_nganh'),
        'ten_nganh': r.get('ten_nganh'),
        'mo_ta': r.get('mo_ta')
    } for r in rows]


# -------- Scores --------

def find_standard_score(major: Optional[str] = None, year: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _read_csv(os.path.join(DATA_DIR, 'standard_score.csv'))
    results: List[Dict[str, Any]] = []
    for r in rows:
        ma = (r.get('Mã xét tuyển') or r.get('ma_xet_tuyen') or r.get('ma_nganh') or '').strip()
        ten = (r.get('Ngành/ Chuyên ngành tuyển sinh') or r.get('ten_nganh') or '').strip()
        if major:
            mq = major.lower()
            if mq not in ma.lower() and mq not in ten.lower():
                continue
        # collect year columns that start with "Năm"
        for k, v in r.items():
            k_l = k.strip().lower() if k else ''
            if not k_l.startswith('năm'):
                continue
            if year and year not in k_l:
                continue
            if v and str(v).strip():
                results.append({'ma_nganh': ma, 'ten_nganh': ten, 'nam': k, 'diem_chuan': v, 'to_hop': r.get('Mã tổ hợp') or r.get('to_hop')})
    return results


def find_floor_score(major: Optional[str] = None, year: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _read_csv(os.path.join(DATA_DIR, 'floor_score.csv'))
    results: List[Dict[str, Any]] = []
    for r in rows:
        ma = (r.get('ma_nganh') or '').strip()
        ten = (r.get('ten_nganh') or '').strip()
        nam = (r.get('nam') or '').strip()
        if major:
            mq = major.lower()
            if mq not in ma.lower() and mq not in ten.lower():
                continue
        if year and year != nam:
            continue
        results.append({
            'ma_nganh': ma,
            'ten_nganh': ten,
            'nam': nam,
            'diem_san_thpt': r.get('diem_san_thpt'),
            'diem_san_hocba': r.get('diem_san_hocba'),
            'diem_san_tsa': r.get('diem_san_tsa'),
            'diem_san_dgnl': r.get('diem_san_dgnl'),
        })
    return results


# -------- Tuition --------

def list_tuition(year: Optional[str] = None, program_query: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _read_csv(os.path.join(DATA_DIR, 'tuition.csv'))
    results: List[Dict[str, Any]] = []
    for r in rows:
        nh = (r.get('nam_hoc') or '').strip()
        ct = (r.get('chuong_trinh') or '').strip()
        if year and year not in nh:
            continue
        if program_query and program_query.lower() not in ct.lower():
            continue
        results.append({'nam_hoc': nh, 'chuong_trinh': ct, 'hoc_phi': r.get('hoc_phi'), 'ghi_chu': r.get('ghi_chu')})
    return results


# -------- Scholarships --------

def list_scholarships(name_query: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _read_csv(os.path.join(DATA_DIR, 'scholarships_huce.csv'))
    if name_query:
        q = name_query.lower()
        rows = [r for r in rows if q in (r.get('ten') or '').lower()]
    return [{
        'ten': r.get('ten'),
        'loai': r.get('loai'),
        'doi_tuong': r.get('doi_tuong'),
        'gia_tri': r.get('gia_tri'),
        'ghi_chu': r.get('ghi_chu')
    } for r in rows]
