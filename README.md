# FanTastiP Project Report

CHEN Yule	2018011660	28th, Oct.



## FTP Server

#### About

An FTP server written in C and running with GNU/Linux.

GCC version: 9.3.0

#### Supported Commands

USER, PASS, RETR, STOR, QUIT, SYST, TYPE, PORT, PASV, MKD, CWD, PWD, LIST, RMD, RNFR,  RNTO, SIZE and REST.

#### Exception Caught

+ **Invalid  command line arguments** when  starting the server.
+ **FTP commands' syntax errors** in parameters or arguments.
+ **Those exceptions occurring when calling those socket APIs**, like *socket()*, *listen()*, *bind()*, *accept()*, and so on.

#### Multi-client Support

The server adopts **multiple processes** to manage multiple processes. Parent process keeps listening for incoming connections, until it is forced to terminate. Every time a new client requests to connect, parent process forks a new child process to deal with this client. A child process will terminate when it receives a QUIT command.

#### Breakpoint Resuming Support

When receiving a REST command, the server would set a breakpoint for the next file transfer. Upon receiving next RETR / STOR command, the server would resume transmission from the breakpoint.

#### Notes

+ Upon receiving a PASV command, the server requires the client to establish a data connection immediately, before the following RETR / STOR commands.
+ When sending or receiving files in response to RETR and STOR commands from a client, the server ignores all control commands (including QUIT) from that particular client until the data connection is completed. 
+ It's not suggested to name directories and files using special characters like spaces. If so, FTP commands about these directories and files are more likely to be rejected.
+ Upon receiving a LIST command, the server obtains directory and file information using shell command *ls -l*. The format of *ls*'s results depends on the server's operating system type.

## FTP Client

#### About

This FTP client is written in Python 3. 

The file *FanTastiP.py* provides a class named *FTP*, which is used to perform the most basic tasks of FTP clients, like sending FTP commands defined by *RFC959* to FTP servers, and receiving replies from FTP servers. *FTP* class provides rarely exception control mechanism.

The file *FantasticFTP.py* provides a class named *FantasticFTP*, inherited *FTP* class, which is used to implemented an FTP client GUI using the Tkinter GUI toolkit. *FantasticFTP* also provides reliable exception control mechanism; when an *FantasticFTP* object calls *FTP* class's method, it always adopts try / except mechanism to catch potential exceptions.

#### Control

+ **IP address entry, port entry, and Connect / Disconnect button**![](1.jpg)

+ **Command prompt**, where green words denote commands and purple words denote responses.![](2.jpg)

+ **Server working directory window**

  The 4 buttons in the upper left corner: "back to the parent directory", "create a new directory", "remove a directory", and "rename a directory or file". 

  Double click a directory inside the window to change working directory.

  ![](3.jpg)

+ **Download / Upload buttons &Task window**

  ![](4.jpg)

#### Exception Handled

+ **Wrong formats of IP address or port number.** When users give IP addresses or port numbers passwords with wrong formats, the client will force users to try again.
+ **Non-standardized responses of LIST command.** A standardized response format of LIST command is something like *“d-wxrwxr-x   2 ftp      dir_name        1024 Sep  5 13:43”*. If file and directory information received after a LIST command is not  standardized, the client will exit.
+ **Illegal directory operations,** such as deleting non-empty directory, creating new directory with an illegal directory name, moving files to a non-existent directory when renaming, and so on.
+  **Connection exceptions.** When a connection is closed unexpectedly, the client cannot perform almost operations anymore, and will open an error-showing pop-up window to remind users to reconnect.
+ **File transfer exceptions,** such as downloading a non-existent file, uploading a file without server directory's writing permissions

#### Breakpoint Resuming Support

+ **Download:** Before sending a "*RETR filename*" command, the client would first check if *filename* exists in the local directory. If it does, the client  would get its size and send a "*REST size*" command to tell the server this breakpoint. Finally, the client sends a RETR commands. 
+ **Upload:**  Before sending a "*STOR filename*" command, the client would first send a "*SIZE filename*" command to ask the server how much of the transfer has been down. If the SIZE command's response is "*213 size*", then the client would send a "*REST size*" command to tell the server this breakpoint. Finally, the client sends a STOR commands.

#### Notes

+ The client only supports connections with the server's IP address. That is, without knowing the target IP address, it cannot establish a connection.
+ The client supports anonymous logins. An empty username would lead to an anonymous login.
+ The client only supports file transfer in binary mode.
+ When transferring a file, the client blocks most of the GUI's buttons.