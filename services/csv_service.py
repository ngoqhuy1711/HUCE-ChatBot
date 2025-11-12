"""
CSV Service - Entry Point với Backward Compatibility

==== CẤU TRÚC MỚI (Module hóa) ====
File này giờ là entry point, re-export tất cả functions từ các module con:

services/
├── csv_service.py          # ← File này (backward compatible)
├── processors/             # Data processing modules
│   ├── cache.py           # CSV caching
│   ├── utils.py           # Text utils & formatting
│   ├── majors.py          # Majors functions
│   ├── scores.py          # Scores functions
│   ├── admissions.py      # Admissions functions
│   ├── academic.py        # Tuition & scholarships
│   ├── contact.py         # Contact info
│   └── cefr.py            # CEFR conversion
└── handlers/               # Intent handling logic
    ├── intent_handler.py  # Intent queries
    └── fallback.py        # Fallback queries

==== TƯƠNG THÍCH NGƯỢC ====
Tất cả import từ csv_service vẫn hoạt động như cũ:
    from services.csv_service import find_standard_score
    from services.csv_service import list_majors
    from services.csv_service import handle_intent_query
    ...

==== CẤU TRÚC DỮ LIỆU CSV ====
1. **majors.csv**: Thông tin ngành học
   - major_code, major_name, description, additional_info

2. **admission_scores.csv**: Điểm chuẩn (nhiều cột năm)
   - program_name, 2020, 2021, 2022, 2023, 2024, 2025, subject_combination

3. **admission_targets.csv**: Chỉ tiêu tuyển sinh
   - major_code, major_name, program_name, admission_method, subject_combination, quota

4. **admission_methods.csv**: Phương thức xét tuyển
   - method_code, abbreviation, method_name, description, requirements

5. **admissions_schedule.csv**: Lịch trình xét tuyển
   - event_name, timeline, admission_method, note

6. **admission_conditions.csv**: Điều kiện xét tuyển
   - nam, admission_method, requirements

7. **subject_combinations.csv**: Tổ hợp môn thi
   - combination_code, subject_names, exam_type, note

8. **tuition.csv**: Học phí
   - academic_year, program_type, tuition_fee, unit, note

9. **scholarships.csv**: Học bổng
   - scholarship_name, value, quantity, academic_year, requirements, note

10. **contact_info.csv**: Thông tin liên hệ
    - university_name, address, email, phone, hotline, website, fanpage, note

11. **cefr_conversion.csv**: Quy đổi điểm chứng chỉ tiếng Anh
    - IELTS, TOEFL iBT, Điểm quy đổi
"""

# ============================================================================
# IMPORTS - Re-export từ các module con
# ============================================================================

from .handlers.fallback import handle_fallback_query
# Handlers
from .handlers.intent_handler import handle_intent_query
# Academic functions
from .processors.academic import (
    list_tuition,
    list_scholarships,
)
# Admissions functions
from .processors.admissions import (
    list_admission_conditions,
    list_admission_quota,
    list_admission_methods_general,
    list_admission_methods,
    list_admissions_schedule,
    get_admission_targets,
    get_combination_codes,
)
# Cache functions
from .processors.cache import read_csv as _read_csv, clear_cache
# CEFR functions
from .processors.cefr import (
    get_cefr_conversion,
    convert_certificate_score,
)
# Contact functions
from .processors.contact import get_contact_info
# Majors functions
from .processors.majors import list_majors
# Scores functions
from .processors.scores import (
    find_standard_score,
    find_floor_score,
    suggest_majors_by_score,
)
# Utility functions
from .processors.utils import (
    format_data_to_text,
)


# ============================================================================
# BACKWARD COMPATIBILITY - Export private functions dưới tên cũ
# ============================================================================
# Những functions này được dùng internally, cần giữ để tương thích

def _read_csv_cached(path: str):
    """Backward compatibility wrapper"""
    return _read_csv(path)


def _strip_diacritics(text: str) -> str:
    """Backward compatibility - already imported above"""
    from .processors.utils import strip_diacritics
    return strip_diacritics(text)


def _normalize_text(text: str) -> str:
    """Backward compatibility - already imported above"""
    from .processors.utils import normalize_text
    return normalize_text(text)


def _canonicalize_vi_ascii(text: str) -> str:
    """Backward compatibility - already imported above"""
    from .processors.utils import canonicalize_vi_ascii
    return canonicalize_vi_ascii(text)


def _clean_program_name(name: str) -> str:
    """Backward compatibility - already imported above"""
    from .processors.utils import clean_program_name
    return clean_program_name(name)


def _infer_major_from_message(message: str):
    """Backward compatibility - already imported above"""
    from .processors.utils import infer_major_from_message
    return infer_major_from_message(message)


def _add_contact_suggestion(message: str) -> str:
    """Backward compatibility - already imported above"""
    from .processors.utils import add_contact_suggestion
    return add_contact_suggestion(message)


# ============================================================================
# PUBLIC API - Tất cả functions được export để dùng ở nơi khác
# ============================================================================
__all__ = [
    # Cache
    "clear_cache",
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
    # Formatting
    "format_data_to_text",
    # Handlers
    "handle_intent_query",
    "handle_fallback_query",
]
