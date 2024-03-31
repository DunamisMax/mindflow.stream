from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Note
from app.forms import CommentForm
from flask_wtf.csrf import CSRFError

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = CommentForm()
    if form.validate_on_submit():
        new_note = Note(text=form.comment.data)
        db.session.add(new_note)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.index'))

    # Implementing simple limit without pagination controls for the homepage
    notes = Note.query.order_by(Note.created_at.desc()).limit(100).all()
    return render_template('index.html', form=form, notes=notes)

@main.route('/comments', methods=['GET'])
def get_comments():
    page = request.args.get('page', 1, type=int)  # Default to first page
    per_page = 100  # Number of items per page
    pagination = Note.query.order_by(Note.created_at.desc()).paginate(page, per_page=per_page, error_out=False)
    notes = pagination.items
    total_pages = pagination.pages
    notes_data = [{'id': note.id, 'text': note.text, 'created_at': note.created_at.isoformat()} for note in notes]
    return jsonify({'notes': notes_data, 'total_pages': total_pages})

@main.route('/comments', methods=['POST'])
def post_comment():
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid request. Please provide the "text" field.'}), 400

    new_note = Note(text=data['text'])
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully!', 'id': new_note.id}), 201
