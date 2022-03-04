import subprocess
file = 'log_files/grow.log'

import subprocess
f = subprocess.Popen(['tail','-F',file],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
while True:
    line = f.stdout.readline().decode()
    print(line)
    if line == 'water\n':
      print("HERE!")
