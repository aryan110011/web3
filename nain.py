from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

active_tasks = {}

<!DOCTYPE html> 
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Messenger Auto Sender Tool</title>
  <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      margin: 0;
      background: #f5f7fc;
      color: #222;
    }
    header {
      background: #0f1d40;
      color: white;
      text-align: center;
      padding: 25px 0;
      font-size: 28px;
      font-weight: bold;
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    nav {
      display: flex;
      background: #1c2e63;
    }
    nav button {
      flex: 1;
      background: #2e438e;
      color: white;
      padding: 15px;
      font-weight: bold;
      border: none;
      cursor: pointer;
      transition: 0.3s;
    }
    nav button:hover,
    nav button.active {
      background: #405bb5;
    }
    section {
      display: none;
      max-width: 900px;
      margin: 30px auto;
      padding: 25px 35px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    section.active {
      display: block;
    }
    h2 {
      color: #0f1d40;
      border-bottom: 3px solid #405bb5;
      padding-bottom: 10px;
    }
    .admin-pic {
      display: block;
      margin: 20px auto 10px;
      width: 130px;
      height: 130px;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid #405bb5;
    }
    .admin-name {
      text-align: center;
      font-weight: bold;
      font-size: 20px;
      margin-bottom: 5px;
    }
    .admin-desc {
      text-align: center;
      font-style: italic;
      color: #405bb5;
      margin-bottom: 15px;
    }
    .made-by {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
      color: #777;
      font-style: italic;
    }
    .accordion-item {
      margin-bottom: 20px;
    }
    .accordion-header {
      background: #405bb5;
      color: white;
      padding: 14px;
      font-weight: bold;
      border-radius: 6px;
      cursor: pointer;
    }
    .accordion-content {
      background: #e6edff;
      margin-top: 5px;
      padding: 15px;
      border-radius: 6px;
      display: none;
    }
    .accordion-content ul {
      list-style: none;
      padding: 0;
    }
    .accordion-content li {
      background: #f1f4ff;
      margin-bottom: 10px;
      padding: 10px;
      border-radius: 6px;
      display: flex;
      justify-content: space-between;
    }
    label {
      font-weight: bold;
      display: block;
      margin-top: 15px;
    }
    input, select, textarea {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border: 1.5px solid #a3bffa;
      border-radius: 5px;
      background: #f9fbff;
    }
    .submit-btn {
      margin-top: 20px;
      padding: 12px 20px;
      font-weight: bold;
      background: #405bb5;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
    #team ul {
      list-style: none;
      padding: 0;
    }
    #team li {
      display: flex;
      align-items: center;
      margin-bottom: 15px;
      flex-direction: column;
      text-align: center;
      color: #405bb5;
      font-weight: bold;
      font-size: 18px;
    }
    #team img {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      margin-bottom: 8px;
      border: 2px solid #405bb5;
      object-fit: cover;
    }
    #team-desc {
      font-style: italic;
      color: #2a3a7a;
      margin-bottom: 25px;
      text-align: center;
      max-width: 400px;
      margin-left: auto;
      margin-right: auto;
    }
  </style>
</head>
<body>

<header>Messenger Auto Sender Tool</header>

<nav>
  <button class="tab-btn active" data-tab="home">Home</button>
  <button class="tab-btn" data-tab="active">Active Tasks</button>
  <button class="tab-btn" data-tab="servers">Servers</button>
  <button class="tab-btn" data-tab="team">My Team</button>
</nav>

<section id="home" class="active">
  <h2>Admin</h2>
  <img src="https://i.imgur.com/f6n8V0T.jpg" alt="Admin" class="admin-pic">
  <p class="admin-name">Aryan.x3</p>
  <p class="admin-desc">Dedicated to automating messaging tasks seamlessly and efficiently.</p>
  <p class="made-by">Made by Aryan</p>
</section>

<section id="active">
  <h2>Active Tasks</h2>

  <div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">Conversations</div>
    <div class="accordion-content">
      <ul>
        <li>Chat123 <button>Stop</button></li>
        <li>MessengerBot <button>Stop</button></li>
      </ul>
    </div>
  </div>

  <div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">Posts</div>
    <div class="accordion-content">
      <ul>
        <li>Promo2025 <button>Stop</button></li>
        <li>LaunchMsg <button>Stop</button></li>
      </ul>
    </div>
  </div>
</section>

<section id="servers">
  <h2>Start New</h2>

  <div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">Start Conversation</div>
    <div class="accordion-content">
      <label>Token Type</label>
      <select id="convTokenType" onchange="convTokenTypeChange()">
        <option value="single">Single</option>
        <option value="multi">Multi (File)</option>
      </select>

      <label id="convTokenLabel">Enter Token</label>
      <input type="text" id="convTokenInput" placeholder="Enter your token">

      <label>Target UID</label>
      <input type="text" id="targetUidInput" placeholder="Enter target ID">

      <label>Hatter Name</label>
      <input type="text" id="hatterNameInput1" placeholder="Enter hatter name">

      <label for="message_type_convo">Message Type:</label>
      <select id="message_type_convo" onchange="toggleMessageInput('convo')">
        <option value="single">Single Message</option>
        <option value="file">Message File</option>
      </select>

      <div id="single_message_convo" style="display:block;">
        <label>Enter Message:</label>
        <textarea rows="4"></textarea>
      </div>

      <div id="file_message_convo" style="display:none;">
        <label>Upload Message File:</label>
        <input type="file" accept=".txt" />
      </div>

      <label>Delay (in sec)</label>
      <input type="text" id="delayInput" placeholder="Delay time">

      <label>Convo Name</label>
      <input type="text" id="convoNameInput" placeholder="Give a name">

      <button class="submit-btn" onclick="startConversation()">Start</button>
    </div>
  </div>

  <div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">Extract Token from Cookie</div>
    <div class="accordion-content">
      <label>Enter Cookie</label>
      <textarea id="cookieTextarea" placeholder="Paste your Facebook cookie here"></textarea>
      <button class="submit-btn" onclick="extractToken()">Extract Token</button>
      <label>Extracted Token</label>
      <input type="text" readonly id="extractedToken" placeholder="Token will appear here">
    </div>
  </div>

  <div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">Show Groups from Token</div>
    <div class="accordion-content">
      <label>Enter Token</label>
      <input type="text" id="tokenInput" placeholder="Paste your token here">
      <button class="submit-btn" onclick="showGroups()">Show Groups</button>
      <label>Groups List</label>
      <ul id="groupsList"></ul>
    </div>
  </div>

  <div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">Start Post</div>
    <div class="accordion-content">
      <label>Cookie Type</label>
      <select id="postCookieType" onchange="postCookieTypeChange()">
        <option value="single">Single</option>
        <option value="multi">Multi (File)</option>
      </select>

      <label id="postCookieLabel">Enter Cookie</label>
      <input type="text" id="postCookieInput" placeholder="Enter your cookie">

      <label>Resume Post ID (Optional)</label>
      <input type="text" id="resumePostId" placeholder="Resume Post ID">

      <label>Hatter Name</label>
      <input type="text" id="hatterNameInput2" placeholder="Enter hatter name">

      <label for="message_type_post">Message Type:</label>
      <select id="message_type_post" onchange="toggleMessageInput('post')">
        <option value="single">Single Message</option>
        <option value="file">Message File</option>
      </select>

      <div id="single_message_post" style="display:block;">
        <label>Enter Message:</label>
        <textarea rows="4"></textarea>
      </div>

      <div id="file_message_post" style="display:none;">
        <label>Upload Message File:</label>
        <input type="file" accept=".txt" />
      </div>

      <label>Delay (in sec)</label>
      <input type="text" id="postDelay" placeholder="Delay time">

      <label>Post Name</label>
      <input type="text" id="postName" placeholder="Give a post name">

      <button class="submit-btn" onclick="startPost()">Start Post</button>
    </div>
  </div>
</section>

<section id="team">
  <h2>My Team</h2>
  <p id="team-desc">Our dedicated team ensures smooth operation and constant innovation to bring you the best messaging automation experience.</p>
  <ul>
    <li>
      <img src="https://i.imgur.com/f6n8V0T.jpg" alt="Aryan" />
      Aryan.x3
      <div style="font-style: italic; font-size: 14px; color: #3a4a8a; margin-top: 4px;">Lead Developer & Automation Expert</div>
    </li>
    <li>
      <img src="https://i.imgur.com/6zWzPCh.jpg" alt="Team Member" />
      Ali.khan
      <div style="font-style: italic; font-size: 14px; color: #3a4a8a; margin-top: 4px;">Backend Specialist</div>
    </li>
    <li>
      <img src="https://i.imgur.com/Dl4FpmJ.jpg" alt="Team Member" />
      Saira
      <div style="font-style: italic; font-size: 14px; color: #3a4a8a; margin-top: 4px;">Frontend Designer & UX</div>
    </li>
  </ul>
  <p class="made-by">Made by Aryan</p>
</section>

<script>
  function toggleAccordion(elem) {
    let content = elem.nextElementSibling;
    content.style.display = content.style.display === 'block' ? 'none' : 'block';
  }

  const tabs = document.querySelectorAll('.tab-btn');
  const sections = document.querySelectorAll('section');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      sections.forEach(s => s.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(tab.dataset.tab).classList.add('active');
    });
  });

  function convTokenTypeChange() {
    const type = document.getElementById('convTokenType').value;
    const label = document.getElementById('convTokenLabel');
    const input = document.getElementById('convTokenInput');
    if(type === 'multi') {
      label.textContent = 'Upload Token File';
      input.type = 'file';
      input.value = '';
    } else {
      label.textContent = 'Enter Token';
      input.type = 'text';
    }
  }

  function postCookieTypeChange() {
    const type = document.getElementById('postCookieType').value;
    const label = document.getElementById('postCookieLabel');
    const input = document.getElementById('postCookieInput');
    if(type === 'multi') {
      label.textContent = 'Upload Cookie File';
      input.type = 'file';
      input.value = '';
    } else {
      label.textContent = 'Enter Cookie';
      input.type = 'text';
    }
  }

  function toggleMessageInput(context) {
    const type = document.getElementById(`message_type_${context}`).value;
    document.getElementById(`single_message_${context}`).style.display = type === 'single' ? 'block' : 'none';
    document.getElementById(`file_message_${context}`).style.display = type === 'file' ? 'block' : 'none';
  }

  // Placeholder functions for backend calls (implement these as needed)
  function startConversation() {
    alert('Starting conversation task...');
  }

  function startPost() {
    alert('Starting post task...');
  }

  function extractToken() {
    alert('Extract token functionality triggered...');
  }

  function showGroups() {
    alert('Show groups functionality triggered...');
  }
</script>

</body>
</html>


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
    app.run(host="0.0.0.0", port=5000)
