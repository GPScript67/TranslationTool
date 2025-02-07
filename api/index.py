from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

def load_vocabulary():
    vocabulary = {}
    current_category = ""
    
    with open('api/japanese_vocabulary_updated.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith('Category:'):
                current_category = line.replace('Category:', '').strip()
                i += 4  # Skip the header and separator line
                vocabulary[current_category] = []
            else:
                parts = [p.strip() for p in line.split()]
                if len(parts) >= 4:
                    english = parts[0]
                    kanji = parts[2] if parts[2] != "-" else ""
                    kana = parts[3] if parts[3] != "-" else ""
                    
                    # Format Japanese text as "Kanji (Kana)"
                    japanese_text = kanji
                    if kana:
                        japanese_text = f"{kanji} ({kana})"
                    
                    vocabulary[current_category].append({
                        'english': english,
                        'japanese': japanese_text,
                        'kanji': kanji,  # Store separately for speech
                    })
            i += 1
    
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
