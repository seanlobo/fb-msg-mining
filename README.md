# Facebook Chat Data Analyzer

## Installing dependencies

Ensure that you have a version of python3 installed. If you don't, navigate to [python's homepage](https://www.python.org/downloads/).
Installing python from here should come with `pip`, python's package manager, but if you don't have `pip` installed, visit
[this page](https://pip.pypa.io/en/stable/installing/) to install it.

After cloning the project to install dependencies run:

    pip3 install -r requirements.txt

Additionally, if you would like to use WordCloud features ensure that you have Java installed. You can find installation instructions
[here](https://www.java.com/en/download/help/download_options.xml).


---

## Step 1:

Run `git clone https://github.com/seanlobo/fb-msg-mining.git` where you would like to clone the project


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


## Step 4:

Extract the zip you get and without editing anything, move the `html` folder inside the project folder.

After doing this the `html` folder should be in the same directory as files and folders such as `README.md`, `setup.py` and `functions`. Ensure that the `html` folder contains a file titled `messages.htm`


## Step 5:

Run `python3 setup.py` and follow prompts

If you have errors at this step and can't figure out why, email me at `seanlobo2010@gmail.com`


## Using the program

run `python3 -i playground.py` to get an interactive session and analyze data, or `python3 fancy_playground.py` for a web browser version.

# Libraries used
While original aspects of this project are open source under the MIT License, various libraries are utilized that are subject to their own
terms and conditions. Licenses can be found in this project, with more information in `credit.txt`.
In particular, the graphing functionality of highcharts is used in this project.
Note that HighCharts and its software is not free for commercial and Governmental use. More information can be found at [highcharts.com](https://www.highcharts.com)

---

## Version history
See [CHANGES.md](CHANGES.md)