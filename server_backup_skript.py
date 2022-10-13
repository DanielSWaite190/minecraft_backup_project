"""
CYCLE TEST
CYCLE TEST
CYCLE TEST
"""
VERSION_NUMBER = '1.1.1 (cycle test)'

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
Global variables that will be manipulated by various functions
Not sure how "pythonic" this is. Am open to refactoring once
I learn a better way
"""
start_time = datetime.datetime.today()
end_time = datetime.datetime.today()
thirty = True
forty = [40,50,55,56,57,58]
backUpDate = None
player_list = []
game_time = 0
#v_number
running = True


# logg_level = logging.critical
logging.basicConfig(level=logging.DEBUG, #filename="backup.log",
    format="[%(asctime)s]  %(message)s")

def create_parser():
    """Creates parser var with data passed into terminal."""
    parser = argparse.ArgumentParser(description="Copies Minecraft world folder" + 
        "every week, if sufficient game time has been loged.")
    parser.add_argument("game_folder", help="Minecraft root game folder")
    parser.add_argument("backup_location", help="Location of new zipped backup")
    return parser

def signal_handler(sig_num, frame):
    """Catches quit signals"""
    global running
    running = False
    logfile.close()
    print()
    print("Closed")
    print()
    

def main(args):
    """Main function holding the master while loop."""
    signal.signal(signal.SIGINT, signal_handler)
    parser = create_parser()
    if not args:
        parser.print_usage()
        sys.exit(1)
    parsed_args = parser.parse_args(args)
    p_logg_file = os.path.abspath(os.path.join(parsed_args.game_folder, 'logs/latest.log'))
    # COMMENT: Pulling logs/latest out of game folder for easy indexing.

    print()
    print(f"---   Minecraft Backup   ---")
    print(f'---   Version {VERSION_NUMBER}')
    global logfile
    global v_number

    while running:
        logfile=open(p_logg_file, 'r')                  #COMMENT: Open MC log file
        v_number = initiate()            #COMMENT: Finds game version number
        read(parsed_args)   #Comment: Main loop that writes to player list
        reset_vars()                            #COMMENT: Reset all global variables
        logfile.close()
        os.system('screen -d -m -S server java -Xms1G -Xmx1G -XX:+UseG1GC -jar spigot.jar nogui')

        if not running:
            logfile.close()
            break
        #COMMENT: Checking for exit signal before sleeping
        time.sleep(30)

def initiate():
    """Pre while loop that confirms legitimate Minecraft log file."""
    while running:
        # num = None
        line = '' #COMMENT: Clear variable for next line
        #COMMENT: Reads the lates line from the file and saves it to var line.
        logline=logfile.readline()
        time.sleep(0.125) #COMMENT: Slows down refresh for performance reasons.
        if logline:
            line = logline
        
        #COMMENT: Each Minecraft log file starts with a version number. This checks for that 
        #         verifying a true MC log file.
        game_version = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\sStarting minecraft server version\s\d+.\d+.\d+", line)
        if game_version:
            num = re.search('version\s\d+.\d+.\d+', line)
            print('Waiting on server...')
        
        #COMMENT: Return to main function once server is done loading.
        done = re.search("! For help, type \"help\"", line)
        if done:
            print("Server is all done.")
            print("Enjoy your game. Don't worry, we've got your back- up!", end='\n')
            sendToSpigotScreen('say Backup program initiated')
            print()
            return num

def read(parsed_args):
    """Main while loop that keeps track of players in the game"""
    while running:
        global backUpDate
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
            print(player_list, end='\n \n') #OUT FOR LOGING

            #COMMENT: When player list goes from 0 to 1, save current time.
            if len(player_list) == 1:
                global start_time
                start_time = datetime.datetime.now()

        #COMMENT: Building model form information in log file
        if log_out:
            player_leaving(line)
            print(player_list, end='\n \n') #OUT FOR LOGING

            #COMMENT: When player list goes from 1 to 0, save current time
                    # and calculate total player time for that session.
            if len(player_list) == 0:
                global end_time
                global game_time
                end_time = datetime.datetime.now()
                game_time_delta = end_time - start_time #COMMENT: Total game time
                game_time += round(game_time_delta.seconds) #COMMENT: Turns game time delta into int
                logging.info(f"Total play time {round(game_time/60)} minutes.") #OUT FOR LOGING 
                if backUpDate == None and game_time/60 >= 2:
                    backUpDate = armBackupSystem()
                    logging.info('Backup armed!') #OUT FOR LOGING
                    logging.info(f'Backup will commence in 60 seconds.') #COMMENT: Technically it commences
                                                                            # on the next day at 00:00 but whatever.
                                                                             #OUT FOR LOGING
                    
        #COMMENT: On scheduled date at 11pm start countdown.                                                                     
        if datetime.date.today() == backUpDate:
        #    datetime.datetime.now().time().hour == 23:
            rreturn = countDown(parsed_args)
            if rreturn == 0:
                return

def new_player(file_line):
    """Finds and stores the name of new players entering the game."""
    logging.debug("Identified a player entering the game") #OUT FOR LOGING
    in_p = re.search(":\s.+\[/", file_line) #COMMENT: Get the name of player joining.
    in_player = in_p.group() #COMMENT: Converting username match object to string.
    in_player = in_player.replace(":","").replace("[/","")[1:] #COMMENT: Removing extra characters and one space.
    logging.debug(f"Player was: {in_player}") #OUT FOR LOGING

    #COMMENT: Player that is already in the game, can not enter in the game again.
    if in_player in player_list:
        print("It looks like someone is trying to join the game, that is already in the game") #OUT FOR LOGING
        pass
    else:
        #COMMENT: Add player to player list.
        player_list.append(in_player)
        logging.info(f"{in_player} log in recorded.") #OUT FOR LOGING

def player_leaving(file_line):
    """Finds and stores the name of players leaving the game."""
    logging.debug("Identified a player leaving the game") #OUT FOR LOGING
    o = re.search(":\s.+left", file_line) #COMMENT: Get the name of player leaving
    out_player = o.group().replace("left", "")[2:][:-1] #COMMENT: Converting player match--
    logging.debug(f"Player was: {out_player}") #OUT FOR LOGING  # --object as string & removing extra spaces
    if out_player in player_list:
        #COMMENT: Remove player from player list.
        player_list.remove(out_player)
        logging.info(f"{out_player} log out recorded.") #OUT FOR LOGING
    else:
        #COMMENT: Players who are not in the game, can not leave the game.
        logging.error("It looks like someone has left the game without logging in before hand.") #OUT FOR LOGING
        pass

def sendToSpigotScreen(command):
    """Send command to Minecraft server, in its respective screen session."""
    os.system(f'screen -S server -p 0 -X stuff "`printf "{command}\r"`"')

def countDown(parsed_args):
    # """Wars players in game that server will be restarting soon."""
    # global thirty
    # global forty
    # current_time = datetime.datetime.now()

    # #COMMENT: Print initial reboot warning. Only at the 30 minute mark.
    # if current_time.minute == 30 and thirty:
    #     thirty = False
    #     sendToSpigotScreen('say Server will undergo regularly scheduled maintenance in 30 minutes. '+
    #     'It will only be down for a few seconds. You can keep playing normally, we will provide a countdown.')

    # #COMMENT: Continues to remind until the 60 second mark.
    # if current_time.minute in forty:
    #     forty.remove(current_time.minute)
    #     sendToSpigotScreen(f'say Server will reboot in {60 - current_time.minute} minutes')
    # if current_time.minute == 59:
    #     backUp(parsed_args)
    #     return 0


    backUp(parsed_args)
    return 0
    #COMMENT: Backup at 60 second mark,
    #   Then hand control back to backUp() > read() > main().
    
def armBackupSystem():
    """Calculate the date of following Saturday."""
    date = datetime.date.today()
    week_num = date.isoweekday()
    days_till_saturday = None

    # COMMENT: Calculate time delta for number of days until next Monday.
    if 6 - week_num < 0:
        #COMMENT: If week day is already Saturday or Sunday
        days_till_saturday = 7
    else:
        #COMMENT: How many days from today is day number 6.
        days_till_saturday = 6 - week_num #COMMENT: Saturday is 6 in isoweekday

    tdelta = datetime.timedelta(days_till_saturday) 
    # return date + tdelta
    return date
    #COMMENT: Today + days_till_satueday

def backUp(parsed_args):
    """Copies Minecraft world folders to designated destination."""
    sendToSpigotScreen(f'say Server will reboot in 60 seconds!')
    time.sleep(60)
    sendToSpigotScreen('stop') #COMMENT: Stoping the Minecraft server with this command.
    time.sleep(4)
    
    today = datetime.datetime.now()
    new_folder = today.strftime("%m-%d-%Y") + f'_{v_number.group()[8:]}'
    #COMMENT: Backup folder name = todays date + game version number.

    backup_location = os.path.join(parsed_args.backup_location, new_folder) #COMMENT: Build
    os.mkdir(backup_location)                                       # backup location path

    os.chdir(parsed_args.game_folder)
    subprocess.call(f"cp -R world {os.path.join(backup_location, 'worldB')}", shell=True)
    subprocess.call(f"cp -R world_nether {os.path.join(backup_location, 'world_netherB')}", shell=True)
    subprocess.call(f"cp -R world_the_end {os.path.join(backup_location, 'world_the_endB')}", shell=True)

    logging.info(f'Worlds copied to {backup_location}.')

def reset_vars():
    """Resets all variables for next backup session."""
    global start_time
    global end_time
    global thirty
    global forty
    global backUpDate
    global player_list
    global game_time
    #COMMENT: global v_number doesn't reset
    #COMMENT: Running is true until program quits

    start_time = datetime.datetime.today()
    end_time = datetime.datetime.today()
    thirty = True
    forty = [40,50,55,56,57,58]
    backUpDate = None
    player_list = []
    game_time = 0
    #COMMENT: v_number = 0
    #COMMENT: logfile doesn't need to be reset.    

if __name__ == '__main__':
    main(sys.argv[1:])