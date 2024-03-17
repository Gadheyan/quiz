from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import random
from datetime import datetime
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://redis:6379/0'
app.config['CACHE_KEY_PREFIX'] = 'quiz_cache'

TIMEOUT_IN_SECONDS = 10
CACHE_INDICATOR_HEADER="x-now-cache"
db = SQLAlchemy(app)
cache = Cache(app)


# Models For The Quiz App
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    options = db.relationship('Option', backref='question', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


def add_cache_headers(f):
    wraps(f)
    def decorated_function(*args, **kwargs):
        cache_key = f"view/{request.path}"
        cache_status = 'Hit' if cache.cache.has(cache_key) else 'Miss'
        print(dir(cache.memoize))
        cached_function = cache.cached(timeout=TIMEOUT_IN_SECONDS)(f)
        response = cached_function(*args, **kwargs)
        response.headers[CACHE_INDICATOR_HEADER] = cache_status
        return response
    return decorated_function


@app.route("/home", methods=['GET'])
@add_cache_headers
def hello_world():
    response = {'message': "Hello World"}
    return jsonify(response)


@app.route('/questions', methods=['POST'])
def add_question():
    """
    Add a new multiple-choice question to the quiz.
    """
    questions = request.json

    for question in questions:
        new_question = Question(text=question['text'])

        # Add options
        options_data = question.get('options', [])
        for option_data in options_data:
            new_option = Option(text=option_data['text'], is_correct=option_data['is_correct'], question=new_question)
            db.session.add(new_option)

        db.session.add(new_question)
        db.session.commit()
    return jsonify({'message': 'Question(s) added successfully'}), 201

@app.route('/quiz', methods=['GET'], endpoint='generate_quiz')
@add_cache_headers
def generate_quiz():
    """
    Generate a quiz with random multiple-choice questions.
    """
    questions = Question.query.all()
    if not questions:
        return jsonify({'message': 'No questions available'}), 404

    num_questions = min(int(request.args.get('num_questions', 5)), len(questions))
    selected_questions = random.sample(questions, num_questions)

    quiz = [{'id': question.id, 'text': question.text, 'options': [{'id': option.id, 'text': option.text} for option in question.options]} for question in selected_questions]
    response = {'quiz': quiz}
    return jsonify(response)

@app.route('/verify', methods=['POST'])
def verify_answer():
    """
    Verify the selected answer for a question in the quiz.
    """
    data = request.json
    question_id = data['question_id']
    selected_option_id = data['selected_option_id']

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'message': 'Question not found'}), 404

    correct_option_id = next((option.id for option in question.options if option.is_correct), None)
    
    if selected_option_id == correct_option_id:
        return jsonify({'is_correct': True, 'correct_option_id': correct_option_id})
    else:
        return jsonify({'is_correct': False, 'correct_option_id': correct_option_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
