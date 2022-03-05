import subprocess
import subprocess
import argparse
from asyncio.log import logger
import datetime
import logging
import signal
import sys
import os
import re


running = True
armed = False
logg_level = logging.critical

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


def main(args):

# signal.signal(signal.SIGINT, signal_handler)

    parser = create_parser()
    if not args:
        parser.print_usage()
        # sys.exit(1)
    parsed_args = parser.parse_args(args)

    test = 5

    players_model = {}
    player_time = datetime.timedelta() 
    f = subprocess.Popen(['tail','-F',parsed_args.logg_file], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while True:
        line = f.stdout.readline().decode()
        match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
        if match:
            logger.debug("Identified a player intering the game")
            in_p = re.search(":\s.+\[/", line) #Regex for username string
            in_player = in_p.group() #Saving username string as player
            in_player = in_player.replace(":","").replace("[/","")[1:] #Removing extra characters and one space
            logger.debug(f"Player was: {in_player}")
            players_model.update({in_player:datetime.datetime.now()})
            logger.info(f"{in_player} logg in recorded.")

        match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)
        if match:
            logger.debug("Identified a player leaving the game")
            o = re.search(":\s.+left", line) #Regex for username string
            out_player = o.group().replace("left", "")[2:][:-1]
            logger.debug(f"Player was: {out_player}")
            if out_player in players_model:
                player_time + datetime.datetime.now()-players_model[out_player]
                        # print(datetime.datetime.now()-players_model[out_player])
                logger.info(f"{in_player} logg out recorded.")
                logger.info(f"{in_player} play time: {player_time}") #Doesn't work unles runnign in real time.
                print()#Block seperation

            else:
                #logg this as an erro something
                logger.error("It looks like someone has left the game without logging in before hand.")
                print() #Block seperation

if __name__ == '__main__':
    main(sys.argv[1:])


# os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))
