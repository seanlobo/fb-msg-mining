from flask import Flask, redirect, url_for, render_template, request

from functions.messagereader import MessageReader


app = Flask(__name__)
m = MessageReader()
current_convo = None


@app.route('/', methods=['GET', 'POST'])
def home_screen():
    return render_template('index.html', m=m, convo=current_convo)


@app.route('/history/')
@app.route('/convo/')
def choose_convo():
    return render_template('skeleton.html', text="Choose a conversation to analyze")


@app.route('/convo/<int:convo_num>/graphs/')
def graph(convo_num):
    global current_convo
    current_convo = m.get_gui_convo(convo_num)

    return render_template('graphs.html', convo=current_convo)


@app.route('/aggregate/')
def choose_aggregate_fn():
    return render_template('skeleton.html', text="Choose what aggregate data to analyze")


if __name__ == '__main__':
    app.run()