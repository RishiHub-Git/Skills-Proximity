#More Fine-Tuned and Refined Json Output
from openai import OpenAI
import json
import re

class LLMSkillExtractor:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def fix_json(self, json_result):
        # Fix trailing comma
        # If it ends with `,"`, it means a broken item started
        if json_result.endswith(','):
            json_result = re.sub(r',\s*$', '', json_result)

        # Attempt to fix the final malformed element
        if not json_result.endswith(']'):
            # Try to close the last quote if it looks like an unclosed string
            if json_result.count('"') % 2 != 0:
                json_result += '"'
            json_result += ']'

        # Remove invalid items like `"SomeText]`
        json_result = re.sub(r'"([^"]+?)\]$', r'"\1"]', json_result)
        return json_result
    
    def extract_skills(self, resume_text):
        prompt = f"""
You are an expert technical recruiter. Analyze the candidate's resume below and return a JSON list of relevant technical and soft skills. Include both:

- Skills explicitly mentioned in the resume
- Inferred skills based on job roles, certifications, or education

⚠️ Return **only** a valid JSON array of skill strings. Do **not** include any explanations or formatting.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )

        result = response.choices[0].message.content.strip()

        # Parse JSON response safely
        try:
            result = result.strip()
            result = self.fix_json(result)

            skills = json.loads(result)
            print('Skills Extracted Successfully. OK')
            return [skill.strip() for skill in skills if isinstance(skill, str)]
        except Exception as e:
            print('🔄 Raw LLM response:', result)
            print('❌ Exception while parsing LLM output:', e)
            return []  # fallback if LLM output is malformed
