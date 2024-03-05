# Flask Quiz App

A simple Flask application for managing a quiz with multiple-choice questions. The application uses SQLite as the database to store questions and their options.

## Installation

1. **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd flask-quiz-app
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Flask application:**

    ```bash
    python app.py
    ```

## API Endpoints

### 1. Add a Question

- **Endpoint:** `/questions`
- **Method:** `POST`
- **Request Format:**

    ```json
    {
        "text": "Question text?",
        "options": [
            {"text": "Option A", "is_correct": true},
            {"text": "Option B", "is_correct": false},
            {"text": "Option C", "is_correct": false},
            {"text": "Option D", "is_correct": false}
        ]
    }
    ```

- **Response Format:**

    ```json
    {
        "message": "Question added successfully"
    }
    ```

### 2. Generate a Quiz

- **Endpoint:** `/quiz`
- **Method:** `GET`
- **Query Parameters:**

    - `num_questions` (optional): Number of questions to include in the quiz (default is 5).

- **Response Format:**

    ```json
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
    ```

### 3. Verify Answer

- **Endpoint:** `/verify`
- **Method:** `POST`
- **Request Format:**

    ```json
    {
        "question_id": 1,
        "selected_option_id": 2
    }
    ```

- **Response Format:**

    ```json
    {
        "is_correct": true,
        "correct_option_id": 2
    }
    ```

## Sample Questions

```json
[
    {
        "text": "What is the capital of France?",
        "options": [
            {"text": "Berlin", "is_correct": false},
            {"text": "Paris", "is_correct": true},
            {"text": "Madrid", "is_correct": false},
            {"text": "Rome", "is_correct": false}
        ]
    },
    ...
]
