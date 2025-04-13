from fileinput import filename
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from tika import parser
import uuid
import json
import re
from dotenv import load_dotenv
from pymongo import MongoClient
#from services.llm_skill_extractor import LLMSkillExtractor
from services.llm_skill_extractor_v2 import LLMSkillExtractor
from services.ontology_skill_extractor import OntologySkillExtractor
from services.semantic_matcher import SkillSimilarityScorer

# Initialize the Flask application
app = Flask(__name__)

#config
UPLOAD_FOLDER = './uploads'
PARSED_FOLDER = './parsed_output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PARSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PARSED_FOLDER'] = PARSED_FOLDER

#Load Environment Variables
#Create an environment variable in system environment with name "OPENAI_PASS_PHRASE" and value as your OpenAI API key
load_dotenv()
passPhrase = os.getenv("OPENAI_PASS_PHRASE")
print("Loaded API key:", passPhrase)

# MongoDB Config
client = MongoClient('mongodb://localhost:27017')
db = client['skills_proximity']
collection = db['parsed_resumes']

#allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

def parse_with_tika(file_path):
    parsed = parser.from_file(file_path)
    return parsed.get('content', '').strip()

def extract_entities(text, job_skills):
    # Simple regex-based extraction (can be replaced with NER models later)
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    
    # Extract phone number (international or local format)
    raw_phones = re.findall(r'(\+\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', text)
    phone = ''.join(raw_phones[0]) if raw_phones else None

    ontology_extractor = OntologySkillExtractor()
    skills_ontology = ontology_extractor.extract_skills(text)

    # Get average vector for resume and job skill sets
    if not skills_ontology or not job_skills:
        similarity_score = 0.0
        match_quality = "Low"
    else:
        # Initialize semantic matcher
        matcher = SkillSimilarityScorer(api_key=passPhrase)
        # Compare with job requirements
        similarity_score = matcher.compute_similarity(skills_ontology, job_skills)

        # Match flag
        if similarity_score >= 1.0:
            match_quality = "Perfect"
        elif similarity_score >= 0.7:
            match_quality = "High"
        elif similarity_score >= 0.6:
            match_quality = "Good"
        else:
            match_quality = "Low"
    
    # Only extract LLM skills if match is Good or above
    if similarity_score >= 0.6:
        llm_extractor = LLMSkillExtractor(api_key=passPhrase)
        skills_llm = llm_extractor.extract_skills(text)
    else:
        skills_llm = []
    
    return {
        'email': email[0] if email else None,
        'phone': phone,
        'skills_ontology': [{"name": s, "source": "Ontology"} for s in skills_ontology],
        'skills_llm': [{"name": s, "source": "LLM"} for s in skills_llm],
        'match_score': similarity_score,
        'match_quality': match_quality
    }

#curl -X POST http://localhost:5000/api/v1/parseResume -F "file=@D:\LRS_Resume.pdf"
@app.route('/api/v1/parseResume', methods=['POST'])
def parse_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(save_path)
        try:
            # Example job skill list
            job_skills = [
                ".NET Core",
                "Angular",
                "Kafka",
                "Redis",
                "Distributed Systems",
                "Microservices",
                "API Gateway",
                "3rd Party Integration Service",
                "Java",
                "Selenium",
                "JSF",
                "Hibernate",
                "PrimeFaces UI",
                "Cohere",
                "OpenAI LLMs",
                "Hugging Face",
                "Azure",
                "DevOps",
                "Generative AI",
                "AI Embedding",
                "RAG",
                "CICD",
                "TFS",
                "ASP.NET MVC",
                "ZAP",
                "Burp Suite",
                "SonarQube",
                "Distributed Caching",
                "ORM",
                "Secure Coding",
                "Agile Practices",
                "JavaScript"
            ]

            parsed_text = parse_with_tika(save_path)
            extracted_entities = extract_entities(parsed_text, job_skills)

            #After parse, file not needed
            os.remove(save_path)
            response_data = {
                'file_id': file_id,
                'filename': filename,
                'parsed_text': parsed_text,
                'entities': extracted_entities
            }

            # Save to file in pretty format
            json_path = os.path.join(app.config['PARSED_FOLDER'], f"{file_id}.json")
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)

            # Save to MongoDB
            insert_result = collection.insert_one(response_data)
            response_data['_id'] = str(insert_result.inserted_id)

            return jsonify(response_data), 200
        except Exception as e:
            #After parse, file not needed
            os.remove(save_path)
            return jsonify({'error': f'Error parsing file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
