import subprocess
import re
file = 'log_files/minecraft.log'

import subprocess
f = subprocess.Popen(['tail','-F',file], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
while True:
    line = f.stdout.readline().decode()
    print(line)

    match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+\[/\d+.\d+.\d+.\d:\d+\]\slogged in", line)
    if match:
      print("Identified a player intering the game")

    match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)
    if match:
      print("Identified a player leaving the game")
      break