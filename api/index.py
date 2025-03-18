from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pandas as pd
import json
import os  # Add this import

app = Flask(__name__)
CORS(app)

# Get the API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=GEMINI_API_KEY)

dataset_context = 'dd'
try:
    df = pd.read_csv('small_output_2.csv', low_memory=False)
    dataset_context = json.dumps(df.to_dict(orient='records'), indent=2)
    print('CSV data loaded into context')
except Exception as e:
    print(f'Error loading CSV file: {e}')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question') if data else None

    print(question)
    if not question:
        return jsonify({'error': 'Question is required.'}), 400

    if dataset_context == 'dd':
        return jsonify({'error': 'Dataset not loaded yet.'}), 500

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a chatbot answering questions about a Reddit dataset. Here is the dataset context:
        {dataset_context}
        The user asks: "{question}"
        Provide a concise answer in a small paragraph.
        """
        result = model.generate_content(prompt)
        answer = result.text
        return jsonify({'answer': answer})
    except Exception as e:
        print(f'Error with Gemini API: {e}')
        return jsonify({'error': 'Failed to fetch answer.'}), 500