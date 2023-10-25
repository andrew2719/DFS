"# DFS"

This Distributed File System Using Blockchain contains several packages that helps with the bulding these are listed below:




1. [DFS_main](../DFS_main)
   - this package contains main, logger, and server files(recieved)
   - this mainly deals with the outer things
   - from this main.py everything starts
   - it starts the server and later everything is done by the server for handling the requests

2. [Server](../Server)
   - this package contains the server files
   - this mainly deals with the inner things
   - it handles the requests and sends back the response
   - it also takes the client side of the local system files and distribute them using the [Distributer](../Handler/PeerHandler.py)

3. [Client](../Client)
   - This can be used to upload the file to the sever
   - when the file is uploaded it will go to the server and server handles that by sending to the [SelfHandler](../Handler/SelfHandler.py)

4. [Handler](../Handler)
   - this handles the incoming requests from the server
   - the server send the data to the handler and handler handles as required for the program
5. [FileManagement](../FileManagement)
   - this is used to handle the file
   - processing the data,making into chunks, maintaing the file structure(creating tables for storing)
   - and later stored in the DFS_main for easy access

encode and decode works only for the string or the json.dumps()

encode means converting the "string" to bytes


decode means converting the bytes to "string"

from string to dict we use json.loads()

from dict to string we use json.dumps()

