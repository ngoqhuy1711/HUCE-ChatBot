import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "admission_scores.csv")
sys.path.insert(0, ROOT)

# Ensure UTF-8 output
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from services.nlp_service import get_nlp_service  # type: ignore


def main():
    with open(DATA, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        names = []
        for r in reader:
            name = (r.get("program_name") or "").strip()
            if name:
                names.append(name)

    nlp = get_nlp_service()

    years = ["2023", "2024"]
    missing = []

    for name in names:
        for year in years:
            msg = f"Điểm chuẩn ngành {name} năm {year}"
            result = nlp.handle_message(msg, {})
            resp = result.get("response", {})
            message = resp.get("message", "")
            if "Không tìm thấy dữ liệu phù hợp" in message:
                missing.append((name, year))

    print("TOTAL QUERIES:", len(names) * len(years))
    print("MISSING COUNT:", len(missing))
    for name, year in missing:
        print(f"- {name} ({year})")


if __name__ == "__main__":
    main()
