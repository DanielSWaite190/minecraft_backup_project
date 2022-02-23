import argparse
import datetime
import signal
import sys
import os
import re


running = True

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

    with open (parsed_args.logg_file, "r") as file:
        for line in file:
            match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
            if match:
                p = re.search(":\s.+\[/", line) #Regex for username string
                t = re.search("\d+:\d+:\d+", line) #Regex for time string

                player = p.group() #Saving username string as player
                time_string = t.group() #Saving time string as time_string

                hours = int(time_string[0:2])
                minute = int(time_string[3:5])
                second = int(time_string[6:8])

                time_stamp = datetime.timedelta(hours=hours, minutes=minute, seconds=second)
                fiv_minets = datetime.timedelta(hours=17, minutes=55, seconds=18)

                # time_stamp = datetime.datetime(hours, minute, second)
                # fiv_minets = datetime.datetime(17, 55, 18)

                players_model.update({player:time_stamp})
                # os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))

    # print(time_stamp)
    # print(fiv_minets)

    x = players_model.get(": Undeflned[/'")

    # print(fiv_minets-time_stamp)
    # print(players_model.get(": Undeflned[/'"))
    print(fiv_minets - time_stamp)

if __name__ == '__main__':
    main(sys.argv[1:])
