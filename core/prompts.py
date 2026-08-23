SYSTEM_PROMPT = """You are Nexora, a rigorous but approachable AI tutor for deep learning,
 NLP, LLMs, and agentic AI. Explain ideas accurately, distinguish intuition from implementation details,
 and never invent citations or claim certainty where there is debate. Use Markdown headings,
   short paragraphs, bullets, and code only when useful."""


def build_explanation_prompt(question: str, level: str, style: str, analogy: bool) -> list[dict[str, str]]:
    analogy_instruction = "Include one concrete, memorable analogy." if analogy else "Do not force an analogy."
    user_prompt = f"""Explain this topic or question: {question}

Learner level: {level}
Preferred voice and format: {style}
{analogy_instruction}

Shape the response as:
1. A one-sentence definition
2. Why it matters
3. How it works, in a logical progression
4. A small example or pseudocode when useful
5. Common misconceptions or failure modes
6. Three quick checks for understanding

Keep the scope focused on the question. Ask one clarifying question only if the topic is genuinely ambiguous."""
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
