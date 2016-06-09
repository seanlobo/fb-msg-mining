from flask import Flask, redirect, url_for, render_template

from functions.messagereader import MessageReader


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


@app.route('/convo/<int:convo_num>/')
def graph(convo_num):
    global current_convo
    current_convo = m.get_gui_convo(convo_num)

    return render_template('graphs.html', total_data=current_convo.data_for_total_graph(),
                           convo=current_convo.get_people())


@app.route('/convo/<int:convo_num>/test')
def test(convo_num):
    return render_template('skeleton.html', text="default")
    # Works!


@app.route('/aggregate/')
def choose_aggregate_fn():
    return render_template('skeleton.html', text="Choose what aggregate data to analyze")


if __name__ == '__main__':
    app.run()