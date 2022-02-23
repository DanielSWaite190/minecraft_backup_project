import re
from time import time

with open ("test.log", "r") as file:
  for line in file:
      match = re.search("\[\d+:\d+:\d+\]\s\[Server thread/INFO]:\s.+left\sthe\sgame", line)
      if match:
        print(line)
        p = re.search(":\s.+left", line) #Regex for username string
        print(p.group())

"""[17:43:12] [Server thread/INFO]: Undeflned left the game"""


