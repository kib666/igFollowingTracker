from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

# Ensure the database exists
conn = sqlite3.connect("ig_tracker.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS following (
        username TEXT,
        timestamp TEXT
    )
""")
conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    """Attempt to log in to Instagram to verify credentials"""
    data = request.json
    ig_username = data.get("username")
    ig_password = data.get("password")

    if not ig_username or not ig_password:
        return jsonify({"error": "Username and password required"}), 400

    # Setup Selenium
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.instagram.com/accounts/login/")
        wait = WebDriverWait(driver, 15)

        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(ig_username)
        password_input.send_keys(ig_password)
        password_input.send_keys(Keys.RETURN)

        # wait until we are redirected or login error appears
        time.sleep(5)
        current_url = driver.current_url
        if "challenge" in current_url or "two_factor" in current_url or "accounts/login" in current_url:
            return jsonify({"error": "Login failed. Please check your credentials."}), 401

        session["ig_username"] = ig_username
        session["ig_password"] = ig_password

        return jsonify({"message": "Login successful!"})

    except Exception as e:
        return jsonify({"error": f"Login error: {str(e)}"}), 500

    finally:
        driver.quit()

@app.route("/scrape", methods=["POST"])
def scrape():
    """Scrape IG following list using session credentials"""
    if "ig_username" not in session or "ig_password" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    target_username = data.get("target_username")

    if not target_username:
        return jsonify({"error": "No username provided"}), 400

    result = scrape_following(target_username, session["ig_username"], session["ig_password"])
    return jsonify(result)

def scrape_following(target_username, ig_username, ig_password):
    """Logs into Instagram with user credentials and scrapes following list"""
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com/accounts/login/")
        wait = WebDriverWait(driver, 15)

        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(ig_username)
        password_input.send_keys(ig_password)
        password_input.send_keys(Keys.RETURN)

        # wait until login completes
        time.sleep(5)

        driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(5)

        following_button = driver.find_element(By.XPATH, "//a[contains(@href, '/following')]")
        following_button.click()
        time.sleep(5)

        following_users = []
        users = driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")

        for user in users:
            following_users.append(user.text)

        conn = sqlite3.connect("ig_tracker.db")
        cursor = conn.cursor()
        for user in following_users:
            cursor.execute("INSERT INTO following VALUES (?, datetime('now'))", (user,))
        conn.commit()
        conn.close()

        return {"message": f"Scraped {len(following_users)} users from {target_username}!"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(debug=True)
