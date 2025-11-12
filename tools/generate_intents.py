#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a balanced intent.csv from majors.csv so every major has example utterances.
This overwrites backend/data/intent.csv with curated, relevant items only.
"""

import csv
import os

import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
MAJORS_CSV = os.path.join(DATA_DIR, "majors.csv")
INTENT_CSV = os.path.join(DATA_DIR, "intent.csv")
ADMISSION_TARGETS_CSV = os.path.join(DATA_DIR, "admission_targets.csv")


def read_majors(path: str):
    majors = []
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            major_code = (row.get("major_code") or "").strip()
            major_name = (row.get("major_name") or "").strip()
            if not major_code and not major_name:
                continue
            key = (major_code, major_name.lower())
            if key in seen:
                continue
            seen.add(key)
            majors.append({"code": major_code, "name": major_name})
    return majors


def read_programs_from_targets(path: str):
    """
    Read unique (program_name, major_code) pairs from admission_targets.csv
    to cover all programs/specializations present in real targets.
    """
    programs = []
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = (row.get("program_name") or "").strip()
            program_name = raw_name.split("/")[-1].strip() if "/" in raw_name else raw_name
            major_code = (row.get("major_code") or "").strip()
            if not program_name and not major_code:
                continue
            key = (program_name.lower(), major_code)
            if key in seen:
                continue
            seen.add(key)
            programs.append({"code": major_code, "name": program_name})
    return programs


def strip_diacritics(text: str) -> str:
    norm = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")


NATURAL_PREFIXES = [
    "cho mình hỏi",
    "bạn ơi",
    "mình đang quan tâm",
    "làm ơn",
    "ad ơi",
    "xin hỏi",
    "cậu ơi",
    "mình cần biết",
]


def augment_with_prefixes(rows, prefixes):
    augmented = []
    for utterance, intent in rows:
        augmented.append((utterance, intent))
        # Skip header row
        if intent == "intent" and utterance == "utterance":
            continue
        for prefix in prefixes:
            combined = f"{prefix} {utterance}".strip()
            augmented.append((combined, intent))
    return augmented


def make_generic_rows():
    base_rows = [
        ("utterance", "intent"),
        ("chào bạn", "chao_hoi"),
        ("xin chào", "chao_hoi"),
        ("hello", "chao_hoi"),
        ("hi bot", "chao_hoi"),
        ("mình chào bạn", "chao_hoi"),
        ("tạm biệt", "tam_biet"),
        ("bye", "tam_biet"),
        ("mình xin phép kết thúc", "tam_biet"),
        ("cảm ơn bạn nhé", "tam_biet"),
        ("giúp tôi", "tro_giup"),
        ("tôi cần trợ giúp", "tro_giup"),
        ("bạn hỗ trợ mình với", "tro_giup"),
        ("giải đáp giúp mình", "tro_giup"),
        ("không hiểu", "fallback"),
        ("tôi chưa rõ", "fallback"),
        ("chưa rõ câu trả lời", "fallback"),
        ("reset hội thoại", "reset_context"),
        ("bắt đầu lại cuộc trò chuyện", "reset_context"),
        ("học phí năm 2025", "hoi_hoc_phi"),
        ("học phí chương trình CLC", "hoi_hoc_phi"),
        ("mức học phí hiện tại", "hoi_hoc_phi"),
        ("có học bổng nào không", "hoi_hoc_bong"),
        ("chính sách học bổng của trường", "hoi_hoc_bong"),
        ("học bổng dành cho tân sinh viên", "hoi_hoc_bong"),
        ("điều kiện tuyển thẳng", "hoi_dieu_kien"),
        ("điều kiện học bạ", "hoi_dieu_kien"),
        ("điều kiện TSA/SPT/VSAT", "hoi_dieu_kien"),
        ("cần những gì để xét tuyển học bạ", "hoi_dieu_kien"),
        ("lịch tuyển sinh 2025", "hoi_thoi_gian_dk"),
        ("timeline tuyển sinh mới nhất", "hoi_thoi_gian_dk"),
        ("thời gian nộp hồ sơ học bạ", "hoi_thoi_gian_dk"),
        ("khi nào mở đăng ký", "hoi_thoi_gian_dk"),
        ("nộp hồ sơ ở đâu", "hoi_kenh_nop_ho_so"),
        ("kênh nộp hồ sơ phương thức CCQT", "hoi_kenh_nop_ho_so"),
        ("đăng ký trên hệ thống nào", "hoi_kenh_nop_ho_so"),
        # Contact info
        ("thông tin liên hệ của trường", "hoi_thong_tin_lien_he"),
        ("số điện thoại hotline là gì", "hoi_thong_tin_lien_he"),
        ("website tuyển sinh ở đâu", "hoi_thong_tin_lien_he"),
        ("cho mình xin fanpage tuyển sinh", "hoi_thong_tin_lien_he"),
        # Certificates / CEFR conversion
        ("quy đổi chứng chỉ tiếng anh", "hoi_chung_chi_nn"),
        ("IELTS tương đương bao nhiêu điểm", "hoi_chung_chi_nn"),
        ("TOEFL, TOEIC quy đổi thế nào", "hoi_chung_chi_nn"),
        ("delf b2 quy ra bao nhiêu điểm", "hoi_chung_chi_nn"),
        # Colloquial variants for key intents
        ("học phí bao nhiêu", "hoi_hoc_phi"),
        ("học phí là mấy", "hoi_hoc_phi"),
        ("bao giờ mở đăng ký", "hoi_thoi_gian_dk"),
        ("khi nào nộp hồ sơ", "hoi_thoi_gian_dk"),
        ("điểm chuẩn năm 2024 là bao nhiêu", "hoi_diem_chuan"),
        ("trúng tuyển cần mấy điểm", "hoi_diem_chuan"),
        ("điểm vào trường có khó không", "hoi_diem_chuan"),
    ]
    return augment_with_prefixes(base_rows, NATURAL_PREFIXES[:4])


def make_global_dataset_rows():
    """
    Add intent examples that reference datasets directly without a specific major.
    """
    rows = []
    # admission_methods
    rows += [
        ("liệt kê các phương thức xét tuyển", "hoi_phuong_thuc"),
        ("có những phương thức tuyển sinh nào", "hoi_phuong_thuc"),
        ("mình muốn biết các phương thức xét tuyển hiện tại", "hoi_phuong_thuc"),
        ("bạn kể giúp mình các hình thức tuyển sinh", "hoi_phuong_thuc"),
    ]
    # subject_combinations
    rows += [
        ("danh sách các tổ hợp xét tuyển", "hoi_to_hop_mon"),
        ("có những khối thi nào", "hoi_to_hop_mon"),
        ("các khối thi dùng để xét tuyển là gì", "hoi_to_hop_mon"),
        ("mình tìm danh sách tổ hợp môn của trường", "hoi_to_hop_mon"),
    ]
    # admission_scores
    rows += [
        ("điểm chuẩn các ngành năm 2024", "hoi_diem_chuan"),
        ("điểm chuẩn 2023", "hoi_diem_chuan"),
        ("cập nhật điểm chuẩn năm ngoái giúp mình", "hoi_diem_chuan"),
        ("cho mình xin bảng điểm chuẩn mới nhất", "hoi_diem_chuan"),
    ]
    # admission_targets
    rows += [
        ("tổng chỉ tiêu tuyển sinh năm 2025", "hoi_chi_tieu"),
        ("chỉ tiêu của trường là bao nhiêu", "hoi_chi_tieu"),
        ("bao nhiêu chỉ tiêu năm nay", "hoi_chi_tieu"),
        ("giữ hộ mình thông tin về tổng chỉ tiêu", "hoi_chi_tieu"),
    ]
    # tuition
    rows += [
        ("bảng học phí các chương trình", "hoi_hoc_phi"),
        ("mức học phí mới nhất", "hoi_hoc_phi"),
        ("review giúp mình tiền học mỗi năm", "hoi_hoc_phi"),
        ("mình muốn biết chi phí học tập", "hoi_hoc_phi"),
    ]
    # scholarships
    rows += [
        ("các loại học bổng đang có", "hoi_hoc_bong"),
        ("học bổng cho tân sinh viên", "hoi_hoc_bong"),
        ("có ưu đãi học bổng nào hấp dẫn không", "hoi_hoc_bong"),
        ("mình quan tâm các suất học bổng", "hoi_hoc_bong"),
    ]
    # admissions_schedule
    rows += [
        ("lịch tuyển sinh", "hoi_thoi_gian_dk"),
        ("timeline tuyển sinh", "hoi_thoi_gian_dk"),
        ("bạn gửi lịch trình tuyển sinh giúp mình", "hoi_thoi_gian_dk"),
        ("mình cần xem lịch xét tuyển chi tiết", "hoi_thoi_gian_dk"),
    ]
    # contact info
    rows += [
        ("địa chỉ trường là gì", "hoi_thong_tin_lien_he"),
        ("fanpage tuyển sinh", "hoi_thong_tin_lien_he"),
        ("cho mình thông tin liên hệ của trường", "hoi_thong_tin_lien_he"),
        ("mình cần hotline và email tuyển sinh", "hoi_thong_tin_lien_he"),
    ]
    # certificates conversion
    rows += [
        ("quy đổi ielts 6.5 sang điểm quy đổi", "hoi_chung_chi_nn"),
        ("delf b2 tương đương bao nhiêu", "hoi_chung_chi_nn"),
        ("mình có chứng chỉ ielts, quy đổi sao", "hoi_chung_chi_nn"),
        ("chứng chỉ tiếng anh quy đổi ra bao nhiêu điểm", "hoi_chung_chi_nn"),
    ]
    return augment_with_prefixes(rows, NATURAL_PREFIXES[2:])


def make_major_rows(majors):
    rows = []
    # Diverse templates per major/program
    year_variants = ["2024", "2023"]
    soft_prefixes = [
        "cho mình hỏi",
        "mình đang tìm hiểu",
        "bạn ơi",
        "mình cần thông tin",
        "ad ơi",
    ]
    for m in majors:
        name = m["name"]
        code = m["code"]
        major_rows = []
        if name:
            # Major intro
            major_rows.append((f"giới thiệu ngành {name}", "hoi_nganh_hoc"))
            major_rows.append((f"ngành {name} học gì", "hoi_nganh_hoc"))
            major_rows.append((f"mô tả ngành {name}", "hoi_nganh_hoc"))
            major_rows.append((f"ngành {name} là gì", "hoi_nganh_hoc"))
            major_rows.append((f"chương trình đào tạo ngành {name}", "hoi_nganh_hoc"))
            major_rows.append((f"cho mình xin mô tả ngành {name}", "hoi_nganh_hoc"))
            major_rows.append((f"mình đang phân vân về ngành {name}, bạn nói giúp", "hoi_nganh_hoc"))
            major_rows.append((f"bạn kể sơ về ngành {name} với được không", "hoi_nganh_hoc"))
            # Combinations
            major_rows.append((f"ngành {name} dùng tổ hợp nào", "hoi_to_hop_mon"))
            major_rows.append((f"khối thi của ngành {name} là gì", "hoi_to_hop_mon"))
            major_rows.append((f"các tổ hợp xét tuyển ngành {name}", "hoi_to_hop_mon"))
            major_rows.append((f"khối thi vào {name} là gì", "hoi_to_hop_mon"))
            major_rows.append((f"cần tổ hợp môn nào để vào ngành {name}", "hoi_to_hop_mon"))
            # Methods
            major_rows.append((f"phương thức xét tuyển ngành {name}", "hoi_phuong_thuc"))
            major_rows.append((f"ngành {name} xét học bạ không", "hoi_phuong_thuc"))
            major_rows.append((f"ngành {name} có tuyển thẳng không", "hoi_phuong_thuc"))
            major_rows.append((f"ngành {name} có VSAT không", "hoi_phuong_thuc"))
            major_rows.append((f"ngành {name} có SPT không", "hoi_phuong_thuc"))
            major_rows.append((f"ngành {name} nhận chứng chỉ quốc tế không", "hoi_phuong_thuc"))
            major_rows.append((f"mình muốn biết ngành {name} có những phương thức nào", "hoi_phuong_thuc"))
            # Scores (years)
            for y in year_variants:
                major_rows.append((f"điểm chuẩn ngành {name} năm {y}", "hoi_diem_chuan"))
                major_rows.append((f"mình cần điểm chuẩn của ngành {name} năm {y}", "hoi_diem_chuan"))
            # Quota
            major_rows.append((f"chỉ tiêu tuyển sinh ngành {name}", "hoi_chi_tieu"))
            major_rows.append((f"năm nay ngành {name} tuyển bao nhiêu chỉ tiêu", "hoi_chi_tieu"))
            # Tuition
            major_rows.append((f"học phí ngành {name}", "hoi_hoc_phi"))
            major_rows.append((f"chi phí học ngành {name} khoảng bao nhiêu", "hoi_hoc_phi"))
            # Major code ask
            major_rows.append((f"mã ngành của {name} là gì", "hoi_ma_nganh"))
            major_rows.append((f"cho mình xin mã ngành của {name}", "hoi_ma_nganh"))
        if code:
            major_rows.append((f"thông tin ngành {code}", "hoi_nganh_hoc"))
            major_rows.append((f"ngành {code} dùng tổ hợp nào", "hoi_to_hop_mon"))
            for y in year_variants:
                major_rows.append((f"điểm chuẩn ngành {code} năm {y}", "hoi_diem_chuan"))
                major_rows.append((f"mình hỏi điểm chuẩn {code} năm {y}", "hoi_diem_chuan"))
            major_rows.append((f"chỉ tiêu tuyển sinh ngành {code}", "hoi_chi_tieu"))
            major_rows.append((f"học phí ngành {code}", "hoi_hoc_phi"))
            major_rows.append((f"phương thức xét tuyển ngành {code}", "hoi_phuong_thuc"))
            major_rows.append((f"ngành {code} có tuyển thẳng không", "hoi_phuong_thuc"))
        for utterance, intent in major_rows:
            rows.append((utterance, intent))
            for prefix in soft_prefixes:
                combined = f"{prefix} {utterance}"
                rows.append((combined, intent))
    return rows


def write_intents(path: str, rows):
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for u, i in rows:
        u_norm = " ".join(u.split())  # collapse spaces
        key = (u_norm.strip().lower(), i)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((u_norm, i))
        # add non-diacritic variant if different
        u_ascii = strip_diacritics(u_norm)
        if u_ascii != u_norm:
            key2 = (u_ascii.strip().lower(), i)
            if key2 not in seen:
                seen.add(key2)
                deduped.append((u_ascii, i))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in deduped:
            writer.writerow(r)


def main():
    majors = read_majors(MAJORS_CSV)
    programs = read_programs_from_targets(ADMISSION_TARGETS_CSV)
    # Merge majors and programs, prioritize explicit majors entries
    merged = majors[:]
    # add programs that are not already in majors by (name, code)
    existing = {(m["name"].lower(), m["code"]) for m in majors}
    for p in programs:
        key = (p["name"].lower(), p["code"])
        if key not in existing:
            merged.append(p)
    rows = make_generic_rows()
    rows += make_global_dataset_rows()
    rows += make_major_rows(merged)
    write_intents(INTENT_CSV, rows)
    print(f"Wrote {len(rows)} rows (before dedup) to {INTENT_CSV}")


if __name__ == "__main__":
    main()
