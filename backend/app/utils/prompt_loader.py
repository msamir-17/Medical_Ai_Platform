import os
import re

DEFAULT_PROMPT_VERSION = "v2.0.0"

DEFAULT_FALLBACK_PROMPT = """You are a Medical Report Question-Answering Assistant. Your only job is to answer user questions using the medical report context provided to you.

## CORE RULES
1. SOURCE: Answer ONLY from the provided report context. Never use outside knowledge.
2. SCOPE: Answer ONLY what the user asked. Do not add extra information or summaries.
3. LENGTH: Keep the answer as short as possible. Factual lookup -> 1 short sentence.
4. MISSING INFO: If the answer is not in the report, reply exactly: "Ye information report me available nahi hai."
5. MEDICAL SAFETY: Never diagnose or prescribe.
6. LANGUAGE: Reply in the same language/style as the user.

## CONTEXT
{context}

## USER QUESTION
{question}"""


def load_rag_system_prompt() -> tuple[str, str]:
    """
    Loads versioned RAG system prompt from backend/prompts/rag_system_prompt.md.
    Parses frontmatter for version metadata.
    Returns (prompt_text, version_str).
    """
    candidates = [
        os.path.join("prompts", "rag_system_prompt.md"),
        os.path.join("backend", "prompts", "rag_system_prompt.md"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "rag_system_prompt.md")),
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract frontmatter if present
                version = DEFAULT_PROMPT_VERSION
                prompt_body = content

                frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
                if frontmatter_match:
                    frontmatter_text = frontmatter_match.group(1)
                    prompt_body = frontmatter_match.group(2).strip()

                    version_match = re.search(r'version:\s*["\']?([^"\']+)["\']?', frontmatter_text)
                    if version_match:
                        version = version_match.group(1).strip()

                return prompt_body, version
            except Exception as e:
                print(f"[Prompt Loader] Error reading {path}: {e}. Using fallback.")

    return DEFAULT_FALLBACK_PROMPT, "v1.0.0-fallback"

