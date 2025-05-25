from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


active_tasks = {}

# Stop task helper
def stop_task(task_id):
    if task_id in active_tasks:
        del active_tasks[task_id]

# Start conversation message sender with hatter name
@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    data = request.json
    task_id = data.get('task_id')
    token = data.get('token')
    target_uid = data.get('target_uid')
    message = data.get('message')
    delay = float(data.get('delay', 5))
    hatter_name = data.get('hatter_name', 'Unknown')

    if not all([task_id, token, target_uid, message]):
        return jsonify({"error": "Missing parameters"}), 400

    if task_id in active_tasks:
        return jsonify({"error": "Task ID already running"}), 400

    active_tasks[task_id] = True

    def send_message():
        url = f"https://graph.facebook.com/v16.0/{target_uid}/messages"
        params = {"access_token": token}
        headers = {"Content-Type": "application/json"}

        while task_id in active_tasks:
            full_message = f"{hatter_name}: {message}"
            data = {"message": {"text": full_message}}
            try:
                response = requests.post(url, params=params, json=data, headers=headers)
                print(f"[{task_id}] Sent message: {full_message} Status: {response.status_code}")
            except Exception as e:
                print(f"[{task_id}] Error sending message: {e}")
            time.sleep(delay)

    threading.Thread(target=send_message, daemon=True).start()
    return jsonify({"status": "started", "task_id": task_id})

# Start post comment sender with hatter name
@app.route('/start_post', methods=['POST'])
def start_post():
    data = request.json
    task_id = data.get('task_id')
    token = data.get('token')
    post_id = data.get('post_id')
    comment = data.get('comment')
    delay = float(data.get('delay', 5))
    hatter_name = data.get('hatter_name', 'Unknown')

    if not all([task_id, token, post_id, comment]):
        return jsonify({"error": "Missing parameters"}), 400

    if task_id in active_tasks:
        return jsonify({"error": "Task ID already running"}), 400

    active_tasks[task_id] = True

    def post_comment():
        url = f"https://graph.facebook.com/{post_id}/comments"
        params = {"access_token": token}

        while task_id in active_tasks:
            full_comment = f"{hatter_name}: {comment}"
            params['message'] = full_comment
            try:
                response = requests.post(url, params=params)
                print(f"[{task_id}] Posted comment: {full_comment} Status: {response.status_code}")
            except Exception as e:
                print(f"[{task_id}] Error posting comment: {e}")
            time.sleep(delay)

    threading.Thread(target=post_comment, daemon=True).start()
    return jsonify({"status": "started", "task_id": task_id})

# Stop task route
@app.route('/stop_task', methods=['POST'])
def stop_task_route():
    data = request.json
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    if task_id not in active_tasks:
        return jsonify({"error": "Task not found"}), 404

    stop_task(task_id)
    return jsonify({"status": "stopped", "task_id": task_id})

# Extract token from cookie (simplified)
@app.route('/extract_token', methods=['POST'])
def extract_token():
    data = request.json
    cookie = data.get('cookie')
    if not cookie:
        return jsonify({"error": "Cookie required"}), 400

    # Very basic and naive token extraction example (adjust per real Facebook cookie structure)
    token = None
    for part in cookie.split(';'):
        if 'c_user' in part or 'xs=' in part:
            # This is a dummy example; real token extraction needs real cookie parsing & possibly encryption decode
            token = part.strip()
            break

    if not token:
        return jsonify({"error": "Token not found in cookie"}), 404

    return jsonify({"token": token})

# Show groups for user token
@app.route('/show_groups', methods=['POST'])
def show_groups():
    data = request.json
    token = data.get('token')
    if not token:
        return jsonify({"error": "Token required"}), 400

    url = "https://graph.facebook.com/me/groups"
    params = {"access_token": token}
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch groups", "details": response.text}), 400
        groups_data = response.json().get('data', [])
        groups = [{"id": g.get("id"), "name": g.get("name")} for g in groups_data]
        return jsonify({"groups": groups})
    except Exception as e:
        return jsonify({"error": "Exception occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
