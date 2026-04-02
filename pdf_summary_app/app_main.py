import os
import time

from pdf_summary_app.pdf_utils import select_pdf_folder
from pdf_summary_app.reference_utils import build_ranked_reference_candidates
from pdf_summary_app.search_utils import load_candidate_references, write_candidate_search_outputs
from pdf_summary_app.summary_outputs import merge_summaries, merge_summaries_by_relevance
from pdf_summary_app.summary_pipeline import summarize_paper_by_sections


def main() -> None:
    pdf_paths = select_pdf_folder()

    if not pdf_paths:
        print("No files selected.")
        return

    pdf_dirs = sorted({os.path.dirname(os.path.abspath(path)) for path in pdf_paths})

    for pdf_dir in pdf_dirs:
        os.chdir(pdf_dir)
        in_dir = [path for path in pdf_paths if os.path.dirname(os.path.abspath(path)) == pdf_dir]

        for path in in_dir:
            filename = os.path.splitext(os.path.basename(path))[0]
            summary_file = f"Summary_{filename}.txt"

            if os.path.exists(summary_file):
                print(f"Skipping {filename}, summary already exists.")
                continue

            print(f"\nProcessing: {filename}")
            try:
                summary = summarize_paper_by_sections(path)
            except Exception as exc:
                print(f"Error summarizing {filename}: {type(exc).__name__}: {exc}")
                continue

            with open(summary_file, "w", encoding="utf-8") as outfile:
                outfile.write(summary)

            print(f"Saving: {summary_file}")
            time.sleep(1)

        merge_summaries()
        merge_summaries_by_relevance()
        build_ranked_reference_candidates(
            include_levels=("Highly Relevant", "Relevant"),
            output_file="CandidateReferences_FromRelevantPapers.txt",
        )
        queries = load_candidate_references("CandidateReferences_FromRelevantPapers.txt", max_items=50)
        write_candidate_search_outputs(queries)
