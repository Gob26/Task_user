document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname === "/tasks") {
        const userId = prompt("Введите ваш ID пользователя:");
        if (userId) {
            loadTasks(userId);
        }
    }

    const createTaskForm = document.getElementById("create-task-form");
    if (createTaskForm) {
        createTaskForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const title = document.getElementById("title").value;
            const description = document.getElementById("description").value;
            const userId = document.getElementById("user_id").value;
            if (title && description && userId) {
                await createTask(title, description, userId);
            }
        });
    }
});

async function loadTasks(userId) {
    const response = await fetch(`/tasks/?user_id=${userId}`);
    const tasks = await response.json();
    const tasksBody = document.getElementById("tasks-body");

    tasksBody.innerHTML = tasks.map(task => `
        <tr>
            <td>${task.id}</td>
            <td>${task.title}</td>
            <td>${task.description}</td>
            <td>${task.user_name}</td>
            <td>${task.user_surname}</td>
            <td>${new Date(task.created_at).toLocaleString()}</td>
            <td>${new Date(task.updated_at).toLocaleString()}</td>
            <td><button onclick="deleteTask(${task.id})">Удалить</button></td>
        </tr>
    `).join("");
}

async function createTask(title, description, userId) {
    const response = await fetch("/tasks/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ title, description, user_id: userId })
    });
    if (response.ok) {
        loadTasks(userId);
    } else {
        alert("Ошибка создания задачи");
    }
}

async function deleteTask(taskId) {
    const response = await fetch(`/tasks/${taskId}`, {
        method: "DELETE"
    });
    if (response.ok) {
        const userId = prompt("Введите ваш ID пользователя:");
        if (userId) {
            loadTasks(userId);
        }
    } else {
        alert("Ошибка удаления задачи");
    }
}
