from flask import Flask,jsonify,request
from database import create_table,get_connection

app = Flask(__name__)
create_table()


@app.route("/")
def home():
    return "Task API is running"

@app.route("/tasks",methods=["GET"])
def get_tasks():
    connection=get_connection()
    tasks=connection.execute(
        "select * from tasks"
    ).fetchall()

    connection.close()
    return jsonify([dict(task) for task in tasks])


from flask import Flask, jsonify, request
from database import create_table, get_connection


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "No valid JSON received"}), 400

    title = data.get("title")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    connection = get_connection()

    cursor = connection.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,)
    )

    connection.commit()

    task_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "id": task_id,
        "title": title,
        "completed": False
    }), 201

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):

    connection = get_connection()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    completed = data.get("completed")

    if title is None and completed is None:
        return jsonify({"error": "No data to update"}), 400

    connection = get_connection()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        connection.close()
        return jsonify({"error": "Task not found"}), 404

    if title is not None and completed is not None:
        connection.execute(
            "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
            (title, int(completed), task_id)
        )
    elif title is not None:
        connection.execute(
            "UPDATE tasks SET title = ? WHERE id = ?",
            (title, task_id)
        )
    else:
        connection.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (int(completed), task_id)
        )

    connection.commit()

    updated_task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return jsonify(dict(updated_task)), 200

@app.route("/tasks/<int:task_id>",methods=["DELETE"])
def delete_task(task_id):
    connection=get_connection()
    task=connection.execute(
        "select * from tasks where id=?",
        (task_id,)
    ).fetchone()

    if task is None:
        return jsonify({"error":"task not found"}),404

    connection.execute(
        "delete from tasks where id=?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return jsonify(
        {"message":"connection deleted succesfully"}
    )


if __name__ == "__main__":
    app.run(debug=True)