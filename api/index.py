from flask import Flask, render_template, request, jsonify
import random
import csv
import os

app = Flask(__name__)

def load_vocabulary():
    vocabulary = {}
    file_path = os.path.join('api', 'japanese_vocabulary_final.csv')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
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
                    'kanji': row['japanese'],
                })
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        vocabulary = {"Default": [{"english": "test", "japanese": "テスト", "kanji": "テスト"}]}
    except Exception as e:
        print(f"Error loading vocabulary: {str(e)}")
        vocabulary = {"Default": [{"english": "test", "japanese": "テスト", "kanji": "テスト"}]}
    
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
            words = [(word, cat) for cat in categories 
                    for word in VOCABULARY.get(cat, [])]
        else:
            words = [(word, cat) for cat, word_list in VOCABULARY.items() 
                    for word in word_list]
        
        return jsonify([{
            'japanese': word[0]['japanese'],
            'english': word[0]['english'],
            'category': word[1],
            'kanji': word[0]['kanji']
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
