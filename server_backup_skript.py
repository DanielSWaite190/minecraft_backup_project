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
    player_time = datetime.timedelta() 
    with open (parsed_args.logg_file, "r") as file:
        for line in file:
            match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
            if match:
                in_p = re.search(":\s.+\[/", line) #Regex for username string
                in_player = in_p.group() #Saving username string as player
                in_player = in_player.replace(":","").replace("[/","")[1:] #Removing extra characters and one space
                players_model.update({in_player:datetime.datetime.now()})


            match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)
            if match:
                o = re.search(":\s.+left", line) #Regex for username string
                out_player = o.group().replace("left", "")[2:][:-1]
                if out_player in players_model:
                    player_time + datetime.datetime.now()-players_model[out_player]
                    # print(datetime.datetime.now()-players_model[out_player])
                else:
                    #logg this as an erro something
                    print("It looks like someone has left the game without logging in before hand.")

if __name__ == '__main__':
    main(sys.argv[1:])


# os.makedirs(os.path.join(parsed_args.backup_location, f"i_am_daniel"))
