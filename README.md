# CIS433-CourseProject

### Authors: Hans Prieto, Joshua Fawcett

## Description
This is a secure messenger application that was created as the final project submission for CIS 433 - Computer and Network Security. It implements a simple client-server messenger application with end-to-end encryption, session keys, and hashing for security. 

## Technologies
* Python version: 3.7.0
* Tkinter version: 8.6.9
* Cryptography module: [link](https://cryptography.io/en/latest/)

## Running the program
If you don't already have it installed, install the cryptography module with:
<pre>pip install cryptography</pre>
Or see the cryptography module link for more information about installation. 
<br>You can run the program with some variation of the following command (python/python3/py...):
<pre>python UI.py</pre>
Note: A server connection is required to be able to send messages. Without a server connection you won't be able to do much. The server was designed to run on an AWS t2.micro instance, but it can also run locally for testing. 
<br>To run the server, use the following command:
<pre>python server.py</pre>
