from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class AddForm(FlaskForm):

    name = StringField('Insert Player Name ')
    submit = SubmitField('Register')
    id = IntegerField()

class DelForm(FlaskForm):

    id = IntegerField("Insert your ID ")
    submit = SubmitField("Delete")

class OwnForm(FlaskForm):
    name = StringField('Insert Rec ')
    puppy_id = IntegerField('Insert ID')
    submit = SubmitField('Submit')
