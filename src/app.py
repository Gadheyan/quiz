from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



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


with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Created tables...")
    
@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hlo, World!</p>."


@app.route('/questions', methods=['POST'])
def add_question():
    """
    Add a new multiple-choice question to the quiz.

    Request JSON format:
    {
        "text": "Question text?",
        "answer": 1,
        "options": [
            {"text": "Option A", "is_correct": true},
            {"text": "Option B", "is_correct": false},
            {"text": "Option C", "is_correct": false},
            {"text": "Option D", "is_correct": false}
        ]
    }

    Response JSON format:
    {"message": "Question added successfully"}

    The 'answer' field represents the correct option's index (0-indexed) in the 'options' array.
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
    return jsonify({'message': 'Question added successfully'}), 201

@app.route('/quiz', methods=['GET'])
def generate_quiz():
    """
    Generate a quiz with random multiple-choice questions.

    Query parameters:
    - num_questions (optional): Number of questions to include in the quiz (default is 5).

    Response JSON format:
    {
        "quiz": [
            {
                "id": 1,
                "text": "Question text?",
                "options": [
                    {"id": 1, "text": "Option A"},
                    {"id": 2, "text": "Option B"},
                    {"id": 3, "text": "Option C"},
                    {"id": 4, "text": "Option D"}
                ]
            },
            ...
        ]
    }
    """
    questions = Question.query.all()
    if not questions:
        return jsonify({'message': 'No questions available'}), 404

    num_questions = min(int(request.args.get('num_questions', 5)), len(questions))
    selected_questions = random.sample(questions, num_questions)

    quiz = [{'id': question.id, 'text': question.text, 'options': [{'id': option.id, 'text': option.text} for option in question.options]} for question in selected_questions]
    return jsonify({'quiz': quiz})

@app.route('/verify', methods=['POST'])
def verify_answer():
    """
    Verify the selected answer for a question in the quiz.

    Request JSON format:
    {
        "question_id": 1,
        "selected_option_id": 2
    }

    Response JSON format:
    {
        "is_correct": true,
        "correct_option_id": 2
    }

    The 'selected_option_id' represents the index (0-indexed) of the selected option in the 'options' array.
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


