from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, request, current_app
from sqlalchemy.exc import SQLAlchemyError

# Adjusted imports to match the application factory pattern
from . import db, limiter
from .models import Note
from .forms import CommentForm

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def index():
    form = CommentForm()
    if form.validate_on_submit():
        note = Note(text=form.comment.data)
        try:
            db.session.add(note)
            db.session.commit()
            flash('Your note was added successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while adding your note. Please try again.', 'error')
            current_app.logger.error(f'Error adding a new note: {e}')
        return redirect(url_for('views.index'))

    # Adjusted call to paginate()
    page = request.args.get('page', 1, type=int)
    per_page = 100
    pagination = Note.query.order_by(Note.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    notes = pagination.items
    return render_template('index.html', form=form, notes=notes, pagination=pagination)

@views.route('/comments', methods=['GET'])
def get_comments():
    page = request.args.get('page', 1, type=int)  # Default to the first page
    per_page = 100  # Specify the number of items per page

    # Correctly call the paginate method with keyword arguments
    pagination = Note.query.order_by(Note.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    notes = pagination.items
    total_pages = pagination.pages

    # Prepare the notes data for JSON response
    notes_data = [{'id': note.id, 'text': note.text, 'created_at': note.created_at.replace(tzinfo=timezone.utc).isoformat() if note.created_at.tzinfo is None else note.created_at.isoformat()} for note in notes]
    return jsonify({
        'notes': notes_data,
        'total_pages': total_pages,
        'current_page': page
    })

@views.route('/comments', methods=['POST'])
@limiter.limit("1 per 5 seconds")
def submit_comment():
    # Logic to submit a comment
    data = request.get_json() or {}
    if 'text' not in data:
        return jsonify({'error': 'Comment text is required.'}), 400

    note = Note(text=data['text'])
    try:
        db.session.add(note)
        db.session.commit()
        return jsonify({'message': 'Comment added successfully!', 'id': note.id, 'created_at': note.created_at.isoformat()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding comment: {e}')
        return jsonify({'error': 'An error occurred while adding the comment.'}), 500