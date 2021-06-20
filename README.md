<h1>PyChatroom</h1>

A simple text based chat client and server program.

<h3> How to use </h3>

1. Run the server.py file, by default the ip is set to localhost and ports 5820 and 5821 are used.
2. Run the client.py file, follow instructions to join server.

<h3> Commands</h3>

* _/dm [user]_     --  sends a direct message to a user.
* _/r_       -- replies to the last direct message received.
* _/upl  [filename] [user]_    -- uploads a file to the server (must be in same directory as client.py)
                                  this can only be downloaded by [user].
* _/dwn [filename]_    -- downloads a file from the server and deletes it from there.
* _/help_       -- Displays all commands.
* _/exit_    -- exits the program.

<h4> Known Issues </h4>

* While typing a message, if you receive another message what you were writing is overwritten.
  This does not happen if using the Python Console.

<h3> Main Planned Updates</h3>

1. Add Encryption for file upload and download
2. Implement a basic GUI.

<h5> Minor Planned Updates </h5>

* Colour Coding for messages, e.g., white for normal text and orange for whispers.
* Save server activity to a log file.