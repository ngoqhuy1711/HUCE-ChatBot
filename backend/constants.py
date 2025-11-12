"""
Constants - Các hằng số dùng chung trong toàn bộ backend

Tập trung tất cả magic strings, intent names, entity labels vào đây
để dễ bảo trì và tránh typo.
"""


# ==============================================================================
# INTENT NAMES - Tên các intent được nhận diện
# ==============================================================================


class Intent:
    """Các intent được hỗ trợ bởi chatbot"""

    # Intent chính - Hỏi thông tin
    HOI_DIEM_CHUAN = "hoi_diem_chuan"
    HOI_DIEM_SAN = "hoi_diem_san"
    HOI_NGANH_HOC = "hoi_nganh_hoc"
    HOI_HOC_PHI = "hoi_hoc_phi"
    HOI_HOC_BONG = "hoi_hoc_bong"
    HOI_CHI_TIEU = "hoi_chi_tieu"
    HOI_TO_HOP_MON = "hoi_to_hop_mon"
    HOI_PHUONG_THUC = "hoi_phuong_thuc"
    HOI_DIEU_KIEN_XET_TUYEN = "hoi_dieu_kien_xet_tuyen"
    HOI_UU_TIEN_XET_TUYEN = "hoi_uu_tien_xet_tuyen"
    HOI_LICH_TUYEN_SINH = "hoi_lich_tuyen_sinh"
    HOI_KENH_NOP_HO_SO = "hoi_kenh_nop_ho_so"
    HOI_LIEN_HE = "hoi_lien_he"

    # Intent đặc biệt
    FALLBACK = "fallback"
    FALLBACK_RESPONSE = "fallback_response"

    # Tất cả intents hợp lệ
    ALL_INTENTS = [
        HOI_DIEM_CHUAN,
        HOI_DIEM_SAN,
        HOI_NGANH_HOC,
        HOI_HOC_PHI,
        HOI_HOC_BONG,
        HOI_CHI_TIEU,
        HOI_TO_HOP_MON,
        HOI_PHUONG_THUC,
        HOI_DIEU_KIEN_XET_TUYEN,
        HOI_UU_TIEN_XET_TUYEN,
        HOI_LICH_TUYEN_SINH,
        HOI_KENH_NOP_HO_SO,
        HOI_LIEN_HE,
        FALLBACK,
        FALLBACK_RESPONSE,
    ]


# ==============================================================================
# ENTITY LABELS - Nhãn các entity được trích xuất
# ==============================================================================


class Entity:
    """Các entity labels được trích xuất từ câu hỏi"""

    # Ngành học
    MA_NGANH = "MA_NGANH"
    TEN_NGANH = "TEN_NGANH"

    # Khối thi
    KHOI_THI = "KHOI_THI"
    TO_HOP_MON = "TO_HOP_MON"

    # Điểm số
    DIEM_SO = "DIEM_SO"
    DIEM_CHUAN = "DIEM_CHUAN"
    DIEM_SAN = "DIEM_SAN"

    # Năm học
    NAM_HOC = "NAM_HOC"
    NAM_TUYEN_SINH = "NAM_TUYEN_SINH"

    # Phương thức xét tuyển
    PHUONG_THUC_XET_TUYEN = "PHUONG_THUC_XET_TUYEN"
    PHUONG_THUC_TUYEN_SINH = "PHUONG_THUC_TUYEN_SINH"
    DIEU_KIEN_XET_TUYEN = "DIEU_KIEN_XET_TUYEN"

    # Chứng chỉ
    CHUNG_CHI = "CHUNG_CHI"
    CHUNG_CHI_UU_TIEN = "CHUNG_CHI_UU_TIEN"
    MUC_DO_CHUNG_CHI = "MUC_DO_CHUNG_CHI"

    # Học phí & học bổng
    HOC_PHI = "HOC_PHI"
    HOC_PHI_CATEGORY = "HOC_PHI_CATEGORY"
    HOC_BONG = "HOC_BONG"
    HOC_BONG_TEN = "HOC_BONG_TEN"

    # Thời gian & địa điểm
    THOI_GIAN_TUYEN_SINH = "THOI_GIAN_TUYEN_SINH"
    THOI_GIAN_BUOC = "THOI_GIAN_BUOC"
    KENH_NOP_HO_SO = "KENH_NOP_HO_SO"

    # Liên hệ
    DON_VI_LIEN_HE = "DON_VI_LIEN_HE"
    DIA_CHI = "DIA_CHI"
    EMAIL = "EMAIL"
    DIEN_THOAI = "DIEN_THOAI"
    HOTLINE = "HOTLINE"
    WEBSITE = "WEBSITE"
    URL = "URL"


# ==============================================================================
# RESPONSE TYPES - Loại response trả về cho frontend
# ==============================================================================


class ResponseType:
    """Các loại response mà API trả về"""

    # Data responses
    MAJOR_INFO = "major_info"
    MAJOR_LIST = "major_list"
    MAJOR_SUGGESTIONS = "major_suggestions"
    STANDARD_SCORE = "standard_score"
    FLOOR_SCORE = "floor_score"
    TUITION = "tuition"
    SCHOLARSHIPS = "scholarships"
    QUOTA = "quota"
    SCHEDULE = "schedule"
    APPLY_CHANNEL = "apply_channel"
    CONDITIONS = "conditions"
    CONTACT = "contact"

    # Helper responses
    SCORE_HELP = "score_help"
    GENERAL_HELP = "general_help"
    CLARIFICATION = "clarification"
    FALLBACK = "fallback"

    # Chart responses (tương lai)
    CHART_DATA = "chart_data"
    COMPARISON = "comparison"


# ==============================================================================
# VALIDATION CONSTANTS - Các giá trị hợp lệ cho validation
# ==============================================================================


class Validation:
    """Các hằng số dùng cho validation input"""

    # Điểm số
    MIN_SCORE = 0.0
    MAX_SCORE = 30.0

    # Năm học
    MIN_YEAR = 2020
    MAX_YEAR = 2030

    # Score types
    SCORE_TYPE_CHUAN = "chuan"
    SCORE_TYPE_SAN = "san"
    VALID_SCORE_TYPES = [SCORE_TYPE_CHUAN, SCORE_TYPE_SAN]

    # Context actions
    ACTION_GET = "get"
    ACTION_SET = "set"
    ACTION_RESET = "reset"
    VALID_ACTIONS = [ACTION_GET, ACTION_SET, ACTION_RESET]

    # Số lượng kết quả tối đa
    MAX_RESULTS = 100
    MAX_SUGGESTIONS = 20


# ==============================================================================
# ERROR MESSAGES - Thông báo lỗi tiếng Việt
# ==============================================================================


class ErrorMessage:
    """Các thông báo lỗi chuẩn cho API"""

    # Validation errors
    INVALID_SCORE = "Điểm số không hợp lệ. Điểm phải từ 0 đến 30."
    INVALID_YEAR = "Năm học không hợp lệ. Vui lòng nhập năm từ 2020 đến 2030."
    INVALID_SCORE_TYPE = "Loại điểm không hợp lệ. Chỉ chấp nhận 'chuan' hoặc 'san'."
    INVALID_ACTION = "Hành động không hợp lệ. Chỉ chấp nhận 'get', 'set' hoặc 'reset'."
    MISSING_PARAMETER = "Thiếu tham số bắt buộc: {param}"

    # Data errors
    NO_DATA_FOUND = "Không tìm thấy dữ liệu phù hợp."
    FILE_NOT_FOUND = "Không tìm thấy file dữ liệu: {filename}"
    DATA_PARSE_ERROR = "Lỗi đọc dữ liệu từ file: {filename}"

    # Server errors
    INTERNAL_ERROR = "Đã xảy ra lỗi nội bộ. Vui lòng thử lại sau."
    NLP_ERROR = "Lỗi xử lý ngôn ngữ tự nhiên. Vui lòng thử lại."
    DATABASE_ERROR = "Lỗi truy cập dữ liệu. Vui lòng thử lại sau."


# ==============================================================================
# SUCCESS MESSAGES - Thông báo thành công tiếng Việt
# ==============================================================================


class SuccessMessage:
    """Các thông báo thành công chuẩn"""

    CONTEXT_RESET = "Đã reset context. Bắt đầu hội thoại mới."
    CONTEXT_UPDATED = "Đã cập nhật context."
    DATA_FOUND = "Tìm thấy {count} kết quả."
