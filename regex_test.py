import re

with open ("test.log", "r") as file:
  t = ''
  for line in file:
      # match = re.search("logged in", line)
      # match = re.search("\[\d+:\d+:\d\]\s\[Server thread/INFO]: .+ \[", line)
      match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
      if match:
        print(line)
        time_stamp = re.search("\[\d+:\d+:\d+\]", line)
        print(time_stamp.group())

""" [17:42:52] [Server thread/INFO]: Undeflned[/127.0.0.1:64839] logged in with entity id 173 at ([world]-1.300000011920929, 92.0, 13.00493822884077) """


      # time_stamp = re.search("\[\d+:\d+:\d+\]", line)
