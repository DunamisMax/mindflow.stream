# app/routes.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .models import Note
from .forms import CommentForm
from . import db
from datetime import datetime, timezone  # Import timezone from standard library

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = CommentForm()
    if form.validate_on_submit():
        new_note = Note(text=form.comment.data, created_at=datetime.now(timezone.utc))  # Ensure Note creation with timezone-aware datetime
        db.session.add(new_note)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('main.index'))
    notes = Note.query.order_by(Note.created_at.desc()).limit(100).all()
    return render_template('index.html', form=form, notes=notes)

@main.route('/comments', methods=['GET'])
def comments():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    pagination = Note.query.order_by(Note.created_at.desc()).paginate(page, per_page=per_page, error_out=False)
    notes = pagination.items
    # Format created_at in ISO format with 'Z' directly in the comprehension
    notes_data = [{
        'id': note.id,
        'text': note.text,
        'created_at': note.created_at.replace(tzinfo=timezone.utc).isoformat() if note.created_at.tzinfo is None else note.created_at.isoformat()
    } for note in notes]
    total_pages = pagination.pages
    return jsonify({'notes': notes_data, 'total_pages': total_pages})

@main.route('/comments', methods=['POST'])
def post_comment():
    data = request.get_json()
    new_note = Note(text=data['text'], created_at=datetime.now(timezone.utc))  # Ensure timezone-aware datetime on creation
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully!', 'id': new_note.id}), 201
