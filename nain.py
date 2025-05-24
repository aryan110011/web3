from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Track running driver globally (not safe for multi-user/multi-thread, but fine for dev)
active_driver = None

def init_driver(cookie_string):
    global active_driver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    active_driver = driver

    driver.get("https://www.facebook.com/")
    driver.delete_all_cookies()

    cookies = cookie_string.split('; ')
    for c in cookies:
        if '=' in c:
            name, value = c.split('=', 1)
            driver.add_cookie({'name': name, 'value': value})

    driver.get("https://www.facebook.com/")
    time.sleep(3)
    return driver

def send_message(driver, target_uid, message):
    url = f"https://www.facebook.com/messages/t/{target_uid}"
    driver.get(url)
    time.sleep(5)
    try:
        input_box = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')
        input_box.send_keys(message)
        input_box.send_keys('\n')
        return "Message sent"
    except Exception as e:
        return f"Failed to send message: {e}"

def post_to_group(driver, group_url, message):
    driver.get(group_url)
    time.sleep(5)
    try:
        post_area = driver.find_element(By.XPATH, '//div[@aria-label="Create a public post"]')
        post_area.click()
        time.sleep(3)
        input_box = driver.find_element(By.XPATH, '//div[@role="dialog"]//div[@aria-label="What\'s on your mind?"]')
        input_box.send_keys(message)
        time.sleep(1)
        post_button = driver.find_element(By.XPATH, '//div[@aria-label="Post"]')
        post_button.click()
        return "Post submitted"
    except Exception as e:
        return f"Failed to post: {e}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    data = request.form
    cookie = data.get('cookie')
    target_uid = data.get('target_uid')
    message_type = data.get('message_type')

    if message_type == 'single':
        message = data.get('message')
    else:
        message_file = request.files.get('message_file')
        if message_file:
            filename = secure_filename(message_file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            message_file.save(path)
            with open(path, 'r', encoding='utf-8') as f:
                message = f.read()
        else:
            return jsonify({"error": "No message file uploaded"}), 400

    try:
        driver = init_driver(cookie)
        result = send_message(driver, target_uid, message)
        driver.quit()
    except Exception as e:
        result = f"Automation failed: {e}"

    return jsonify({
        "status": "success",
        "action": "start_conversation",
        "message": result
    })

@app.route('/start_post', methods=['POST'])
def start_post():
    data = request.form
    cookie = data.get('cookie')
    group_url = data.get('group_url')
    message_type = data.get('message_type')

    if message_type == 'single':
        message = data.get('message')
    else:
        message_file = request.files.get('message_file')
        if message_file:
            filename = secure_filename(message_file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            message_file.save(path)
            with open(path, 'r', encoding='utf-8') as f:
                message = f.read()
        else:
            return jsonify({"error": "No message file uploaded"}), 400

    try:
        driver = init_driver(cookie)
        result = post_to_group(driver, group_url, message)
        driver.quit()
    except Exception as e:
        result = f"Automation failed: {e}"

    return jsonify({
        "status": "success",
        "action": "start_post",
        "message": result
    })

@app.route('/stop_task', methods=['POST'])
def stop_task():
    global active_driver
    if active_driver:
        try:
            active_driver.quit()
            active_driver = None
            return jsonify({"status": "stopped"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "no active task"})

@app.route('/extract_token', methods=['POST'])
def extract_token():
    cookie = request.form.get('cookie')
    if not cookie:
        return jsonify({"error": "No cookie provided"}), 400
    token = "EAAGm0PX..." if "c_user=" in cookie else "Invalid cookie"
    return jsonify({"token": token})

if __name__ == '__main__':
    app.run(debug=True)
