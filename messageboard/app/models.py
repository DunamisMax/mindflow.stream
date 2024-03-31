from typing import Dict
from . import db
from datetime import datetime

class Note(db.Model):
    """
    Note model represents a single note/comment in the application.

    Attributes:
        id (int): Unique identifier for each note.
        text (str): Content of the note, limited to 500 characters.
        created_at (datetime): Timestamp when the note is created, defaults to the current time.
    """
    __tablename__ = 'notes'
    id: int = db.Column(db.Integer, primary_key=True)
    text: str = db.Column(db.String(500), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Provides a readable representation of a Note instance, showing its ID."""
        return f'<Note {self.id}>'

    def to_dict(self) -> Dict[str, any]:
        """
        Serializes a Note instance to a dictionary format, which can be easily converted to JSON.

        Returns:
            dict: A dictionary representation of the note, including its id, text, and created_at fields.
        """
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at.isoformat()
        }
