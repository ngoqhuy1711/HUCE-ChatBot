"""
Scores Module - Xử lý điểm chuẩn, điểm sàn
"""

import os
from typing import Any, Dict, List, Optional

from config import DATA_DIR
from .cache import read_csv
from .utils import strip_diacritics, canonicalize_vi_ascii, clean_program_name


def find_standard_score(
        major: Optional[str] = None, year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm điểm chuẩn (theo ngành và/hoặc năm học)

    Args:
        major: Tên hoặc mã ngành
        year: Năm học (vd: "2020", "2021", "2022", "2023", "2024", "2025")

    Returns:
        List điểm chuẩn theo ngành và năm
    """
    rows = read_csv(os.path.join(DATA_DIR, "admission_scores.csv"))
    if not rows:
        return []

    # Lấy danh sách các cột năm từ header
    year_columns = []
    if rows:
        first_row_keys = list(rows[0].keys())
        for key in first_row_keys:
            if key.isdigit() and len(key) == 4:
                year_num = int(key)
                if 2020 <= year_num <= 2025:
                    year_columns.append(key)
        year_columns.sort()

    results: List[Dict[str, Any]] = []

    for r in rows:
        program_name = (r.get("program_name") or "").strip()
        if not program_name:
            continue

        program_name_cleaned = clean_program_name(program_name)
        program_name_lower = program_name_cleaned.lower()
        program_name_ascii = strip_diacritics(program_name_lower)
        program_name_ascii = canonicalize_vi_ascii(program_name_ascii)

        # Lọc theo ngành nếu có
        if major:
            mq = major.lower()
            mq_ascii = strip_diacritics(mq)
            mq_ascii = canonicalize_vi_ascii(mq_ascii)
            if (mq not in program_name_lower) and (mq_ascii not in program_name_ascii):
                continue

        # Lấy điểm cho từng năm
        for year_key in year_columns:
            if year and year != year_key:
                continue

            score_value = r.get(year_key, "")
            if not score_value:
                continue

            score_str = str(score_value).strip()
            score_lower = score_str.lower()

            # Bỏ qua các giá trị đặc biệt
            if score_lower in ["chưa tuyển", "chua tuyen", ""]:
                continue
            if "tuyển chung" in score_lower or "tuyen chung" in score_lower:
                continue
            if "chưa" in score_lower and "tuyển" in score_lower:
                continue

            # Thử chuyển đổi sang số
            try:
                score_str_clean = score_str.replace(",", ".")
                score_float = float(score_str_clean)

                results.append(
                    {
                        "program_name": program_name_cleaned,
                        "nam": year_key,
                        "diem_chuan": score_float,
                        "subject_combination": r.get("subject_combination", ""),
                    }
                )
            except (ValueError, TypeError):
                continue

    return results


def find_floor_score(
        major: Optional[str] = None, year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm điểm sàn (theo ngành và/hoặc năm học)
    
    NOTE: File floor_score.csv đã được xóa. Hàm này trả về empty list để tương thích ngược.
    
    Args:
        major: Tên hoặc mã ngành
        year: Năm học

    Returns:
        List điểm sàn (trả về empty list)
    """
    return []


def suggest_majors_by_score(request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gợi ý ngành học dựa trên điểm số hoặc chứng chỉ

    Args:
        request_data: Dict chứa điểm số và chứng chỉ

    Returns:
        List các ngành phù hợp với điểm số
    """
    diem_thpt = request_data.get("diem_thpt")
    diem_tsa = request_data.get("diem_tsa")
    diem_dgnl = request_data.get("diem_dgnl")
    chung_chi = request_data.get("chung_chi")
    nam = request_data.get("nam", "2025")

    suggestions = []

    # Lấy điểm chuẩn để so sánh
    standard_scores = find_standard_score(year=nam)

    for score_data in standard_scores:
        diem_chuan = score_data.get("diem_chuan")
        if not diem_chuan:
            continue

        try:
            diem_chuan_float = float(str(diem_chuan).replace(",", "."))
        except (ValueError, TypeError):
            continue

        # So sánh điểm THPT
        if diem_thpt and diem_thpt >= diem_chuan_float:
            suggestions.append(
                {
                    "program_name": score_data.get("program_name"),
                    "diem_chuan": diem_chuan,
                    "diem_thpt": diem_thpt,
                    "subject_combination": score_data.get("subject_combination"),
                    "nam": score_data.get("nam"),
                    "match_type": "thpt",
                    "confidence": min(
                        1.0, (diem_thpt - diem_chuan_float) / diem_chuan_float + 1.0
                    ),
                }
            )

        # So sánh điểm TSA
        if diem_tsa and diem_tsa >= diem_chuan_float:
            suggestions.append(
                {
                    "program_name": score_data.get("program_name"),
                    "diem_chuan": diem_chuan,
                    "diem_tsa": diem_tsa,
                    "subject_combination": score_data.get("subject_combination"),
                    "nam": score_data.get("nam"),
                    "match_type": "tsa",
                    "confidence": min(
                        1.0, (diem_tsa - diem_chuan_float) / diem_chuan_float + 1.0
                    ),
                }
            )

        # So sánh điểm ĐGNL
        if diem_dgnl and diem_dgnl >= diem_chuan_float:
            suggestions.append(
                {
                    "program_name": score_data.get("program_name"),
                    "diem_chuan": diem_chuan,
                    "diem_dgnl": diem_dgnl,
                    "subject_combination": score_data.get("subject_combination"),
                    "nam": score_data.get("nam"),
                    "match_type": "dgnl",
                    "confidence": min(
                        1.0, (diem_dgnl - diem_chuan_float) / diem_chuan_float + 1.0
                    ),
                }
            )

    # Sắp xếp theo confidence giảm dần
    suggestions.sort(key=lambda x: x.get("confidence", 0), reverse=True)

    # Loại bỏ trùng lặp (giữ ngành có confidence cao nhất)
    seen_programs = set()
    unique_suggestions = []
    for suggestion in suggestions:
        program_name = suggestion.get("program_name")
        if program_name and program_name not in seen_programs:
            seen_programs.add(program_name)
            unique_suggestions.append(suggestion)

    return unique_suggestions[:20]  # Trả về tối đa 20 gợi ý
