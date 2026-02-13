from flask import Flask, render_template, request, jsonify
import random
import os
import requests

app = Flask(__name__)

# ==========================
# SAT QUESTION BANK
# ==========================

math_questions = [
    {"question": "Solve for x: 3x - 5 = 16", "options": ["7", "5", "3", "9"], "answer": "7"},
    {"question": "If x² = 49, what are the values of x?", "options": ["7", "-7", "7 and -7", "0"], "answer": "7 and -7"},
    {"question": "What is the slope of y = 4x + 2?", "options": ["4", "2", "-4", "0"], "answer": "4"},
    {"question": "Simplify: (x + 2)(x - 2)", "options": ["x² - 4", "x² + 4", "x² - 2", "x² + 2"], "answer": "x² - 4"},
    {"question": "What is 30% of 250?", "options": ["75", "60", "80", "90"], "answer": "75"},
    {"question": "If f(x) = 2x², find f(3).", "options": ["18", "12", "6", "9"], "answer": "18"},
    {"question": "Area of triangle: base 10, height 6?", "options": ["30", "60", "16", "20"], "answer": "30"},
    {"question": "Solve: x/4 = 5", "options": ["20", "9", "25", "10"], "answer": "20"},
    {"question": "Mean of 2, 4, 6, 8?", "options": ["5", "6", "4", "8"], "answer": "5"},
    {"question": "If a = 3, b = 4, find a² + b².", "options": ["25", "7", "12", "49"], "answer": "25"},
]

english_questions = [
    {"question": "Choose the correct sentence.",
     "options": ["She go to school.", "She goes to school.", "She going school.", "She gone school."],
     "answer": "She goes to school."},
    {"question": "Synonym of 'meticulous'?",
     "options": ["Careless", "Precise", "Lazy", "Rough"],
     "answer": "Precise"},
    {"question": "Correct punctuation: 'Its raining heavily'",
     "options": ["It's raining heavily.", "Its raining heavily.", "Its raining heavily!", "Its raining heavily,"],
     "answer": "It's raining heavily."},
    {"question": "Fill blank: He ___ to the store yesterday.",
     "options": ["go", "went", "gone", "going"],
     "answer": "went"},
    {"question": "Antonym of 'expand'?",
     "options": ["Grow", "Increase", "Shrink", "Stretch"],
     "answer": "Shrink"},
]

# ==========================
# ROUTES
# ==========================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/math")
def math():
    return render_template("math.html")

@app.route("/english")
def english():
    return render_template("english.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/quiz-options")
def quiz_options():
    return render_template("quiz-options.html")

@app.route("/start-quiz/<int:duration>", methods=["GET", "POST"])
def start_quiz(duration):

    num_questions = 5 if duration == 30 else 8

    selected_math = random.sample(math_questions, min(num_questions, len(math_questions)))
    selected_english = random.sample(english_questions, min(num_questions, len(english_questions)))

    if request.method == "POST":
        results = []
        total_score = 0

        for i, q in enumerate(selected_math, start=1):
            user_ans = request.form.get(f"math_{i}")
            is_correct = user_ans == q["answer"]
            if is_correct:
                total_score += 1
            results.append({
                "question": q["question"],
                "user_answer": user_ans,
                "correct_answer": q["answer"],
                "is_correct": is_correct
            })

        for i, q in enumerate(selected_english, start=1):
            user_ans = request.form.get(f"eng_{i}")
            is_correct = user_ans == q["answer"]
            if is_correct:
                total_score += 1
            results.append({
                "question": q["question"],
                "user_answer": user_ans,
                "correct_answer": q["answer"],
                "is_correct": is_correct
            })

        return render_template(
            "quiz-results.html",
            results=results,
            total_score=total_score,
            total_questions=len(results)
        )

    return render_template(
        "start-quiz.html",
        math_questions=selected_math,
        english_questions=selected_english,
        duration=duration
    )

# ==========================
# AI CHAT (WORKING VERSION)
# ==========================

HF_TOKEN = os.environ.get("HF_TOKEN")

@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    user_input = request.json.get("message")

    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": user_input,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        data = response.json()

        if isinstance(data, dict) and data.get("error"):
            return jsonify({"reply": f"Error: {data['error']}"})

        reply = data[0]["generated_text"]

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

    return jsonify({"reply": reply})


# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
