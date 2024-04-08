import os
import uuid
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
NOTES_FOLDER = 'notes'

def create_notes_folder():
    if not os.path.exists(NOTES_FOLDER):
        os.makedirs(NOTES_FOLDER)

create_notes_folder()

def save_note_as_md(title, content):
    filename = str(uuid.uuid4()) + '.md'
    filepath = os.path.join(NOTES_FOLDER, filename)
    with open(filepath, 'w',encoding='utf-8') as file:
        file.write(f"# {title}\n")
        file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write(content)

def update_note_as_md(title, content, filename):
    filepath = os.path.join(NOTES_FOLDER, filename)
    with open(filepath, 'w' ,encoding='utf-8') as file:
        file.write(f"# {title}\n")
        file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write(content)

def list_notes():
    notes = []
    for filename in os.listdir(NOTES_FOLDER):
        with open(os.path.join(NOTES_FOLDER, filename), 'r',encoding='utf-8') as file:
            title = file.readline().strip('#').strip()
            timestamp = file.readline().strip('Date:').strip()
            content = file.read()
            notes.append({'title': title, 'timestamp': timestamp, 'content': content,'filename':filename})
    return notes

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/save', methods=['POST'])
def save():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    filename = data.get('filename')  # Get the filename from the request data
    if title and content:
        try:
            if filename:  # If a filename is provided, update the existing note
                update_note_as_md(title, content, filename)
            else:  # Otherwise, save a new note
                save_note_as_md(title, content)
            return 'Note saved successfully!', 200
        except Exception as e:
            return jsonify({'error': f'Failed to save note: {str(e)}'}), 500  # Return detailed error message
    else:
        return jsonify({'error': 'Title and content are required.'}), 400

@app.route('/list')
def list_notes_route():
    try:
        notes = list_notes()
        return jsonify({'notes': notes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/note/<filename>')
def get_note_by_filename(filename):
    try:
        with open(os.path.join(NOTES_FOLDER, filename), 'r',encoding='utf-8') as file:
            title = file.readline().strip('#').strip()
            timestamp = file.readline().strip('Date:').strip()
            content = file.read()
            return jsonify({'title': title, 'timestamp': timestamp, 'content': content, 'filename': filename}), 200
    except FileNotFoundError:
        return jsonify({'error': 'Note not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
