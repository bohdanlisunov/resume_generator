import json
import re


import json

def load_vacancies(file="vacancies.json"):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_base_resume():
    """Завантажує основний текст резюме як джерело фактів"""
    with open("data/base_resume.txt", "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(vacancy):
    """Сильний промпт з жорсткою адаптацією під вакансію"""
    base = load_base_resume()
    keywords = ", ".join(vacancy.get("keywords", []))
    target_title = vacancy.get("title", "")

    return f"""You are a senior resume writer and ATS optimization expert.

You are competing with 500+ candidates. This resume must match the job максимально точно.

CRITICAL RULES:
- Use ONLY facts from BASE RESUME
- DO NOT invent achievements or metrics
- DO NOT copy text directly — rewrite EVERYTHING
- If text is похожий на original → rewrite again

TARGET POSITION: {target_title}
KEYWORDS: {keywords}

YOUR TASK:

1. TITLE
- Use Title Case
- Match target role exactly

2. SUMMARY
- 3–4 sentences
- Fully rewritten
- Focus on impact and relevance
- Use keywords naturally

3. SKILLS
- Keep only relevant skills
- Reorder by importance
- Format: Skill | Skill | Skill

4. EXPERIENCE (CRITICAL)
For EACH job:
- Rewrite ALL bullet points
- DO NOT copy original wording
- Focus on relevant experience for THIS job
- Use strong action verbs
- Adapt responsibilities to match target role
- You MAY reframe tasks but NOT invent

5. JOB TITLES
- MUST BE IN UPPERCASE
- Adapt to target role if relevant

6. FORMAT
- Plain text only
- Bullets start with "- "
- No markdown, no symbols like ** or #

BASE RESUME (Source of Truth):
---------------------
{base}
---------------------

STRICT OUTPUT FORMAT:

{{{{TITLE}}}}
{target_title}

{{{{SUMMARY}}}}
<text>

{{{{SKILLS}}}}
Skill | Skill | Skill

{{{{JOB_TITLE_1}}}}
<UPPERCASE TITLE>
{{{{BULLETS_1}}}}
- bullet
{{{{TECH_STACK_1}}}}
<tools>

{{{{JOB_TITLE_2}}}}
<UPPERCASE TITLE>
{{{{BULLETS_2}}}}
- bullet
{{{{TECH_STACK_2}}}}
<tools>

{{{{JOB_TITLE_3}}}}
<UPPERCASE TITLE>
{{{{BULLETS_3}}}}
- bullet
{{{{TECH_STACK_3}}}}
<tools>

{{{{JOB_TITLE_4}}}}
<UPPERCASE TITLE>
{{{{BULLETS_4}}}}
- bullet
{{{{TECH_STACK_4}}}}
<tools>

{{{{JOB_TITLE_5}}}}
<UPPERCASE TITLE>
{{{{BULLETS_5}}}}
- bullet
{{{{TECH_STACK_5}}}}
<tools>

{{{{JOB_TITLE_6}}}}
<UPPERCASE TITLE>
{{{{BULLETS_6}}}}
- bullet
{{{{TECH_STACK_6}}}}
<tools>

{{{{JOB_TITLE_7}}}}
<UPPERCASE TITLE>
{{{{BULLETS_7}}}}
- bullet
{{{{TECH_STACK_7}}}}
<tools>

{{{{JOB_TITLE_8}}}}
<UPPERCASE TITLE>
{{{{BULLETS_8}}}}
- bullet
{{{{TECH_STACK_8}}}}
<tools>
"""


def parse_response(response: str) -> dict:
    """Стабільний парсер для витягування секцій {{TAG}}"""
    result = {}

    pattern = re.compile(
        r"\{\{(.*?)\}\}\s*\n(.*?)(?=\n\{\{|\Z)",
        re.DOTALL
    )

    matches = pattern.findall(response)

    for key, value in matches:
        clean_key = key.strip()
        clean_value = value.strip()
        result[clean_key] = clean_value

    return result