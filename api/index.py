# api/index.py
from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import random
import os
import tempfile

app = Flask(__name__)

def load_vocabulary():
    vocabulary = {}
    current_category = ""
    
    with open('api/japanese_vocab.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                current_category = line.replace('# Category: ', '').replace('# ', '')
                vocabulary[current_category] = []
            elif ',' in line:
                japanese, english = line.split(',')
                vocabulary[current_category].append((japanese, english))
    
    return vocabulary

VOCABULARY = load_vocabulary()
TEMP_DIR = tempfile.gettempdir()

@app.route('/')
def home():
    categories = list(VOCABULARY.keys())
    return render_template('index.html', categories=categories)

@app.route('/get_audio/<word>')
def get_audio(word):
    # Create a unique filename for this word
    filename = f"speech_{hash(word)}.mp3"
    filepath = os.path.join(TEMP_DIR, filename)
    
    # Generate audio file if it doesn't exist
    if not os.path.exists(filepath):
        tts = gTTS(text=word, lang='ja')
        tts.save(filepath)
    
    return send_file(filepath, mimetype='audio/mp3')

@app.route('/get_quiz', methods=['POST'])
def get_quiz():
    data = request.json
    categories = data.get('categories', [])
    num_questions = int(data.get('num_questions', 10))
    direction = data.get('direction', 'jp_to_en')
    
    if categories:
        all_words = [(jp, en, cat) for cat in categories 
                     for jp, en in VOCABULARY.get(cat, [])]
    else:
        all_words = [(jp, en, cat) for cat, words in VOCABULARY.items() 
                     for jp, en in words]
    
    num_questions = min(num_questions, len(all_words))
    questions = random.sample(all_words, num_questions)
    
    quiz_questions = []
    for jp, en, category in questions:
        if direction == 'jp_to_en':
            quiz_questions.append({
                'question': jp,
                'answer': en,
                'category': category
            })
        else:
            quiz_questions.append({
                'question': en,
                'answer': jp,
                'category': category
            })
    
    return jsonify(quiz_questions)

if __name__ == '__main__':
    app.run(debug=True)
