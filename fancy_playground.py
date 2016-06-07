from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)


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