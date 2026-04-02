import os
import re
import unicodedata
from dataclasses import dataclass

from pdf_summary_app.config import KEYWORDS
from pdf_summary_app.summary_outputs import extract_relevance_level, list_summary_files


@dataclass(frozen=True)
class RefKey:
    title_key: str
    author_key: str
    year: str


@dataclass
class RefCandidate:
    raw_citation: str
    why_lines: list[str]
    source_papers: set[str]
    freq: int = 0
    strength: int = 0


def strip_markdown_emphasis(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    return text


def normalize_title_key(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"(?i)^\s*summary_", "", text)
    text = re.sub(r"(?i)\.txt\s*$", "", text)
    text = unicodedata.normalize("NFKD", text).lower().strip()
    text = re.sub(r"[\u2013\u2014]", "-", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_author_key(text: str) -> str:
    return normalize_title_key(text)


def extract_section_block(summary_text: str, section_number: int) -> str:
    lines = summary_text.splitlines()
    start_re = re.compile(rf"\bSECTION\s+{section_number}\s*:", re.IGNORECASE)
    any_section_re = re.compile(r"\bSECTION\s+(\d+)\s*:", re.IGNORECASE)

    start_idx = None
    for index, line in enumerate(lines):
        if start_re.search(line):
            start_idx = index + 1
            break
    if start_idx is None:
        return ""

    collected = []
    for index in range(start_idx, len(lines)):
        line = lines[index]
        match = any_section_re.search(line)
        if match:
            found_num = int(match.group(1))
            if found_num != section_number:
                break
            continue
        collected.append(line)

    return "\n".join(collected).strip()


def parse_reviewed_paper_key_from_section1(section1_text: str) -> tuple[str, str, str]:
    text = strip_markdown_emphasis(section1_text)
    lines = [line.rstrip("\n") for line in text.splitlines()]

    def strip_bullet_prefix(value: str) -> str:
        return re.sub(r"^\s*[-*]\s*", "", value).strip()

    def extract_field(label_patterns: list[str]) -> str:
        for label_pattern in label_patterns:
            match = re.search(rf"(?im)^\s*[-*]?\s*{label_pattern}\s*:\s*(.+?)\s*$", text)
            if match:
                value = strip_bullet_prefix(match.group(1).strip())
                return "" if value.lower() == "not reported" else value

        label_res = [re.compile(rf"(?i)^\s*[-*]?\s*{label_pattern}\s*$") for label_pattern in label_patterns]
        for idx, line in enumerate(lines):
            if any(regex.match(line.strip()) for regex in label_res):
                for next_idx in range(idx + 1, len(lines)):
                    next_line = lines[next_idx].strip()
                    if not next_line:
                        continue
                    if any(regex.match(next_line) for regex in label_res):
                        continue
                    value = strip_bullet_prefix(next_line)
                    return "" if value.lower() == "not reported" else value
        return ""

    title = extract_field([r"Paper\s*Title", r"Title"])
    authors_line = extract_field([r"Authors?", r"Author\(s\)"])
    year_line = extract_field([r"Year\s*of\s*Publication", r"Publication\s*Year", r"Year"])

    first_author = ""
    if authors_line:
        first_author = re.split(r"[;,]|\s+and\s+", authors_line, maxsplit=1, flags=re.IGNORECASE)[0].strip()

    year = ""
    if year_line:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", year_line)
        if match:
            year = match.group(1)
    if not year:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        if match:
            year = match.group(1)

    return (normalize_title_key(title), normalize_author_key(first_author), year)


def split_references_section6(section6_text: str) -> list[str]:
    section6_text = strip_markdown_emphasis(section6_text).strip()
    section6_text = re.sub(r"(?im)^\s*Key References\s*$", "", section6_text).strip()
    parts = re.split(r"(?m)^\s*(?=\d+\.\s+)", section6_text)
    return [part.strip() for part in parts if part.strip()]


def extract_first_author_surname(author_str: str) -> str:
    author_str = author_str.strip()
    first = author_str.split(",")[0].strip()
    return normalize_author_key(first)


def parse_ref_block(ref_block: str) -> tuple[RefKey, str, str]:
    ref_block = strip_markdown_emphasis(ref_block)
    lines = [line.rstrip() for line in ref_block.splitlines() if line.strip()]
    if not lines:
        return RefKey("", "", ""), "", ""

    raw_line = lines[0].strip()
    citation = re.sub(r"^\s*\d+\.\s*", "", raw_line).strip()

    why_lines = []
    for line in lines[1:]:
        if re.match(r"^\s*-\s+", line):
            why_lines.append(re.sub(r"^\s*-\s+", "", line).strip())
    why_text = " ".join(why_lines).strip()

    title = ""
    match = re.search(r'[\"](.{5,250}?)[\"]', citation)
    if match:
        title = match.group(1).strip()

    authors_part = citation.split('"', 1)[0].strip()
    first_author = extract_first_author_surname(authors_part) if authors_part else ""

    blob = " ".join(lines)
    match = re.search(r"\b(19\d{2}|20\d{2})\b", blob)
    year = match.group(1) if match else ""

    key = RefKey(
        title_key=normalize_title_key(title),
        author_key=normalize_author_key(first_author),
        year=year,
    )
    return key, citation, why_text


def relevance_explanation_strength(explanation: str) -> int:
    text = explanation.lower()
    score = 0
    for keyword in KEYWORDS:
        if keyword in text:
            score += 2
    if re.search(r"\b\d+(\.\d+)?\s*hz\b", text):
        score += 2
    if "not reported" in text:
        score -= 2
    return max(0, min(score, 30))


def build_ranked_reference_candidates(
    include_levels=("Highly Relevant", "Relevant"),
    output_file="CandidateReferences_FromRelevantPapers.txt",
) -> None:
    summary_files = list_summary_files()

    reviewed_title_only: set[str] = set()
    reviewed_author_year: set[tuple[str, str]] = set()

    for summary_file in summary_files:
        with open(summary_file, "r", encoding="utf-8") as infile:
            text = infile.read()
        section1 = extract_section_block(text, 1)
        title_key, author_key, year = parse_reviewed_paper_key_from_section1(section1)
        if title_key:
            reviewed_title_only.add(title_key)
        if author_key and year:
            reviewed_author_year.add((author_key, year))

    candidates: dict[RefKey, RefCandidate] = {}

    for summary_file in summary_files:
        with open(summary_file, "r", encoding="utf-8") as infile:
            text = infile.read()

        level = extract_relevance_level(text)
        if level not in include_levels:
            continue

        section6 = extract_section_block(text, 6)
        if not section6:
            continue

        for block in split_references_section6(section6):
            key, raw_citation, why = parse_ref_block(block)
            if not (key.title_key or key.author_key or key.year):
                continue

            if key not in candidates:
                candidates[key] = RefCandidate(
                    raw_citation=raw_citation,
                    why_lines=[why] if why else [],
                    source_papers={summary_file},
                )
            else:
                candidates[key].source_papers.add(summary_file)
                if why:
                    candidates[key].why_lines.append(why)

    for candidate in candidates.values():
        candidate.freq = len(candidate.source_papers)
        candidate.strength = max((relevance_explanation_strength(line) for line in candidate.why_lines), default=0)

    filtered: list[tuple[RefKey, RefCandidate]] = []
    for key, candidate in candidates.items():
        if key.title_key and key.title_key in reviewed_title_only:
            continue
        if (not key.title_key) and key.author_key and key.year:
            if (key.author_key, key.year) in reviewed_author_year:
                continue
        filtered.append((key, candidate))

    filtered.sort(key=lambda item: (-item[1].freq, -item[1].strength, item[1].raw_citation.lower()))

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("===== Candidate References to Find Next =====\n")
        outfile.write(f"Sources included: {', '.join(include_levels)}\n")
        outfile.write(f"Total candidates (post-dedupe, post-reviewed-removal): {len(filtered)}\n")
        outfile.write("=" * 60 + "\n\n")

        for index, (_, candidate) in enumerate(filtered, 1):
            outfile.write(f"{index}. {candidate.raw_citation}\n")
            outfile.write(f"   Frequency across papers: {candidate.freq}\n")
            outfile.write(f"   Relevance-explanation strength: {candidate.strength}\n")

            if candidate.why_lines:
                scored = sorted(
                    [(relevance_explanation_strength(line), line) for line in candidate.why_lines if line],
                    key=lambda item: -item[0],
                )
                for _, line in scored:
                    outfile.write(f"   Why it matters (from summaries): {line}\n")
            else:
                outfile.write("   Why it matters (from summaries): Not reported\n")

            outfile.write(f"   Mentioned in: {', '.join(sorted(candidate.source_papers))}\n\n")

    print(f"Saving: {output_file}")
