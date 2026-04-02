import os
import re
from urllib.parse import quote_plus


def load_candidate_references(
    candidate_file: str = "CandidateReferences_FromRelevantPapers.txt",
    max_items: int = 50,
) -> list[str]:
    if not os.path.exists(candidate_file):
        print(f"[WARN] Candidate file not found: {candidate_file}")
        return []

    queries = []
    with open(candidate_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            match = re.match(r"^\d+\.\s+(.*)$", line)
            if not match:
                continue
            citation = match.group(1)

            title_match = re.search(r'[\"](.{5,250}?)[\"]', citation)
            if title_match:
                queries.append(title_match.group(1).strip())
            else:
                queries.append(citation)

            if len(queries) >= max_items:
                break

    return queries


def write_candidate_search_outputs(
    queries: list[str],
    out_queries: str = "CandidateReferences_Queries.txt",
    out_links: str = "CandidateReferences_Links.txt",
) -> None:
    with open(out_queries, "w", encoding="utf-8") as outfile:
        for query in queries:
            outfile.write(query + "\n")
    print(f"Saving: {out_queries}")

    with open(out_links, "w", encoding="utf-8") as outfile:
        for query in queries:
            scholar = "https://scholar.google.com/scholar?q=" + quote_plus(query)
            semantic = "https://www.semanticscholar.org/search?q=" + quote_plus(query)
            crossref = "https://search.crossref.org/?q=" + quote_plus(query)
            outfile.write(
                f"{query}\n"
                f"  Scholar: {scholar}\n"
                f"  Semantic Scholar: {semantic}\n"
                f"  Crossref: {crossref}\n\n"
            )
    print(f"Saving: {out_links}")
