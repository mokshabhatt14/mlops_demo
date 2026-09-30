const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const listHint = document.querySelector("#list-hint");
const responseStatus = document.querySelector("#response-status");
const responseJson = document.querySelector("#response-json");
const requestUrl = document.querySelector("#request-url");
const connectionLabel = document.querySelector("#connection-label");
const addForm = document.querySelector("#add-form");
const taskInput = document.querySelector("#task-input");
let tasks = [];
let activeFilter = "all";

async function callApi(method, path, payload) {
    requestUrl.textContent = `${method} ${path}`;
    responseStatus.textContent = "SENDING";
    responseStatus.className = "response-status";

    try {
        const options = { method, headers: {} };
        if (payload) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(payload);
        }

        const response = await fetch(path, options);
        const body = await response.json();
        responseStatus.textContent = `${response.status} ${response.statusText}`;
        responseStatus.className = `response-status ${response.ok ? "is-success" : "is-error"}`;
        responseJson.textContent = JSON.stringify(body, null, 2);

        if (!response.ok) {
            const detail = Array.isArray(body.detail) ? body.detail.map((issue) => issue.msg).join(", ") : body.detail;
            throw new Error(detail || `Request failed (${response.status})`);
        }
        connectionLabel.textContent = "API connected";
        return body;
    } catch (error) {
        if (responseStatus.textContent === "SENDING") {
            responseStatus.textContent = "OFFLINE";
            responseStatus.className = "response-status is-error";
            responseJson.textContent = JSON.stringify({ error: error.message }, null, 2);
            connectionLabel.textContent = "API unavailable";
        }
        throw error;
    }
}

function visibleTasks() {
    if (activeFilter === "open") return tasks.filter((task) => !task.completed);
    if (activeFilter === "done") return tasks.filter((task) => task.completed);
    return tasks;
}

function renderTasks() {
    taskCount.textContent = tasks.length;
    const shown = visibleTasks();
    taskList.replaceChildren();

    if (shown.length === 0) {
        const empty = document.createElement("li");
        empty.className = "empty-state";
        const title = document.createElement("strong");
        const detail = document.createElement("span");
        title.textContent = tasks.length === 0 ? "No tasks yet." : "Nothing to show here.";
        detail.textContent = tasks.length === 0 ? "Write a task above and press Save task." : "Try another button or write a task.";
        empty.append(title, detail);
        taskList.append(empty);
        listHint.textContent = "0 shown";
        return;
    }

    for (const task of shown) {
        const row = document.createElement("li");
        row.className = `task-row${task.completed ? " is-complete" : ""}`;

        const checkbox = document.createElement("input");
        checkbox.className = "task-check";
        checkbox.type = "checkbox";
        checkbox.checked = task.completed;
        checkbox.setAttribute("aria-label", `${task.completed ? "Reopen" : "Complete"}: ${task.title}`);
        checkbox.addEventListener("change", async () => {
            checkbox.disabled = true;
            try {
                const updated = await callApi("PUT", `/api/tasks/${task.id}`, {
                    title: task.title,
                    completed: checkbox.checked,
                });
                tasks = tasks.map((item) => item.id === updated.id ? updated : item);
                renderTasks();
            } catch (error) {
                checkbox.checked = !checkbox.checked;
                checkbox.disabled = false;
                listHint.textContent = error.message;
            }
        });

        const copy = document.createElement("span");
        copy.className = "task-copy";
        const title = document.createElement("span");
        title.className = "task-title";
        title.textContent = task.title;
        const meta = document.createElement("span");
        meta.className = "task-meta";
        meta.textContent = task.completed ? "Finished" : "Not done yet";
        copy.append(title, meta);

        const number = document.createElement("span");
        number.className = "task-number";
        number.textContent = `#${task.id}`;
        row.append(checkbox, copy, number);
        taskList.append(row);
    }

    const openCount = tasks.filter((task) => !task.completed).length;
    listHint.textContent = `${shown.length} shown · ${openCount} open`;
}

async function loadTasks() {
    taskList.setAttribute("aria-busy", "true");
    listHint.textContent = "Loading tasks...";
    try {
        tasks = await callApi("GET", "/api/tasks");
        renderTasks();
    } catch (error) {
        listHint.textContent = "Could not load tasks";
        taskList.replaceChildren();
    } finally {
        taskList.setAttribute("aria-busy", "false");
    }
}

addForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = taskInput.value.trim();
    if (!title) return;

    const id = tasks.reduce((largest, task) => Math.max(largest, task.id), 0) + 1;
    const submitButton = addForm.querySelector("button[type='submit']");
    submitButton.disabled = true;
    try {
        const saved = await callApi("PUT", `/api/tasks/${id}`, { title, completed: false });
        tasks = [...tasks, saved].sort((first, second) => first.id - second.id);
        activeFilter = "all";
        document.querySelectorAll(".filter-button").forEach((button) => {
            const selected = button.dataset.filter === activeFilter;
            button.classList.toggle("is-selected", selected);
            button.setAttribute("aria-pressed", String(selected));
        });
        taskInput.value = "";
        renderTasks();
        taskInput.focus();
    } catch (error) {
        listHint.textContent = error.message;
    } finally {
        submitButton.disabled = false;
    }
});

document.querySelector("#refresh-button").addEventListener("click", loadTasks);

document.querySelectorAll(".filter-button").forEach((button) => {
    button.addEventListener("click", () => {
        activeFilter = button.dataset.filter;
        document.querySelectorAll(".filter-button").forEach((filterButton) => {
            const selected = filterButton === button;
            filterButton.classList.toggle("is-selected", selected);
            filterButton.setAttribute("aria-pressed", String(selected));
        });
        renderTasks();
    });
});

loadTasks();