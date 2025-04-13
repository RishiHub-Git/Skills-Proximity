import re

class OntologySkillExtractor:
    def __init__(self, skill_list_path="skills_ontology.txt"):
        with open(skill_list_path, 'r', encoding='utf-8') as f:
            self.skills = [line.strip().lower() for line in f if line.strip()]

    def extract_skills(self, resume_text):
        found_skills = set()
        text = resume_text.lower()
        for skill in self.skills:
            pattern = rf'\b{re.escape(skill)}\b'
            if re.search(pattern, text):
                found_skills.add(skill)
        return list(found_skills)
