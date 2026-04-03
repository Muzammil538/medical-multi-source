import requests

BASE_URL = "http://127.0.0.1:5000"

session = requests.Session()
# 1. Login
data = {"username": "testuser", "password": "password123"}
res = session.post(f"{BASE_URL}/", data=data)
if "Welcome" not in res.text:
    print("Login failed")
    exit(1)

# 2. Open an existing chat or create a new one
res = session.get(f"{BASE_URL}/new_chat", allow_redirects=False)
chat_url = BASE_URL + res.headers['Location']

# 3. Ask a question
print("Sending question...")
res = session.post(chat_url, data={"question": "What is the best treatment for a headache?"})

# 4. Check response
if "Medical Guidance" in res.text:
    print("✅ Received medical guidance successfully!")
else:
    print("❌ Failed to receive medical guidance.")
    print("Status Code:", res.status_code)
    try:
        err_msg = [line for line in res.text.split('\n') if "Exception" in line or "Error" in line]
        if err_msg:
            print("Server errors:", err_msg)
    except:
        pass
