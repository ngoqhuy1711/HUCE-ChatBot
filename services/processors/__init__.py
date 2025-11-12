"""
Processors module - Các hàm xử lý dữ liệu CSV

Module này chứa các processors xử lý dữ liệu từ CSV files:
- Cache: Caching mechanism cho CSV
- Utils: Text normalization và formatting
- Majors: Xử lý thông tin ngành học
- Scores: Xử lý điểm chuẩn, điểm sàn
- Admissions: Xử lý thông tin xét tuyển
- Academic: Xử lý học phí và học bổng
- Contact: Xử lý thông tin liên hệ
- CEFR: Xử lý quy đổi điểm chứng chỉ
"""

from .academic import list_tuition, list_scholarships
from .admissions import (
    list_admission_conditions,
    list_admission_quota,
    list_admission_methods_general,
    list_admission_methods,
    list_admissions_schedule,
    get_admission_targets,
    get_combination_codes,
)
from .cache import read_csv, clear_cache
from .cefr import get_cefr_conversion, convert_certificate_score
from .contact import get_contact_info
from .majors import list_majors
from .scores import find_standard_score, find_floor_score, suggest_majors_by_score
from .utils import (
    strip_diacritics,
    normalize_text,
    canonicalize_vi_ascii,
    clean_program_name,
    infer_major_from_message,
    format_data_to_text,
    add_contact_suggestion,
)

__all__ = [
    # Cache
    "read_csv",
    "clear_cache",
    # Utils
    "strip_diacritics",
    "normalize_text",
    "canonicalize_vi_ascii",
    "clean_program_name",
    "infer_major_from_message",
    "format_data_to_text",
    "add_contact_suggestion",
    # Majors
    "list_majors",
    # Scores
    "find_standard_score",
    "find_floor_score",
    "suggest_majors_by_score",
    # Admissions
    "list_admission_conditions",
    "list_admission_quota",
    "list_admission_methods_general",
    "list_admission_methods",
    "list_admissions_schedule",
    "get_admission_targets",
    "get_combination_codes",
    # Academic
    "list_tuition",
    "list_scholarships",
    # Contact
    "get_contact_info",
    # CEFR
    "get_cefr_conversion",
    "convert_certificate_score",
]
