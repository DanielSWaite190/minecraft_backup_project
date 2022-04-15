"""
A script to automate the process of copying Minecraft worlds to a new and safe location in the case of corruption in the original folder.
This program works by reading the Minecraft (Spigot) log file in real time. By keeping track of players entering and exiting the game,
the program will calculate the total time the server is active (players are in the game). If this active time is above 30 minutes,
a backup will be scheduled for that following Saturday night. Thirty minutes before the scheduled backup, all players on the server will 
Receive a warning followed by a ten minute interval countdown. When this countdown completes, the server will stop, 
the files will be copied to the specified destination and the server will start backup.
(C) 2022 Daniel S. Waite
"""
VERSION_NUMBER = 1

import subprocess
import argparse
import datetime
import logging
import signal
import time
import sys
import os
import re

"""
Global variabels that will be manipulated by various functions
Not sure how "pythonic" this is. Am open to refactoring once
I learn a better way
"""
start_time = datetime.datetime.today()
end_time = datetime.datetime.today()
thirty = [30,40,50,55,56,57,58]
backUpDate = None
player_list = []
game_time = 0
v_number = ''
running = True

# logg_level = logging.critical
logging.basicConfig(level=logging.DEBUG, #filename="backup.log",
    format="[Backup Server Program] [%(levelname)s]: %(message)s")

def create_parser():
    parser = argparse.ArgumentParser(description="Copies Minecragt world folder" + 
        "evry week, if sufficent game time has been loged.")
    parser.add_argument("game_folder", help="Minecraft root game folder")
    parser.add_argument("backup_location", help="Location of new ziped backup")
    return parser

def signal_handler(sig_num, frame):
    """Catches quit signals"""
    print()
    print("Closed")
    print()
    global running
    running = False

def main(args):
    """Main function holding the master while loop."""
    signal.signal(signal.SIGINT, signal_handler)
    parser = create_parser()
    if not args:
        parser.print_usage()
        sys.exit(1)
    parsed_args = parser.parse_args(args)
    p_logg_file = os.path.join(parsed_args.game_folder, 'logs/latest.log')
    # COMMENT: Pulling logs/latest out of game folder for easy indexing.

    logfile=open(p_logg_file, 'r') #COMMENT: Open MC log file
    global v_number
    v_number = initiate(logfile) #COMMENT: initiate() returns game version number.

    while running:
        line = '' #COMMENT: Clear variable for next line
        logline=logfile.readline()
        time.sleep(0.125) #COMMENT: Slows down refresh for performance reasons.
        if logline:
            line = logline

        log_in = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[\/\d+\.\d+\.\d+\.\d+:\d+\]\slogged\sin", line)
        log_out = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)

        #COMMENT: Building model form information in log file
        if log_in:
            new_player(line)
            print(player_list, end='\n \n')

            #COMMENT: When player list goes from 0 to 1, save curent time.
            if len(player_list) == 1:
                global start_time
                start_time = datetime.datetime.now()

        #COMMENT: Building model form information in log file
        if log_out:
            player_leaving(line)
            print(player_list, end='\n \n')

            #COMMENT: When player list goes from 1 to 0, save curent time
                    # and caculate total player time for that sesion.
            if len(player_list) == 0:
                global end_time
                global game_time
                end_time = datetime.datetime.now()
                game_time_delta = end_time - start_time #COMMENT: Total game time
                game_time += round(game_time_delta.seconds) #COMMENT: Truns game time delta into int
                logging.info(f"Total play time {round(game_time/60)} minutes.")
                if game_time/60 >= 60:
                    global backUpDate
                    backUpDate = armBackupSystem() # <--- Change to 'Next BackUp Date'
                    logging.info('Backup armed!')
                    logging.info(f'Backup will commence at {backUpDate} at 23:59.') #COMMENT: Technicaly it commences
                                                                            # on the next day at 00:00 but whatever.
        #COMMENT: On schedueled date at 11pm start countdown.                                                                     
        if datetime.date.today() == backUpDate and \
           datetime.datetime.now().time().hour <= 23:
            countDown(parsed_args)

    if not running:
        logfile.close() 

def initiate(logfile):
    """Pre while loop that confirms legitimate Minecraft log file."""
    print()
    print(f"---   Mineraft Backup   ---")
    print(f'---   Version {VERSION_NUMBER}')
    # logging.debug('Starting Mineraft backup program...')
    while running:
        line = '' #COMMENT: Clear variable for next line
        #COMMENT: Reads the lates line from the file and saves it to var line.
        logline=logfile.readline()
        time.sleep(0.125) #COMMENT: Slows down refresh for performance reasons.
        if logline:
            line = logline
        
        #COMMENT: Each Minecraft log file starts with a version number. This checks for that 
                # verifing a true MC log file.
        game_version = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\sStarting minecraft server version\s\d+.\d+.\d+", line)
        if game_version:
            num = re.search('version\s\d+.\d+.\d+', line)
            # logging.debug('Identified Minecraft logging sesion.')
            # logging.debug(f'This game is running {num.group()}---')
            [print('') for i in range(2)] #Print a few extra spaces 
            print('Waiting on server on server...')
        
        #COMMENT: Return to main function once server is done loading.
        done = re.search("! For help, type \"help\"", line)
        if done:
            print("Server is all done.")
            print("Enjoy your game. Don't worry, we've got your back- up!", end='\n')
            print()
            return num

    if not running:
        logfile.close()

def new_player(file_line):
    logging.debug("Identified a player intering the game")
    in_p = re.search(":\s.+\[/", file_line) #COMMENT: Get the name of player joining.
    in_player = in_p.group() #COMMENT: Converting username match object to string.
    in_player = in_player.replace(":","").replace("[/","")[1:] #COMMENT: Removing extra characters and one space.
    logging.debug(f"Player was: {in_player}")

    #COMMENT: Player that is already in the game, can not enter in the game again.
    if in_player in player_list:
        print("It looks like someone is trying to join the game, that is already in the game")
    else:
        #COMMENT: Add player to player list.
        player_list.append(in_player)
        logging.info(f"{in_player} logg in recorded.")

def player_leaving(file_line):
    logging.debug("Identified a player leaving the game")
    o = re.search(":\s.+left", file_line) #COMMENT: Get the name of player leaving
    out_player = o.group().replace("left", "")[2:][:-1] #COMMENT: Converting player match--
    logging.debug(f"Player was: {out_player}")#          --object as string & removing extra spaces
    if out_player in player_list:
        #COMMENT: Remove player from player list.
        player_list.remove(out_player)
        logging.info(f"{out_player} logg out recorded.")
    else:
        #COMMENT: Players who are not in the game, can not leave the game.
        logging.error("It looks like someone has left the game without logging in before hand.")

def sendToSpigotScreen(command):
    """Send command to Minecraft server, in it's respective screen sesion."""
    os.system(f'Screen -S server -p 0 -X stuff "`printf "{command}\r"`"')

def countDown(parsed_args):
    """Wars players in game that server will be restarting soon."""
    global thirty
    current_time = datetime.datetime.now()

    #COMMENT: Print inishal reboot warning. Only at the 30 minet mark.
    if current_time.minute == 30:
        sendToSpigotScreen('say Server will undergo regularly sedueld maitnace in 30 Minetes.')
        sendToSpigotScreen('say It will only be down for a few seconds.')
        sendToSpigotScreen('say You can keep playing normaly, we will provide a countdow.')
        thirty.remove(current_time.minute)

    #COMMENT: Continues to remind until the 60 second mark.
    if current_time.minute in thirty:
        sendToSpigotScreen(f'say Server will reboot in {60 - current_time.minute} minutes')
        thirty.remove(current_time.minute)
    if current_time.minute == 59:
        backUp(parsed_args)
        #COMMENT: Backup at 60 second mark.

def armBackupSystem():
    """Caculate the date of following Saturday."""
    date = datetime.date.today()
    week_num = date.isoweekday()
    days_till_satueday = None

    #COMMENT: Caculate time delta of number of days until next Saturday.
    if 6 - week_num < 0:
        #COMMENT: If week day is already Saturday or Sunday
        days_till_satueday = 7
    else:
        #COMMENT: How many days from today is day number 6.
        days_till_satueday = 6 - week_num #COMMENT: Saturday is 6 in isoweekday

    tdelta = datetime.timedelta(days_till_satueday) 
    return date + tdelta
    #COMMENT: Today + days_till_satueday

def backUp(parsed_args):
    sendToSpigotScreen(f'say Server will reboot in 60 seconds!')
    time.sleep(60)
    sendToSpigotScreen('stop') #COMMENT: Stoping the Minecraft server with this command.
    time.sleep(5)
    
    global v_number
    today = datetime.datetime.now()
    new_folder = today.strftime("%m-%d-%Y") + f'_{v_number.group()[8:]}'
    #COMMENT: Backup folder name = todays date + game version number.

    os.chdir(parsed_args.game_folder)
    backup_location = os.path.join(parsed_args.backup_location, new_folder) #COMMENT: Build
    os.mkdir(backup_location)                                     # backup location string

    subprocess.call(f"cp -R world {os.path.join(backup_location, 'worldB')}", shell=True)
    subprocess.call(f"cp -R world_nether {os.path.join(backup_location, 'world_netherB')}", shell=True)
    subprocess.call(f"cp -R world_the_end {os.path.join(backup_location, 'world_the_endB')}", shell=True)

    logging.info(f'Worlds copyed to {backup_location}.')

    #COMMENT: Rebot server
    # Reseting all variabels for next seesion
    # Then restarting minecraft server on last line.
    global start_time
    global end_time
    global thirty
    global backUpDate
    global player_list
    global game_time
    #Comment: v_number is set to glbal
    #     on the top of this function 

    start_time = datetime.datetime.today()
    end_time = datetime.datetime.today()
    thirty = [30,40,50,55,56,57,58]
    backUpDate = None
    player_list = []
    game_time = 0
    v_number = 0
    sendToSpigotScreen('java -Xms1G -Xmx1G -XX:+UseG1GC -jar spigot.jar nogui')

if __name__ == '__main__':
    main(sys.argv[1:])