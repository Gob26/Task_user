import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(ac: AsyncClient):
    response = await ac.post("/users/", json={"name": "John", "surname": "Doe"})
    print(f"Create User Response: {response.status_code} - {response.text}")  # Отладочный вывод
    assert response.status_code == 200
    data = response.json()
    assert "id" in data  # Проверяем, что ID присутствует
    assert data["name"] == "John"
    assert data["surname"] == "Doe"



@pytest.mark.asyncio
async def test_create_task(ac: AsyncClient):
    # Сначала создаем пользователя
    user_response = await ac.post("/users/", json={"name": "Jane", "surname": "Smith"})
    print(f"Create User Response: {user_response.status_code} - {user_response.text}")  # Отладочный вывод
    assert user_response.status_code == 200
    user_data = user_response.json()
    user_id = user_data.get("id")
    print(f"User ID: {user_id}")  # Отладочный вывод

    assert user_id is not None, "User ID is None"

    # Затем создаем задачу для этого пользователя
    task_response = await ac.post("/tasks/", json={"title": "Test Task", "description": "This is a test task"},
                                  params={"user_id": user_id})
    print(f"Create Task Response: {task_response.status_code} - {task_response.text}")  # Отладочный вывод
    assert task_response.status_code == 200
    task_data = task_response.json()
    assert "id" in task_data  # Проверяем, что ID задачи присутствует
    assert "title" in task_data
    assert "description" in task_data
    assert "user_name" in task_data
    assert "user_surname" in task_data
    assert task_data["title"] == "Test Task"
    assert task_data["description"] == "This is a test task"
    assert task_data["user_name"] == "Jane"
    assert task_data["user_surname"] == "Smith"


@pytest.mark.asyncio
async def test_read_tasks(ac: AsyncClient):
    # Создаем пользователя и задачи
    user_response = await ac.post("/users/", json={"name": "Alice", "surname": "Johnson"})
    print(f"Create User Response: {user_response.status_code} - {user_response.text}")  # Отладочный вывод
    assert user_response.status_code == 200
    user_data = user_response.json()
    user_id = user_data.get("id")
    print(f"User ID: {user_id}")  # Отладочный вывод

    assert user_id is not None, "User ID is None"

    # Создаем задачи для пользователя
    await ac.post("/tasks/", json={"title": "Task 1", "description": "First task"}, params={"user_id": user_id})
    await ac.post("/tasks/", json={"title": "Task 2", "description": "Second task"}, params={"user_id": user_id})

    # Читаем задачи пользователя
    tasks_response = await ac.get(f"/tasks/?user_id={user_id}")
    print(f"Read Tasks Response: {tasks_response.status_code} - {tasks_response.text}")  # Отладочный вывод
    assert tasks_response.status_code == 200
    tasks_data = tasks_response.json()

    assert isinstance(tasks_data, list), "Tasks data should be a list"
    assert len(tasks_data) == 2, "Expected 2 tasks"

    task_titles = [task["title"] for task in tasks_data]
    assert "Task 1" in task_titles, "Task 1 is missing"
    assert "Task 2" in task_titles, "Task 2 is missing"

    # Дополнительная проверка для каждой задачи
    for task in tasks_data:
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "user_name" in task
        assert "user_surname" in task
        assert "created_at" in task
        assert "updated_at" in task
        assert isinstance(task["created_at"], str)
        assert isinstance(task["updated_at"], str)
