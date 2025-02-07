# api/index.py
from flask import Flask, render_template, request, jsonify
import random
import requests
from urllib.parse import quote

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

@app.route('/')
def home():
    categories = list(VOCABULARY.keys())
    return render_template('index.html', categories=categories)

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
                'category': category,
                'audio_url': f'https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q={quote(jp)}'
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
