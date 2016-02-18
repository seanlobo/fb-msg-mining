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


You start with a MessageReader object stored in the variable m, which holds all your chat history for all contacts. You can use this object to get ConvoReader instances, which allow you to process data for specific CONVersations. The following outline common methods and uses:


### MessageReader

####`print_names()` 

Prints to the screen your contacts in decreasing order of chatted frequency, e.g. :
```python
1) Most chatted chat
2) Second most chatted chat
3) etc.
```

###`get_convo(people)`
Returns a ConvoReader object representing the conversation
passed as a list of names, string name or index of conversation
(from print_names). If an invalid parameter is passed return None

	Parameters:
		people: Which conversation you would like to get. Either the number from the output of 
			print_names(), the name of the conversation you want (e.g. 'sean lobo, jason perrin') 
			or a list of names (e.g. ['jason perrin', 'sean lobo'])


### ConvoReader class ###

####`print_people()`
Prints to the screen an alphabetically sorted list of peoplein the conversation

####`messages(name=None)`
Number of messages for people in the chat 

	Parameters:
		name (optional): The name (as a string) of the person you are interested in
	Return:
		A number if name is not passed, otherwise a Counter object storing the number
		of mesages as values paired with names of people as keys.


####`word(name=None)`
Number of words for people in the chat

		Parameters:
			name (optional): The name (as a string) of the person you are interested in
		Return:
			A number if name is not passed, otherwise a Counter object storing the number
			of words as values paired with names of people as keys.


####`ave_words(name=None)`
Average number of words for people in the chat

	Parameters:
		name (optional): The name (as a string) of the person you are interested in
	Return:
		A number if name is not passed, otherwise a Counter object storing the average
		number of words as values paired with names of people as keys.


####`frequency(person=None, word=None, limit=True)`
Prints the requency of words for people in the chat
	
	Parameters:
		person (optional): The name (as a string) of the person you are interested in
		word (optional): The word (as a string) you are interested in
		limit (optional): bool or int. If int desplays maximum that many words, 
				if false desplays all words, if true desplays top 10. Should only be used
				if word is left out, and is ignored if a value for word is given

####`prettify()`

Prints a "pretty" version of the conversation history

####`print_msgs_graph(contact=None)`
Prettily prints to the screen the message history of a chat
	
	Parameter:
		contact (optional): the name (as a string) of the person you are interested in.
			(default: all contacts)


####`msgs_by_weekday()`

Returns a list containing frequency of chatting by days of week, ordered by index, with 0 being Monday and 6 Sunday

####`print_msgs_by_day(window=60, contact=None, threshold=None)`
Prints to the screen a graphical result of messages sent by day
	
	Parameters:
		window (optional): The length of each bin in minutes (default, 60 minutes, or 1 hour)
		contact (optional): The contact you are interested in. (default, all contacts)
		threshold (optional): The minimum threshold needed to print one '#'




