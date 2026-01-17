import os
import re
import requests
import pandas as pd

URLS = {
    # Length / height for age
    "boys_length_0-13_weeks_pctl": "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_boys_p_0_13.xlsx",
    "boys_length_0-2_years_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_boys_p_0_2.xlsx",
    "boys_height_2-5_years_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_boys_p_2_5.xlsx",
    "girls_length_0-13_weeks_pctl": "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_0_13.xlsx",
    "girls_length_0-2_years_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_0_2.xlsx",
    "girls_height_2-5_years_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/tab_lhfa_girls_p_2_5.xlsx",

    # Weight for age
    "boys_weight_0-13_weeks_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/tab_wfa_boys_p_0_13.xlsx",
    "boys_weight_0-5_years_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/tab_wfa_boys_p_0_5.xlsx",
    "girls_weight_0-13_weeks_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/tab_wfa_girls_p_0_13.xlsx",
    "girls_weight_0-5_years_pctl":"https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/tab_wfa_girls_p_0_5.xlsx",
}

RAW_DIR = "data/raw_excel"
CSV_DIR = "data/csv"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)


def download_excel(name: str, url: str) -> str:
    """Download an Excel file and return its local path."""
    filename = f"{name}.xlsx"
    path = os.path.join(RAW_DIR, filename)

    response = requests.get(url)
    response.raise_for_status()

    with open(path, "wb") as f:
        f.write(response.content)

    return path


def excel_to_csv(excel_path: str, prefix: str) -> None:
    """Convert all sheets in an Excel file to CSV."""
    xls = pd.ExcelFile(excel_path)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        safe_filename = re.sub(r"[^A-Za-z0-9_-]+", "_", prefix.strip())
        safe_sheet = re.sub(r"[^A-Za-z0-9_-]+", "_", sheet.strip())
        csv_path = os.path.join(CSV_DIR, f"{safe_filename}_{safe_sheet}.csv")
        df.to_csv(csv_path, index=False)


def fetch_all_growth_charts() -> None:
    """Download and convert all WHO growth chart Excel files."""
    for name, url in URLS.items():
        excel_path = download_excel(name, url)
        excel_to_csv(excel_path, name)

if __name__ == "__main__":
    fetch_all_growth_charts()
