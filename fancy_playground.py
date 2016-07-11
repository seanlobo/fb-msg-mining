from flask import Flask, redirect, url_for, render_template, request, abort

from functions.messagereader import MessageReader
from functions.guiconvoreader import GUIConvoReader


app = Flask(__name__)
m = MessageReader()
all_gui_convo_readers = [None for _ in range(len(m) + 1)]


@app.route('/', methods=['GET', 'POST'])
def home_screen():
    return render_template('index.html')


@app.route('/convo/', methods=['GET', 'POST'])
def choose_convo():
    if request.method == 'POST':
        return redirect("/convo/{0}/graphs/".format(request.form['convo_num']), code=302)
    else:  # request.method == 'GET'
        return render_template('convo.html', text="Choose a conversation to analyze", m=m)


@app.route('/convo/<int:convo_num>/graphs/')
def graph(convo_num):
    current_convo = load_all_gui(convo_num)

    return render_template('graphs.html', convo=current_convo)


@app.route('/convo/<int:convo_num>/total_messages/<contact>/<int:cumulative>/<int:forward_shift>/<int:negative>')
def total_messages_data(convo_num, contact, cumulative, forward_shift, negative):
    current_convo = load_all_gui(convo_num)
    contact = current_convo.to_contact_string(contact)

    valid_url = (contact is None or current_convo.contains_contact(contact)) and (cumulative == 0 or cumulative == 1) \
                and (negative in [0, 1])
    if not valid_url:
        print("invalid contact or cumulative value")
        abort(404)

    if negative == 1:
        forward_shift *= -1
    try:
        return current_convo.data_for_total_graph(contact=contact, cumulative=(current_convo == 1),
                                                  forward_shift=forward_shift)
    except AssertionError:
        abort(404)


@app.route('/convo/<int:convo_num>/messages_by_day/<contact>/')
def messages_by_day_data(convo_num, contact):
    current_convo = load_all_gui(convo_num)
    contact = current_convo.to_contact_string(contact)

    if not current_convo.contains_contact(contact) or contact is None:
        abort(404)

    return current_convo.data_for_msgs_by_day(contact=contact)


@app.route('/convo/<int:convo_num>/messages_by_time/<contact>/<int:window>')
def messages_by_time_data(convo_num, contact, window):
    current_convo = load_all_gui(convo_num)
    if not current_convo.contains_contact(contact):
        abort(404)
    contact = current_convo.to_contact_string(contact)

    try:
        return current_convo.data_for_msgs_by_time(window=window, contact=contact)
    except AssertionError:
        abort(404)


def load_all_gui(convo_num) -> GUIConvoReader:
    if convo_num > len(m):
        abort(404)
    global all_gui_convo_readers
    if all_gui_convo_readers[convo_num] is None:
        all_gui_convo_readers[convo_num] = m.get_gui_convo(convo_num)
    return all_gui_convo_readers[convo_num]


if __name__ == '__main__':
    app.run()
