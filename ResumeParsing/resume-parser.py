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

def extract_entities(text):
    # Simple regex-based extraction (can be replaced with NER models later)
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    
    # Extract phone number (international or local format)
    raw_phones = re.findall(r'(\+\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', text)
    phone = ''.join(raw_phones[0]) if raw_phones else None

    # Combine skills from both LLM and Ontology
    llm_extractor = LLMSkillExtractor(api_key= passPhrase)
    ontology_extractor = OntologySkillExtractor()
    
    # Extracted using both methods
    skills_llm = llm_extractor.extract_skills(text)
    skills_ontology = ontology_extractor.extract_skills(text)

    return {
        'email': email[0] if email else None,
        'phone': phone,
        'skills_llm': skills_llm,
        'skills_ontology': skills_ontology
    }

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
            parsed_text = parse_with_tika(save_path)
            extracted_entities = extract_entities(parsed_text)

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
