import re

with open ("test.log", "r") as file:
  for line in file:
      match = re.search("logged in", line)
      # match = re.search("\[Server thread/INFO]: .+ \[\d", line)
      if match:
          print(line)
