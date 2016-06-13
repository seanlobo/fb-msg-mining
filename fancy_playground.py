from flask import Flask, redirect, url_for, render_template, request

from functions.messagereader import MessageReader


app = Flask(__name__)
m = MessageReader()
current_convo = None


@app.route('/', methods=['GET', 'POST'])
def home_screen():
    return render_template('index.html', m=m, convo=current_convo)


@app.route('/convo/', methods=['GET', 'POST'])
def choose_convo():
    if request.method == 'POST':
        return redirect("/convo/{0}/graphs/".format(request.form['convo_num']), code=302)
    else:  # request.method == 'GET'
        return render_template('convo.html', text="Choose a conversation to analyze", m=m)


@app.route('/convo/<int:convo_num>/graphs/')
def graph(convo_num):
    global current_convo
    current_convo = m.get_gui_convo(convo_num)

    return render_template('graphs.html', convo=current_convo)


if __name__ == '__main__':
    app.run()