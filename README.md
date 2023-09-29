"# DFS"

This Distributed File System Using Blockchain contains several packages that helps with the bulding these are listed below:

1. DFS_main
   - this package contains main, logger, and server files(recieved)
   - this mainly deals with the outer things
   - from this main.py everything starts
   - it starts the server and later everything is done by the server for handling the requests

2. Server
   - this package contains the server files
   - this mainly deals with the inner things
   - it handles the requests and sends the response to the client

3. Client
   - This can be used to upload the file to the sever
   - when the file is uploaded it will go to the FileManager to complete the required tasks

4. Handler
   - this handles the incoming requests from the server
   - the server send the data to the handler and handler handles as required for the programe
5. FileManager
   - this is used to handle the file
   - processing the data,making into chunks, maintaing the file structure(creating tables for storing)
   - and later stored in the DFS_main for easy access