import argparse
import datetime
import signal
import sys
import os
import re


running = True
armed = False

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


    players_model = {}
    player_time = 0
    with open (parsed_args.logg_file, "r") as file:
        for line in file:
            match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
            if match:
                p = re.search(":\s.+\[/", line) #Regex for username string
                player = p.group() #Saving username string as player
                player = player.replace(":","").replace("[/","")[1:] #Removing extra characters and one space
                players_model.update({player:datetime.datetime.now()})


            match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)
            if match:
                l = re.search(":\s.+left", line) #Regex for username string
                lef = l.group().replace("left", "")[2:]
                print(lef)

    print(player)
    print(lef)
    print(players_model)

if __name__ == '__main__':
    main(sys.argv[1:])


# os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))
