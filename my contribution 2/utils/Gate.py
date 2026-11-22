CATEGORIES = {
    "Simple Cell Lookup",
    "Filter + Lookup (WHERE Condition)",
    "Aggregation (COUNT)",
    "Superlative / Argmax",
    "Comparison Between Two Companies",
    "Arithmetic Operations over Table Cells",
    "Multi-Step and Compositional WikiTQ-Style Questions",
}

def normalize_category(text: str) -> str:
    t = (text or "").strip()
    # Sometimes models add punctuation or quotes
    t = t.strip("'\" \n\t.")
    return t
def safe_generate_category(gpt_llm, statement: str, llm_options=None, retries=3) -> str:
    prompt = (
        f"Here is a question: '{statement}'\n"
        "Classify this question into one of the following categories and return only the category name:\n"
        "Simple Cell Lookup, Filter + Lookup (WHERE Condition), Aggregation (COUNT), Superlative / Argmax, "
        "Comparison Between Two Companies, Arithmetic Operations over Table Cells, Multi-Step and Compositional WikiTQ-Style Questions."
    )

    last = ""
    for _ in range(retries):
        resp = gpt_llm.generate(prompt, **(llm_options or {})) if llm_options is not None else gpt_llm.generate(prompt)

        # If your generate() returns an object, adapt extraction here:
        text = resp if isinstance(resp, str) else str(resp)

        text = normalize_category(text)
        last = text
        if text in CATEGORIES:
            return text

    # Fallback so your pipeline never breaks
    return last or "Unknown"