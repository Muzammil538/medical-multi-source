import os
from flask import Flask, render_template, request, redirect, url_for, flash
import json
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text
from models import db, User, ChatSession, ChatMessage
from model_pipeline import process_query
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ---------------- AUTH ----------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        age_str = request.form.get('age', '')
        gender = request.form.get('gender')
        medical_condition = request.form.get('medical_condition')

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for('register'))

        try:
            age = int(age_str) if age_str.isdigit() else None
        except ValueError:
            age = None

        user = User(
            username=username,
            password=generate_password_hash(password),
            age=age,
            gender=gender,
            medical_condition=medical_condition
        )
        db.session.add(user)
        try:
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("Username already exists or database error occurred.", "danger")

    return render_template("register.html")

# ---------------- HOME ----------------

@app.route('/home')
@login_required
def home():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", sessions=sessions)

@app.route('/new_chat')
@login_required
def new_chat():
    session = ChatSession(user_id=current_user.id)
    db.session.add(session)
    db.session.commit()
    return redirect(url_for('chat', session_id=session.id))

# ---------------- CHAT ----------------

@app.route('/chat/<int:session_id>', methods=['GET','POST'])
@login_required
def chat(session_id):
    session = db.session.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        return redirect(url_for('home'))

    sources = []
    evaluation = {}

    if request.method == 'POST':
        question = request.form['question']

        user_profile = {
            "age": current_user.age,
            "gender": current_user.gender,
            "medical_condition": current_user.medical_condition,
            "fallback_model": current_user.fallback_model
        }

        answer, sources, evaluation = process_query(user_profile, question)

        if not session.title:
            session.title = question[:30] + '...' if len(question) > 30 else question

        db.session.add(ChatMessage(session_id=session_id, role="user", content=question))
        
        # Serialize the AI's response
        ai_data = {
            "text": answer,
            "sources": sources,
            "evaluation": evaluation
        }
        db.session.add(ChatMessage(session_id=session_id, role="assistant", content=json.dumps(ai_data)))
        db.session.commit()
    else:
        answer = None

    messages_raw = ChatMessage.query.filter_by(session_id=session_id).all()
    messages = []
    for msg in messages_raw:
        if msg.role == 'assistant':
            try:
                data = json.loads(msg.content)
            except Exception:
                data = {"text": msg.content, "sources": [], "evaluation": {}}
            
            # Simple parser to split the text into sections based on headers
            # Note: headers generated are ---MEDICAL GUIDANCE---, ---SYMPTOM EXPLANATION---, etc.
            text = data.get("text", "")
            
            import re
            def extract_section(header, full_text):
                pattern = f"---{header}---\n(.*?)(?:\n---|$)"
                match = re.search(pattern, full_text, re.DOTALL)
                return match.group(1).strip() if match else ""
                
            data["medical_guidance"] = extract_section("MEDICAL GUIDANCE", text) or text
            data["symptom_explanation"] = extract_section("SYMPTOM EXPLANATION", text)
            data["precautions"] = extract_section("PRECAUTIONS", text)
            data["clinical_reasoning"] = extract_section("CLINICAL REASONING", text)
            
            # If parsing failed or old format, we just show original text in medical guidance
            if not data["symptom_explanation"]:
                data["medical_guidance"] = text
                
            messages.append({"role": "assistant", "data": data, "id": msg.id})
        else:
            messages.append({"role": "user", "content": msg.content, "id": msg.id})

    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()

    return render_template("chat.html",
                           messages=messages,
                           sessions=sessions,
                           current_session=session_id,
                           user=current_user)

@app.route('/history')
@login_required
def history():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return render_template("history.html", sessions=sessions)

# ---------------- PROFILE ----------------

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.age = request.form['age']
        current_user.gender = request.form['gender']
        current_user.medical_condition = request.form['medical_condition']
        db.session.commit()
    return render_template("profile.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------- SETTINGS ----------------

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        fallback = request.form.get('fallback_model', '').strip()
        current_user.fallback_model = fallback
        db.session.commit()
        flash("Settings updated successfully. Your custom fallback model is saved.", "success")
        return redirect(url_for('settings'))
    return render_template("settings.html")

# ---------------- CHAT MANAGEMENT ----------------

@app.route('/chat/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_chat(session_id):
    session = db.session.get(ChatSession, session_id)
    if session and session.user_id == current_user.id:
        ChatMessage.query.filter_by(session_id=session_id).delete()
        db.session.delete(session)
        db.session.commit()
        flash("Chat session deleted.", "success")
    return redirect(url_for('history'))

@app.route('/chat/<int:session_id>/edit_title', methods=['POST'])
@login_required
def edit_chat_title(session_id):
    session = db.session.get(ChatSession, session_id)
    if session and session.user_id == current_user.id:
        new_title = request.form.get('title', '').strip()
        if new_title:
            session.title = new_title[:200]
            db.session.commit()
    return redirect(url_for('chat', session_id=session_id))

# ---------------- RUN ----------------

def ensure_db_schema():
    inspector = inspect(db.engine)
    if "chat_session" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("chat_session")]
        if "title" not in columns:
            db.session.execute(text("ALTER TABLE chat_session ADD COLUMN title VARCHAR(200)"))
            db.session.commit()
    if "user" in inspector.get_table_names():
        user_cols = [col["name"] for col in inspector.get_columns("user")]
        if "fallback_model" not in user_cols:
            db.session.execute(text("ALTER TABLE user ADD COLUMN fallback_model VARCHAR(100)"))
            db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_db_schema()
    app.run(debug=False, use_reloader=False)