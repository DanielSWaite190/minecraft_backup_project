import argparse
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

    players = {}

    with open (parsed_args.logg_file, "r") as file:
        for line in file:
            match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
            if match:
                player = re.search(":\s.+\[/", line)
                time_stamp = re.search("\d+:\d+:\d+", line)
                players.update({player.group():time_stamp.group()})
                

                # os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))
                # print("dezz nuts!")
    print(players)


if __name__ == '__main__':
    main(sys.argv[1:])
