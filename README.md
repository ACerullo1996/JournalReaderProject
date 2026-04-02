# ProjectPDFSummary_RAVS

## Overview
This application processes research paper PDFs and creates structured text summaries using OpenAI. The workflow is designed for neuroscience and neural engineering literature review, with prompts tailored to extract metadata, methods, results, interpretation, limitations, key references, relevance to the project, and an introduction-ready summary.

## Main Features
- Select a folder containing PDF files through a file dialog
- Extract text from each PDF with PyMuPDF
- Summarize each paper in 8 structured sections using the OpenAI API
- Save one summary text file per paper
- Merge all summaries into combined output files
- Group summaries by relevance level
- Build a ranked list of candidate references from relevant papers
- Generate search query and search link files for follow-up paper discovery

## Project Structure
- `ProjectPDFSummary_RAVS.py`
  Main entry point for the app.
- `pdf_summary_app/config.py`
  Prompt text, model configuration, keyword lists, and `.env` loading.
- `pdf_summary_app/pdf_utils.py`
  PDF selection, PDF listing, and PDF text extraction utilities.
- `pdf_summary_app/openai_utils.py`
  OpenAI API calls and retry logic.
- `pdf_summary_app/summary_pipeline.py`
  Per-paper section-by-section summarization flow.
- `pdf_summary_app/summary_outputs.py`
  Summary merge and relevance bucket output generation.
- `pdf_summary_app/reference_utils.py`
  Reference parsing, ranking, and candidate selection.
- `pdf_summary_app/search_utils.py`
  Search query and search link output generation.
- `requirements.txt`
  Python package dependencies.
- `.env`
  Stores `OPENAI_API_KEY` for the app.

## Requirements
- Python 3.12 recommended
- A valid OpenAI API key
- Installed packages from `requirements.txt`
- A desktop environment that supports `tkinter` file dialogs

## Installed/Tested Package Versions
- `openai==0.28.0`
- `PyMuPDF==1.25.5`

## Setup
1. Open a terminal in the project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure the `.env` file contains your OpenAI API key:

```env
OPENAI_API_KEY=your_key_here
```

4. If you are cloning the project from GitHub, create your local `.env` from the example file and add your real key.

## GitHub Notes
- The real `.env` file is intended to stay local and should not be committed.
- Use `.env.example` as the template for local setup.
- Python cache files and generated summary outputs are ignored by `.gitignore`.

## How to Run
Run the main script:

```bash
python ProjectPDFSummary_RAVS.py
```

## What Happens When You Run It
1. A folder picker opens.
2. Choose a folder containing PDF files.
3. The app processes each PDF in that folder.
4. A summary file is created for each paper, named like `Summary_<paper_name>.txt`.
5. After processing, the app also creates combined outputs in the selected PDF folder.

## Generated Output Files
- `Summary_<paper_name>.txt`
  Structured summary for an individual PDF.
- `AllSummaries.txt`
  Combined summaries for all processed papers.
- `AllHighlyRelevantSummaries.txt`
- `AllRelevantSummaries.txt`
- `AllLooselyRelevantSummaries.txt`
- `AllNotRelevantSummaries.txt`
  Combined summaries grouped by relevance.
- `CandidateReferences_FromRelevantPapers.txt`
  Ranked follow-up references extracted from relevant paper summaries.
- `CandidateReferences_Queries.txt`
  Search queries for candidate references.
- `CandidateReferences_Links.txt`
  Search links for Google Scholar, Semantic Scholar, and Crossref.

## Notes
- If a summary file already exists for a PDF, that paper is skipped.
- Output files are written into the selected PDF folder, not necessarily the project root.
- The app uses a GUI folder picker, so it should be run in an environment with desktop access.
- The OpenAI client code currently uses the API style compatible with `openai==0.28.0`.

## Troubleshooting
- If the app says `No files selected.`, re-run it and choose a folder with PDF files.
- If the OpenAI API call fails, confirm that `OPENAI_API_KEY` is present in `.env`.
- If `tkinter` dialogs do not open, run the app from a local desktop Python session rather than a headless environment.
- If PyMuPDF is missing, reinstall dependencies with:

```bash
pip install -r requirements.txt
```
