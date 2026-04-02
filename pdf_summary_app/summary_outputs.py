import os
import re
from typing import Optional

from pdf_summary_app.config import RELEVANCE_LABELS


def list_summary_files() -> list[str]:
    return sorted(
        [filename for filename in os.listdir() if filename.startswith("Summary_") and filename.lower().endswith(".txt")]
    )


def merge_summaries(output_file: str = "AllSummaries.txt") -> None:
    summary_files = list_summary_files()
    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in summary_files:
            paper_name = os.path.splitext(filename)[0].replace("Summary_", "", 1)
            with open(filename, "r", encoding="utf-8") as infile:
                outfile.write(f"\n\n===== Summary for: {paper_name} =====\n\n")
                outfile.write(infile.read())
                outfile.write("\n" + "=" * 50 + "\n")
    print(f"Saving merged summaries: {output_file}")


def extract_relevance_level(summary_text: str) -> Optional[str]:
    pattern = r"^\s*Relevance\s*Level\s*:\s*(Highly Relevant|Relevant|Loosely Relevant|Not Relevant)\s*$"
    match = re.search(pattern, summary_text, flags=re.MULTILINE)
    return match.group(1) if match else None


def merge_summaries_by_relevance() -> None:
    summary_files = list_summary_files()
    buckets: dict[str, list[tuple[str, str]]] = {label: [] for label in RELEVANCE_LABELS}

    for filename in summary_files:
        with open(filename, "r", encoding="utf-8") as infile:
            text = infile.read()

        level = extract_relevance_level(text)
        if level not in buckets:
            level = "Not Relevant"
        buckets[level].append((filename, text))

    outputs = {
        "Highly Relevant": "AllHighlyRelevantSummaries.txt",
        "Relevant": "AllRelevantSummaries.txt",
        "Loosely Relevant": "AllLooselyRelevantSummaries.txt",
        "Not Relevant": "AllNotRelevantSummaries.txt",
    }

    for level, output_name in outputs.items():
        with open(output_name, "w", encoding="utf-8") as outfile:
            outfile.write(f"===== {level} Summaries =====\n")
            outfile.write(f"Total papers: {len(buckets[level])}\n")
            outfile.write("=" * 50 + "\n\n")

            for filename, text in buckets[level]:
                paper_name = os.path.splitext(filename)[0].replace("Summary_", "", 1)
                outfile.write(f"\n\n===== Summary for: {paper_name} =====\n\n")
                outfile.write(text)
                outfile.write("\n" + "=" * 50 + "\n")

        print(f"Saving: {output_name}  ({len(buckets[level])} papers)")
