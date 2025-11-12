"""
Utility Functions - Text normalization và formatting
"""

import os
import re
from typing import Any, Dict, List, Optional

import unicodedata

from config import DATA_DIR


def strip_diacritics(text: str) -> str:
    """
    Loại bỏ dấu tiếng Việt.
    
    Args:
        text: Chuỗi có dấu
        
    Returns:
        Chuỗi không dấu
    """
    if not isinstance(text, str):
        return text
    norm = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")


def normalize_text(text: str) -> str:
    """
    Chuẩn hóa text: bỏ dấu, lowercase, strip.
    
    Args:
        text: Chuỗi cần chuẩn hóa
        
    Returns:
        Chuỗi đã chuẩn hóa
    """
    if not isinstance(text, str):
        return ""
    return strip_diacritics(text).lower().strip()


def canonicalize_vi_ascii(text: str) -> str:
    """
    Chuẩn hóa một số biến thể thường gặp sau khi bỏ dấu (ki/ky, từ thừa).
    
    Args:
        text: Chuỗi không dấu
        
    Returns:
        Chuỗi đã chuẩn hóa
    """
    if not isinstance(text, str):
        return ""
    t = text
    # Chuẩn hóa 'ki thuat' -> 'ky thuat'
    t = t.replace("ki thuat", "ky thuat")
    # Loại bỏ từ đệm phổ biến
    t = t.replace(" nganh ", " ")
    t = " ".join(t.split())
    return t


def clean_program_name(name: str) -> str:
    """
    Chuẩn hóa tên chương trình: nếu ở dạng 'Ngành/ Chuyên ngành' → chỉ giữ 'Chuyên ngành'.
    
    Args:
        name: Tên chương trình
        
    Returns:
        Tên đã clean
    """
    if not isinstance(name, str):
        return name
    parts = [p.strip() for p in name.split("/") if p is not None]
    if len(parts) >= 2:
        return parts[-1]
    return name.strip()


def infer_major_from_message(message: str) -> Optional[str]:
    """
    Suy luận tên ngành/chương trình từ message khi entity extractor không bắt được.
    So khớp không dấu, không phân biệt hoa thường.
    Ưu tiên khớp dài nhất.
    
    Args:
        message: Message từ user
        
    Returns:
        Tên ngành được suy luận, hoặc None
    """
    from .cache import read_csv

    if not message:
        return None

    msg_norm = normalize_text(message)
    if not msg_norm:
        return None

    # Thêm một số biến thể thường gặp (ki/ky, nganh/ngành, ...)
    variants = {msg_norm}
    base = msg_norm
    for repl in [
        (" ki thuat ", " ky thuat "),
        (" ki thuat", " ky thuat"),
        ("ky thuat", " ki thuat"),
        (" nganh ", " "),
        (" ngành ", " "),
        (" diem chuan ", " "),
        (" diem ", " "),
        (" chuan ", " "),
        (" nam ", " "),
    ]:
        base = base.replace(repl[0], repl[1])
        variants.add(base)
    # Remove numbers (years) and extra spaces
    variants.add(re.sub(r"\b(19|20)\d{2}\b", " ", msg_norm))
    variants.add(re.sub(r"\d+", " ", msg_norm))
    variants = {" ".join(v.split()) for v in variants if v}

    candidates: List[str] = []

    # majors.csv
    for r in read_csv(os.path.join(DATA_DIR, "majors.csv")):
        name = (r.get("major_name") or "").strip()
        if name:
            candidates.append(name)

    # admission_scores.csv (program_name)
    for r in read_csv(os.path.join(DATA_DIR, "admission_scores.csv")):
        pname = (r.get("program_name") or "").strip()
        if pname:
            candidates.append(pname)

    # admission_targets.csv (program_name, major_name)
    for r in read_csv(os.path.join(DATA_DIR, "admission_targets.csv")):
        pname = (r.get("program_name") or "").strip()
        mname = (r.get("major_name") or "").strip()
        if pname:
            candidates.append(pname)
        if mname:
            candidates.append(mname)

    best_match = None
    best_len = 0
    for cand in candidates:
        cnorm = normalize_text(cand)
        if not cnorm:
            continue
        for vn in variants:
            # Match if candidate contains the user phrase OR user phrase contains the candidate
            if cnorm in vn or vn in cnorm:
                # Use overlap length as score (prefer longer, more specific matches)
                overlap_len = len(cnorm) if cnorm in vn else len(vn)
                if overlap_len > best_len:
                    best_match = cand
                    best_len = overlap_len

    return best_match


def format_data_to_text(data: List[Dict[str, Any]], data_type: str) -> str:
    """
    Format data thành text đẹp để hiển thị.
    
    Args:
        data: List of dicts (dữ liệu từ CSV)
        data_type: Loại data (standard_score, scholarships, etc.)
    
    Returns:
        Text đã format
    """
    if not data:
        return "Không tìm thấy dữ liệu phù hợp."

    lines = []

    if data_type == "standard_score":
        for idx, item in enumerate(data, 1):
            lines.append(f"**{idx}. {item.get('program_name', 'N/A')}**")
            lines.append(f"   • **Tổ hợp:** {item.get('subject_combination', 'N/A')}")
            lines.append(f"   • **Năm {item.get('nam', 'N/A')}:** {item.get('diem_chuan', 'N/A')}")
            lines.append("")

    elif data_type == "floor_score":
        lines.append("Thông tin điểm sàn hiện không có sẵn.")

    elif data_type == "scholarships":
        for idx, item in enumerate(data, 1):
            lines.append(f"**{idx}. {item.get('scholarship_name', 'N/A')}**")
            if item.get('value'):
                lines.append(f"   • **Giá trị:** {item.get('value')}")
            if item.get('quantity'):
                lines.append(f"   • **Số lượng:** {item.get('quantity')}")
            if item.get('academic_year'):
                lines.append(f"   • **Năm học:** {item.get('academic_year')}")
            if item.get('requirements'):
                lines.append(f"   • **Yêu cầu:** {item.get('requirements')}")
            if item.get('note'):
                lines.append(f"   • **Ghi chú:** {item.get('note')}")
            lines.append("")

    elif data_type == "tuition":
        for idx, item in enumerate(data, 1):
            lines.append(f"**{idx}. {item.get('program_type', 'N/A')}**")
            unit = item.get('unit') or "VNĐ"
            lines.append(f"   • **Học phí:** {item.get('tuition_fee', 'N/A')} {unit}")
            if item.get('academic_year'):
                lines.append(f"   • **Năm học:** {item.get('academic_year')}")
            if item.get('note'):
                lines.append(f"   • {item.get('note')}")
            lines.append("")

    elif data_type == "major_info":
        for idx, item in enumerate(data, 1):
            major_name = item.get('major_name', 'N/A')
            major_code = item.get('major_code', 'N/A')
            description = item.get('description', '')
            additional_info = item.get('additional_info', '')

            lines.append(f"**{idx}. {major_name}** (Mã ngành: {major_code})")
            lines.append("")

            if description:
                desc_lines = description.split('\n')
                for desc_line in desc_lines:
                    if desc_line.strip():
                        lines.append(f"{desc_line}")
                lines.append("")

            if additional_info:
                lines.append("**Thông tin bổ sung:**")
                info_lines = additional_info.split('\n')
                for info_line in info_lines:
                    if info_line.strip():
                        lines.append(f"{info_line}")
                lines.append("")

    elif data_type == "admission_conditions":
        for idx, item in enumerate(data, 1):
            lines.append(f"**{idx}. {item.get('admission_method', 'N/A')}**")
            lines.append(f"   • **Điều kiện:** {item.get('requirements', 'N/A')}")
            if item.get('nam'):
                lines.append(f"   • **Năm:** {item.get('nam')}")
            lines.append("")

    elif data_type == "admission_quota":
        for idx, item in enumerate(data, 1):
            major_name = item.get('major_name', 'N/A')
            major_code = item.get('major_code', 'N/A')
            chi_tieu = item.get('chi_tieu', 0)
            chi_tiet = item.get('chi_tiet', [])

            lines.append(f"**{idx}. {major_name}**")
            lines.append(f"   • **Mã ngành:** {major_code}")
            lines.append(f"   • **Tổng chỉ tiêu:** {chi_tieu}")

            if chi_tiet:
                lines.append(f"   • **Chi tiết theo phương thức:**")
                for detail in chi_tiet:
                    method = detail.get('admission_method', 'N/A')
                    combo = detail.get('subject_combination', '')
                    quota = detail.get('chi_tieu', 0)
                    if combo:
                        lines.append(f"      - {method} ({combo}): {quota}")
                    else:
                        lines.append(f"      - {method}: {quota}")

            lines.append("")

    elif data_type == "admission_methods":
        grouped = {}
        for item in data:
            nganh = item.get('major_name', 'N/A')
            method_code = item.get('admission_method', '') or item.get('method_code', '')
            method_name = item.get('method_name', '')
            abbreviation = item.get('abbreviation', '')

            if nganh not in grouped:
                grouped[nganh] = {
                    'major_code': item.get('major_code', 'N/A'),
                    'phuong_thuc_list': []
                }

            # Create method display name
            # If method_name contains " / " (multiple methods combined), format differently
            if " / " in method_name:
                # Multiple methods combined, use a cleaner format
                # Split and format each method separately
                method_parts = method_name.split(" / ")
                abbrev_parts = abbreviation.split(" / ") if abbreviation else []
                display_parts = []
                for i, part in enumerate(method_parts):
                    # Extract method name (remove duplicate abbreviation if exists)
                    # e.g., "TSA - Thi đánh giá tư duy - TSA" -> "TSA - Thi đánh giá tư duy"
                    part_clean = part
                    if i < len(abbrev_parts) and abbrev_parts[i]:
                        abbrev = abbrev_parts[i]
                        # Remove duplicate abbreviation from part
                        if part.startswith(f"{abbrev} - "):
                            part_clean = part[len(f"{abbrev} - "):]
                        # Remove trailing abbreviation if exists
                        if part_clean.endswith(f" - {abbrev}"):
                            part_clean = part_clean[:-len(f" - {abbrev}")]
                        # Format: "ABBREV - Method Name"
                        display_parts.append(f"{abbrev} - {part_clean}")
                    else:
                        display_parts.append(part_clean)
                display_name = ", ".join(display_parts) if display_parts else method_name
            elif method_name and abbreviation:
                # Remove duplicate abbreviation if exists
                method_name_clean = method_name
                if method_name.startswith(f"{abbreviation} - "):
                    method_name_clean = method_name[len(f"{abbreviation} - "):]
                if method_name_clean.endswith(f" - {abbreviation}"):
                    method_name_clean = method_name_clean[:-len(f" - {abbreviation}")]
                display_name = f"{abbreviation} - {method_name_clean}"
            elif method_name:
                display_name = method_name
            elif abbreviation:
                display_name = abbreviation
            elif method_code:
                display_name = method_code
            else:
                display_name = "N/A"

            # Add to list if not already present
            if display_name not in grouped[nganh]['phuong_thuc_list']:
                grouped[nganh]['phuong_thuc_list'].append(display_name)

        for idx, (nganh, info) in enumerate(grouped.items(), 1):
            lines.append(f"**{idx}. {nganh}**")
            major_code = info.get('major_code', 'N/A')
            if major_code != 'N/A':
                lines.append(f"   • **Mã ngành:** {major_code}")
            lines.append(f"   • **Các phương thức xét tuyển:**")
            for pt in info['phuong_thuc_list']:
                lines.append(f"      - {pt}")
            lines.append("")

    elif data_type == "admission_methods_general":
        for idx, item in enumerate(data, 1):
            method_name = item.get('method_name', 'N/A')
            abbreviation = item.get('abbreviation', '')
            description = item.get('description', '')
            requirements = item.get('requirements', '')

            if abbreviation and method_name:
                display_name = f"{abbreviation} - {method_name}"
            elif method_name:
                display_name = method_name
            elif abbreviation:
                display_name = abbreviation
            else:
                display_name = "N/A"

            lines.append(f"**{idx}. {display_name}**")
            if description:
                lines.append(f"   • **Mô tả:** {description}")
            if requirements:
                lines.append(f"   • **Yêu cầu:** {requirements}")
            lines.append("")

    elif data_type == "admissions_schedule":
        # Import locally to avoid circular dependency
        from .admissions import list_admission_methods_general

        method_groups = {}
        for item in data:
            method = item.get('admission_method', 'Tất cả')
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(item)

        method_names_map = {}
        for method in list_admission_methods_general():
            abbr = method.get("abbreviation", "").strip()
            name = method.get("method_name", "")
            if abbr:
                method_names_map[abbr.upper()] = name

        idx = 1
        for method_key, items in method_groups.items():
            if method_key.lower() in ["tất cả", "tat ca"]:
                method_display = "Tất cả phương thức"
            else:
                method_codes = [m.strip().upper() for m in method_key.split(",") if m.strip()]
                method_names = []
                for code in method_codes:
                    if code in method_names_map:
                        method_names.append(f"{code} - {method_names_map[code]}")
                    else:
                        method_names.append(code)
                method_display = ", ".join(method_names)

            for item in items:
                event_name = item.get('event_name', 'N/A')
                timeline = item.get('timeline', 'N/A')
                note = item.get('note', '')

                lines.append(f"**{idx}. {event_name}**")
                lines.append(f"   • **Phương thức:** {method_display}")
                lines.append(f"   • **Thời gian:** {timeline}")
                if note and note.strip():
                    lines.append(f"   • **Ghi chú:** {note}")
                lines.append("")
                idx += 1

    elif data_type == "apply_channels":
        lines.append("Thông tin kênh nộp hồ sơ có thể được tìm trong lịch trình xét tuyển.")

    else:
        for idx, item in enumerate(data, 1):
            lines.append(f"{idx}. {str(item)}")

    return "\n".join(lines)


def add_contact_suggestion(message: str) -> str:
    """
    Thêm gợi ý liên hệ vào cuối message.
    
    Args:
        message: Message gốc
        
    Returns:
        Message đã thêm gợi ý liên hệ
    """
    from .contact import get_contact_info

    contact_info = get_contact_info()
    if contact_info and contact_info.get("fanpage"):
        contact_suggestion = (
            f"\n\n**Nếu câu hỏi chưa được giải đáp đầy đủ, bạn có thể liên hệ:**\n"
            f"   • **Fanpage:** {contact_info.get('fanpage')}\n"
            f"   • **Hotline:** {contact_info.get('hotline')}\n"
            f"   • **Email:** {contact_info.get('email')}"
        )
        return message + contact_suggestion
    return message
