import pandas as pd

from ai_document_search_backend.utils.relative_path_from_file import relative_path_from_file

SOURCE_DATA_PATH = relative_path_from_file(__file__, "../../data/NTNU2.xlsx")
OUTPUT_DATA_PATH = relative_path_from_file(__file__, "../../data/clean_data.csv")

df = pd.read_excel(SOURCE_DATA_PATH, engine="openpyxl")

# Change the extension to lowercase.
df["link"] = df["link"].apply(lambda x: x.replace(".PDF", ".pdf"))

# Get the filename from the link.
df["filename"] = df["link"].apply(lambda x: x.split("/")[-1])

# Check that there are no duplicate filenames.
assert len(df["filename"].unique()) == len(df["filename"])

# Columns we want to keep and their new names.
columns_to_keep = {
    "link": "link",
    "shortname": "shortname",
    "isin": "isin",
    "issuer_name": "issuer_name",
    "filename": "filename",
    "Industry": "industry",
    "risk_type": "risk_type",
    "Green": "green",
}
df = df[list(columns_to_keep.keys())].rename(columns=columns_to_keep)

# Replace "Green" with "Yes" and fill nulls with "No"
df["green"] = df["green"].apply(lambda x: "Yes" if x == "Green" else "No")

df.to_csv(OUTPUT_DATA_PATH, index=False)
