from flask import Blueprint, request, jsonify
from models.notes import Note
from db import db

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

@notes_bp.route('/', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    if not notes:
        return jsonify({'message': 'No notes found'}), 404
    return jsonify([{'id': n.id, 'title': n.title, 'content': n.content} for n in notes])

@notes_bp.route('/', methods=['POST'])
def add_notes():
    data = request.get_json()
    new_note = Note(title=data['title'], content=data['content'])
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'message': 'Note added'}), 201

@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'message':'No note'}), 404
    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content
    })

@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    note.title = data['title']
    note.content = data['content']
    db.session.commit()
    return jsonify({'message': 'Note updated'})

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted'})
