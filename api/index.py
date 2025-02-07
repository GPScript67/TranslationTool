from flask import Flask, render_template, request, jsonify
import random
import csv

app = Flask(__name__)

def load_vocabulary():
    vocabulary = {}
    
    with open('japanese_vocabulary_clean.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row['category']
            if category not in vocabulary:
                vocabulary[category] = []
                
            japanese_text = row['japanese']
            if row['kana']:
                japanese_text = f"{row['japanese']} ({row['kana']})"
                
            vocabulary[category].append({
                'english': row['english'],
                'japanese': japanese_text,
                'kanji': row['japanese'],  # For speech synthesis
            })
    
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
        if categories:
            words = [word for cat in categories 
                    for word in VOCABULARY.get(cat, [])]
        else:
            words = [word for cat, word_list in VOCABULARY.items() 
                    for word in word_list]
        
        return jsonify([{
            'japanese': word['japanese'],
            'english': word['english'],
            'category': cat,
            'kanji': word['kanji']
        } for word in words])
    
    else:
        num_questions = int(data.get('num_questions', 10))
        direction = data.get('direction', 'jp_to_en')
        
        if categories:
            all_words = [(word, cat) for cat in categories 
                        for word in VOCABULARY.get(cat, [])]
        else:
            all_words = [(word, cat) for cat, words in VOCABULARY.items() 
                        for word in words]
        
        num_questions = min(num_questions, len(all_words))
        questions = random.sample(all_words, num_questions)
        
        quiz_questions = []
        for word, category in questions:
            if direction == 'jp_to_en':
                quiz_questions.append({
                    'question': word['japanese'],
                    'answer': word['english'],
                    'category': category,
                    'kanji': word['kanji']
                })
            else:
                quiz_questions.append({
                    'question': word['english'],
                    'answer': word['japanese'],
                    'category': category,
                    'kanji': word['kanji']
                })
        
        return jsonify(quiz_questions)

if __name__ == '__main__':
    app.run(debug=True)
