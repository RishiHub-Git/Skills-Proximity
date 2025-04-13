from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SkillSimilarityScorer:
    def __init__(self, api_key, model="text-embedding-3-large"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _get_embedding(self, input_text):
        response = self.client.embeddings.create(
            input=input_text,
            model=self.model
        )
        return response.data[0].embedding

    def compute_similarity(self, candidate_skills, job_skills):
        if not candidate_skills or not job_skills:
            return 0.0

        # Turn lists into combined text for context-based embedding
        candidate_input = ", ".join(candidate_skills)
        job_input = ", ".join(job_skills)

        try:
            emb_candidate = self._get_embedding(candidate_input)
            emb_job = self._get_embedding(job_input)
            similarity = cosine_similarity([emb_candidate], [emb_job])[0][0]
            return round(float(similarity), 3)
        except Exception as e:
            print("❌ Error generating embeddings:", e)
            return 0.0
