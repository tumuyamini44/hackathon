
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

# Gemini API configuration
API_KEY = os.getenv("GEMINI_API_KEY")
print("Gemini API key loaded:", bool(API_KEY))

client = genai.Client(api_key=API_KEY) if API_KEY else None


# Existing website pages
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/schemes")
def schemes():
    return render_template("schemes.html")


@app.route("/eligibility")
def eligibility():
    return render_template("eligibility.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/guidance")
def guidance():
    return render_template("guide.html")

@app.route("/voice")
def voice():
    return render_template("voice.html")

# AI Chatbot API
@app.route("/api/chat", methods=["POST"])
def ai_chat():
    if client is None:
        return jsonify({
            "reply": "Gemini API key is missing. Please check your .env file."
        }), 500

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "Please enter your question."
        }), 400

    if len(user_message) > 2000:
        return jsonify({
            "reply": "Please keep your question within 2000 characters."
        }), 400

   
    prompt = f"""
    You are Sahayak AI, an intelligent Indian Government Schemes
    Assistant.

    Your main goal is to help people discover suitable government 
    schemes based on their needs and personal details.

    FEATURES:

    1. SCHEME INFORMATION
    - Explain government scheme names and their purpose.
    - Describe benefits in simple words.
    - Explain who can apply.

    2. SMART SCHEME RECOMMENDATION
    - Understand the user's needs and situation.
    - Recommend relevant central and Andhra Pradesh state schemes.
    - Consider details such as age, occupation, education,
     income range, location and family situation when relevant.
    - Explain why each suggested scheme may be useful.
    - Do not recommend unrelated schemes.
    - If important details are missing, ask simple questions.

    3. ELIGIBILITY GUIDANCE
    - Explain eligibility requirements clearly.
    - Ask for missing information when necessary.
    - Never guarantee eligibility without checking official rules.

    4. APPLICATION GUIDANCE
    - Explain the general application process.
    - Mention required documents only when verified.
    - Suggest official government portals for applications.

    5. LANGUAGE SUPPORT
    - Understand both Telugu and English.
    - Reply in the language used by the user.
    - Use simple language and clear points. 

    6. ACCURACY
    - Never invent scheme names, benefits, income limits,
    deadlines or eligibility conditions.
    - Clearly mention when information is uncertain
    or may have changed.
    - Recommend checking official government sources
    for the latest information.

    EXAMPLE:
    If a student asks for financial assistance, suggest
    relevant education scholarship schemes and explain
    their purpose and possible eligibility.

    USER QUESTION:
    {user_message}
    """


    try:
        print("CHAT REQUEST RECEIVED", flush=True)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        reply = response.text

        if not reply:
            reply = "Sorry, I couldn't generate an answer. Please try again."

        return jsonify({"reply": reply})

    except Exception as e:
        print("GEMINI ERROR:", repr(e), flush=True)

        return jsonify({
            "reply": "AI Error: " + str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
