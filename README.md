# Facebook Message Mining

## Installing dependencies

Ensure that you have a version of python3 installed. If you don't, navigate to [python's homepage](https://www.python.org/downloads/).
Installing python from here should come with `pip`, python's package manager, but if you don't have `pip` installed,
visit [this page](https://pip.pypa.io/en/stable/installing/) to install it.

Using `virtualenv` is recommended as well. You can install it with `brew install virtualenv` on a mac
(try `brew install pyenv-virtualenv` if `virtualenv` isn't found) or with `pip install virtualenv`

Additionally, if you would like to use WordCloud features ensure that you have Java installed. You can find
installation instructions [here](https://www.java.com/en/download/help/download_options.xml).


---

## Step 1:

Clone the project and install dependencies in `virtualenv`. From a directory where you would like to download the
project:

```bash
$ git clone https://github.com/seanlobo/fb-msg-mining.git
$ cd fb-msg-mining
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```


## Step 2:

[Request a copy of your Facebook data:](https://www.facebook.com/help/131112897028467/)

Go to Facebook and click on Settings -> "Download a copy" link near the middle of the page.
You'll need to put in your facebook password in order to request the download, and you should
receive a confirmation email from facebook immediately, sent to the email you used when signing up.
**It can take less than an hour or up to a week to get your archive, and you only have around 24 hours
before the link sent to you expires, so check carefully!**

Note that at all times your data is only analyzed locally.


## Step 3:

When you get an email with the download link, use the link emailed to you by facebook
to download a copy of your data **within 24 hours**

Extract the zip you get and without editing anything, move the `html` folder inside the project folder.
After doing this the `html` folder should be in the same directory as files and folders such as `README.md`, `setup.py`
and `functions`. Ensure that the `html` folder contains a file titled `messages.htm`

Run `python3 setup.py` and follow prompts


## Using the program

Run `python3 fancy_playground.py` to get a web browser session, or `python3 -i playground.py` for an interactive python
session.

# Libraries used
While original aspects of this project are open source under the MIT License, various libraries are utilized that are
subject to their own
terms and conditions. Licenses can be found in this project, with more information in `credit.txt`.
In particular, the graphing functionality of highcharts is used in this project.
Note that HighCharts and its software is not free for commercial and Governmental use. More information can be found at
[highcharts.com](https://www.highcharts.com)

---

## Version history
See [CHANGES.md](CHANGES.md)
