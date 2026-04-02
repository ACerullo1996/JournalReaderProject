import time

from pdf_summary_app.config import SECTION_PROMPTS
from pdf_summary_app.openai_utils import call_section
from pdf_summary_app.pdf_utils import extract_and_normalize_text


def extract_section_header(prompt: str) -> str:
    for line in prompt.strip().splitlines():
        line = line.strip()
        if line:
            if not line.upper().startswith("SECTION"):
                raise ValueError(f"Invalid section header (must start with 'SECTION'): '{line}'")
            return line
    raise ValueError("SECTION_PROMPT has no valid header line.")


def summarize_paper_by_sections(pdf_path: str) -> str:
    full_text = extract_and_normalize_text(pdf_path)
    compiled: list[str] = []
    prior_sections_context: list[str] = []

    for section_id in sorted(SECTION_PROMPTS.keys()):
        section_prompt = SECTION_PROMPTS[section_id]
        section_header = extract_section_header(section_prompt)
        print(f"  -> Extracting {section_header}")

        contextual_text = full_text
        if prior_sections_context:
            contextual_text += (
                "\n\n===== PREVIOUS SECTION SUMMARIES (FOR CONTEXT ONLY) =====\n"
                + "\n\n".join(prior_sections_context)
            )

        section_text = call_section(section_id=section_id, full_text=contextual_text)
        compiled.append(f"===== {section_header} =====\n{section_text}")
        prior_sections_context.append(f"{section_header}\n{section_text}")

        time.sleep(0.5)

    return "\n\n".join(compiled)
