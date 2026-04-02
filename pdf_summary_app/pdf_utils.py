import os
import re
import tkinter as tk
from tkinter import filedialog

import fitz


def select_pdfs() -> list[str]:
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(
        title="Select multiple PDF files",
        filetypes=[("PDF files", "*.pdf")],
    )
    return list(files)


def list_pdfs_in_folder(folder: str, recursive: bool = False) -> list[str]:
    pdfs = []
    if recursive:
        for root, _, files in os.walk(folder):
            for filename in files:
                if filename.lower().endswith(".pdf"):
                    pdfs.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(folder):
            if filename.lower().endswith(".pdf"):
                pdfs.append(os.path.join(folder, filename))
    return sorted(pdfs)


def select_pdf_folder() -> list[str]:
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select folder containing PDF files")
    return list_pdfs_in_folder(folder, recursive=False)


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_and_normalize_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    raw_text = "\n".join(page.get_text() for page in doc)
    return normalize_text(raw_text)
