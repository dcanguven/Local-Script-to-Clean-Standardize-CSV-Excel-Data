import pandas as pd
import json
import os
import re

CURRENCY_PATTERNS = {
    "USD": [r"\$", r"\bUSD\b", r"US\$"],
    "EUR": [r"€", r"\bEUR\b"],
    "GBP": [r"£", r"\bGBP\b"],
    "TRY": [r"₺", r"\bTRY\b", r"\bTL\b"],
    "CAD": [r"\bCAD\b", r"C\$"],
    "AUD": [r"\bAUD\b", r"A\$"],
    "INR": [r"\bINR\b", r"₹"],
    "JPY": [r"\bJPY\b", r"¥"],
    "CNY": [r"\bCNY\b", r"\bRMB\b", r"¥"],
    "CHF": [r"\bCHF\b"],
    "SEK": [r"\bSEK\b"],
    "NOK": [r"\bNOK\b"]
}

def detect_currency(x, default="USD"):
    s = str(x).upper()
    for code, pats in CURRENCY_PATTERNS.items():
        for p in pats:
            if re.search(p, s):
                return code
    return default


def load_files(path):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    elif path.endswith((".xls", ".xlsx")):
        return pd.read_excel(path)
    else:
        raise ValueError("Unsupported file format. Please provide CSV or Excel.")

def normalize_headers(df, mapping_file="config/header_map.json"):
    with open(mapping_file, "r") as f:
        header_map = json.load(f)

    df.columns = [col.strip().lower() for col in df.columns]
    df.rename(columns=lambda x: header_map.get(x, x), inplace=True)
    return df

def clean_columns(df):
    cols = [c for c in ["record_id","date","description","address","contractor_owner","valuation","fees"] if c in df.columns]
    df = df.loc[:, cols]
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()
    if "valuation" in df.columns:
        df["valuation_currency"] = df["valuation"].apply(detect_currency)
    if "fees" in df.columns:
        df["fees_currency"] = df["fees"].apply(detect_currency)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    for c in ("valuation","fees"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(r"[^\d\.\-]","",regex=True), errors="coerce")
    df = df.drop_duplicates(subset=["record_id"]) if "record_id" in df.columns else df.drop_duplicates()
    return df

def enrich_classification(df, rules_file="config/classification_rules.json"):
    with open(rules_file, "r") as f:
        cfg = json.load(f)
    fields = [c for c in cfg.get("search_fields", []) if c in df.columns]
    labels = cfg.get("priority", [])
    rules = cfg.get("rules", {})

    def classify_row(row):
        text = " ".join(str(row[c]) for c in fields).lower()
        for label in labels:
            for kw in rules.get(label, []):
                if re.search(rf"\b{re.escape(kw.lower())}\b", text):
                    return label.capitalize()
        return "Unknown"

    df["classification"] = df.apply(classify_row, axis=1) if fields else "Unknown"
    return df

def export_output(df, path):
    df.to_csv(path, index=False)