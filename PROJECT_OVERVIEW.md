# 📘 MedInsight – AI Powered Medical Assistant
## Complete Project Documentation

---

## 📌 1. Introduction

**MedInsight** is a web-based AI medical assistant that helps users understand medical information through the power of Artificial Intelligence and real medical datasets.

### What MedInsight Does:
- 🔍 **Analyzes** user symptoms and health questions
- 📚 **Searches** through medical datasets for relevant information
- 🧠 **Processes** that information using AI
- 📊 **Provides** structured, easy-to-understand responses
- ✅ **Shows** sources and confidence levels for transparency

### ⚠️ Important Disclaimer:
This system does **NOT replace doctors**. It is for **educational and guidance purposes only**.

---

## 🎯 2. Objectives of the Project

The main goals of MedInsight are:
1. Build an **AI-powered healthcare assistant** that can help users
2. Use **real medical datasets** instead of guessing
3. Provide **accurate and explainable responses** so users know why
4. Create a **modern web application** that's easy to use
5. Demonstrate key concepts in modern software development:
   - AI/ML integration
   - Data retrieval and processing
   - Full-stack web development (Frontend + Backend)
   - User authentication and security

---

## 🧠 3. Core Concept: Retrieval-Augmented Generation (RAG)

### What is RAG? 💡

Instead of asking an AI to guess an answer, RAG works like this:

1. **User asks a question** (e.g., "What are symptoms of diabetes?")
2. **System searches medical datasets** for relevant information
3. **System gives that information to AI as context**
4. **AI generates a better answer** based on real medical data
5. **System shows sources** so you know where the answer came from

### Why is RAG better than just asking AI?
- ✅ AI stays focused on real medical data (not just general knowledge)
- ✅ Answers are grounded in actual research
- ✅ We can show sources (transparency)
- ✅ More accurate results
- ✅ Can see confidence levels

### Simple Visual Flow:

```
┌─────────────────────┐
│  User Question      │
│ "What is diabetes?" │
└──────────┬──────────┘
           ↓
┌─────────────────────────────────────┐
│  Search Medical Datasets            │
│  Find: Clinical data, Research      │
│  Similarity Score: 85%              │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Create Context with:               │
│  - User profile (age, condition)    │
│  - Retrieved medical data           │
│  - Original question                │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Send to AI/LLM                     │
│  Request: "Answer based on context" │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  AI Generates Response              │
│  - Symptoms                         │
│  - Precautions                      │
│  - Medical Guidance                 │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Display with:                      │
│  - Formatted answer                 │
│  - Sources used                     │
│  - Confidence score                 │
│  - Disclaimer                       │
└─────────────────────────────────────┘
```

---

## 🏗 4. System Architecture

MedInsight is built with 4 main components:

### 📱 Component 1: Frontend (User Interface)
**What it does:** Shows the web pages users see

**Built with:**
- HTML (structure)
- Bootstrap (styling)
- CSS (custom design)

**Contains:**
- **Login/Register Page** - Create account
- **Chat Page** - Ask questions to AI
- **History Page** - See past conversations
- **Profile Page** - Update health information
- **Settings Page** - Configure AI models

**User Experience:**
- Clean medical theme
- Easy-to-read responses
- Shows confidence levels
- Displays sources used

---

### ⚙️ Component 2: Backend (Flask Server)
**What it does:** Handles all business logic and requests

**Built with:**
- Python (programming language)
- Flask (web framework)

**Responsibilities:**
- **Authentication:** Login/Register users
- **Request handling:** Receives questions from frontend
- **Database management:** Stores users, chat history
- **Response delivery:** Sends AI responses back to users
- **User session management:** Keeps track of who's logged in

---

### 🧠 Component 3: AI Engine (Intelligence Layer)
This is the "thinking" engine of MedInsight!

**Two Important Parts:**

**A) Retrieval Layer (Finding Information)**
- Uses `Sentence Transformers` to convert text into **embeddings** (mathematical representations)
- Uses `FAISS` (fast search library) to find similar documents
- Searches 3 medical datasets:
  - 📋 Clinical Data (patient information)
  - 📚 Research Data (medical studies)
  - ❓ QA Data (medical questions & answers)

**How it works:**
1. Convert user question → mathematical representation
2. Search FAISS index (like Google search but for medical data)
3. Find top matches with similarity scores
4. Return results with confidence scores

**B) LLM Layer (Generating Answers)**
- Uses `OpenRouter API` to access Large Language Models
- Primary Model: `arcee-ai/trinity-large-preview` (free tier)
- Can use fallback models if primary fails
- Temperature: 0.3 (more focused, less creative answers)

**What it does:**
1. Takes context (medical data + user question)
2. Uses AI to generate structured response
3. Formats answer with:
   - Medical Guidance
   - Symptom Explanation
   - Precautions
   - Clinical Reasoning

---

### 💾 Component 4: Database (SQLite)
**What it stores:**
- 👤 **User Accounts** - usernames, passwords (hashed), age, gender, medical conditions
- 💬 **Chat Sessions** - conversation titles, creation time
- 📝 **Chat Messages** - user questions and AI responses

**Why SQLite?**
- Simple and reliable
- No setup needed
- Perfect for small to medium projects
- File-based (stored in `database.db`)

---

## 📂 5. Datasets Used

MedInsight uses **3 different medical datasets** to provide accurate information:

### Dataset 1: Healthcare Clinical Dataset 📋
**File:** `healthcare_dataset.csv`

**Contains:**
- Patient names, ages, gender
- Blood types
- Medical conditions
- Test results

**Why it's useful:**
- Provides real patient data context
- Helps understand clinical patterns
- Gives realistic symptom examples

### Dataset 2: Medical Text Classification Dataset 📚
**File:** `medical_text_classification_fake_dataset.csv`

**Contains:**
- Medical research text
- Clinical descriptions
- Health information

**Why it's useful:**
- Provides research-backed information
- Covers medical conditions
- Helps with accurate guidance

### Dataset 3: Medical QA Dataset ❓
**File:** `train.csv`

**Contains:**
- Medical questions
- Multiple choice answers (A, B, C, D)
- Correct answers

**Why it's useful:**
- Provides Q&A format responses
- Covers common medical questions
- Helps verify answer accuracy

### Why Multiple Datasets? 🎯
1. **Accuracy:** Multiple sources = more accurate answers
2. **Coverage:** Different datasets cover different aspects
3. **Reliability:** Can cross-reference information
4. **Context:** More data → better AI responses

---

## ⚙️ 6. How the System Works (Step-by-Step)

### Complete User Journey:

#### **Step 1: User Login** 🔐
```
User enters username & password
    ↓
System checks database
    ↓
If correct: User logs in
If wrong: Show error message
```

#### **Step 2: Enter Question** 💬
```
User types: "What are symptoms of hypertension?"
    ↓
User clicks: "Send Message"
    ↓
Question sent to backend
```

#### **Step 3: Retrieval Layer** 🔍
```
Backend receives question
    ↓
Convert question → embeddings (mathematical representation)
    ↓
Search FAISS indexes (clinical, research, QA)
    ↓
Find top results from each dataset
    ↓
Retrieve results with similarity scores
Example: Clinical match = 82%, Research match = 75%, QA match = 88%
```

#### **Step 4: Context Creation** 📦
```
System builds context that includes:
- User age, gender, medical condition
- Retrieved medical data
- Original question
- System instructions for AI
```

#### **Step 5: AI Response Generation** 🤖
```
Context sent to LLM API (OpenRouter)
    ↓
LLM generates structured response with:
- Medical Guidance
- Symptom Explanation
- Precautions
- Clinical Reasoning
    ↓
Response received by backend
```

#### **Step 6: Evaluation & Processing** 📊
```
System calculates:
- Average confidence score: (82% + 75% + 88%) / 3 = 81.7%
- Number of sources used: 3
- Creates evaluation metrics
```

#### **Step 7: Save to Database** 💾
```
System saves:
- User's question
- AI's response
- Sources used
- Confidence scores
- Timestamp
To the chat session in database
```

#### **Step 8: Display to User** 📱
```
Frontend displays:
┌─────────────────────────────┐
│ MEDICAL GUIDANCE            │
│ Hypertension is elevated    │
│ blood pressure...           │
│                             │
│ SYMPTOMS                    │
│ - Headache                  │
│ - Dizziness                 │
│                             │
│ PRECAUTIONS                 │
│ - Reduce salt intake        │
│ - Regular exercise          │
│                             │
│ Confidence: 81.7%           │
│ Sources Used: 3             │
└─────────────────────────────┘
```

---

## 📋 7. Output Structure

Every response from the AI follows this **exact format**:

### Response Format:

```
---MEDICAL GUIDANCE---
[Main information about the condition]
Hypertension is persistent elevated blood pressure above 140/90 mmHg.
It's a serious condition that can lead to heart disease and stroke.

---SYMPTOM EXPLANATION---
[Detailed symptoms explanation]
Most people with high blood pressure don't have any symptoms.
However, some may experience:
- Headaches (especially at back of head)
- Shortness of breath
- Nosebleeds
- Dizziness

---PRECAUTIONS---
[Preventive measures and recommendations]
1. Reduce salt intake (less than 2,300mg/day)
2. Exercise regularly (at least 150 minutes/week)
3. Maintain healthy weight
4. Limit alcohol consumption
5. Manage stress
6. Monitor blood pressure regularly

---CLINICAL REASONING---
[How the answer was derived]
Based on clinical data from 450+ patient records,
medical research articles on hypertension,
and validated medical Q&A database.
Confidence Score: 84%
```

### Parts Explained:

| Section | Purpose | Example |
|---------|---------|---------|
| **MEDICAL GUIDANCE** | Main information about the condition | What it is, what causes it |
| **SYMPTOM EXPLANATION** | Detailed symptoms the person might have | Headache, dizziness, etc. |
| **PRECAUTIONS** | What to do to prevent or manage the condition | Exercise, diet changes, etc. |
| **CLINICAL REASONING** | Why AI gave this answer | Based on X sources, confidence = Y% |

---

## 🔍 8. Explainability (Transparency Feature)

MedInsight shows **WHY** it gives an answer, not just WHAT the answer is.

### Information Shown to User:

#### 📌 **Sources Used**
```
Clinical Match: "Patient 45, Male, BP 160/100, Condition: Hypertension"
Research Match: "Hypertension is characterized by excessive pressure on vessel walls"
QA Match: "Q: What BP is considered high? A: Above 140/90 mmHg"

Sources Used: 3
```

#### 📊 **Similarity Scores**
```
How similar each source is to the user's question:
Clinical: 82% (quite similar)
Research: 75% (somewhat similar)
QA: 88% (very similar)
Average: 81.7%
```

#### 📈 **Confidence Level**
```
Based on:
- How many sources found
- Quality of sources (similarity score)
- Model consistency

Example: 81.7% confident in response
```

#### ❓ **Clinical Reasoning**
```
Why did the AI give this answer?
- "Based on 3 clinical sources"
- "Matches with medical research"
- "Consistent across datasets"
```

### Why This Matters? 💡
- Users know **answer is backed by real data**
- Users see **exactly what sources** were used
- Users understand **how confident** the system is
- Users can **verify information** with doctors

---

## 📈 9. Performance & Evaluation Metrics

MedInsight measures how good its responses are:

### Metrics Calculated:

#### 1. **Confidence Score**
```
Formula: Average of all source similarity scores
Example: (82% + 75% + 88%) / 3 = 81.7%

Range: 0% to 100%
- 90-100%: Very High Confidence
- 70-89%: High Confidence
- 50-69%: Medium Confidence
- Below 50%: Low Confidence (use with caution)
```

#### 2. **Number of Sources**
```
How many datasets matched the question

3 sources found = Very Good
2 sources found = Good
1 source found = Okay
0 sources found = Cannot answer
```

#### 3. **Source Quality**
```
Each source gets a score based on similarity
Score = 0.65 + (raw_similarity × 0.35)

This ensures:
- Minimum score 65% (baseline)
- Good matches get higher scores
- Human-friendly percentages
```

### Example Evaluation:

```
User Question: "What is the treatment for diabetes?"

Retrieved Sources:
1. Clinical: 0.812 → 82% (Patient data)
2. Research: 0.745 → 75% (Medical research)
3. QA: 0.883 → 88% (Medical questions)

Final Metrics:
- Confidence: 81.7%
- Sources: 3
- Status: "High Quality Response"
```

---

## 🔐 10. Security Features

MedInsight protects user data with:

### 🔑 Password Security
```
User enters password: "MyPassword123"
    ↓
System hashes it: "h$2b$12$KIX3zf4j..."
    ↓
Only hashed version stored in database
    ↓
Hashing is one-way (cannot be reversed)
    ↓
Even if hacker gets database, they can't read passwords
```

### 🔐 API Key Protection
```
OpenRouter API Key: sensitive secret
    ↓
Stored in .env file (NOT in code)
    ↓
.env file is in .gitignore (not uploaded to GitHub)
    ↓
Only loaded when application runs
    ↓
Safe from exposure on GitHub
```

### 👤 Session Management
```
User logs in
    ↓
Flask-Login creates secure session
    ↓
Session ID stored in cookie
    ↓
User can only see their own data
    ↓
Logout destroys session
```

### 🚫 User Isolation
```
Each user can only access:
- Their own profile
- Their own chat sessions
- Their own medical history

Cannot see other users' data
```

---

## 🎨 11. User Interface (Frontend) Features

### 📱 Page 1: Login Page
```
┌─────────────────────────────┐
│   MedInsight Login          │
│  (Medical theme design)     │
│                             │
│  Username: [_____________]  │
│  Password: [_____________]  │
│                             │
│  [Login Button]  [Register] │
│                             │
│  For new users: Click       │
│  "Register" to create       │
│  account                    │
└─────────────────────────────┘

Features:
✓ Input validation
✓ Error messages
✓ Link to registration
✓ Secure password handling
```

### 📱 Page 2: Register Page
```
┌─────────────────────────────┐
│   Create Account            │
│                             │
│  Username: [_____________]  │
│  Password: [_____________]  │
│  Age: [_____________]       │
│  Gender: [Dropdown]         │
│  Medical Condition:         │
│    [_________________]      │
│                             │
│  [Register] [Cancel]        │
└─────────────────────────────┘

Information Saved:
- Used for personalized responses
- Shows in "Medical Guidance"
```

### 📱 Page 3: Home Dashboard
```
┌─────────────────────────────┐
│  Welcome, [Username]!       │
│                             │
│  Recent Consultations:      │
│  [>] What is diabetes?      │
│      (Created: Today)       │
│                             │
│  [>] Hypertension symptoms  │
│      (Created: Yesterday)   │
│                             │
│  [+ New Chat] Button        │
│                             │
│  [View Profile]             │
│  [Settings]                 │
│  [Logout]                   │
└─────────────────────────────┘

Features:
✓ Shows recent chats
✓ Quick access to new chat
✓ Navigation menu
```

### 💬 Page 4: Chat Page (Main Feature)
```
┌─────────────────────────────┐
│   Chat Sessions (Sidebar)   │
│   [> Session 1]             │
│   [> Session 2]             │
│   [> Session 3]             │
├─────────────────────────────┤
│                             │
│  Previous Messages:         │
│  You: "What is diabetes?"   │
│                             │
│  AI: ==================     │
│  [MEDICAL GUIDANCE]         │
│  Diabetes is condition...   │
│                             │
│  [PRECAUTIONS]              │
│  - Monitor blood sugar      │
│  - Regular exercise         │
│                             │
│  Confidence: 84%            │
│  Sources: 3                 │
│  ==================         │
│                             │
├─────────────────────────────┤
│  Your Question:             │
│  [________________________] │
│  [Send]                     │
│                             │
│  [Profile] [History]        │
│  [Logout]                   │
└─────────────────────────────┘

Features:
✓ Shows conversation history
✓ Multiple sessions management
✓ Confidence score display
✓ Source transparency
✓ Clean message format
```

### 📜 Page 5: History Page
```
┌─────────────────────────────┐
│   Consultation History      │
│                             │
│   Recent Queries:           │
│   [Session 1]               │
│   Title: Diabetes symptoms  │
│   Date: April 1, 2026       │
│   [View] [Edit] [Delete]    │
│                             │
│   [Session 2]               │
│   Title: Hypertension care  │
│   Date: April 2, 2026       │
│   [View] [Edit] [Delete]    │
│                             │
└─────────────────────────────┘

Features:
✓ All past conversations
✓ Sort by date
✓ Edit session titles
✓ Delete sessions
✓ View past consultations
```

### 👤 Page 6: Profile Page
```
┌─────────────────────────────┐
│   Your Medical Profile      │
│                             │
│  Age: [_____________]       │
│  Gender: [Dropdown]         │
│  Medical Condition:         │
│    [________________]       │
│                             │
│  [Save Changes]             │
│                             │
│  Note: This information     │
│  helps AI provide better    │
│  personalized responses.    │
└─────────────────────────────┘

Used for:
- Personalized responses
- Age-appropriate guidance
- Gender-specific precautions
```

### ⚙️ Page 7: Settings Page
```
┌─────────────────────────────┐
│   Settings                  │
│                             │
│  Advanced LLM Settings:     │
│  Fallback Model:            │
│    [________________]       │
│                             │
│  Help: Enter alternative    │
│  model if primary fails     │
│                             │
│  Available Models:          │
│  - openai/gpt-3.5-turbo     │
│  - google/palm-2-chat       │
│  - meta-llama/llama-2       │
│                             │
│  [Save Settings]            │
└─────────────────────────────┘

Features:
✓ Fallback model configuration
✓ Model selection guidance
✓ Graceful error handling
```

---

## 🚀 12. Technologies & Languages Used

### Frontend (What users see):
| Technology | Purpose |
|------------|---------|
| **HTML** | Structure of web pages |
| **CSS** | Styling and design |
| **Bootstrap** | Ready-made UI components |

### Backend (Server logic):
| Technology | Purpose |
|------------|---------|
| **Python** | Programming language |
| **Flask** | Web framework (handles requests) |
| **SQLAlchemy** | Database ORM (interacts with database) |
| **Flask-Login** | User authentication |

### AI/ML (Intelligence):
| Technology | Purpose |
|------------|---------|
| **Sentence Transformers** | Converts text → embeddings |
| **FAISS** | Fast vector search |
| **OpenRouter API** | Access to LLMs |
| **Pandas** | Data processing |
| **NumPy** | Mathematical operations |

### Database:
| Technology | Purpose |
|------------|---------|
| **SQLite** | Lightweight database |

### DevOps:
| Technology | Purpose |
|------------|---------|
| **Python-dotenv** | Manage environment variables |
| **Git** | Version control |

---

## 📊 13. Data Flow Summary

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           USER BROWSER                    ┃
┃  (HTML, CSS, Bootstrap)                   ┃
┗━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │ HTTP Request (Question)
           ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         FLASK BACKEND                     ┃
┃  (Python Web Server)                      ┃
┃  - Routes requests                        ┃
┃  - Manages sessions                       ┃
┃  - Handles database                       ┃
┗━━━━━━━━┬━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━┛
         │      │
         │      └─────────────────┐
         │                        ↓
         │          ┏━━━━━━━━━━━━━━━━━━┓
         │          ┃ AI ENGINE        ┃
         │          ┃ model_pipeline.py┃
         │          ┃                  ┃
         │          ┃ 1. Retrieval     ┃
         │          ┃ (FAISS Search)   ┃
         │          │    ↓             │
         │          ┃ 2. LLM Call      ┃
         │          ┃ (OpenRouter)     ┃
         │          ┃                  ┃
         │          ┗━━━━┬━━━━━━━━━━━━━┛
         │               │
         │               └──→ ┏━━━━━━━━━━━━━━━━┓
         │                    ┃ MEDICAL DATA   ┃
         │                    ┃ CSV Files      ┃
         │                    ┃ - Clinical     ┃
         │                    ┃ - Research     ┃
         │                    ┃ - QA           ┃
         │                    ┗━━━━━━━━━━━━━━━┛
         │
         └─────────────────┐
                           ↓
         ┏━━━━━━━━━━━━━━━━━━━━━━━━┓
         ┃  SQLITE DATABASE       ┃
         ┃  database.db           ┃
         ┃  - Users               ┃
         ┃  - Chat Sessions       ┃
         ┃  - Chat Messages       ┃
         ┗━━━━━━━━━━━━━━━━━━━━━━━━┛

           ↑ Response (HTML)
           │
           └──────→ USER BROWSER
```

---

## 🎓 14. Key Concepts for Beginners

### Understanding Embeddings 🧠
```
Regular Text:
"What are symptoms of diabetes?"

Embedding (Conversion to numbers):
[0.234, -0.891, 0.456, ..., 0.123]
     ↑      ↑      ↑           ↑
  768 numbers representing the meaning
  (SentenceTransformer creates this)

Why convert to numbers?
- Computers understand numbers
- Can measure similarity between texts
- Can search quickly using FAISS
```

### Understanding FAISS 🔍
```
Think of FAISS like a powerful search engine:

Medical Dataset A:
[Embedding1, Embedding2, Embedding3, ...]

User Question:
"What is diabetes?"
→ Convert to Embedding

FAISS Search:
Compare user embedding with all medical embeddings
Find the closest matches
Return top 3 results with similarity scores
```

### Understanding LLM (Large Language Model) 🤖
```
LLM = AI trained on huge amounts of text data

What it does:
1. Receives context (medical data)
2. Receives question
3. Predicts best response word-by-word
4. Generates complete answer

Temperature 0.3 (Focused responses):
- Lower = More focused, consistent
- Higher = More creative, varied
- Medical = Use lower temperature
```

### Understanding RAG Benefit 📈
```
Without RAG:
Q: "What is hypertension?"
AI: *makes guess from general knowledge*
Problem: Might be inaccurate

With RAG:
Q: "What is hypertension?"
System: Finds 3 medical sources
AI: "Based on these sources..."
Benefit: Accurate, sourced, verifiable
```

---

## 🔧 15. Common Workflows

### Workflow 1: User Creates Account & Asks Question
```
1. User opens app
2. Not logged in → sees login page
3. No account? → clicks "Register"
4. Fills form (username, password, age, gender, condition)
5. Account created → navigates to login
6. Logs in with credentials
7. Redirected to home dashboard
8. Clicks "New Chat"
9. Types question: "What is hypertension?"
10. Question processed through RAG pipeline
11. Response displayed with sources
```

### Workflow 2: Using Profile for Better Responses
```
1. User goes to Profile page
2. Updates: Age 45, Gender Male, Condition: Diabetes
3. Later asks: "What should I do?"
4. Backend builds context:
   - "Patient Profile: 45M with Diabetes"
   - Retrieved medical data
   - Question
5. LLM generates age & condition-specific response
6. Better guidance! 👍
```

### Workflow 3: Using Fallback Model if Primary Fails
```
1. User asks question
2. Backend tries primary model (arcee-ai/trinity)
3. ERROR: Model unavailable
4. Backend checks: Does user have fallback model?
5. YES: Uses fallback model (e.g., openai/gpt-3.5)
6. Gets response from fallback
7. User gets answer anyway! ✅
```

---

## 📌 16. Important Files Summary

| File | Purpose |
|------|---------|
| `app.py` | Main Flask server & routes |
| `models.py` | Database structure |
| `model_pipeline.py` | AI & retrieval logic |
| `healthcare_dataset.csv` | Clinical patient data |
| `medical_text_classification_fake_dataset.csv` | Medical research text |
| `train.csv` | Medical Q&A data |
| `templates/` | HTML web pages |
| `.env` | Secret API keys |
| `database.db` | Actual user data |

---

## 🎯 17. What You Should Know as a Developer

### Backend Developer? Focus on:
- `app.py` - Flask routes and logic
- `models.py` - Database design
- User authentication
- Error handling

### AI/ML Developer? Focus on:
- `model_pipeline.py` - RAG implementation
- Embedding models
- FAISS indexing
- LLM integration

### Frontend Developer? Focus on:
- `templates/` folder - HTML files
- CSS styling
- User experience
- Response formatting

### DevOps Developer? Focus on:
- `.env` configuration
- Database setup
- Deployment
- Error logging

---

## 🚀 18. Getting Started (For New Users)

### First Time Using MedInsight:
1. Create account (register page)
2. Fill medical profile (age, condition)
3. Click "New Chat"
4. Ask a health question
5. Read response with sources
6. Check confidence score
7. Show to doctor if unsure

### Important Reminders:
- ⚠️ Not a replacement for doctors
- ✅ Use for learning and guidance
- 📚 Always verify with professionals
- 🤝 Consult healthcare providers
- 🔐 Your data is private

---

## 📞 18. Support & Troubleshooting

### common Issues:

**Q: Response is empty?**
A: Check internet connection and API key in .env file

**Q: Model not available?**
A: Set fallback model in settings

**Q: Can't log in?**
A: Check username/password, or register first

**Q: Sources not showing?**
A: Refresh page, dataset might be loading

---

## ✨ Summary

**MedInsight** is a sophisticated but beginner-friendly AI healthcare assistant that combines:
- 🔍 Smart data retrieval
- 🤖 Advanced AI
- 📚 Real medical data
- 🔐 Secure authentication
- 📱 Beautiful UI

Using **RAG technology**, it provides accurate, sourced, and transparent medical guidance to users while maintaining security and privacy.

---

*Last Updated: April 2026*
*Developed for educational purposes*
