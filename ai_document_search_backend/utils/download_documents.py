import os
import shutil
from pathlib import Path

import pandas as pd
import requests

from ai_document_search_backend.utils.relative_path_from_file import relative_path_from_file

SOURCE_DATA_PATH = relative_path_from_file(__file__, "../../data/NTNU_2023v2.xlsx")
DATA_DOWNLOAD_FOLDER = relative_path_from_file(__file__, "../../data/pdfs")

if os.path.exists(DATA_DOWNLOAD_FOLDER):
    shutil.rmtree(DATA_DOWNLOAD_FOLDER)
os.makedirs(DATA_DOWNLOAD_FOLDER)

documents = pd.read_excel(SOURCE_DATA_PATH, engine="openpyxl", sheet_name="Documents")
real_estate_bonds = pd.read_excel(
    SOURCE_DATA_PATH, engine="openpyxl", sheet_name="116 Real Estate", usecols=range(19)
)
df = documents.merge(real_estate_bonds, on="isin", how="inner")
# df = df[df["Currency"] == "EUR"]  # try getting only English ones
df = df[df["MarketNewsTypeName"] == "BondTerms"]

pdf_links = df["link"].tolist()
print(f"Number of PDFs: {len(pdf_links)}")

for pdf_link in pdf_links:
    filename = pdf_link.split("/")[-1]
    print(f"Downloading {filename}...")
    res = requests.get(pdf_link)
    with open(Path(DATA_DOWNLOAD_FOLDER) / filename, "wb") as f:
        f.write(res.content)
