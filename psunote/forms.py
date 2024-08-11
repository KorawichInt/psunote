from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets

import models


class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        data = []
        if valuelist:
            data = [x.strip() for x in valuelist[0].split(",")]

        if not self.remove_duplicates:
            self.data = data
            return

        self.data = []
        for d in data:
            if d not in self.data:
                self.data.append(d)

    def _value(self):
        if self.data:
            # return ", ".join(self.data)
            return ", ".join([t.name if isinstance(t, models.Tag) else t for t in self.data])
        else:
            return ""


BaseNoteForm = model_form(
    models.Note, base_class=FlaskForm, exclude=["created_date", "updated_date"], db_session=models.db.session
)


class NoteForm(BaseNoteForm):
    tags = TagListField("Tag")

    def populate_obj(self, obj):
        # First, call the default populate_obj to handle other fields
        super().populate_obj(obj)

        # Handle the tags field separately
        tag_names = self.tags.data
        tag_objects = []

        for name in tag_names:
            tag = models.Tag.query.filter_by(name=name).first()
            if not tag:
                tag = models.Tag(name=name)
                models.db.session.add(tag)
            tag_objects.append(tag)

        obj.tags = tag_objects
