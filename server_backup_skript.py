import subprocess
import argparse
import datetime
import logging
import logging
import signal
import sys
import os
import re
from tracemalloc import start

backingUp = None
# logg_level = logging.critical

logging.basicConfig(level=logging.DEBUG, #filename="backup.log",
    format="[Backup Server Program] [%(levelname)s]: %(message)s")

def create_parser():
    parser = argparse.ArgumentParser(description="Copies Minecragt world folder evry week, or when sufficent game time has been loged.")
    parser.add_argument("logg_file", help="Minecraft logg file of server to backup")
    parser.add_argument("word_folder", help="Minecraft wolrd folder to be backedup")
    parser.add_argument("backup_location", help="Location of new ziped backup")
    return parser


def signal_handler(sig_num, frame):
    """Catches quit signals"""
    # global running
    running = False
    return None

# Global variabels that will be manipulated by various functions
# Not sure how pythonic this is- am open to refactoring once
#    I learn a better way
player_list = []
start_time = None
end_time = None
def main(args):
# signal.signal(signal.SIGINT, signal_handler)
    parser = create_parser()
    if not args:
        parser.print_usage()
        # sys.exit(1)
    parsed_args = parser.parse_args(args)

    f = subprocess.Popen(['tail','-F',parsed_args.logg_file], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while True:     
        line = f.stdout.readline().decode()
        log_in = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
        log_out = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)

        #Building model form information in log file
        if log_in:
            new_player(line)
            print(player_list, end='\n \n') #Make loger.debug
        if log_out:
            player_leaving(line)
            print(player_list, end='\n \n') #Make loger.debug
        
        #Keep track of how long the server is active
        if len(player_list) == 1:
            global start_time
            start_time = datetime.datetime.now()
        if len(player_list) == 0:
            global end_time
            end_time = datetime.datetime.now()
            game_time = end_time - start_time
            logging.info(f"Total play time: {game_time.seconds/60}")
            if game_time.seconds/60 >= 30:
                global backingUp
                backingUp = armBackupSystem()

        if datetime.date.today() == backingUp:
            countDown()

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


def countDown():
    x = datetime.datetime.now()
    # x = datetime.time(10,10,10)
    thirty = [30,40,50,55,56,57,58,59]
    if x.minute in thirty:
        sendSpigotCommand(f'Server will reboot in {60 - x.minute} minutes')
        thirty.remove(x.minute)
    if x.minute == 00:
        backUp()

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

def backUp():
    pass

if __name__ == '__main__':
    main(sys.argv[1:])

# os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))
