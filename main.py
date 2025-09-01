from cleaning import load_files, normalize_headers, clean_columns, enrich_classification, export_output

def main():
    df = load_files("data/sample.csv")
    df = normalize_headers(df)
    df = clean_columns(df)
    df = enrich_classification(df)
    export_output(df, "output/sample_std.csv")

if __name__ == "__main__":
    main()