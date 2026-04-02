import time

import openai

from pdf_summary_app.config import MODEL_PAPER, OPENAI_API_KEY, SECTION_PROMPTS, SYSTEM_PROMPT


openai.api_key = OPENAI_API_KEY


def chat_completion_with_retry(
    messages,
    model: str,
    max_tokens: int = 1400,
    temperature: float = 0.0,
    retries: int = 2,
) -> str:
    last_err = None
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            last_err = exc
            sleep_seconds = min(60, 2 ** attempt)
            print(f"API error ({type(exc).__name__}): {exc}\nRetrying in {sleep_seconds}s...")
            time.sleep(sleep_seconds)
    raise last_err


def call_section(section_id: int, full_text: str) -> str:
    section_prompt = SECTION_PROMPTS[section_id].strip()
    user_prompt = f"{section_prompt}\n\nFULL PAPER TEXT:\n{full_text}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    return chat_completion_with_retry(
        messages=messages,
        model=MODEL_PAPER,
        max_tokens=1400,
        temperature=0,
        retries=2,
    )
