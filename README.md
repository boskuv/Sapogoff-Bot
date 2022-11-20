# Sapogoff-Bot
TG bot which acts as event reminder

## Motivation
The idea appeared while WORLD CUP 2022 to remind about future matches 

## Quick Start
- `$ mkdir db` 
- `$ touch db/matches.db`
- `$ cp bot.ini.example bot.ini`
- `$ sudo chmod a+rw db db/*`
- add your token, chats and admin id to 'bot.ini'
- run a docker container, using compose `docker-compose up -d`