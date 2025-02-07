# api/index.py
from flask import Flask, render_template, request, jsonify
import random

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

@app.route('/get_words', methods=['POST'])
def get_words():
    data = request.json
    categories = data.get('categories', [])
    mode = data.get('mode', 'quiz')
    
    if mode == 'flashcards':
        # For flashcards, we want all words from selected categories
        if categories:
            words = [(jp, en, cat) for cat in categories 
                    for jp, en in VOCABULARY.get(cat, [])]
        else:
            words = [(jp, en, cat) for cat, words in VOCABULARY.items() 
                    for jp, en in words]
        
        return jsonify([{
            'japanese': jp,
            'english': en,
            'category': cat
        } for jp, en, cat in words])
    
    else:
        # Original quiz logic
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
