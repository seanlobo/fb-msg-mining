import time
import os
import sys
from flask import Flask, redirect, render_template, request, abort

from functions.messagereader import MessageReader
from functions.guiconvoreader import GUIConvoReader
from functions.wordcloud import WordCloud


app = Flask(__name__)

print("For the time being please use Chrome")
print("Setting up could take a few moments ", end="")
initial_time = time.time()
m = MessageReader()
all_gui_convo_readers = [m.get_convo_gui(i) for i in range(1, len(m) + 1)]


# ---------------------------------------------------   HOME PAGE   -------------------------------------------------- #

@app.route('/')
def home_screen():
    return render_template('index.html')

# ---------------------------------------------------   HOME PAGE   -------------------------------------------------- #


# ----------------------------------------------------   GRAPHS   ---------------------------------------------------- #

@app.route('/graphs/')
def graphs_home():
    return redirect('/graphs/conversation/', code=302)


@app.route('/word_clouds/conversation/')
@app.route('/graphs/conversation/')
def table():
    sort = 'length'
    mode = 'down'
    if 'sort' in request.args:
        sort = request.args['sort']
    if 'mode' in request.args:
        mode = request.args['mode']

    if sort == 'length':
        sort = ['length', 'alpha', 'contacted']
    elif sort == 'alpha':
        sort = ['alpha', 'length', 'contacted']
    else:  # sort == 'contacted'
        sort = ['contacted', 'alpha', 'length']

    reverse = mode == 'down'

    if 'query' in request.args:
        data = m.quick_stats.match_name(request.args['query'].lower())
    else:
        data = m.quick_stats.ordered_values(sort, reverse=reverse)
    return render_template('table.html', m=m, p=m.quick_stats, sort=sort, mode=mode, reverse=reverse, data=data)


@app.route('/graphs/conversation/<int:convo_num>/')
def graphs(convo_num):
    current_convo = load_all_gui(convo_num)

    return render_template('graphs.html', convo=current_convo, convo_num=convo_num)


@app.route('/graphs/conversation/<int:convo_num>/next/')
def next_page(convo_num):
    if convo_num == len(all_gui_convo_readers):
        return redirect('/graphs/conversation/{0}/'.format(1), code=302)
    return redirect('/graphs/conversation/{0}/'.format(convo_num + 1), code=302)


@app.route('/graphs/conversation/<int:convo_num>/prev/')
def prev_page(convo_num):
    if convo_num == 1:
        return redirect('/graphs/conversation/{0}/'.format(len(all_gui_convo_readers)), code=302)
    return redirect('/graphs/conversation/{0}/'.format(convo_num - 1), code=302)


@app.route('/graphs/conversation/<int:convo_num>/total_messages/<contact>/'
           '<int:cumulative>/<int:forward_shift>/<int:negative>/')
def total_messages_data(convo_num, contact, cumulative, forward_shift, negative):
    current_convo = load_all_gui(convo_num)
    contact = current_convo.to_contact_string(contact)

    valid_url = (contact is None or current_convo.contains_contact(contact)) and (cumulative in [0, 1]) \
                                                                             and (negative in [0, 1])
    if not valid_url:
        print("invalid contact or cumulative value")
        abort(404)

    if negative == 1:
        forward_shift *= -1
    cumulative = cumulative == 1
    try:
        return current_convo.data_for_total_graph(contact=contact, cumulative=cumulative,
                                                  forward_shift=forward_shift)
    except AssertionError:
        abort(404)


@app.route('/graphs/conversation/<int:convo_num>/messages_by_day/<contact>/')
def messages_by_day_data(convo_num, contact):
    current_convo = load_all_gui(convo_num)
    contact = current_convo.to_contact_string(contact)

    if not current_convo.contains_contact(contact) and contact is not None:
        abort(404)

    return current_convo.data_for_msgs_by_day(contact=contact)


@app.route('/graphs/conversation/<int:convo_num>/messages_by_time/<contact>/<int:window>/')
def messages_by_time_data(convo_num, contact, window):
    current_convo = load_all_gui(convo_num)

    contact = current_convo.to_contact_string(contact)
    try:
        return current_convo.data_for_msgs_by_time(window=window, contact=contact)
    except AssertionError:
        abort(404)


# ----------------------------------------------------   GRAPHS   ---------------------------------------------------- #

@app.route('/word_clouds/')
def word_clouds_home():
    return redirect('/word_clouds/conversation/', code=302)


@app.route('/word_clouds/conversation/<int:convo_num>/', methods=['GET', 'POST'])
def word_cloud(convo_num):
    current_convo = load_all_gui(convo_num)
    if request.method == 'GET':
        input_word_files = WordCloud.get_input_text_files()
        excluded_word_files = WordCloud.get_excluded_word_files()
        image_files = WordCloud.get_image_files()
        return render_template('word_clouds.html',
                               excluded_word_files=excluded_word_files,
                               image_files=image_files,
                               input_word_files=input_word_files,
                               excluded_word_path=WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH,
                               input_word_path=WordCloud.WORD_CLOUD_INPUT_PATH,
                               image_path=WordCloud.WORD_CLOUD_IMAGE_PATH)
    else:
        wc_preferences = {key: val for key, val in request.form.items()}
        ready = current_convo.setup_new_word_cloud(wc_preferences)

        print(str(ready), file=sys.stderr)
        if current_convo.ready_for_word_cloud():
            current_convo.create_word_cloud()
            return 'created!'
        else:
            return str(ready)

# -------------------------------------------------   COMING SOON   ------------------------------------------------- #

@app.route('/coming_soon/')
def coming_soon():
    return render_template('coming_soon.html')


def load_all_gui(convo_num) -> GUIConvoReader:
    if convo_num < 1 or len(m) < convo_num:
        abort(404)
    return all_gui_convo_readers[convo_num - 1]

print("(took {0:.2f} seconds to load)".format(time.time() - initial_time))
if __name__ == '__main__':
    app.run()
