# 🧠 AI-Powered Resume Parser and Skill Matcher

This project is an end-to-end system for extracting, enriching, and matching candidate resume skills against job descriptions using:

- ✅ Apache Tika for resume parsing (`.pdf`, `.docx`)
- ✅ Ontology-based skill extraction (ESCO-enhanced)
- ✅ LLM-based skill inference (OpenAI GPT-4o or GPT-3.5)
- ✅ OpenAI Embeddings (`text-embedding-3-large`) for similarity scoring
- ✅ MongoDB storage for parsed profiles
- ✅ Conditional LLM usage based on skill match score
- ✅ Secure `.env`-based configuration

---

## 📦 Features

| Module                         | Description                                                        |
|--------------------------------|--------------------------------------------------------------------|
| `resume-parser.py`             | Flask microservice to upload and parse resumes                    |
| `services/ontology_skill_extractor.py` | Extracts skills using a preloaded ontology                     |
| `services/llm_skill_extractor.py`      | Extracts inferred skills via OpenAI LLM (conditionally)       |
| `utils/embedding_matcher.py`           | Compares candidate and job skills using OpenAI embeddings      |
| `utils/json_fixer.py`                  | Repairs malformed LLM JSON output                              |
| `convert_esco_json_to_ontology.py`     | Extracts skills from ESCO JSON format into `skills_ontology.txt` |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-org/resume-skill-matcher.git
cd resume-skill-matcher
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare `.env` file

```env
# .env
OPENAI_PASS_PHRASE=your-openai-api-key
MONGO_URI=mongodb://localhost:27017
```

### 4. Start the Flask microservice

```bash
python resume-parser.py
```

You can now POST resumes to:

```
POST http://localhost:5000/api/v1/parseResume
```

---

## 🧪 API Usage

```bash
curl -X POST http://localhost:5000/api/v1/parseResume \
  -F "file=@D:/resume.pdf"
```

Response (simplified):

```json
{
  "email": "jane@example.com",
  "phone": "+91-9876543210",
  "skills_ontology": [...],
  "skills_llm": [...],
  "match_score": 0.78,
  "match_quality": "High"
}
```

---

## 🧰 Ontology Enrichment with ESCO

To extract skills from ESCO JSON structure:

```bash
python convert_esco_json_to_ontology.py path/to/esco_node.json
```

This will generate `skills_ontology.txt`.

---

## 🧠 Skill Match Logic

| Match Score Range | Flag      |
|-------------------|-----------|
| `< 0.6`           | Low       |
| `0.6 – 0.7`       | Good      |
| `0.7 – 0.99`      | High      |
| `1.0`             | Perfect   |

LLM skill extraction is triggered **only when score ≥ 0.6**.

---

## 🧱 Folder Structure

```
.
├── resume-parser.py
├── .env
├── skills_ontology.txt
├── convert_esco_json_to_ontology.py
├── services/
│   ├── llm_skill_extractor.py
│   └── ontology_skill_extractor.py
├── utils/
│   ├── embedding_matcher.py
│   └── json_fixer.py
├── parsed_output/
├── uploads/
└── requirements.txt
```

---

## ✅ TODOs

- [ ] Add deduplication of LLM and ontology skills
- [ ] Auto-enrich ontology with LLM-extracted skills
- [ ] Resume/job description language detection
- [ ] Web dashboard to manage parsed profiles

---

## 🤝 Contributing

Pull requests welcome! Please fork the repo and submit a PR for review.

---

## 🛡 Security

Ensure `.env` is listed in `.gitignore`:
```
.env
```

To remove `.env` from Git if already committed:

```bash
git rm --cached .env
```

---

## 📄 License

MIT License
