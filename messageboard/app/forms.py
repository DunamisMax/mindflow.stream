from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
import re

class NoHTMLValidator(ValidationError):
    """
    Custom validator to ensure that input does not contain HTML tags or angle brackets.
    This is crucial for preventing XSS attacks by sanitizing user input to remove potentially malicious HTML.
    """

    def __init__(self, message=None):
        super().__init__(message or "Input must not contain HTML tags or angle brackets ('<' or '>').")

    def __call__(self, form, field):
        if re.search(r'<[^>]*>', field.data):
            raise self

class CommentForm(FlaskForm):
    """
    Form class for submitting comments, with validation rules to enhance security and data integrity.
    Ensures comments are free of HTML and within character limits to prevent common web vulnerabilities.
    """
    comment = TextAreaField(
        'Comment',
        validators=[
            DataRequired(message="Comment cannot be empty."),
            Length(min=1, max=1500, message="Comment must be between 1 and 1500 characters."),
            NoHTMLValidator()
        ]
    )
    submit = SubmitField('Post Comment')
