// web_client/script.js

const API_GATEWAY_URL = "http://localhost:8000"; // Address of your FastAPI Gateway

const tasksOutput = document.getElementById('tasksOutput');
const usersOutput = document.getElementById('usersOutput');
const appLogs = document.getElementById('appLogs');

function log(message, type = 'info') {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    appLogs.prepend(logEntry); // Add new logs to the top
    // Optionally remove old logs if too many
    if (appLogs.children.length > 50) {
        appLogs.removeChild(appLogs.lastChild);
    }
}

async function handleResponse(response, outputElement) {
    let data;
    try {
        data = await response.json();
    } catch (e) {
        log(`Error parsing response: ${e.message}`, 'error');
        outputElement.innerHTML = `<pre>Error: ${response.status} ${response.statusText}\nCould not parse response.</pre>`;
        return;
    }

    if (response.ok) {
        log(`Request successful: ${response.status}`, 'success');
        outputElement.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } else {
        log(`Request failed: ${response.status} - ${data.detail || response.statusText}`, 'error');
        outputElement.innerHTML = `<pre>Error: ${response.status} - ${data.detail || response.statusText}\n${JSON.stringify(data, null, 2)}</pre>`;
    }
}

// --- Task Operations (gRPC via Gateway) ---

async function createTask() {
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const createdBy = document.getElementById('taskCreatedBy').value;

    if (!title || !description || !createdBy) {
        log("Please fill all task fields (title, description, created by).", 'error');
        return;
    }

    log(`Creating task: ${title}...`, 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, created_by: createdBy })
        });
        await handleResponse(response, tasksOutput);
    } catch (error) {
        log(`Network error creating task: ${error.message}`, 'error');
    }
}

async function listTasks() {
    log("Listing tasks...", 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/tasks`);
        await handleResponse(response, tasksOutput);
    } catch (error) {
        log(`Network error listing tasks: ${error.message}`, 'error');
    }
}

async function updateTask() {
    const id = document.getElementById('updateTaskId').value;
    const title = document.getElementById('updateTaskTitle').value;
    const description = document.getElementById('updateTaskDescription').value;
    const status = document.getElementById('updateTaskStatus').value;

    if (!id) {
        log("Please enter Task ID to update.", 'error');
        return;
    }

    const updateData = {};
    if (title) updateData.title = title;
    if (description) updateData.description = description;
    if (status) updateData.status = status;

    if (Object.keys(updateData).length === 0) {
        log("No fields provided for update.", 'info');
        return;
    }

    log(`Updating task ID ${id}...`, 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });
        await handleResponse(response, tasksOutput);
    } catch (error) {
        log(`Network error updating task: ${error.message}`, 'error');
    }
}

async function deleteTask() {
    const id = document.getElementById('deleteTaskId').value;

    if (!id) {
        log("Please enter Task ID to delete.", 'error');
        return;
    }

    log(`Deleting task ID ${id}...`, 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/tasks/${id}`, {
            method: 'DELETE'
        });
        // DELETE 204 No Content, so no JSON to parse
        if (response.status === 204) {
            log(`Task ID ${id} deleted successfully (204 No Content).`, 'success');
            tasksOutput.innerHTML = `<pre>Task ID ${id} deleted successfully.</pre>`;
        } else {
            await handleResponse(response, tasksOutput); // Handle other status codes
        }
    } catch (error) {
        log(`Network error deleting task: ${error.message}`, 'error');
    }
}

async function getTaskById() {
    const id = document.getElementById('deleteTaskId').value; // Reusing deleteTaskId field for simplicity

    if (!id) {
        log("Please enter Task ID to search.", 'error');
        return;
    }

    log(`Searching task ID ${id}...`, 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/tasks/${id}`);
        await handleResponse(response, tasksOutput);
    } catch (error) {
        log(`Network error searching task: ${error.message}`, 'error');
    }
}

// --- User Operations (SOAP via Gateway) ---

async function createUser() {
    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;

    if (!name || !email) {
        log("Please fill all user fields (name, email).", 'error');
        return;
    }

    log(`Creating user: ${name}...`, 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });
        await handleResponse(response, usersOutput);
    } catch (error) {
        log(`Network error creating user: ${error.message}`, 'error');
    }
}

async function listUsers() {
    log("Listing users...", 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/users`);
        await handleResponse(response, usersOutput);
    } catch (error) {
        log(`Network error listing users: ${error.message}`, 'error');
    }
}

async function getUserById() {
    const id = document.getElementById('userName').value; // Reusing userName field for simplicity

    if (!id) {
        log("Please enter User ID to search.", 'error');
        return;
    }

    log(`Searching user ID ${id}...`, 'info');
    try {
        const response = await fetch(`${API_GATEWAY_URL}/users/${id}`);
        await handleResponse(response, usersOutput);
    } catch (error) {
        log(`Network error searching user: ${error.message}`, 'error');
    }
}

// Initial log
document.addEventListener('DOMContentLoaded', () => {
    log("Application loaded. Ensure all backend services are running.", 'info');
});

