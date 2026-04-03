import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    session = requests.Session()

    print("--- 1. Testing Registration ---")
    data = {"username": "testuser", "password": "password123", "age": "30", "gender": "Male", "medical_condition": "Healthy"}
    res = session.post(f"{BASE_URL}/register", data=data)
    if res.status_code == 200:
        print("✅ Registration completed")
    else:
        print(f"❌ Registration failed: {res.status_code}")
        return

    print("--- 2. Testing Login ---")
    login_data = {"username": "testuser", "password": "password123"}
    res = session.post(f"{BASE_URL}/", data=login_data)
    if "Welcome, testuser" in res.text:
        print("✅ Logged in successfully")
    else:
        print("❌ Login failed")
        return

    print("--- 3. Testing Home ---")
    res = session.get(f"{BASE_URL}/home")
    if res.status_code == 200 and "Start New Consultation" in res.text:
         print("✅ Home loaded successfully")
    else:
         print("❌ Home load failed")

    print("--- 4. Testing Profile Update ---")
    prof_data = {"age": "31", "gender": "Male", "medical_condition": "Cough"}
    res = session.post(f"{BASE_URL}/profile", data=prof_data)
    if res.status_code == 200:
        print("✅ Profile updated")
    else:
        print("❌ Profile update failed")

    print("--- 5. Testing Create Chat ---")
    res = session.get(f"{BASE_URL}/new_chat", allow_redirects=False)
    if res.status_code == 302 and "/chat/" in res.headers['Location']:
        chat_url = BASE_URL + res.headers['Location']
        print(f"✅ Created new chat session: {chat_url}")
    else:
        print("❌ Create chat failed")
        return

    print("--- 6. Testing Chat Ask Question (skip full process to save time/API, just check page loads) ---")
    res = session.get(chat_url)
    if res.status_code == 200:
        print("✅ Chat page loaded")
    else:
        print("❌ Chat page load failed")

    # Let's post a question! Note: This requires OpenRouter config. 
    # To prevent failing tests due to external API keys, we'll skip the actual query post.

    print("--- 7. Testing History Page ---")
    res = session.get(f"{BASE_URL}/history")
    if res.status_code == 200 and "Consultation History" in res.text:
        print("✅ History page loaded successfully")
    else:
        print("❌ History page failed")
        
    print("--- 8. Testing Logout ---")
    res = session.get(f"{BASE_URL}/logout")
    if res.status_code == 200:
        print("✅ Logout completed")

if __name__ == '__main__':
    run_tests()
