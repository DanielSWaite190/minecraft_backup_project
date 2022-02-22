#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""
__author__ = "Daniel S. Waite"

import argparse
import datetime
import logging
import signal
import time
import sys
import os
import re

directory_model = {}
exit_flag = False

logging.basicConfig(
    format="%(asctime)s %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_parser():
    """Creates parsing arguments."""

    parser = argparse.ArgumentParser(
        description="Searches a given directory for a specific line of text")
    parser.add_argument(
        "directory", help="The directory that will be scaned for magic" +
        "stringt")
    parser.add_argument("magic_string", help="The text that will be searched")
    parser.add_argument(
        "--polling_interva", "-p", default=1,
        help="How many times program refreshes in seconds. Default is 1")
    parser.add_argument(
        "--file_extension", "-e", default=".txt",
        help="File extension of file to search. Default is .txt")
    return parser


def signal_handler(sig_num, frame):
    """Catches quit signals"""
    global exit_flag
    logger.warning('Received ' + signal.Signals(sig_num).name)
    logger.warning(sig_num)
    exit_flag = True
    return None


def main(args):
    """The main while loop that runs the program"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = create_parser()
    if not args:
        parser.print_usage()
        # sys.exit(1)

    parsed_args = parser.parse_args(args)

    start_time = datetime.datetime.now()
    logger.info(
        "\n" +
        "-" * 105 +
        f"\n\tRunning {__file__}" +
        f"\n\tStarted on {start_time.isoformat()}\n" +
        "-" * 105
    )

    # if not os.path.exists(parsed_args.directory):
    # os.mkdir(parsed_args.directory)

    # Loop number 1
    while not exit_flag:
        try:
            initiate_model(parsed_args.directory, parsed_args.file_extension)

            # Loop number 2
            while not exit_flag:
                sync_model(parsed_args.directory, parsed_args.file_extension)
                read_files(
                    parsed_args.magic_string, parsed_args.directory,
                    parsed_args.file_extension)

                # print(f"Curent Model: {directory_model}")
                time.sleep(float(parsed_args.polling_interva))

        except FileNotFoundError as e:
            logger.error(f"This file do not exist {e}")
        except Exception as e:
            logger.error(e)
            pass

        time.sleep(float(parsed_args.polling_interva))

    up_time = datetime.datetime.now() - start_time
    logger.info(
        "\n" +
        "-" * 105 +
        f"\n\tStop {__file__}" +
        f"\n\tUp time was {up_time}\n" +
        "-" * 105
    )


def initiate_model(directory_location, file_extension):
    """Initializing the directory model at the start of the program"""
    global directory_model
    for item in os.listdir(directory_location):
        # If the item in the for loop is a file and that file has the corect
        #           extension.
        if os.path.isfile(os.path.join(os.path.abspath(
                directory_location), item)) and os.path.splitext(os.path.join(
                    os.path.abspath(
                        directory_location), item))[1] == file_extension:
            directory_model[item] = 0
    # print(f"Initiate Model: {directory_model} \n")


def read_files(magic_string, directory_location, file_extension):
    """Reads all files curently represented in directory model"""
    for file_name in directory_model:
        file_to_open = os.path.join(os.path.abspath(
            directory_location), file_name)
        line_count = 0
        contents = []

        with open(file_to_open, "r") as f:
            for line in f:
                contents.append(line)
            for line in contents[directory_model[file_name]:]:
                match = re.findall("%s" % magic_string, line)
                line_count += 1
                if match:
                    report_magic_text(
                        file_name, directory_model[os.path.basename(
                            file_name)] + line_count)
        if line_count != 0:
            update_model(
                file_to_open, directory_location, file_extension, line_count)
    return


def update_model(file_name, directory_location, file_extension, line_count):
    """Updates the last line read in directory model entrys"""
    global directory_model
    # 1) Update line counts for know files.
    directory_model[os.path.basename(
        file_name)] = directory_model[os.path.basename(file_name)] + line_count
    return


def sync_model(directory_location, file_extension):
    """Rebuilds directory model. Removing and adding entrys where needed"""
    # Check for new file entries, initializing their line counts to zero.
    directory_model_copy = directory_model.copy()
    for item in os.listdir(directory_location):
        # If the item in not already saved in model, is a file and that file
        #   has the corect extension.
        if item not in directory_model_copy.keys():
            if os.path.isfile(os.path.join(os.path.abspath(
                directory_location), item)) and os.path.splitext(os.path.join(
                    os.path.abspath(
                        directory_location), item))[1] == file_extension:
                directory_model[item] = 0
                directory_model_copy[item] = "x"
                logger.info(f"The file {item} was added to your directory.")

    # If files from the directory model are not in actual directory, delete
    #               them from the model.
    for key in directory_model_copy.keys():
        if key not in os.listdir(directory_location):
            del directory_model[key]
            logger.info(f"The file {key} was REMOVED to your directory!")
    return


def report_magic_text(file_name, line_count):
    """Log out magic text and the line it was found on"""
    logger.info(
        f"Magic text was found in the +"
        f"{os.path.basename(file_name)} file, on line {line_count}.")
    return


if __name__ == '__main__':
    main(sys.argv[1:])
