from flask import Flask, redirect, url_for, render_template

from functions.messagereader import MessageReader
from functions.convoreader import ConvoReader
from functions.customdate import CustomDate
from functions import emojis


app = Flask(__name__)
m = MessageReader()
current_convo = None


@app.route('/')
def home_screen():
    return render_template('skeleton.html', text="Home Screen")


@app.route('/history/')
@app.route('/convo/')
def choose_convo():
    return render_template('skeleton.html', text="Choose a conversation to analyze")


@app.route('/aggregate/')
def choose_aggregate_fn():
    return render_template('skeleton.html', text="Choose what aggregate data to analyze")


if __name__ == '__main__':
    app.run()