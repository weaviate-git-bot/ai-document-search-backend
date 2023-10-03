import pandas as pd

from ai_document_search_backend.utils.relative_path_from_file import relative_path_from_file

SOURCE_DATA_PATH = relative_path_from_file(__file__, "../../data/NTNU_2023v2.xlsx")
OUTPUT_DATA_PATH = relative_path_from_file(__file__, "../../data/clean_data.csv")

documents = pd.read_excel(SOURCE_DATA_PATH, engine="openpyxl", sheet_name="Documents")
real_estate_bonds = pd.read_excel(
    SOURCE_DATA_PATH, engine="openpyxl", sheet_name="116 Real Estate", usecols=range(19)
)
df = documents.merge(real_estate_bonds, on="isin", how="inner")
# df = df[df["Currency"] == "EUR"]  # try getting only English ones
# TODO later all types
df = df[df["MarketNewsTypeName"] == "BondTerms"]

df["link"] = df["link"].apply(lambda x: x.replace(".PDF", ".pdf"))

# Neither filenames nor ISINs are unique.
# Let's take unique filenames and extract ISINs from them (the value before underscore).
df["filename"] = df["link"].apply(lambda x: x.split("/")[-1])
df = df.drop_duplicates(subset=["filename"])
df["isin"] = df["filename"].apply(lambda x: x.split("_")[0])

df = df[["isin", "link", "filename", "IndustryGrouping", "MarketNewsTypeName"]]
df.to_csv(OUTPUT_DATA_PATH, index=False)
