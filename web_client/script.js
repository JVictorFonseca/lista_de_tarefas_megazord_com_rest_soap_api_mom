// web_client/script.js

const API_GATEWAY_URL = "http://localhost:8000"; // Address of your FastAPI Gateway

const tasksOutput = document.getElementById('tasksOutput');
const usersOutput = document.getElementById('usersOutput');
const appLogs = document.getElementById('appLogs');
const tasksListContainer = document.getElementById('tasksListContainer');
const usersListContainer = document.getElementById('usersOutput'); // Usando a mesma div para usuários

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

// NEW: Function to toggle sections based on navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Deactivate all navigation buttons
    document.querySelectorAll('.nav-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show the selected section and activate its button
    document.getElementById(`${sectionId}-section`).classList.add('active');
    document.querySelector(`.nav-button[onclick="showSection('${sectionId}')"]`).classList.add('active');
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

        // NEW: Check if the response is a list of tasks or users
        if (data.tasks && Array.isArray(data.tasks)) {
            renderTasksList(data.tasks);
            // After rendering the list, update the raw JSON output as well
            tasksOutput.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else if (data.users && Array.isArray(data.users)) {
            renderUsersList(data.users);
             usersOutput.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else if (data.task) {
            // Check if a single task was created/updated
            renderSingleTask(data.task);
             tasksOutput.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else if (data.user) {
             renderSingleUser(data.user);
             usersOutput.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
            outputElement.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
    } else {
        log(`Request failed: ${response.status} - ${data.detail || response.statusText}`, 'error');
        outputElement.innerHTML = `<pre>Error: ${response.status} - ${data.detail || response.statusText}\n${JSON.stringify(data, null, 2)}</pre>`;
    }
}

// NEW: Function to render a list of tasks visually
function renderTasksList(tasks) {
    tasksListContainer.innerHTML = ''; // Clear previous tasks

    if (tasks.length === 0) {
        tasksListContainer.innerHTML = '<p class="info-message">Nenhuma tarefa encontrada.</p>';
        return;
    }

    const taskListHtml = tasks.map(task => {
        const statusClass = task.status === 'concluída' ? 'status-completed' : (task.status === 'em progresso' ? 'status-in-progress' : 'status-pending');
        return `
            <div class="task-card">
                <div class="task-header">
                    <span class="task-id">#${task.id}</span>
                    <span class="task-status ${statusClass}">${task.status}</span>
                </div>
                <div class="task-body">
                    <h3 class="task-title">${task.title}</h3>
                    <p class="task-description">${task.description}</p>
                </div>
                <div class="task-footer">
                    <span class="task-created-by">Criado por: ${task.created_by}</span>
                    <div class="task-actions">
                        <button onclick="fillTaskFormForUpdate(${task.id}, '${task.title.replace(/'/g, "\\'")}', '${task.description.replace(/'/g, "\\'")}', '${task.status}')">Editar</button>
                        <button onclick="fillTaskFormForDelete(${task.id})">Excluir</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    tasksListContainer.innerHTML = taskListHtml;
}

// NEW: Function to render a single task visually
function renderSingleTask(task) {
    tasksListContainer.innerHTML = '';
    const statusClass = task.status === 'concluída' ? 'status-completed' : (task.status === 'em progresso' ? 'status-in-progress' : 'status-pending');
    tasksListContainer.innerHTML = `
        <div class="task-card">
            <div class="task-header">
                <span class="task-id">#${task.id}</span>
                <span class="task-status ${statusClass}">${task.status}</span>
            </div>
            <div class="task-body">
                <h3 class="task-title">${task.title}</h3>
                <p class="task-description">${task.description}</p>
            </div>
            <div class="task-footer">
                <span class="task-created-by">Criado por: ${task.created_by}</span>
                <div class="task-actions">
                    <button onclick="fillTaskFormForUpdate(${task.id}, '${task.title.replace(/'/g, "\\'")}', '${task.description.replace(/'/g, "\\'")}', '${task.status}')">Editar</button>
                    <button onclick="fillTaskFormForDelete(${task.id})">Excluir</button>
                </div>
            </div>
        </div>
    `;
}

// NEW: Function to render a list of users visually
function renderUsersList(users) {
    usersListContainer.innerHTML = ''; // Clear previous users

    if (users.length === 0) {
        usersListContainer.innerHTML = '<p class="info-message">Nenhum usuário encontrado.</p>';
        return;
    }

    const usersListHtml = users.map(user => {
        return `
            <div class="user-card">
                <div class="user-header">
                    <span class="user-id">ID: #${user.user_id}</span>
                </div>
                <div class="user-body">
                    <h3 class="user-name">${user.name}</h3>
                    <p class="user-email">Email: ${user.email}</p>
                </div>
            </div>
        `;
    }).join('');

    usersListContainer.innerHTML = usersListHtml;
}

// NEW: Function to render a single user visually
function renderSingleUser(user) {
    usersListContainer.innerHTML = '';
    usersListContainer.innerHTML = `
        <div class="user-card">
            <div class="user-header">
                <span class="user-id">ID: #${user.user_id}</span>
            </div>
            <div class="user-body">
                <h3 class="user-name">${user.name}</h3>
                <p class="user-email">Email: ${user.email}</p>
            </div>
        </div>
    `;
}

// NEW: Helper functions to fill the forms for quick updates/deletes
function fillTaskFormForUpdate(id, title, description, status) {
    document.getElementById('updateTaskId').value = id;
    document.getElementById('updateTaskTitle').value = title;
    document.getElementById('updateTaskDescription').value = description;
    document.getElementById('updateTaskStatus').value = status;
    log(`Formulário de atualização preenchido para a Tarefa #${id}.`, 'info');
}

function fillTaskFormForDelete(id) {
    document.getElementById('deleteTaskId').value = id;
    log(`ID #${id} adicionado ao campo de exclusão.`, 'info');
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
        listTasks(); // Refresh the list after creating a new task
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
        listTasks(); // Refresh the list after updating
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
            listTasks(); // Refresh the list after deleting
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
        listUsers(); // Refresh the list after creating a new user
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
    const id = document.getElementById('userId').value; // Usando o novo campo de busca

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

// NEW: Function to handle navigation and initial load
document.addEventListener('DOMContentLoaded', () => {
    log("Application loaded. Ensure all backend services are running.", 'info');
    showSection('tasks');
});
