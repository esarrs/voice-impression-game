#######################################################
##### IMPORT SECTION #############################
###############################################
import os
from forms import AddForm, DelForm, OwnForm
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import random

# import resemblyzer
from resemblyzer import preprocess_wav, VoiceEncoder
from pathlib import Path

encoder = VoiceEncoder("cpu")

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mykey'


#######################################################
##### SQL DATABASE SECTION #########################
###############################################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)


#######################################################
##### MODELS SECTION ##############################
###############################################

class Puppy(db.Model):

    __tablename__ = 'puppies'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text, unique=True)
    score = db.Column(db.Integer)
    #### ONE to ONE RELATIONSHIP ####
    owner = db.relationship('Owner',backref='puppy',uselist=False)

    def __init__(self,name,id,score):
        self.name = name
        self.id = id
        self.score = score


    def __repr__(self):
        # if self.owner:
        #     return f"ID: {self.id} --> Player: {self.name} | score: {self.score}"
        # else:
            return f"{self.name} ||| {self.score} pts"


class Owner(db.Model):

    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    #We use puppies.id because __table__ = 'puppies'
    puppy_id = db.Column(db.Integer, db.ForeignKey('puppies.id'))

    def __init__(self,name,puppy_id):
        self.name = name
        self.puppy_id = puppy_id

    def __repr__(self):
        return f"Owner name: "


#######################################################
##### VIEW FUNCTIONS -- HAVE FORMS ################
###############################################

### Home Page ###
@app.route('/')
def index():
    return render_template('home.html')

### Add Puppy Page ###
@app.route('/add',methods=['GET','POST'])
def add_pup():

    print("we don't need")

    form = AddForm()

    if form.validate_on_submit():

        # name = form.name.data
        # id = form.id.data
        # new_pup = Puppy(name,id)
        #
        # db.session.add(new_pup)
        # db.session.commit()

        return redirect(url_for('list_pup'))
    return render_template('add.html',form=form)


### Delete Puppy Page ###
@app.route('/delete', methods=['GET','POST'])
def del_pup():

    form = DelForm()

    if form.validate_on_submit():
        id = form.id.data
        pup = Puppy.query.get(id)

        db.session.delete(pup)
        db.session.commit()

        return redirect(url_for('list_pup'))
    return render_template('delete.html', form=form)

@app.route('/owner',methods=['GET','POST'])
def own_pup():

    form = OwnForm()

    if form.validate_on_submit():
        name = form.name.data
        puppy_id = form.puppy_id.data
        new_owner = Owner(name,puppy_id)

        db.session.add(new_owner)
        db.session.commit()

        return redirect(url_for('list_pup'))
    return render_template('owner.html',form=form)



### List of Puppy Page ###
@app.route('/list')
def list_pup():

    allpuppies = Puppy.query.all()

    return render_template('list.html', allpuppies=allpuppies)


### Upload ###
@app.route('/upload',methods=['POST','GET'])
def upload():

    if request.method == "POST":

        #### connecting flask python with javascript
        ## saving recorded audio file name with player's name -> esar.wav
        recorder_name = request.form['recorder_name']
        print("Recorder name: ", recorder_name)  #to check on the console
        f = request.files['audio_data']

        with open('audio.wav','wb') as audio:
            ext_type = 'audio.wav'.split('.')[-1]  #This will e.g "split mypic" "." "jpg". We just want "jpg#
            storage_filename = str(recorder_name)+'.'+ext_type  #Then we store the pic as user's "usename.jpg

            f.save(storage_filename)
        print('file uploaded successfully')


        # compare 2 wav files and save it

        # process sample wav
        wav_fpath1 = Path("./audios/uchisan3.wav")
        wav1 = preprocess_wav(wav_fpath1)

        # process users audio
        wav_fpath2 = Path(storage_filename)
        wav2 = preprocess_wav(wav_fpath2)

        # compare
        embed1 = encoder.embed_utterance(wav1[500:15500])
        embed2 = encoder.embed_utterance(wav2[500:15500])
        score = embed1 @embed2


        score = int(score*100)

        # save it

        # if recorder_name == "":
        #     recorder_name = "test1"

        _id = random.randint(100000, 999999)
        # new_pup = Puppy(recorder_name, _id, score)

        print("name: ",recorder_name, ", id: ", _id, ", score: ", score)

        # Update score for already registered name
        # check name is table puppies filter by name
        user = Puppy.query.filter_by(name=recorder_name).first()
        print("User: ", user)

        if user is None:
            user = Puppy(recorder_name, _id, score)
            db.session.add(user)
            print("User2: ", user)
        else:
            user.score = score

        # db.session.add(new_pup)

        db.session.commit()

        # return json.dumps({"status": "success"})
        return "ok"
        # print(url_for('list_pup'))
        # return redirect("https://18.176.91.61/list")
        # return redirect(url_for('list_pup'))
    else:
        return render_template("home.html")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6339)
