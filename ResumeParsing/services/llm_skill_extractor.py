from openai import OpenAI

class LLMSkillExtractor:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def extract_skills(self, resume_text):
        prompt = f"""
You are an expert HR assistant. Extract all relevant technical and soft skills from the following resume text. Include both explicitly mentioned and inferred skills (based on job roles or experience). Return a clean list of skills.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )

        result = response.choices[0].message.content
        skill_lines = [line.strip('-• \n') for line in result.splitlines() if line.strip()]
        return skill_lines
