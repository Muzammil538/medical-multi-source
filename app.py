import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text
from models import db, User, ChatSession, ChatMessage
from model_pipeline import process_query
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
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
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password']),
            age=request.form['age'],
            gender=request.form['gender'],
            medical_condition=request.form['medical_condition']
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
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

    sources = []
    evaluation = {}

    if request.method == 'POST':
        question = request.form['question']

        user_profile = {
            "age": current_user.age,
            "gender": current_user.gender,
            "medical_condition": current_user.medical_condition
        }

        answer, sources, evaluation = process_query(user_profile, question)

        if not session.title:
            session.title = question[:40]

        db.session.add(ChatMessage(session_id=session_id, role="user", content=question))
        db.session.add(ChatMessage(session_id=session_id, role="assistant", content=answer))
        db.session.commit()
    else:
        answer = None

    messages = ChatMessage.query.filter_by(session_id=session_id).all()
    sessions = ChatSession.query.filter_by(user_id=current_user.id).all()

    return render_template("chat.html",
                           messages=messages,
                           sessions=sessions,
                           current_session=session_id,
                           sources=sources,
                           evaluation=evaluation,
                           answer=answer,
                           user=current_user)

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

# ---------------- RUN ----------------

def ensure_db_schema():
    inspector = inspect(db.engine)
    if "chat_session" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("chat_session")]
        if "title" not in columns:
            db.session.execute(text("ALTER TABLE chat_session ADD COLUMN title VARCHAR(200)"))
            db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_db_schema()
    app.run(debug=False, use_reloader=False)