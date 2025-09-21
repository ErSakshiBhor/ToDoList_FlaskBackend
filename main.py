from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId

# --- Flask App and MongoDB Configuration ---
app = Flask(__name__)
# Configure MongoDB connection using the URI you provided
app.config["MONGO_URI"] = "mongodb+srv://to_list:Todo#123@todo.baqwe9c.mongodb.net/?retryWrites=true&w=majority&appName=ToDo"
mongo = PyMongo(app, origins="https://to-do-list-react-frontend.vercel.app/")

# Enable CORS to allow the React frontend to make requests
CORS(app)

# --- API Endpoints ---

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Fetches all tasks from the MongoDB database.
    Converts the MongoDB ObjectId to a string for JSON serialization.
    """
    tasks = list(mongo.db.tasks.find({}))
    for task in tasks:
        task['_id'] = str(task['_id'])
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    """
    Adds a new task to the database.
    The task data (title) is expected in the request body.
    """
    data = request.json
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    # Insert the new task with a default completed status of False
    new_task = {
        'title': data['title'],
        'completed': False
    }
    result = mongo.db.tasks.insert_one(new_task)
    
    # Return the newly created task with its unique ID
    new_task['_id'] = str(result.inserted_id)
    return jsonify(new_task), 201

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    """
    Deletes a task by its ID.
    Uses ObjectId to query the database.
    """
    try:
        result = mongo.db.tasks.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception:
        return jsonify({'error': 'Invalid ID format'}), 400

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    """
    Updates the 'completed' status or the 'title' of a task by its ID.
    The new data is sent in the request body.
    """
    try:
        data = request.json
        update_fields = {}
        if 'completed' in data:
            update_fields['completed'] = data['completed']
        if 'title' in data:
            update_fields['title'] = data['title']

        if not update_fields:
            return jsonify({'error': 'No fields to update provided'}), 400
        
        # Update the task with the new data
        result = mongo.db.tasks.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_fields}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'message': 'Task updated successfully'}), 200
    except Exception:
        return jsonify({'error': 'Invalid ID format'}), 400

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True)
