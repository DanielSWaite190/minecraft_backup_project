import subprocess
import argparse
import datetime
import logging
import logging
import signal
import time
import sys
import os
import re

backUpDate = None
# logg_level = logging.critical

logging.basicConfig(level=logging.DEBUG, #filename="backup.log",
    format="[Backup Server Program] [%(levelname)s]: %(message)s")

def create_parser():
    parser = argparse.ArgumentParser(description="Copies Minecragt world folder" + 
        "evry week, or when sufficent game time has been loged.")
    parser.add_argument("logg_file", help="Minecraft logg file of server to backup")
    parser.add_argument("game_folder", help="Minecraft wolrd folder to be backedup")
    parser.add_argument("backup_location", help="Location of new ziped backup")
    return parser


def signal_handler(sig_num, frame):
    """Catches quit signals"""
    # global running
    running = False
    return None

# Global variabels that will be manipulated by various functions
# Not sure how "pythonic" this is. Am open to refactoring once
#I learn a better way
player_list = []
start_time = datetime.datetime.today()
end_time = datetime.datetime.today()
game_time = 0

def main(args):
# signal.signal(signal.SIGINT, signal_handler)
    parser = create_parser()
    if not args:
        parser.print_usage()
        # sys.exit(1)
    parsed_args = parser.parse_args(args)

    logfile=open(parsed_args.logg_file, 'r')
    while True:
        line = '' #Clear variable for next line
        logline=logfile.readline()
        time.sleep(1) #Slows down refresh for performance reasons.
        if logline:
            line = logline

        log_in = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
        log_out = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)
        # versionNum = re.search("Starting minecraft server version \d+.\d+.\d+", line)

        #Building model form information in log file
        if log_in:
            new_player(line)
            print(player_list, end='\n \n') #Make loger.debug

            if len(player_list) == 1:
                global start_time
                start_time = datetime.datetime.now()

        if log_out:
            player_leaving(line)
            print(player_list, end='\n \n') #Make loger.debug

            if len(player_list) == 0:
                global end_time
                global game_time
                end_time = datetime.datetime.now()
                game_time_delta = end_time - start_time #game time delta
                game_time += round(game_time_delta.seconds)    #Truns game time delta into int
                logging.info(f"Total play time {round(game_time/60)} minutes.")
                if game_time/60 >= 30:
                    global backUpDate
                    backUpDate = armBackupSystem() # <--- Change to 'Next BackUp Date'
                    logging.info('Backup armed')
            
        if datetime.date.today() == backUpDate:
            countDown(parsed_args)

def new_player(file_line):
    logging.debug("Identified a player intering the game")
    in_p = re.search(":\s.+\[/", file_line) #Regex for username string
    in_player = in_p.group() #Converting username match object as string
    in_player = in_player.replace(":","").replace("[/","")[1:] #Removing extra characters and one space
    logging.debug(f"Player was: {in_player}")

    if in_player in player_list:
        print("It looks like someone is trying to join the game, that is already in the game")
    else:
        player_list.append(in_player)
        logging.info(f"{in_player} logg in recorded.")

def player_leaving(file_line):
    logging.debug("Identified a player leaving the game")
    o = re.search(":\s.+left", file_line) #Finding the exact player that is leaving
    out_player = o.group().replace("left", "")[2:][:-1] #Converting player match--
    logging.debug(f"Player was: {out_player}")#          --object as string & removing extra spaces
    if out_player in player_list:
        player_list.remove(out_player)
        logging.info(f"{out_player} logg out recorded.")
    else:
        logging.error("It looks like someone has left the game without logging in before hand.")

def sendSpigotCommand(command):
    os.system(f'Screen -S server -p 0 -X stuff "`printf "{command}\r"`"')

def countDown(parsed_args):
    current_time = datetime.datetime.now()
    thirty = [30,40,50,55,56,57,58]
    if current_time.minute in thirty:
        sendSpigotCommand(f'say Server will reboot in {60 - current_time.minute} minutes')
        thirty.remove(current_time.minute)
    if current_time.minute == 59:
        backUp(parsed_args)

def armBackupSystem():
    date = datetime.date.today()
    week_num = date.isoweekday()
    days_till_satueday = None

    if 5 - week_num < 0:
        days_till_satueday = 6
    else:
        days_till_satueday = 5 - week_num

    tdelta = datetime.timedelta(days_till_satueday) 
    return date + tdelta

def backUp(parsed_args):
    sendSpigotCommand(f'say Server will reboot in 60 seconds!')
    time.sleep(60)
    sendSpigotCommand('stop')
    time.sleep(5)
    
    today = datetime.datetime.now()
    new_folder = today.strftime("%m-%d-%Y")

    os.chdir(parsed_args.game_folder)
    backup_location = os.path.join(parsed_args.backup_location, new_folder)
    os.mkdir(backup_location) #date and version

    subprocess.call(f"cp -R world {os.path.join(backup_location, 'worldB')}", shell=True)
    subprocess.call(f"cp -R world_nether {os.path.join(backup_location, 'world_netherB')}", shell=True)
    subprocess.call(f"cp -R world_the_end {os.path.join(backup_location, 'world_the_endB')}", shell=True)
    #Rebot server
    sendSpigotCommand('screen -d -m -S server java -Xms1G -Xmx1G -XX:+UseG1GC -jar spigot.jar nogui')

if __name__ == '__main__':
    main(sys.argv[1:])