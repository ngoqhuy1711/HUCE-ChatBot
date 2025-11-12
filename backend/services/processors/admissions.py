"""
Admissions Module - Xử lý thông tin xét tuyển
"""

import os
from typing import Any, Dict, List, Optional

from config import DATA_DIR
from .cache import read_csv


def list_admission_conditions(
        phuong_thuc: Optional[str] = None, year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm điều kiện xét tuyển (lọc theo phương thức và/hoặc năm)

    Args:
        phuong_thuc: Phương thức xét tuyển (THPT, học bạ, TSA, etc.)
        year: Năm học

    Returns:
        List điều kiện xét tuyển phù hợp
    """
    rows = read_csv(os.path.join(DATA_DIR, "admission_conditions.csv"))
    results: List[Dict[str, Any]] = []

    for r in rows:
        nam = (r.get("nam") or "").strip()
        pt = (r.get("admission_method") or "").strip()

        # Lọc theo năm nếu có
        if year and year not in nam:
            continue

        # Lọc theo phương thức nếu có
        if phuong_thuc and phuong_thuc.lower() not in pt.lower():
            continue

        results.append(
            {
                "nam": nam,
                "admission_method": pt,
                "requirements": r.get("requirements"),
            }
        )
    return results


def list_admission_quota(
        major: Optional[str] = None, year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm chỉ tiêu tuyển sinh (lọc theo ngành và/hoặc năm)
    
    Args:
        major: Tên hoặc mã ngành
        year: Năm học (hiện tại chỉ có dữ liệu 2025)

    Returns:
        List chỉ tiêu tuyển sinh chi tiết theo ngành/phương thức/tổ hợp
    """
    targets = get_admission_targets(ma_nganh=major if major and len(major) == 7 else None)

    # Filter by major name if provided
    if major and len(major) != 7:
        from .utils import strip_diacritics
        mq = strip_diacritics(major.lower())
        targets = [
            t for t in targets
            if mq in strip_diacritics(t.get("major_name", "").lower())
               or mq in strip_diacritics(t.get("program_name", "").lower())
        ]

    # Group by major and calculate totals
    major_quotas = {}
    for target in targets:
        ma_nganh = target.get("major_code", "")
        ten_nganh = target.get("major_name", "")
        key = (ma_nganh, ten_nganh)

        if key not in major_quotas:
            major_quotas[key] = {
                "major_code": ma_nganh,
                "major_name": ten_nganh,
                "nam": "2025",
                "chi_tieu": 0,
                "chi_tiet": []
            }

        chi_tieu_str = target.get("quota", "0")
        try:
            chi_tieu = int(chi_tieu_str)
        except ValueError:
            chi_tieu = 0

        major_quotas[key]["chi_tiet"].append({
            "admission_method": target.get("admission_method", ""),
            "subject_combination": target.get("subject_combination", ""),
            "chi_tieu": chi_tieu
        })

    # Calculate unique quotas per Ma_xt
    results = []
    for key, data in major_quotas.items():
        ma_xt_quotas = {}
        for t in targets:
            if t.get("major_code") == data["major_code"]:
                ma_xt = t.get("admission_code", "")
                chi_tieu_str = t.get("quota", "0")
                try:
                    chi_tieu = int(chi_tieu_str)
                    if ma_xt and ma_xt not in ma_xt_quotas:
                        ma_xt_quotas[ma_xt] = chi_tieu
                except ValueError:
                    continue

        data["chi_tieu"] = sum(ma_xt_quotas.values())
        results.append(data)

    return results


def list_admission_methods_general() -> List[Dict[str, Any]]:
    """
    Lấy danh sách tổng quát các phương thức xét tuyển

    Returns:
        List phương thức xét tuyển tổng quát
    """
    rows = read_csv(os.path.join(DATA_DIR, "admission_methods.csv"))
    results: List[Dict[str, Any]] = []

    for r in rows:
        results.append(
            {
                "method_code": r.get("method_code"),
                "abbreviation": r.get("abbreviation"),
                "method_name": r.get("method_name"),
                "description": r.get("description"),
                "requirements": r.get("requirements"),
            }
        )
    return results


def list_admission_methods(major: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tìm kiếm phương thức xét tuyển (lọc theo ngành nếu có)

    Args:
        major: Tên hoặc mã ngành

    Returns:
        List phương thức xét tuyển chi tiết theo ngành
    """
    targets = get_admission_targets(ma_nganh=major if major and len(major) == 7 else None)

    # Filter by major name if provided
    if major and len(major) != 7:
        from .utils import strip_diacritics
        mq = strip_diacritics(major.lower())
        targets = [
            t for t in targets
            if mq in strip_diacritics(t.get("major_name", "").lower())
               or mq in strip_diacritics(t.get("program_name", "").lower())
        ]

    # Group by major and method
    methods_map = {}
    # Load all methods once for mapping
    # Note: Some method_code may have multiple entries (e.g., 402 has both TSA and SPT)
    # So we create a list of methods for each method_code
    all_methods = list_admission_methods_general()
    method_mapping = {}
    for m in all_methods:
        method_code = m.get("method_code")
        if method_code not in method_mapping:
            method_mapping[method_code] = []
        method_mapping[method_code].append({
            "method_name": m.get("method_name", ""),
            "abbreviation": m.get("abbreviation", ""),
            "description": m.get("description", ""),
        })

    for target in targets:
        ma_nganh = target.get("major_code", "")
        ten_nganh = target.get("major_name", "")
        phuong_thuc = target.get("admission_method", "")

        key = (ma_nganh, phuong_thuc)
        if key not in methods_map:
            # Get method info from mapping (may have multiple methods for same code)
            method_list = method_mapping.get(phuong_thuc, [])

            # For method_code with multiple entries, combine them
            # e.g., 402 -> "TSA - Thi đánh giá tư duy - TSA / SPT - Thi đánh giá năng lực - SPT"
            if len(method_list) > 1:
                method_names = []
                abbreviations = []
                descriptions = []
                for method_info in method_list:
                    abbrev = method_info.get("abbreviation", "")
                    name = method_info.get("method_name", "")
                    desc = method_info.get("description", "")
                    if abbrev and name:
                        method_names.append(f"{abbrev} - {name}")
                    elif name:
                        method_names.append(name)
                    elif abbrev:
                        method_names.append(abbrev)
                    if abbrev:
                        abbreviations.append(abbrev)
                    if desc:
                        descriptions.append(desc)
                method_name = " / ".join(method_names) if method_names else ""
                abbreviation = " / ".join(abbreviations) if abbreviations else ""
                method_desc = " / ".join(descriptions) if descriptions else ""
            elif len(method_list) == 1:
                method_info = method_list[0]
                method_name = method_info.get("method_name", "")
                abbreviation = method_info.get("abbreviation", "")
                method_desc = method_info.get("description", "")
            else:
                # No mapping found, use method_code as fallback
                method_name = ""
                abbreviation = ""
                method_desc = ""

            methods_map[key] = {
                "major_code": ma_nganh,
                "major_name": ten_nganh,
                "admission_method": phuong_thuc,  # Keep method_code for backward compatibility
                "method_code": phuong_thuc,
                "method_name": method_name,
                "abbreviation": abbreviation,
                "description": method_desc,
                "subject_combination": []
            }

        # Add combination if exists
        to_hop = target.get("subject_combination", "").strip()
        if to_hop and to_hop not in methods_map[key]["subject_combination"]:
            methods_map[key]["subject_combination"].append(to_hop)

    # Convert to list and format to_hop
    results = []
    for data in methods_map.values():
        data["subject_combination"] = ", ".join(data["subject_combination"])
        results.append(data)

    return results


def list_admissions_schedule(phuong_thuc: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tìm kiếm lịch trình xét tuyển (lọc theo phương thức nếu có)

    Args:
        phuong_thuc: Phương thức xét tuyển (có thể là mã hoặc tên)

    Returns:
        List lịch trình xét tuyển phù hợp
    """
    rows = read_csv(os.path.join(DATA_DIR, "admissions_schedule.csv"))

    # Load mapping từ admission_methods.csv
    method_mapping = {}
    for method in list_admission_methods_general():
        method_code = method.get("method_code", "")
        abbreviation = method.get("abbreviation", "").strip().upper()
        method_name = method.get("method_name", "").lower()

        if abbreviation:
            method_mapping[abbreviation.lower()] = abbreviation
            method_mapping[abbreviation] = abbreviation

        if method_code and method_code not in method_mapping:
            method_mapping[method_code] = abbreviation

        if method_name:
            if "học bạ" in method_name or "hoc ba" in method_name:
                if "học bạ" not in method_mapping:
                    method_mapping["học bạ"] = abbreviation
                if "hoc ba" not in method_mapping:
                    method_mapping["hoc ba"] = abbreviation
            if "tuyển thẳng" in method_name or "tuyen thang" in method_name:
                if "tuyển thẳng" not in method_mapping:
                    method_mapping["tuyển thẳng"] = abbreviation
                if "tuyen thang" not in method_mapping:
                    method_mapping["tuyen thang"] = abbreviation
            if "chứng chỉ quốc tế" in method_name or "chung chi quoc te" in method_name:
                if "chứng chỉ quốc tế" not in method_mapping:
                    method_mapping["chứng chỉ quốc tế"] = abbreviation
                if "chung chi quoc te" not in method_mapping:
                    method_mapping["chung chi quoc te"] = abbreviation
                if "ccqt" not in method_mapping:
                    method_mapping["ccqt"] = abbreviation
            if "v-sat" in method_name or "vsat" in method_name:
                if "v-sat" not in method_mapping:
                    method_mapping["v-sat"] = abbreviation
                if "vsat" not in method_mapping:
                    method_mapping["vsat"] = abbreviation
            if "tsa" in method_name or "đánh giá tư duy" in method_name:
                if "tsa" not in method_mapping:
                    method_mapping["tsa"] = abbreviation
            if "spt" in method_name or "đánh giá năng lực" in method_name:
                if "spt" not in method_mapping:
                    method_mapping["spt"] = abbreviation
            if "thpt" in method_name and "năng khiếu" not in method_name:
                if "thpt" not in method_mapping:
                    method_mapping["thpt"] = abbreviation

    # Chuẩn hóa phương thức tìm kiếm
    search_methods = set()
    if phuong_thuc:
        phuong_thuc_lower = phuong_thuc.lower().strip()
        phuong_thuc_upper = phuong_thuc.upper().strip()

        if phuong_thuc_lower in method_mapping:
            mapped_abbr = method_mapping[phuong_thuc_lower].upper()
            search_methods.add(mapped_abbr)
        elif phuong_thuc_upper in method_mapping:
            mapped_abbr = method_mapping[phuong_thuc_upper].upper()
            search_methods.add(mapped_abbr)
        else:
            search_methods.add(phuong_thuc_upper)

    results: List[Dict[str, Any]] = []

    for r in rows:
        event_name = (r.get("event_name") or "").strip()
        if not event_name:
            continue

        pt_raw = (r.get("admission_method") or "").strip()

        # Lọc theo phương thức nếu có
        if phuong_thuc:
            pt_raw_lower = pt_raw.lower().strip()
            if pt_raw_lower in ["tất cả", "tat ca"]:
                pass
            elif search_methods:
                methods_in_row = [m.strip().upper() for m in pt_raw.split(",") if m.strip()]
                matched = False
                for method_in_row in methods_in_row:
                    if method_in_row in search_methods:
                        matched = True
                        break

                if not matched:
                    continue
            else:
                phuong_thuc_lower = phuong_thuc.lower().strip()
                if phuong_thuc_lower not in pt_raw_lower:
                    methods_in_row = [m.strip().lower() for m in pt_raw.split(",") if m.strip()]
                    if phuong_thuc_lower not in methods_in_row:
                        continue

        results.append(
            {
                "event_name": event_name,
                "timeline": r.get("timeline") or "",
                "admission_method": pt_raw,
                "note": r.get("note") or "",
            }
        )
    return results


def get_admission_targets(
        ma_nganh: Optional[str] = None,
        phuong_thuc: Optional[str] = None,
        to_hop: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lấy chỉ tiêu tuyển sinh theo ngành, phương thức, tổ hợp môn

    Args:
        ma_nganh: Mã ngành (vd: "7580101")
        phuong_thuc: Mã phương thức tuyển sinh (vd: "100", "301")
        to_hop: Tổ hợp môn (vd: "A00", "A01")

    Returns:
        List các chỉ tiêu phù hợp
    """
    rows = read_csv(os.path.join(DATA_DIR, "admission_targets.csv"))
    results = []

    for row in rows:
        # Filter by ma_nganh
        if ma_nganh and row.get("major_code", "").strip() != ma_nganh.strip():
            continue

        # Filter by phuong_thuc
        if phuong_thuc and row.get("admission_method", "").strip() != phuong_thuc.strip():
            continue

        # Filter by to_hop
        if to_hop:
            to_hop_list = row.get("subject_combination", "").split(",")
            to_hop_list = [x.strip() for x in to_hop_list]
            if to_hop.strip() not in to_hop_list:
                continue

        results.append(row)

    return results


def get_combination_codes(ky_thi: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lấy danh sách tổ hợp môn thi

    Args:
        ky_thi: Loại kỳ thi (THPT, THPT_NK, HB, TSA, SPT, VSAT)

    Returns:
        List các tổ hợp môn
    """
    rows = read_csv(os.path.join(DATA_DIR, "subject_combinations.csv"))

    if ky_thi:
        results = []
        for row in rows:
            ky_thi_list = row.get("exam_type", "").split(",")
            ky_thi_list = [x.strip() for x in ky_thi_list]
            if ky_thi.strip() in ky_thi_list:
                results.append(row)
        return results

    return rows
