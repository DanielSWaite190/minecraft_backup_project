#!/bin/sh

cd "$( dirname "$0" )"
screen -d -m -S server java -Xms1G -Xmx1G -XX:+UseG1GC -jar spigot.jar nogui
screen -d -m -S backup python server_backup_skript.py latest.log game ~/Desktop/
