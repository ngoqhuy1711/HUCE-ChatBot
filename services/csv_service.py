"""
CSV Service - Xử lý dữ liệu từ các file CSV

==== VAI TRÒ TRONG HỆ THỐNG ====
Module này là "kho dữ liệu" của chatbot, chịu trách nhiệm:
1. Đọc và cache dữ liệu từ CSV
2. Filter/search dữ liệu theo tiêu chí
3. Cung cấp API đơn giản cho các service khác

==== CẤU TRÚC DỮ LIỆU CSV ====
1. **major_intro.csv**: Thông tin ngành học
   - ma_nganh, ten_nganh, mo_ta

2. **standard_score.csv**: Điểm chuẩn (nhiều cột năm)
   - Mã xét tuyển, Ngành/Chuyên ngành, Mã tổ hợp
   - Năm 2023, Năm 2024, Năm 2025, ...

3. **floor_score.csv**: Điểm sàn
   - ma_nganh, ten_nganh, nam
   - diem_san_thpt, diem_san_hocba, diem_san_tsa, diem_san_dgnl

4. **tuition.csv**: Học phí
   - nam_hoc, chuong_trinh, hoc_phi, ghi_chu

5. **scholarships_huce.csv**: Học bổng
   - ten, loai, doi_tuong, gia_tri, ghi_chu

==== CƠ CHẾ CACHE ====
Cache theo mtime (modification time):
- Lần đầu: Đọc file, lưu (mtime, data) vào cache
- Lần sau: So sánh mtime → Nếu giống thì dùng cache, khác thì đọc lại

Lợi ích:
- Giảm 90% I/O disk (đọc file rất chậm)
- Tự động reload khi file thay đổi
- Đơn giản, không cần invalidation logic

==== CÁC LOẠI HÀM ====
1. **list_***: Lấy danh sách (có thể filter)
   - list_majors(), list_tuition(), list_scholarships()

2. **find_***: Tìm kiếm cụ thể (thường trả về nhiều kết quả)
   - find_standard_score(), find_floor_score()

3. **suggest_***: Gợi ý thông minh
   - suggest_majors_by_score() (so sánh điểm, tính confidence)

4. **handle_***: Xử lý logic phức tạp (intent → response)
   - handle_intent_query(), handle_fallback_query()
"""

import csv
import os
from typing import Any, Dict, List, Optional, Tuple
from config import DATA_DIR

# ============================================================================
# CSV CACHE - Lưu trữ dữ liệu CSV trong bộ nhớ để tăng tốc
# ============================================================================
# Cấu trúc: {path: (mtime, data)}
# - path: Đường dẫn file CSV
# - mtime: Thời điểm file được sửa lần cuối (modification time)
# - data: List các dict (mỗi dict là 1 row)
_CSV_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


def _read_csv_cached(path: str) -> List[Dict[str, Any]]:
    """
    Đọc CSV với cơ chế cache thông minh.

    Thuật toán:
    1. Kiểm tra file có tồn tại không → Không → Trả []
    2. Lấy mtime (modification time) của file
    3. Kiểm tra cache:
       - Có cache VÀ mtime giống → Dùng cache (HIT)
       - Không cache HOẶC mtime khác → Đọc file mới (MISS)
    4. Lưu vào cache cho lần sau
    5. Trả về data

    Args:
        path (str): Đường dẫn tuyệt đối đến file CSV

    Returns:
        list[dict]: Danh sách các row (mỗi row là dict)

    Ví dụ:
        >>> _read_csv_cached("data/major_intro.csv")
        [
            {"ma_nganh": "KT", "ten_nganh": "Kiến trúc", "mo_ta": "..."},
            {"ma_nganh": "XD", "ten_nganh": "Xây dựng", "mo_ta": "..."},
            ...
        ]
    """
    # Bước 1: Kiểm tra file tồn tại
    if not os.path.isfile(path):
        return []

    # Bước 2: Lấy mtime (thời điểm file sửa lần cuối)
    mtime = os.path.getmtime(path)

    # Bước 3: Kiểm tra cache
    cached = _CSV_CACHE.get(path)
    if cached and cached[0] == mtime:
        # Cache HIT: mtime giống nghĩa là file không đổi
        return cached[1]

    # Cache MISS: Đọc file mới
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Bước 4: Lưu vào cache
    _CSV_CACHE[path] = (mtime, rows)

    # Bước 5: Trả về data
    return rows


def _read_csv(path: str) -> List[Dict[str, Any]]:
    """
    Wrapper đơn giản cho _read_csv_cached.

    Dùng hàm này thay vì gọi _read_csv_cached trực tiếp
    để dễ thay đổi implementation sau này.

    Args:
        path (str): Đường dẫn file CSV

    Returns:
        list[dict]: Dữ liệu từ CSV (đã cache)
    """
    return _read_csv_cached(path)


# -------- Majors - Ngành học --------


def list_majors(query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tìm kiếm thông tin ngành học (lọc theo tên/mã ngành nếu có)

    Args:
        query: Từ khóa tìm kiếm (tên ngành hoặc mã ngành)

    Returns:
        List các ngành học phù hợp
    """
    rows = _read_csv(os.path.join(DATA_DIR, "major_intro.csv"))

    # Lọc theo từ khóa nếu có
    if query:
        q = query.lower()
        rows = [
            r
            for r in rows
            if q in (r.get("ten_nganh") or "").lower()
            or q in (r.get("ma_nganh") or "").lower()
        ]

    # Trả về format chuẩn
    return [
        {
            "ma_nganh": r.get("ma_nganh"),
            "ten_nganh": r.get("ten_nganh"),
            "mo_ta": r.get("mo_ta"),
        }
        for r in rows
    ]


# -------- Scores - Điểm số --------


def find_standard_score(
    major: Optional[str] = None, year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm điểm chuẩn (theo ngành và/hoặc năm học)

    Args:
        major: Tên hoặc mã ngành
        year: Năm học

    Returns:
        List điểm chuẩn theo ngành và năm
    """
    rows = _read_csv(os.path.join(DATA_DIR, "standard_score.csv"))
    results: List[Dict[str, Any]] = []

    for r in rows:
        # Lấy mã ngành và tên ngành (hỗ trợ nhiều format)
        ma = (
            r.get("Mã xét tuyển") or r.get("ma_xet_tuyen") or r.get("ma_nganh") or ""
        ).strip()
        ten = (
            r.get("Ngành/ Chuyên ngành tuyển sinh") or r.get("ten_nganh") or ""
        ).strip()

        # Lọc theo ngành nếu có
        if major:
            mq = major.lower()
            if mq not in ma.lower() and mq not in ten.lower():
                continue

        # Tìm các cột năm (bắt đầu bằng "Năm")
        for k, v in r.items():
            k_l = k.strip().lower() if k else ""
            if not k_l.startswith("năm"):
                continue
            if year and year not in k_l:
                continue
            if v and str(v).strip():
                results.append(
                    {
                        "ma_nganh": ma,
                        "ten_nganh": ten,
                        "nam": k,
                        "diem_chuan": v,
                        "to_hop": r.get("Mã tổ hợp") or r.get("to_hop"),
                    }
                )
    return results


def find_floor_score(
    major: Optional[str] = None, year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm điểm sàn (theo ngành và/hoặc năm học)

    Args:
        major: Tên hoặc mã ngành
        year: Năm học

    Returns:
        List điểm sàn theo ngành và năm
    """
    rows = _read_csv(os.path.join(DATA_DIR, "floor_score.csv"))
    results: List[Dict[str, Any]] = []

    for r in rows:
        ma = (r.get("ma_nganh") or "").strip()
        ten = (r.get("ten_nganh") or "").strip()
        nam = (r.get("nam") or "").strip()

        # Lọc theo ngành nếu có
        if major:
            mq = major.lower()
            if mq not in ma.lower() and mq not in ten.lower():
                continue

        # Lọc theo năm nếu có
        if year and year != nam:
            continue

        results.append(
            {
                "ma_nganh": ma,
                "ten_nganh": ten,
                "nam": nam,
                "diem_san_thpt": r.get("diem_san_thpt"),  # Điểm sàn THPT
                "diem_san_hocba": r.get("diem_san_hocba"),  # Điểm sàn học bạ
                "diem_san_tsa": r.get("diem_san_tsa"),  # Điểm sàn TSA
                "diem_san_dgnl": r.get("diem_san_dgnl"),  # Điểm sàn ĐGNL
            }
        )
    return results


# -------- Tuition - Học phí --------


def list_tuition(
    year: Optional[str] = None, program_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm thông tin học phí (lọc theo năm và/hoặc chương trình)

    Args:
        year: Năm học
        program_query: Chương trình đào tạo

    Returns:
        List học phí theo năm và chương trình
    """
    rows = _read_csv(os.path.join(DATA_DIR, "tuition.csv"))
    results: List[Dict[str, Any]] = []

    for r in rows:
        nh = (r.get("nam_hoc") or "").strip()
        ct = (r.get("chuong_trinh") or "").strip()

        # Lọc theo năm nếu có
        if year and year not in nh:
            continue

        # Lọc theo chương trình nếu có
        if program_query and program_query.lower() not in ct.lower():
            continue

        results.append(
            {
                "nam_hoc": nh,
                "chuong_trinh": ct,
                "hoc_phi": r.get("hoc_phi"),
                "ghi_chu": r.get("ghi_chu"),
            }
        )
    return results


# -------- Scholarships - Học bổng --------


def list_scholarships(name_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tìm kiếm thông tin học bổng (lọc theo tên học bổng nếu có)

    Args:
        name_query: Tên học bổng cần tìm

    Returns:
        List học bổng phù hợp
    """
    rows = _read_csv(os.path.join(DATA_DIR, "scholarships_huce.csv"))

    # Lọc theo tên học bổng nếu có
    if name_query:
        q = name_query.lower()
        rows = [r for r in rows if q in (r.get("ten") or "").lower()]

    return [
        {
            "ten": r.get("ten"),  # Tên học bổng
            "loai": r.get("loai"),  # Loại học bổng
            "doi_tuong": r.get("doi_tuong"),  # Đối tượng
            "gia_tri": r.get("gia_tri"),  # Giá trị
            "ghi_chu": r.get("ghi_chu"),  # Ghi chú
        }
        for r in rows
    ]


# -------- Advanced Features - Tuần 5 --------


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
                    "ma_nganh": score_data.get("ma_nganh"),
                    "ten_nganh": score_data.get("ten_nganh"),
                    "diem_chuan": diem_chuan,
                    "diem_thpt": diem_thpt,
                    "to_hop": score_data.get("to_hop"),
                    "nam": score_data.get("nam"),
                    "match_type": "thpt",
                    "confidence": min(
                        1.0, (diem_thpt - diem_chuan_float) / diem_chuan_float + 1.0
                    ),
                }
            )

        # So sánh điểm TSA (nếu có)
        if diem_tsa and diem_tsa >= diem_chuan_float:
            suggestions.append(
                {
                    "ma_nganh": score_data.get("ma_nganh"),
                    "ten_nganh": score_data.get("ten_nganh"),
                    "diem_chuan": diem_chuan,
                    "diem_tsa": diem_tsa,
                    "to_hop": score_data.get("to_hop"),
                    "nam": score_data.get("nam"),
                    "match_type": "tsa",
                    "confidence": min(
                        1.0, (diem_tsa - diem_chuan_float) / diem_chuan_float + 1.0
                    ),
                }
            )

        # So sánh điểm ĐGNL (nếu có)
        if diem_dgnl and diem_dgnl >= diem_chuan_float:
            suggestions.append(
                {
                    "ma_nganh": score_data.get("ma_nganh"),
                    "ten_nganh": score_data.get("ten_nganh"),
                    "diem_chuan": diem_chuan,
                    "diem_dgnl": diem_dgnl,
                    "to_hop": score_data.get("to_hop"),
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
    seen_nganh = set()
    unique_suggestions = []
    for suggestion in suggestions:
        ma_nganh = suggestion.get("ma_nganh")
        if ma_nganh not in seen_nganh:
            seen_nganh.add(ma_nganh)
            unique_suggestions.append(suggestion)

    return unique_suggestions[:20]  # Trả về tối đa 20 gợi ý


def handle_intent_query(
    analysis: Dict[str, Any], context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Xử lý câu hỏi dựa trên intent được nhận diện

    Args:
        analysis: Kết quả phân tích NLP
        context: Context hội thoại hiện tại

    Returns:
        Response phù hợp với intent
    """
    intent = analysis.get("intent", "fallback")
    entities = analysis.get("entities", [])

    # Lấy thông tin từ entities
    major_info = None
    year_info = None
    score_type = None

    for entity in entities:
        label = entity.get("label", "")
        text = entity.get("text", "")

        if label in ["MA_NGANH", "TEN_NGANH"]:
            major_info = text
        elif label == "NAM_HOC":
            year_info = text
        elif label in ["DIEM_CHUAN", "DIEM_SAN"]:
            score_type = "chuan" if "chuẩn" in text.lower() else "san"

    # Xử lý theo intent
    if intent.startswith("hoi_diem_chuan"):
        if major_info:
            results = find_standard_score(major=major_info, year=year_info)
            return {
                "type": "standard_score",
                "data": results,
                "message": f'Điểm chuẩn ngành {major_info} năm {year_info or "2025"}:',
            }
        else:
            return {
                "type": "clarification",
                "message": "Bạn muốn hỏi điểm chuẩn ngành nào? Vui lòng cung cấp tên ngành.",
            }

    elif intent.startswith("hoi_diem_san"):
        if major_info:
            results = find_floor_score(major=major_info, year=year_info)
            return {
                "type": "floor_score",
                "data": results,
                "message": f'Điểm sàn ngành {major_info} năm {year_info or "2025"}:',
            }
        else:
            return {
                "type": "clarification",
                "message": "Bạn muốn hỏi điểm sàn ngành nào? Vui lòng cung cấp tên ngành.",
            }

    elif intent.startswith("hoi_nganh_hoc"):
        if major_info:
            results = list_majors(major_info)
            return {
                "type": "major_info",
                "data": results,
                "message": f"Thông tin ngành {major_info}:",
            }
        else:
            return {
                "type": "clarification",
                "message": "Bạn muốn tìm hiểu ngành nào? Vui lòng cung cấp tên ngành.",
            }

    elif intent.startswith("hoi_hoc_phi"):
        results = list_tuition(year=year_info)
        return {
            "type": "tuition",
            "data": results,
            "message": f'Học phí năm {year_info or "2025"}:',
        }

    elif intent.startswith("hoi_hoc_bong"):
        results = list_scholarships()
        return {
            "type": "scholarships",
            "data": results,
            "message": "Thông tin học bổng:",
        }

    else:
        return {
            "type": "fallback",
            "message": "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi về điểm chuẩn, điểm sàn, ngành học, học phí hoặc học bổng.",
        }


def handle_fallback_query(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Xử lý câu hỏi khi không nhận diện được intent rõ ràng

    Args:
        message: Câu hỏi từ người dùng
        context: Context hội thoại hiện tại

    Returns:
        Response fallback
    """
    message_lower = message.lower()

    # Tìm kiếm từ khóa chung
    if any(word in message_lower for word in ["ngành", "môn", "học"]):
        # Gợi ý tìm kiếm ngành
        results = list_majors()
        return {
            "type": "major_suggestions",
            "data": results[:10],  # Top 10 ngành
            "message": "Dưới đây là danh sách các ngành học tại HUCE:",
        }

    elif any(word in message_lower for word in ["điểm", "chuẩn", "sàn"]):
        return {
            "type": "score_help",
            "message": 'Bạn có thể hỏi về điểm chuẩn hoặc điểm sàn của các ngành. Ví dụ: "Điểm chuẩn ngành Kiến trúc năm 2025"',
        }

    elif any(word in message_lower for word in ["học phí", "tiền", "phí"]):
        results = list_tuition()
        return {"type": "tuition", "data": results, "message": "Thông tin học phí:"}

    elif any(word in message_lower for word in ["học bổng", "scholarship"]):
        results = list_scholarships()
        return {
            "type": "scholarships",
            "data": results,
            "message": "Thông tin học bổng:",
        }

    else:
        return {
            "type": "general_help",
            "message": "Tôi có thể giúp bạn tra cứu thông tin về:\n- Điểm chuẩn/điểm sàn các ngành\n- Thông tin ngành học\n- Học phí\n- Học bổng\n- Gợi ý ngành theo điểm số\n\nBạn muốn hỏi gì?",
        }
