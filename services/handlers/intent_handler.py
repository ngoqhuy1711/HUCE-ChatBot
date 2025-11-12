"""
Intent Handler - Xử lý các intent được nhận diện từ NLP
"""

from typing import Any, Dict

from services.processors import (
    infer_major_from_message,
    find_standard_score,
    find_floor_score,
    list_majors,
    list_tuition,
    list_scholarships,
    list_admission_conditions,
    list_admission_quota,
    list_admission_methods_general,
    list_admission_methods,
    list_admissions_schedule,
    get_admission_targets,
    get_combination_codes,
    format_data_to_text,
    add_contact_suggestion,
    clean_program_name,
)

DEFAULT_OUTRO = "Nếu cần thêm thông tin nào nữa, bạn cứ nhắn mình nhé."
SOFT_APOLOGY = (
    "Mình chưa tìm thấy thông tin phù hợp trong dữ liệu hiện tại. "
    "Bạn thử mô tả cụ thể hơn hoặc hỏi sang nội dung gần nhất xem sao nhé."
)


def _compose_message(intro: str = "", formatted_text: str = "", outro: str = "", include_contact: bool = False) -> str:
    """
    Ghép các phần của phản hồi thành một đoạn hội thoại tự nhiên.
    """
    segments = []
    if intro:
        segments.append(intro.strip())
    if formatted_text:
        segments.append(formatted_text.strip())
    if outro:
        segments.append(outro.strip())
    message = "\n\n".join(segments)
    if include_contact:
        message = add_contact_suggestion(message)
    return message


def _build_data_response(
        response_type: str,
        results: list,
        intro: str,
        formatted_text: str,
        empty_hint: str,
        outro: str = DEFAULT_OUTRO,
) -> Dict[str, Any]:
    """
    Tạo response thân thiện cho intent có dữ liệu.
    """
    if results:
        message = _compose_message(intro, formatted_text, outro)
    else:
        hint = empty_hint or SOFT_APOLOGY
        message = _compose_message(hint, "", "", include_contact=True)
    return {
        "type": response_type,
        "data": results,
        "message": message,
    }


def handle_intent_query(
        analysis: Dict[str, Any], context: Dict[str, Any], original_message: str = ""
) -> Dict[str, Any]:
    """
    Xử lý câu hỏi dựa trên intent được nhận diện

    Args:
        analysis: Kết quả phân tích NLP
        context: Context hội thoại hiện tại
        original_message: Message gốc từ user

    Returns:
        Response phù hợp với intent
    """
    intent = analysis.get("intent", "fallback")
    entities = analysis.get("entities", [])

    # Lấy thông tin từ entities
    major_info = None
    year_info = None
    for entity in entities:
        label = entity.get("label", "")
        text = entity.get("text", "")

        if label in ["MA_NGANH", "TEN_NGANH", "CHUYEN_NGANH"]:
            major_info = text
        elif label in ["NAM_HOC", "NAM_TUYEN_SINH"]:
            year_info = text

    # Nếu chưa có major_info, thử suy luận từ message gốc
    if not major_info and original_message:
        inferred_major = infer_major_from_message(original_message)
        if inferred_major:
            major_info = inferred_major

    # Xử lý theo intent
    if intent.startswith("hoi_diem_chuan"):
        return _handle_diem_chuan(major_info, year_info)

    elif intent.startswith("hoi_diem_san"):
        return _handle_diem_san(major_info, year_info)

    elif intent.startswith("hoi_nganh_hoc"):
        return _handle_nganh_hoc(major_info)

    elif intent.startswith("hoi_hoc_phi"):
        return _handle_hoc_phi(year_info)

    elif intent.startswith("hoi_hoc_bong"):
        return _handle_hoc_bong()

    elif intent.startswith("hoi_dieu_kien"):
        return _handle_dieu_kien(entities, year_info)

    elif intent.startswith("hoi_chi_tieu"):
        return _handle_chi_tieu(major_info, year_info)

    elif intent.startswith("hoi_phuong_thuc"):
        return _handle_phuong_thuc(major_info, original_message)

    elif intent.startswith("hoi_thoi_gian_dk"):
        return _handle_thoi_gian_dk(entities)

    elif intent.startswith("hoi_to_hop_mon") or intent.startswith("hoi_khoi_thi"):
        return _handle_to_hop_mon(major_info)

    elif intent.startswith("hoi_kenh_nop_ho_so"):
        return _handle_kenh_nop_ho_so()

    else:
        return {
            "type": "fallback",
            "message": _compose_message(
                "Xin lỗi, mình chưa hiểu rõ bạn muốn hỏi gì. Bạn thử nói rõ hơn (ví dụ: điểm chuẩn, học phí, ngành học...) nhé.",
                include_contact=True,
            ),
        }


def _handle_diem_chuan(major_info, year_info):
    """Xử lý intent hỏi điểm chuẩn"""
    if major_info:
        results = find_standard_score(major=major_info, year=year_info)
        formatted_text = format_data_to_text(results, "standard_score")
        year_label = year_info or "các năm gần đây"
        intro = (
            f"✅ Mình tìm được {len(results)} kết quả điểm chuẩn của ngành {major_info} năm {year_label}."
            if results
            else ""
        )
        empty_hint = (
            f"Mình chưa thấy dữ liệu điểm chuẩn cho ngành {major_info} trong hệ thống. "
            "Bạn thử kiểm tra lại tên ngành hoặc hỏi mình về năm khác xem sao nhé."
        )
        return _build_data_response(
            "standard_score",
            results,
            intro,
            formatted_text,
            empty_hint,
        )
    else:
        return {
            "type": "clarification",
            "message": _compose_message(
                "Bạn cho mình xin tên ngành bạn quan tâm để mình tra điểm chuẩn giúp nhé?",
                include_contact=True,
            ),
        }


def _handle_diem_san(major_info, year_info):
    """Xử lý intent hỏi điểm sàn"""
    if major_info:
        results = find_floor_score(major=major_info, year=year_info)
        formatted_text = format_data_to_text(results, "floor_score")
        intro = (
            f"✅ Đây là thông tin điểm sàn mình tìm được cho ngành {major_info}."
            if results
            else ""
        )
        empty_hint = (
            f"Điểm sàn của ngành {major_info} hiện chưa có sẵn. "
            "Bạn thử hỏi mình về điểm chuẩn hoặc phương thức xét tuyển khác nhé."
        )
        return _build_data_response(
            "floor_score",
            results,
            intro,
            formatted_text,
            empty_hint,
        )
    else:
        return {
            "type": "clarification",
            "message": _compose_message(
                "Bạn đang thắc mắc điểm sàn của ngành nào? Cho mình xin tên ngành để kiểm tra nhé.",
                include_contact=True,
            ),
        }


def _handle_nganh_hoc(major_info):
    """Xử lý intent hỏi thông tin ngành học"""
    if major_info:
        results = list_majors(major_info)
        formatted_text = format_data_to_text(results, "major_info")
        intro = (
            f"✨ Đây là những thông tin nổi bật về ngành {major_info}."
            if results
            else ""
        )
        empty_hint = (
            f"Mình chưa tìm thấy ngành có tên {major_info}. "
            "Bạn thử kiểm tra lại tên ngành hoặc mô tả cụ thể hơn nhé."
        )
        return _build_data_response(
            "major_info",
            results,
            intro,
            formatted_text,
            empty_hint,
        )
    else:
        return {
            "type": "clarification",
            "message": _compose_message(
                "Bạn đang tìm hiểu ngành nào vậy? Cho mình xin tên ngành để hỗ trợ chi tiết nhé.",
                include_contact=True,
            ),
        }


def _handle_hoc_phi(year_info):
    """Xử lý intent hỏi học phí"""
    results = list_tuition(year=year_info)
    formatted_text = format_data_to_text(results, "tuition")
    if year_info:
        intro = f"💰 Mình tổng hợp được mức học phí năm {year_info} như sau."
        empty_hint = (
            f"Mình chưa tìm thấy dữ liệu học phí cho năm {year_info}. "
            "Bạn thử hỏi mình về năm khác hoặc xem học phí chương trình cụ thể nhé."
        )
    else:
        intro = "💰 Đây là thông tin học phí mới nhất mà mình có."
        empty_hint = "Mình chưa có dữ liệu học phí để chia sẻ ngay lúc này."
    return _build_data_response(
        "tuition",
        results,
        intro,
        formatted_text,
        empty_hint,
    )


def _handle_hoc_bong():
    """Xử lý intent hỏi học bổng"""
    results = list_scholarships()

    # Phân loại học bổng trong nước và quốc tế
    domestic_scholarships = []
    international_scholarships = []

    international_keywords = ["Anh", "Bỉ", "Ý", "Pháp", "Đức", "Slovakia", "Hoa Kỳ", "Mexico", "Canada",
                              "Australia", "New Zealand", "Nhật Bản", "Hàn Quốc", "Singapore", "Thái Lan",
                              "Trung Quốc", "quốc tế", "Chevening", "DAAD", "MEXT", "Fulbright", "KGSP",
                              "ARES", "VEF", "AMEXCID", "AID", "JDS"]

    for scholarship in results:
        name = scholarship.get('scholarship_name', '')
        is_international = any(keyword in name for keyword in international_keywords)
        if is_international:
            international_scholarships.append(scholarship)
        else:
            domestic_scholarships.append(scholarship)

    # Format text với phân loại
    formatted_lines = []
    if domestic_scholarships:
        formatted_lines.append("### 🏛️ Học bổng trong nước (HUCE)")
        formatted_lines.append("")
        formatted_lines.append(format_data_to_text(domestic_scholarships, "scholarships"))

    if international_scholarships:
        formatted_lines.append("### 🌍 Học bổng quốc tế")
        formatted_lines.append("")
        formatted_lines.append(format_data_to_text(international_scholarships, "scholarships"))

    formatted_text = "\n".join(formatted_lines)

    intro = f"🎁 Mình tìm thấy {len(results)} suất học bổng, bao gồm {len(domestic_scholarships)} học bổng trong nước và {len(international_scholarships)} học bổng quốc tế."
    empty_hint = "Hiện mình chưa có thông tin học bổng cập nhật. Bạn thử quay lại sau hoặc hỏi trực tiếp phòng tuyển sinh nhé."

    return _build_data_response(
        "scholarships",
        results,
        intro,
        formatted_text,
        empty_hint,
    )


def _handle_dieu_kien(entities, year_info):
    """Xử lý intent hỏi điều kiện xét tuyển"""
    phuong_thuc = None
    for entity in entities:
        label = entity.get("label", "")
        if label == "PHUONG_THUC":
            phuong_thuc = entity.get("text", "")
            break

    results = list_admission_conditions(phuong_thuc=phuong_thuc, year=year_info)
    formatted_text = format_data_to_text(results, "admission_conditions")

    year_label = year_info or "2025"
    if phuong_thuc:
        intro = (
            f"📌 Đây là điều kiện xét tuyển phương thức {phuong_thuc} năm {year_label}."
            if results
            else ""
        )
        empty_hint = (
            f"Hiện mình chưa tìm được điều kiện cho phương thức {phuong_thuc} năm {year_label}. "
            "Bạn thử kiểm tra lại tên phương thức hoặc hỏi mình về năm khác nhé."
        )
    else:
        intro = (
            f"📌 Mình tổng hợp điều kiện xét tuyển chung năm {year_label} cho bạn đây."
            if results
            else ""
        )
        empty_hint = (
            f"Mình chưa thấy dữ liệu điều kiện xét tuyển năm {year_label}. "
            "Bạn thử hỏi cụ thể theo phương thức để mình tra cứu chính xác hơn nhé."
        )

    return _build_data_response(
        "admission_conditions",
        results,
        intro,
        formatted_text,
        empty_hint,
    )


def _handle_chi_tieu(major_info, year_info):
    """Xử lý intent hỏi chỉ tiêu tuyển sinh"""
    results = list_admission_quota(major=major_info, year=year_info)
    formatted_text = format_data_to_text(results, "admission_quota")

    year_label = year_info or "2025"
    if major_info:
        intro = (
            f"🎯 Đây là chỉ tiêu tuyển sinh ngành {major_info} năm {year_label}."
            if results
            else ""
        )
        empty_hint = (
            f"Mình chưa tìm thấy chỉ tiêu cho ngành {major_info} năm {year_label}. "
            "Bạn thử hỏi mình về ngành khác hoặc xem chỉ tiêu tổng của trường nhé."
        )
    else:
        intro = (
            f"🎯 Dưới đây là tổng quan chỉ tiêu tuyển sinh năm {year_label}."
            if results
            else ""
        )
        empty_hint = (
            f"Mình chưa có dữ liệu chỉ tiêu năm {year_label} lúc này. "
            "Bạn thử hỏi lại sau hoặc yêu cầu chỉ tiêu theo từng ngành nhé."
        )

    return _build_data_response(
        "admission_quota",
        results,
        intro,
        formatted_text,
        empty_hint,
    )


def _handle_phuong_thuc(major_info, original_message):
    """Xử lý intent hỏi phương thức xét tuyển"""
    search_major = major_info
    if not search_major and original_message:
        # Use infer_major_from_message to get major name from message
        search_major = infer_major_from_message(original_message)

    if not search_major:
        results = list_admission_methods_general()
        formatted_text = format_data_to_text(results, "admission_methods_general")
        intro = (
            "📚 Đây là danh sách các phương thức xét tuyển hiện có của trường."
            if results
            else ""
        )
        empty_hint = "Mình chưa lấy được danh sách phương thức xét tuyển. Bạn thử hỏi lại sau một chút nhé."
        return _build_data_response(
            "admission_methods_general",
            results,
            intro,
            formatted_text,
            empty_hint,
        )

    results = list_admission_methods(major=search_major)
    formatted_text = format_data_to_text(results, "admission_methods")
    intro = (
        f"📚 Ngành {search_major} đang tuyển sinh theo những phương thức sau."
        if results
        else ""
    )
    empty_hint = (
        f"Mình chưa thấy phương thức tuyển sinh cụ thể cho ngành {search_major}. "
        "Bạn thử cung cấp tên ngành rõ hơn hoặc kiểm tra xem ngành còn tuyển không nhé."
    )

    return _build_data_response(
        "admission_methods",
        results,
        intro,
        formatted_text,
        empty_hint,
    )


def _handle_thoi_gian_dk(entities):
    """Xử lý intent hỏi thời gian đăng ký"""
    phuong_thuc = None
    for entity in entities:
        label = entity.get("label", "")
        if label in ["PHUONG_THUC", "PHUONG_THUC_XET_TUYEN", "PHUONG_THUC_TUYEN_SINH"]:
            phuong_thuc = entity.get("text", "")
            break

    results = list_admissions_schedule(phuong_thuc=phuong_thuc)
    formatted_text = format_data_to_text(results, "admissions_schedule")

    if phuong_thuc:
        intro = (
            f"🗓️ Đây là mốc thời gian dành cho phương thức {phuong_thuc}."
            if results
            else ""
        )
        empty_hint = (
            f"Mình chưa thấy lịch dành cho phương thức {phuong_thuc}. "
            "Bạn thử hỏi lại với tên viết tắt chính xác hoặc xem lịch tổng quát nhé."
        )
    else:
        intro = (
            "🗓️ Đây là lịch trình tuyển sinh chung mà mình ghi nhận được."
            if results
            else ""
        )
        empty_hint = "Hiện mình chưa có lịch tuyển sinh cập nhật. Bạn thử hỏi lại sau hoặc truy cập fanpage tuyển sinh nhé."

    return _build_data_response(
        "admissions_schedule",
        results,
        intro,
        formatted_text,
        empty_hint,
    )


def _handle_to_hop_mon(major_info):
    """Xử lý intent hỏi tổ hợp môn"""
    if not major_info:
        return {
            "type": "clarification",
            "message": _compose_message(
                "Bạn muốn mình tra tổ hợp môn cho ngành nào vậy? Cho mình xin tên ngành nhé.",
                include_contact=True,
            ),
        }

    targets = get_admission_targets(ma_nganh=major_info if len(major_info) == 7 else None)

    if len(major_info) != 7:
        mq = major_info.lower()
        targets = [
            t for t in targets
            if mq in t.get("major_name", "").lower()
               or mq in t.get("program_name", "").lower()
        ]

    if not targets:
        return {
            "type": "major_combo",
            "data": [],
            "message": _compose_message(
                f"Mình chưa tìm thấy tổ hợp môn cho ngành {major_info}. Bạn thử kiểm tra lại tên ngành hoặc hỏi mình về ngành tương tự nhé.",
                include_contact=True,
            ),
        }

    # Load combination details
    combo_details = {
        row.get("combination_code"): {
            "subjects": row.get("subject_names", ""),
            "note": row.get("note", "")
        }
        for row in get_combination_codes()
    }

    # Load method details
    method_details = {
        row.get("method_code"): {
            "abbreviation": row.get("abbreviation", ""),
            "method_name": row.get("method_name", ""),
        }
        for row in list_admission_methods_general()
    }

    # Group by program and admission method
    programs = {}
    for t in targets:
        program_name = clean_program_name(t.get("program_name", "N/A"))
        major_code = t.get("major_code", "N/A")
        method_code = t.get("admission_method", "")
        combinations = t.get("subject_combination", "")

        if program_name not in programs:
            programs[program_name] = {
                "program_name": program_name,
                "major_code": major_code,
                "methods": {}
            }

        if combinations and combinations.strip() and combinations.strip().upper() != "TT":
            if method_code not in programs[program_name]["methods"]:
                programs[program_name]["methods"][method_code] = set()

            for combo in combinations.split(","):
                combo = combo.strip()
                if combo:
                    programs[program_name]["methods"][method_code].add(combo)

    # Format output
    formatted_lines = []
    for idx, (prog_name, data) in enumerate(programs.items(), 1):
        formatted_lines.append(f"**{idx}. {prog_name}**")
        formatted_lines.append(f"   • **Mã ngành:** {data['major_code']}")
        formatted_lines.append("")

        if data["methods"]:
            for method_code, combos in sorted(data["methods"].items()):
                method_info = method_details.get(method_code, {})
                abbr = method_info.get("abbreviation", "")
                full_name = method_info.get("method_name", "")

                if abbr and full_name:
                    method_display = f"{abbr} - {full_name}"
                elif full_name:
                    method_display = full_name
                elif abbr:
                    method_display = abbr
                else:
                    method_display = f"Phương thức {method_code}"

                formatted_lines.append(f"   📋 **{method_display}:**")

                for combo in sorted(combos):
                    if combo in combo_details:
                        detail = combo_details[combo]
                        subjects = detail["subjects"]
                        note = detail["note"]

                        formatted_lines.append(f"      • **{combo}:** {subjects}")
                        if note:
                            formatted_lines.append(f"        _{note}_")
                    else:
                        formatted_lines.append(f"      • **{combo}**")

                formatted_lines.append("")
        else:
            formatted_lines.append(f"   • Xét tuyển thẳng hoặc chứng chỉ quốc tế")
            formatted_lines.append("")

    formatted_text = "\n".join(formatted_lines)
    intro = f"📘 Các tổ hợp môn áp dụng cho ngành {major_info} đây nhé."
    message = _compose_message(intro, formatted_text, DEFAULT_OUTRO)

    return {
        "type": "major_combo",
        "data": targets,
        "message": message,
    }


def _handle_kenh_nop_ho_so():
    """Xử lý intent hỏi kênh nộp hồ sơ"""
    results = list_admissions_schedule()
    formatted_text = format_data_to_text(results, "admissions_schedule")
    intro = (
        "📮 Đây là các kênh nộp hồ sơ tương ứng với từng giai đoạn tuyển sinh."
        if results
        else ""
    )
    empty_hint = (
        "Hiện mình chưa cập nhật danh sách kênh nộp hồ sơ. "
        "Bạn thử truy cập hệ thống tuyển sinh của trường hoặc liên hệ hotline để được hỗ trợ nhanh nhé."
    )
    return _build_data_response(
        "admissions_schedule",
        results,
        intro,
        formatted_text,
        empty_hint,
    )
