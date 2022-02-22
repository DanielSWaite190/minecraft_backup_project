import re
from time import time

with open ("test.log", "r") as file:
  for line in file:
      match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
      if match:
        time_stamp = re.search("\d+:\d+:\d+", line)
        player = re.search(":\s.+\[/", line)
        # print(player.group())
        print(time_stamp.group())

""" [17:42:52] [Server thread/INFO]: Undeflned[/127.0.0.1:64839] logged in with entity id 173 at ([world]-1.300000011920929, 92.0, 13.00493822884077) """


      # time_stamp = re.search("\[\d+:\d+:\d+\]", line)
