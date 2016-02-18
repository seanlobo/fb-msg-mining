# Facebook Chat Data Analyzer

## Installing dependencies

To install dependencies run:

    pip3 install -r requirements.txt


## Step 1:

Request a copy of your Facebook data:

Go to Facebook and click on Settings -> "Download a copy" link near the middle of the page.
You'll need to put in your facebook password in order to request the download, and you should
recieve an email from facebook immediately, sent to the email you used when signing up.


## Step 2:

When you get an email with the download link, use the link emailed to you by facebook 
to download a copy of your data


## Step 3:

Extract the zip you get and put `html/messages.htm` in a location you have access to. 


## Step 4:

Run `git clone https://github.com/seanlobo/fb-msg-mining.git` where you would like to clone the project


## Step 5:

Rename `paths.txt.examples` --> `paths.txt`


## Step 6:

Add the absolute path to `html/messages.htm` to `paths.txt`

Create a directory where you would like to store all of you facebook data, and create a 
`data.txt` file inside that directory
Add the absolute path to `data.txt` to `paths.txt`


## Step 7:

Run `python3 main.py`

If you have errors at this step and can't figure out why, email me at `seanlobo2010@gmail.com`


## Using Fb-msg-mining

After setup is complete, run `python3 -i test.py`

Below are descriptions of the two main classes, MessageReader and ConvoReader.

| Class   | Description |
|-------------|-------------|
|MessageReader | Holds information for all chats, as well as the time and date history was downloaded at. Has methods to get ConvoReader objects for specific chats |
|ConvoReader | Holds all the chat history for a specific conversation, including all messages sent, and for each message the time and person who sent them. Can perform analysis on chat history, see below for more details |


You start with a MessageReader object stored in the variable m, which holds all your chat history for all contacts.


```python
### MessageReader class ###
m.print_names() # prints to the screen your contacts in decreasing order of chatted frequency
 # 1) Most chatted
 # 2) Second most common
 # 3) etc.

nth_convo = m.get_convo(n) # returns the nth conversation, where n referres to the output of m.print_names()
```

### ConvoReader class ###

| Method   | Description |
|-------------|-------------|
|print_people( ) | Prints to the screen an alphabetically sorted list of people in the conversation |
|messages(name=None) | Returns either the number of messages spoken by the specified person, or if no name is passed, a Counter object storing the number of mesages as values paired with names of people as keys for all people in the chat |
|ave_words(name=None) | Returns either the average number of words spoken per message by the specified person, or if no name is passed, a Counter object storing the average number of words per message as values paired with names of people as keys
|frequency(person=None, word=None) | Returns either the average number of words spoken per message by the specified person, or if no name is passed, a Counter object storing the average number of words per message as values paired with names of people as keys.
| prettify( ) | Returns a string that \"prettily\" shows the conversation history |
| print_msgs_graph(contact=None) | Prettily prints to the screen the message history of a chat |
| msgs_by_weekday( ) | Returns a list containing frequency of chatting by days of week, ordered by index, with 0 being Monday and 6 Sunday |
| print_msgs_by_day(window=60, threshold=None, contact=None) | Prints to the screen a graphical result of msgs_by_day |
| save_word_freq( ) | Saves to a file the ordered rankings of word frequencies by person in the chat |




