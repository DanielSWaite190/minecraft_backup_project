# minecraft_backup_project

A script to automate the process of copying Minecraft worlds to a new and safe location in the case of corruption in the original folder.
This program works by reading the Minecraft (Spigot) log file in real time. By keeping track of players entering and exiting the game,
the program will calculate the total time the server is active (players are in the game). If this active time is above 30 minutes,
a backup will be scheduled for that following Saturday night. Thirty minutes before the scheduled backup, all players on the server will 
Receive a warning followed by a ten minute interval countdown. When this countdown completes, the server will stop, 
the files will be copied to the specified destination and the server will start backup.

![wallpaper](https://user-images.githubusercontent.com/56490534/166081835-acf26660-8ebc-401b-98d0-a39873e55bca.png)


ToDo Next:

1.1.2
Make a new branch
**Logging**
Make player list only log in debug mode. Add option to log to a file. 

1.2.0
Make a new branch
**MOTD** (message of the day)
Make a sub-function to edit the server.properties file and change the message of the day after each backup.

1.2.1
Make a new branch
**Java Update**
Check for out of date java file in log stream and download a new version. Either by stoping the server then, or seeing a flag for the next backup.

1.3.0
Make a new branch
**Live Weather**
Link game weather to a weather api
