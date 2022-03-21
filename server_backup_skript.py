import subprocess
import argparse
import logging
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


player_list = []
# start_time = 0
start_time = datetime.datetime.now()
end_time = 0
game_time = 0

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

        if log_in:
            new_player(line)
            print(player_list)
            print()#space

        if log_out:
            player_leaving(line)
            print(player_list)
            print()#space
            
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
    
    if len(player_list) == 1:
        start_time = datetime.datetime.now()
        start_time == 1 #A cheat to get start_time to work on the above line. NEEDS TO BE RESOLVED


def player_leaving(file_line):
            logging.debug("Identified a player leaving the game")
            o = re.search(":\s.+left", file_line) #Finding the exact player that is leaving
            out_player = o.group().replace("left", "")[2:][:-1] #Converting player match--
            logging.debug(f"Player was: {out_player}")#          --object as string & removing extra spaces
            if out_player in player_list:
                player_list.remove(out_player)
                logging.info(f"{out_player} logg out recorded.")

                if len(player_list) == 0:
                    end_time = datetime.datetime.now()
                    game_time = end_time - start_time
                    logging.info(f"Total play time: {game_time}")
            else:
                logging.error("It looks like someone has left the game without logging in before hand.")


if __name__ == '__main__':
    main(sys.argv[1:])

# os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))
