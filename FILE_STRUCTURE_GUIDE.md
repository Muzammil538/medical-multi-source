# 📂 MedInsight - Complete File Structure Guide
## Every File Explained for Beginners

---

## 📝 Table of Contents

1. [Core Application Files](#core-application-files)
   - app.py
   - models.py
   - model_pipeline.py

2. [Data Files](#data-files)
   - Healthcare Dataset
   - Medical Classification Dataset
   - Medical QA Dataset

3. [Template Files (UI)](#template-files-ui)
   - HTML Pages

4. [Configuration Files](#configuration-files)
   - .env, requirements.txt, etc.

5. [Database & Instance](#database--instance)

---

# 🏗️ CORE APPLICATION FILES

---

## 1️⃣ **app.py** - Main Flask Server

**What it does:** This is the "heart" of MedInsight. It handles all web requests and coordinates everything.

**Location:** `/Users/themam/Documents/GitHub/medical-multi-source/app.py`

### Key Sections:

#### **Section A: Imports & Setup**
```python
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ChatSession, ChatMessage
from model_pipeline import process_query
```

**What each import does:**
- `Flask` → Creates web server
- `LoginManager` → Manages user login/logout
- `generate_password_hash` → Encrypts passwords securely
- `models` → Database tables (User, ChatSession, ChatMessage)
- `process_query` → Calls the AI engine (retrieval + LLM)

#### **Section B: App Configuration**
```python
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)
```

**Explanation:**
- `SECRET_KEY` → Used to encrypt sessions (from `.env` file)
- `SQLALCHEMY_DATABASE_URI` → Path to database
- `db.init_app()` → Connects database to Flask app

### **Route: LOGIN PAGE** 🔐
```python
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
```

**How it works:**
1. User goes to `/` (home URL)
2. If GET request → Show login page (`login.html`)
3. If POST request (form submitted):
   - Get username from form
   - Search database for user
   - Check if password matches (using hashing)
   - If correct → Login user and go to home
   - If wrong → Show error message

**Important Code:**
- `User.query.filter_by(username=...)` → Search database
- `check_password_hash()` → Verify password securely
- `login_user(user)` → Create login session
- `flash()` → Show error message to user

### **Route: REGISTER PAGE** 📝
```python
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        age_str = request.form.get('age', '')
        gender = request.form.get('gender')
        medical_condition = request.form.get('medical_condition')
        
        # Validate inputs
        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for('register'))
        
        # Convert age to integer
        try:
            age = int(age_str) if age_str.isdigit() else None
        except ValueError:
            age = None
        
        # Create new user object
        user = User(
            username=username,
            password=generate_password_hash(password),
            age=age,
            gender=gender,
            medical_condition=medical_condition
        )
        
        # Save to database
        db.session.add(user)
        try:
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("Username already exists or database error occurred.", "danger")
    
    return render_template("register.html")
```

**How it works:**
1. Get form data from registration page
2. Validate that username and password are provided
3. Convert age to integer (if valid)
4. Create new User object with hashed password
5. Try to save to database
6. If success → Go to login page
7. If fail (username exists) → Show error

**Important Code:**
- `request.form.get()` → Get data from HTML form
- `generate_password_hash()` → Encrypt password
- `db.session.add()` → Add to database
- `db.session.commit()` → Save changes
- `db.session.rollback()` → Undo if error

### **Route: HOME PAGE** 🏠
```python
@app.route('/home')
@login_required
def home():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", sessions=sessions)
```

**How it works:**
1. `@login_required` → Only logged-in users can access
2. Get all chat sessions for current user
3. Render home page with their sessions

### **Route: NEW CHAT** ➕
```python
@app.route('/new_chat')
@login_required
def new_chat():
    session = ChatSession(user_id=current_user.id)
    db.session.add(session)
    db.session.commit()
    return redirect(url_for('chat', session_id=session.id))
```

**How it works:**
1. Create new ChatSession
2. Link to current user
3. Save to database
4. Redirect to chat page with new session

### **Route: CHAT PAGE** 💬 (MOST IMPORTANT!)
```python
@app.route('/chat/<int:session_id>', methods=['GET','POST'])
@login_required
def chat(session_id):
    # Check if session belongs to current user
    session = db.session.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        return redirect(url_for('home'))
    
    sources = []
    evaluation = {}
    
    if request.method == 'POST':
        # Step 1: Get question from user
        question = request.form['question']
        
        # Step 2: Build user profile
        user_profile = {
            "age": current_user.age,
            "gender": current_user.gender,
            "medical_condition": current_user.medical_condition,
            "fallback_model": current_user.fallback_model
        }
        
        # Step 3: Call AI engine to process query
        answer, sources, evaluation = process_query(user_profile, question)
        
        # Step 4: Set session title from first question
        if not session.title:
            session.title = question[:30] + '...' if len(question) > 30 else question
        
        # Step 5: Save user message
        db.session.add(ChatMessage(session_id=session_id, role="user", content=question))
        
        # Step 6: Save AI response with metadata
        ai_data = {
            "text": answer,
            "sources": sources,
            "evaluation": evaluation
        }
        db.session.add(ChatMessage(
            session_id=session_id, 
            role="assistant", 
            content=json.dumps(ai_data)
        ))
        db.session.commit()
    
    # Step 7: Load all messages for display
    messages_raw = ChatMessage.query.filter_by(session_id=session_id).all()
    messages = []
    
    for msg in messages_raw:
        if msg.role == 'assistant':
            # Parse AI response
            try:
                data = json.loads(msg.content)
            except Exception:
                data = {"text": msg.content, "sources": [], "evaluation": {}}
            
            # Extract sections from formatted response
            import re
            text = data.get("text", "")
            
            def extract_section(header, full_text):
                pattern = f"---{header}---\n(.*?)(?:\n---|$)"
                match = re.search(pattern, full_text, re.DOTALL)
                return match.group(1).strip() if match else ""
            
            data["medical_guidance"] = extract_section("MEDICAL GUIDANCE", text) or text
            data["symptom_explanation"] = extract_section("SYMPTOM EXPLANATION", text)
            data["precautions"] = extract_section("PRECAUTIONS", text)
            data["clinical_reasoning"] = extract_section("CLINICAL REASONING", text)
            
            messages.append({"role": "assistant", "data": data, "id": msg.id})
        else:
            messages.append({"role": "user", "content": msg.content, "id": msg.id})
    
    # Step 8: Get all sessions for sidebar
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    
    # Step 9: Render chat template
    return render_template("chat.html",
                           messages=messages,
                           sessions=sessions,
                           current_session=session_id,
                           user=current_user)
```

**This is the CORE of the application! Let me break it down:**

**Request Processing (POST):**
```
1. User submits question
   ↓
2. Get question: "What is diabetes?"
   ↓
3. Build user profile from database
   ↓
4. Call process_query() from model_pipeline.py
   → This does the RAG magic!
   ↓
5. Get answer + sources + evaluation
   ↓
6. Save both messages to database
   ↓
7. Submit complete
```

**Response Display (GET):**
```
1. Load all messages from database
   ↓
2. For each assistant message:
   - Parse the JSON
   - Extract sections (MEDICAL GUIDANCE, SYMPTOMS, etc.)
   ↓
3. Load sidebar with all sessions
   ↓
4. Render HTML with formatted messages
```

### **Route: HISTORY PAGE** 📚
```python
@app.route('/history')
@login_required
def history():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return render_template("history.html", sessions=sessions)
```

**Shows all past consultations sorted by date.**

### **Route: PROFILE PAGE** 👤
```python
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.age = request.form['age']
        current_user.gender = request.form['gender']
        current_user.medical_condition = request.form['medical_condition']
        db.session.commit()
    return render_template("profile.html")
```

**Allows users to update their medical information.**

### **Route: SETTINGS PAGE** ⚙️
```python
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
```

**Users can set a fallback AI model if primary fails.**

### **Route: LOGOUT** 🚪
```python
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
```

**Ends user session and redirects to login.**

### **Helper Functions**

```python
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
```

**Checks if database columns exist, adds them if missing.**

### **Main Entry Point**
```python
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_db_schema()
    app.run(debug=False, use_reloader=False)
```

**When you run `python app.py`:**
1. Creates database tables if they don't exist
2. Adds any missing columns
3. Starts Flask server

---

## 2️⃣ **models.py** - Database Structure

**What it does:** Defines how data is stored in the database.

**Location:** `/Users/themam/Documents/GitHub/medical-multi-source/models.py`

### Complete Code:
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    medical_condition = db.Column(db.String(200))
    fallback_model = db.Column(db.String(100), default='')
```

**User Table Explanation:**

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer | Unique user identifier (auto-incremented) |
| `username` | String | Login name (must be unique) |
| `password` | String | Hashed password (encrypted) |
| `age` | Integer | User's age |
| `gender` | String | User's gender |
| `medical_condition` | String | User's known medical condition |
| `fallback_model` | String | Fallback LLM if primary fails |

**Example row:**
```
id: 1
username: "john_doe"
password: "$2b$12$kdf...encrypted..." 
age: 45
gender: "male"
medical_condition: "hypertension"
fallback_model: "openai/gpt-3.5-turbo"
```

### ChatSession Table:
```python
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Stores each conversation:**

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer | Unique session ID |
| `user_id` | Integer | Which user owns this session |
| `title` | String | Session title (e.g., "Diabetes symptoms") |
| `created_at` | DateTime | When conversation started |

**Example row:**
```
id: 5
user_id: 1 (belonging to john_doe)
title: "What is diabetes?"
created_at: 2026-04-01 10:30:45
```

### ChatMessage Table:
```python
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer)
    role = db.Column(db.String(20))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

**Stores individual messages:**

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer | Unique message ID |
| `session_id` | Integer | Which session this belongs to |
| `role` | String | "user" or "assistant" |
| `content` | Text | The actual message |
| `timestamp` | DateTime | When message was created |

**Example rows:**
```
Row 1:
id: 101
session_id: 5
role: "user"
content: "What is diabetes?"
timestamp: 2026-04-01 10:31:00

Row 2:
id: 102
session_id: 5
role: "assistant"
content: '{"text": "---MEDICAL GUIDANCE---\nDiabetes is...", "sources": [...], "evaluation": {...}}'
timestamp: 2026-04-01 10:31:05
```

**Relationships:**
```
User (id: 1)
  ├─→ ChatSession (user_id: 1, id: 5)
       ├─→ ChatMessage (role: user, session_id: 5)
       └─→ ChatMessage (role: assistant, session_id: 5)
  └─→ ChatSession (user_id: 1, id: 6)
       ├─→ ChatMessage (role: user, session_id: 6)
       └─→ ChatMessage (role: assistant, session_id: 6)
```

---

## 3️⃣ **model_pipeline.py** - AI Engine (Heart of Intelligence)

**What it does:** This is where the magic happens! It handles data retrieval and LLM calls.

**Location:** `/Users/themam/Documents/GitHub/medical-multi-source/model_pipeline.py`

### Section 1: Imports & Constants
```python
import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import requests

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "arcee-ai/trinity-large-preview:free"

_embedding_model = None
```

**What each import does:**
- `pandas` → Load CSV files
- `faiss` → Fast vector search
- `SentenceTransformer` → Convert text to embeddings
- `requests` → Call LLM API
- `load_dotenv()` → Load API keys from `.env`

**Constants:**
- `OPENROUTER_API_KEY` → Secret key for OpenRouter API
- `MODEL_NAME` → Which LLM to use

### Section 2: Embedding Model (Lazy Loading)
```python
def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model
```

**What it does:**
- Loads embedding model only once (first use)
- "all-MiniLM-L6-v2" converts text → 384-dimension vectors
- Lazy loading saves memory

**Why important:**
- Embeddings are how we measure similarity
- We use this to find relevant medical data

### Section 3: Global Cache Variables
```python
_clinical_df = None
_research_df = None
_qa_df = None
_clinical_docs = None
_research_docs = None
_qa_docs = None
_clinical_index = None
_research_index = None
_qa_index = None
```

**These cache data so we don't reload CSVs every time**
- `_clinical_df` → Loaded clinical data
- `_clinical_index` → FAISS index for clinical data
- etc.

### Section 4: Load Data Function
```python
def load_data():
    clinical = pd.read_csv("healthcare_dataset.csv", nrows=500)
    research = pd.read_csv("medical_text_classification_fake_dataset.csv", nrows=500)
    qa = pd.read_csv("train.csv", nrows=500)
    return clinical, research, qa
```

**What it does:**
1. Load 3 CSV files
2. Take first 500 rows from each (for performance)
3. Return as pandas DataFrames

**Example:**
```
clinical CSV:
┌──────┬─────┬────────┬──────┬──────────────┐
│ Name │ Age │ Gender │ Blood Type │ Condition │
├──────┼─────┼────────┼──────┼──────────────┤
│ John │ 45  │ M      │ O+   │ Hypertension │
│ Jane │ 38  │ F      │ A+   │ Diabetes     │
└──────┴─────┴────────┴──────┴──────────────┘
```

### Section 5: Text Conversion Functions
```python
def clinical_text(row):
    return (
        f"Clinical: Name {row.get('Name', 'N/A')}, Age {row.get('Age', 'N/A')}, "
        f"Gender {row.get('Gender', 'N/A')}, Blood Type {row.get('Blood Type', 'N/A')}, "
        f"Medical Condition {row.get('Medical Condition', 'N/A')}, "
        f"Test Results {row.get('Test Results', 'N/A')}"
    )

def research_text(row):
    return f"Research: {row['text']}"

def qa_text(row):
    options = [row['opa'], row['opb'], row['opc'], row['opd']]
    return f"Q: {row['question']} A: {options[int(row['cop'])]}"
```

**What they do:**
Convert each row to searchable text format

**Example outputs:**
```
clinical_text() → "Clinical: Name John, Age 45, Gender M, Blood Type O+, Medical Condition Hypertension, Test Results High BP"

research_text() → "Research: Hypertension is persistent elevated blood pressure caused by genetics and lifestyle..."

qa_text() → "Q: What causes diabetes? A: Insulin resistance and pancreatic dysfunction"
```

### Section 6: Initialization Function
```python
def initialize():
    global _clinical_df, _research_df, _qa_df
    global _clinical_docs, _research_docs, _qa_docs
    global _clinical_index, _research_index, _qa_index

    if _clinical_index is not None:
        return  # Already initialized

    # Load data
    _clinical_df, _research_df, _qa_df = load_data()
    
    # Convert to text
    _clinical_docs = _clinical_df.apply(clinical_text, axis=1).tolist()
    _research_docs = _research_df.apply(research_text, axis=1).tolist()
    _qa_docs = _qa_df.apply(qa_text, axis=1).tolist()

    # Build FAISS indexes
    _clinical_index = build_index(_clinical_docs)
    _research_index = build_index(_research_docs)
    _qa_index = build_index(_qa_docs)
```

**What it does:**
1. Check if already initialized (skip if yes)
2. Load CSVs
3. Convert rows to text
4. Build FAISS indexes

**Happens automatically** on first query

### Section 7: Build FAISS Index
```python
def build_index(docs):
    # Convert all documents to embeddings
    emb = get_embedding_model().encode(docs, show_progress_bar=False, normalize_embeddings=True)
    
    # Create FAISS index
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(np.array(emb))
    return index
```

**What it does:**
1. Convert all documents to embeddings (e.g., 500 docs → 500 vectors)
2. Create FAISS index for fast searching
3. Add all embeddings to index

**Result:** Ultra-fast similarity search! ⚡

### Section 8: Retrieve Function (MAIN RETRIEVAL LOGIC) 🔍
```python
def retrieve(query, top_k=1):
    initialize()  # Load data if not already loaded
    
    # Convert query to embedding
    q_emb = get_embedding_model().encode([query], normalize_embeddings=True)

    def search(index, docs):
        # Find top_k similar documents
        D, I = index.search(q_emb, top_k)
        results = []
        
        for sim, idx in zip(D[0], I[0]):
            # sim is cosine similarity (0-1)
            raw_sim = float(sim)
            
            # Convert to human-readable percentage
            # Baseline 65% + (similarity * 35%)
            score = 0.65 + (raw_sim * 0.35)
            score = max(0.0, min(1.0, score))
            
            results.append({
                "text": docs[idx],
                "score": round(score, 3)
            })
        return results

    # Search all three indexes
    return {
        "clinical": search(_clinical_index, _clinical_docs),
        "research": search(_research_index, _research_docs),
        "qa": search(_qa_index, _qa_docs)
    }
```

**How it works step-by-step:**

```
1. User asks: "What is diabetes?"
   ↓
2. Convert to embedding: [0.234, -0.891, ..., 0.123]
   ↓
3. Search clinical index:
   - Compare with all 500 clinical embeddings
   - Find most similar one
   - Get similarity score (0.82)
   ↓
4. Search research index:
   - Find most similar research doc
   - Get similarity score (0.75)
   ↓
5. Search QA index:
   - Find most similar QA
   - Get similarity score (0.88)
   ↓
6. Convert scores to percentages:
   - Clinical: 0.65 + (0.82 × 0.35) = 82%
   - Research: 0.65 + (0.75 × 0.35) = 75%
   - QA: 0.65 + (0.88 × 0.35) = 88%
   ↓
7. Return all results with scores
```

### Section 9: LLM Call Function (WHERE AI GENERATES RESPONSE) 🤖
```python
def call_llm(prompt, fallback_model=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    def _execute(model):
        # Prepare API request
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Provide structured medical guidance."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3  # Lower = more focused
        }
        try:
            # Call OpenRouter API
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                              headers=headers, json=data)
            return res.json()
        except Exception as e:
            return {"error": {"message": str(e)}}

    # Try primary model first
    result = _execute(MODEL_NAME)
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    
    # If primary fails and fallback exists, try fallback
    if fallback_model:
        result_fallback = _execute(fallback_model)
        if "choices" in result_fallback:
            return result_fallback["choices"][0]["message"]["content"]
    
    # If both fail, return error message
    return "Error: LLM API failed"
```

**How it works:**

```
1. Prepare headers with API key authorization
2. Try primary model (arcee-ai/trinity-large-preview)
   - Send prompt with system message and user prompt
   - Set temperature=0.3 (focused responses)
   ↓
3. If success → Extract and return AI response
4. If failure and fallback exists → Try fallback model
5. If all fail → Return error message with details
```

### Section 10: Main Process Query Function (ORCHESTRATES EVERYTHING) 🎯
```python
def process_query(user_profile, question):
    fallback = user_profile.get('fallback_model', '')
    
    # Step 1: Retrieve relevant documents
    retrieved = retrieve(query=question, top_k=1)
    
    # Step 2: Build context from retrieved documents
    context = ""
    sources = []
    for source_type, items in retrieved.items():  # "clinical", "research", "qa"
        for item in items:
            context += item["text"] + "\n"
            sources.append({
                "type": source_type,
                "score": item["score"],
                "text": item["text"]
            })
    
    # Step 3: Build prompt with user profile + context + question
    prompt = f"""
Patient:
Age: {user_profile.get('age')}
Gender: {user_profile.get('gender')}
Condition: {user_profile.get('medical_condition')}

Context:
{context}

Question:
{question}

Respond strictly in this exact format with these exact headers:

---MEDICAL GUIDANCE---
(Put your guidance here)

---SYMPTOM EXPLANATION---
(Put symptom explanation here)

---PRECAUTIONS---
(Put precautions here)

---CLINICAL REASONING---
(Explain briefly how the answer is derived from context)
"""
    
    # Step 4: Call LLM to generate response
    answer = call_llm(prompt, fallback)
    
    # Step 5: Calculate evaluation metrics
    if sources:
        avg_score = round(sum([s["score"] for s in sources]) / len(sources), 2)
    else:
        avg_score = 0.0
    
    evaluation = {
        "confidence": avg_score,
        "num_sources": len(sources)
    }
    
    # Step 6: Return everything
    return answer, sources, evaluation
```

**Complete Flow:**

```
INPUT: user_profile, question
            ↓
Step 1: Search medical data
        retrieve(question)
        → clinical + research + QA matches
            ↓
Step 2: Build context string
        "Patient: 45M with Diabetes
         Context: [retrieved medical data]
         Question: [user question]"
            ↓
Step 3: Build full prompt for LLM
        Include patient info, context, question
        Specify exact output format
            ↓
Step 4: Call OpenRouter API
        Send prompt to LLM (arcee-ai/trinity or fallback)
        LLM generates response
            ↓
Step 5: Calculate metrics
        Average confidence from sources
        Count number of sources
            ↓
OUTPUT: (answer, sources, evaluation)
```

**Example execution:**

```
Input:
- user_profile = {"age": 45, "gender": "M", "medical_condition": "Diabetes"}
- question = "What should I eat?"

Retrieval:
- Clinical match: "Patient 45M with Diabetes, symptoms..."
- Research match: "Diabetes diet should be low sugar..."
- QA match: "Q: Diabetes diet? A: Low carb, high fiber..."

Context:
"Patient: 45M with Diabetes
 Context: [3 relevant documents]
 Question: What should I eat?"

LLM Response:
"---MEDICAL GUIDANCE---
For diabetes, maintain balanced nutrition...

---SYMPTOM EXPLANATION---
Poor diet worsens blood sugar...

---PRECAUTIONS---
- Avoid sugary foods
- Choose high-fiber items
- Monitor portions

---CLINICAL REASONING---
Based on dietary guidelines for diabetes management."

Evaluation:
- confidence: 81.7%
- sources: 3
```

---

# 📊 DATA FILES

---

## **healthcare_dataset.csv** - Clinical Patient Data

**What it contains:** Real-world clinical data about patients

**Key columns:**
```
Name          - Patient's name
Age           - Patient's age
Gender        - M/F/Other
Blood Type    - Blood type (A+, B-, etc.)
Medical Condition - Disease/condition (Hypertension, Diabetes, etc.)
Admission Type - Emergency, Urgent, Routine
Discharge Type - Discharged, Died, etc.)
Test Results  - Lab results (Normal, Abnormal)
Hospital (Stays) - Duration of hospital stay
```

**Example rows:**
```
Olivia,30,F,O+,Asthma,Emergency,Discharged,Normal,3
Noah,45,M,AB+,Hypertension,Routine,Discharged,Abnormal,2
Ava,28,F,B-,Arthritis,Urgent,Discharged,Normal,1
```

**How it's used:**
- Converted to text by `clinical_text()` function
- Indexed in FAISS for searching
- Provides patient context to LLM

---

## **medical_text_classification_fake_dataset.csv** - Research Data

**What it contains:** Medical research and clinical text

**Key columns:**
```
text - Medical information/research text
(other classification columns for training)
```

**Example rows:**
```
"Hypertension is persistent elevated blood pressure above 140/90 mmHg.
It's a major risk factor for heart disease and stroke affected by genetics
and lifestyle factors."

"Diabetes mellitus is a chronic disorder of carbohydrate metabolism
characterized by insufficient insulin production or insulin resistance."
```

**How it's used:**
- Provides evidence-based medical information
- Indexed for similarity search
- Supplies context for LLM responses

---

## **train.csv** - Medical Q&A Data

**What it contains:** Medical questions with multiple choice answers

**Key columns:**
```
question - Medical question
opa      - Option A
opb      - Option B
opc      - Option C
opd      - Option D
cop      - Correct option (0=A, 1=B, 2=C, 3=D)
```

**Example rows:**
```
id,question,opa,opb,opc,opd,cop
1,"What causes diabetes?","Poor diet","Genetic predisposition","Sedentary lifestyle","All of the above",3
2,"What is hypertension?","Low blood pressure","High cholesterol","High blood pressure","Heart disease",2
```

**How it's used:**
- Converted to text by `qa_text()` function
- Provides validated medical Q&A
- Helps verify answer accuracy

---

## **synthetic_clinical_dataset.csv** - Additional Clinical Data

**Purpose:** Extra clinical examples for better search results

---

## **validation.csv** - Validation Data

**Purpose:** Used for evaluation/testing (if implemented)

---

# 🎨 TEMPLATE FILES (UI/FRONTEND)

---

All templates are in `/templates/` folder. They are HTML files that create the web interface.

## **base.html** - Base Template (Foundation)

**Purpose:** Parent template for all pages (navigation, styling, etc.)

**Key sections:**
- Navigation bar (header)
- Main content area (yields to child templates)
- Footer
- Common CSS/JS

**Used by:** All other templates

---

## **login.html** - Login Page

**Purpose:** Initial page users see

**Form fields:**
- Username input
- Password input
- Login button
- Register link

**Backend route:** `/` (app.py line ~30)

---

## **register.html** - Registration Page

**Purpose:** New user account creation

**Form fields:**
- Username
- Password
- Age
- Gender (dropdown)
- Medical Condition
- Register button
- Login link

**Backend route:** `/register` (app.py line ~45)

---

## **home.html** - Dashboard

**Purpose:** Shows user's recent conversations

**Elements:**
- Welcome message
- List of recent chat sessions
- "New Chat" button
- Navigation to Profile/Settings

**Backend route:** `/home` (app.py line ~75)

---

## **chat.html** - Chat Interface (MAIN FEATURE)

**Purpose:** Main conversation page

**Key elements:**
```
┌──────────────────────────┐
│ Sidebar (Sessions List)  │
├──────────────────────────┤
│                          │
│ Chat Messages Display    │
│ - User message bubbles   │
│ - AI response bubbles    │
│ - Medical guidance       │
│ - Precautions           │
│ - Confidence score      │
│                          │
├──────────────────────────┤
│ Input Area               │
│ [Text input]  [Send]     │
└──────────────────────────┘
```

**Features:**
- Shows conversation history
- Displays AI response in formatted sections
- Shows confidence bar
- Lists sources used
- Multiple session management

**Backend route:** `/chat/<session_id>` (app.py line ~100)

---

## **history.html** - Consultation History

**Purpose:** Shows all past conversations

**Elements:**
- Table/List of sessions
- Session titles
- Creation dates
- View/Edit/Delete buttons
- Search functionality (optional)

**Backend route:** `/history` (app.py line ~165)

---

## **profile.html** - User Medical Profile

**Purpose:** Edit personal medical information

**Form fields:**
- Age
- Gender
- Medical Condition
- Save button

**Backend route:** `/profile` (app.py line ~173)

---

## **settings.html** - Advanced Settings

**Purpose:** Configure AI model settings

**Form fields:**
- Fallback LLM model (optional)
- Model options: openai/gpt-3.5, google/palm-2, etc.
- Save button

**Backend route:** `/settings` (app.py line ~181)

---

# ⚙️ CONFIGURATION FILES

---

## **.env** - Environment Variables (SECRETS!)

**Location:** `/Users/themam/Documents/GitHub/medical-multi-source/.env`

**Contains:**
```
SECRET_KEY=your_secret_key_here
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
DATABASE_URL=sqlite:///database.db
```

**⚠️ IMPORTANT:**
- **NEVER commit to GitHub**
- In `.gitignore`
- Contains API keys and secrets
- Only on your local machine

**Used by:**
- `app.py` - Loads SECRET_KEY
- `model_pipeline.py` - Loads OPENROUTER_API_KEY

---

## **.env.example** - Template

**Purpose:** Shows what variables are needed

**Contains:**
```
SECRET_KEY=your_secret_key_here
OPENROUTER_API_KEY=your_openrouter_api_key
DATABASE_URL=sqlite:///database.db
```

**Used by:** New developers copy this to create `.env`

---

## **requirements.txt** - Python Dependencies

**Contains all Python packages needed:**
```
Flask
Flask-SQLAlchemy
Flask-Login
python-dotenv
sentence-transformers
faiss-cpu
pandas
numpy
requests
werkzeug
```

**How to use:**
```bash
pip install -r requirements.txt
```

---

## **.gitignore** - Files NOT to upload

**Contains:**
```
.env
__pycache__/
*.pyc
venv/
database.db
instance/
```

**Why:**
- `.env` has secrets
- `__pycache__` is auto-generated
- `database.db` is local data
- `venv/` is just dependencies

---

# 💾 DATABASE & INSTANCE

---

## **database.db** - SQLite Database

**Location:** `/Users/themam/Documents/GitHub/medical-multi-source/database.db`

**Contains:**
- All user accounts
- All chat sessions
- All messages

**Automatically created** by Flask on first run

**Tables:**
1. `user` - User accounts
2. `chat_session` - Conversations
3. `chat_message` - Individual messages

---

## **instance/** - Flask Instance Folder

**Purpose:** Stores instance-specific files

**Contains:**
- `config.py` (if used)
- Local configuration

---

# 🧪 TEST FILES

---

## **test_script.py** - General Testing

**Purpose:** Testing various functions

## **test_llm.py** - LLM Testing

**Purpose:** Testing OpenRouter API integration

---

# 📋 SUMMARY TABLE

| File | Purpose | Code Type |
|------|---------|-----------|
| `app.py` | Flask server & routes | Python |
| `models.py` | Database structure | Python |
| `model_pipeline.py` | AI/retrieval logic | Python |
| `healthcare_dataset.csv` | Clinical data | Data |
| `medical_text_classification_fake_dataset.csv` | Research data | Data |
| `train.csv` | Medical Q&A | Data |
| `templates/login.html` | Login page | HTML |
| `templates/register.html` | Register page | HTML |
| `templates/home.html` | Dashboard | HTML |
| `templates/chat.html` | Main chat UI | HTML |
| `templates/history.html` | History page | HTML |
| `templates/profile.html` | Profile form | HTML |
| `templates/settings.html` | Settings page | HTML |
| `.env` | Secrets & config | Config |
| `requirements.txt` | Dependencies | Config |
| `database.db` | Actual database | Data |

---

# 🎓 BEGINNER'S WORKFLOW

### To Understand How a User Question Gets Answered:

**1. User enters question** in `chat.html`
   ↓
**2. Form submitted to** `app.py` `/chat/<session_id>` route
   ↓
**3. Backend calls** `model_pipeline.py` → `process_query()`
   ↓
**4. Retrieval happens:**
   - Convert question to embedding
   - Search 3 FAISS indexes
   - Get top results with scores
   ↓
**5. Context built** with user profile + retrieved data
   ↓
**6. LLM called** via OpenRouter API
   ↓
**7. Response formatted** with sections
   ↓
**8. Saved to database** (`models.py` ChatMessage)
   ↓
**9. Displayed** in `chat.html` template
   ↓
**User sees answer!** ✅

---

## 🚀 Getting Started (For Developers)

### To add a new feature:

1. **Backend change?** → Edit `app.py` or `model_pipeline.py`
2. **Database change?** → Edit `models.py`
3. **UI change?** → Edit `templates/` HTML files
4. **New data source?** → Add CSV file + loader in `model_pipeline.py`
5. **Test the change** by running `python app.py`

### Common edits:

**Change LLM model:**
```python
# In model_pipeline.py
MODEL_NAME = "openai/gpt-3.5-turbo"  # Change this
```

**Add form field:**
```python
# In models.py - add column to User class
symptoms = db.Column(db.String(500))

# In app.py - handle in route
current_user.symptoms = request.form['symptoms']
```

**Change prompt format:**
```python
# In model_pipeline.py - modify prompt string
prompt = f"""
...(customize format)...
"""
```

---

*This guide covers all essential files and concepts!* 🎉
