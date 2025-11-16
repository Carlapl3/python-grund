from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage for tasks
tasks = [
    {"id": 1, "title": "Learn Python", "completed": False},
    {"id": 2, "title": "Build a web app", "completed": False},
    {"id": 3, "title": "Deploy to production", "completed": False}
]

# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Todo App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            padding: 30px;
            margin-top: 50px;
        }

        h1 {
            color: #667eea;
            margin-bottom: 10px;
            text-align: center;
        }

        .time {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .add-task {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }

        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }

        button:hover {
            background: #5568d3;
        }

        .tasks {
            list-style: none;
        }

        .task-item {
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }

        .task-item:hover {
            transform: translateX(5px);
        }

        .task-item.completed {
            opacity: 0.6;
        }

        .task-item.completed .task-title {
            text-decoration: line-through;
            color: #999;
        }

        .task-checkbox {
            width: 20px;
            height: 20px;
            margin-right: 15px;
            cursor: pointer;
        }

        .task-title {
            flex: 1;
            font-size: 16px;
        }

        .delete-btn {
            background: #e74c3c;
            padding: 6px 12px;
            font-size: 14px;
        }

        .delete-btn:hover {
            background: #c0392b;
        }

        .stats {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
        }

        .empty-state {
            text-align: center;
            color: #999;
            padding: 40px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Flask Todo App</h1>
        <div class="time" id="currentTime"></div>

        <div class="add-task">
            <input type="text" id="taskInput" placeholder="Add a new task..." onkeypress="handleKeyPress(event)">
            <button onclick="addTask()">Add Task</button>
        </div>

        <ul class="tasks" id="taskList"></ul>

        <div class="stats" id="stats"></div>
    </div>

    <script>
        // Update current time
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleString();
        }
        updateTime();
        setInterval(updateTime, 1000);

        // Load tasks on page load
        loadTasks();

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                addTask();
            }
        }

        async function loadTasks() {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            renderTasks(tasks);
        }

        function renderTasks(tasks) {
            const taskList = document.getElementById('taskList');

            if (tasks.length === 0) {
                taskList.innerHTML = '<div class="empty-state">No tasks yet. Add one above!</div>';
                updateStats(0, 0);
                return;
            }

            taskList.innerHTML = tasks.map(task => `
                <li class="task-item ${task.completed ? 'completed' : ''}">
                    <input type="checkbox" class="task-checkbox"
                           ${task.completed ? 'checked' : ''}
                           onchange="toggleTask(${task.id})">
                    <span class="task-title">${task.title}</span>
                    <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
                </li>
            `).join('');

            const completed = tasks.filter(t => t.completed).length;
            updateStats(tasks.length, completed);
        }

        function updateStats(total, completed) {
            const stats = document.getElementById('stats');
            stats.textContent = `Total: ${total} | Completed: ${completed} | Remaining: ${total - completed}`;
        }

        async function addTask() {
            const input = document.getElementById('taskInput');
            const title = input.value.trim();

            if (!title) {
                alert('Please enter a task!');
                return;
            }

            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title})
            });

            if (response.ok) {
                input.value = '';
                loadTasks();
            }
        }

        async function toggleTask(id) {
            await fetch(`/api/tasks/${id}/toggle`, {method: 'POST'});
            loadTasks();
        }

        async function deleteTask(id) {
            await fetch(`/api/tasks/${id}`, {method: 'DELETE'});
            loadTasks();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    new_task = {
        "id": max([t["id"] for t in tasks], default=0) + 1,
        "title": data.get("title", ""),
        "completed": False
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task:
        task["completed"] = not task["completed"]
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return '', 204

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Flask Todo App Starting!")
    print("="*50)
    print("📍 Open your browser and go to: http://localhost:5001")
    print("⌨️  Press CTRL+C to stop the server")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
