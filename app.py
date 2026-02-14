from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import ChatMessage, ChatSession, db, User
from model_pipeline import process_query



app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])
        
        user = User(
            username=request.form['username'],
            password=hashed_password,
            age=request.form['age'],
            gender=request.form['gender'],
            medical_condition=request.form['medical_condition']
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('home'))

    
    return render_template('login.html')


@app.route('/chat/<int:session_id>', methods=['GET', 'POST'])
@login_required
def chat(session_id):

    session = ChatSession.query.get_or_404(session_id)

    if request.method == 'POST':
        question = request.form['question']

        user_profile = {
            "age": current_user.age,
            "gender": current_user.gender,
            "medical_condition": current_user.medical_condition
        }

        answer, sources = process_query(user_profile, question)

        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=question
        )

        # Save AI response
        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=answer
        )

        db.session.add(user_msg)
        db.session.add(ai_msg)
        db.session.commit()

    messages = ChatMessage.query.filter_by(session_id=session_id).all()
    sessions = ChatSession.query.filter_by(user_id=current_user.id).all()

    return render_template("chat.html",
                           messages=messages,
                           sessions=sessions,
                           current_session=session_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
  
  
@app.route('/new_chat')
@login_required
def new_chat():
    session = ChatSession(user_id=current_user.id)
    db.session.add(session)
    db.session.commit()
    return redirect(url_for('chat', session_id=session.id))



@app.route('/history')
@login_required
def history():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).all()
    return render_template("history.html", sessions=sessions)


@app.route('/home')
@login_required
def home():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", sessions=sessions)






if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, use_reloader=False)


