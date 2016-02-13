# Facebook Chat Data Analyzer

## Installing dependencies

To install dependencies run:

    pip3 install -r requirements.txt


## Step 1:

Request a copy of your Facebook data

Settings -> "Download a copy" link near the bottom of page


## Step 2:

Use the link emailed to you by facebook to download a copy of your data


## Step 3:

Extract the zip you get and put `html/messages.htm` in a location you have access to


## Step 4:

Rename `paths.txt.examples` --> `paths.txt`


## Step 5:

Add the absolute path to `html/messages.htm` to `paths.txt`

Add the absolute path to `data.txt`, the location where chat data will be stored, to `paths.txt`


## Step 6:

Run `main.py`
