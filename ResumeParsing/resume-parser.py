from fileinput import filename
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from tika import parser
import uuid
import json

# Initialize the Flask application
app = Flask(__name__)

#config
UPLOAD_FOLDER = './uploads'
PARSED_FOLDER = './parsed_output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PARSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PARSED_FOLDER'] = PARSED_FOLDER

#allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

def parse_with_tika(file_path):
    parsed = parser.from_file(file_path)
    return parsed.get('content', '').strip()

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

            #After parse, file not needed
            os.remove(save_path)
            response_data = {
                'file_id': file_id,
                'filename': filename,
                'parsed_text': parsed_text
            }

            # Save to file in pretty format
            json_path = os.path.join(app.config['PARSED_FOLDER'], f"{file_id}.json")
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)

            return jsonify(response_data), 200
        except Exception as e:
            #After parse, file not needed
            os.remove(save_path)
            return jsonify({'error': f'Error parsing file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
