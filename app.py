#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps.
# Created by revox 2020-2021
# Modifications made by Robert Furr (robtech21) and YeahNotSewerSide
# Mining Pools added by mkursadulusoy - 2021-09-06

import hashlib
from posixpath import split
import sys
import os
from os import mkdir
from pathlib import Path
from socket import socket
import sys  # Only python3 included libraries
import time
import random
import requests
from threading import Thread
from array import *
import configparser


config = configparser.ConfigParser()
DATA = 'Setting'

if not Path(DATA).is_dir():
            mkdir(DATA)
            
if not Path('Setting/settings.cfg').is_file():           
    #usernames = input('Username: ')
    #threads = int(input('Number of threads(0 by default): '))
    #if threads == 0:
     #   threads = 10
    #identifier = int(input('Identifier(0 by default): '))
    #if identifier == 0:
     #   identifier = str('Arduino')
    config['Setting']={'usernames':'dechimmo1official',
                       'threads':'6',
                        'identifier':'Arduino'
                        }

usernames = config["Setting"]['usernames']
threads = int(config["Setting"]['threads'])
identifier = str(config["Setting"]["identifier"])
usernames = [usernames]

'''
if not Path("Setting/ids.txt")==False:
    with open("Setting/ids.txt", "w") as file:
        for lines in range(10000):
            file.write(random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef') + '\n')
'''

#with open("Setting/ids.txt") as file:



def minerok(i,usernames):
    ids = ''
    shares = 0
    sleep = 0.012
    username=usernames
    soc = socket()
    def current_time():
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        return current_time

    for i in range(0, threads):
        ids = random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')+random.choice('0123456789abcdef')

    UseLowerDiff = True
    chipID = ids
    devicename = identifier+'-'+ str(i)
    print('Thread', i,f'{current_time()} : HI ' + username + " on this crazy miner with chipID of: " + chipID)

    def fetch_pools():
        while True:
            try:
                response = requests.get(
                    "https://server.duinocoin.com/getPool"
                ).json()
                NODE_ADDRESS = response["ip"]
                NODE_PORT = response["port"]

                return NODE_ADDRESS, NODE_PORT
            except Exception as e:
                print('Thread', i,f'{current_time()} : Error retrieving mining node, retrying in 15s')
                time.sleep(15)


    while True:
        try:
            print('Thread', i,f'{current_time()} : Searching for fastest connection to the server')
            try:
                NODE_ADDRESS, NODE_PORT = fetch_pools()
            except Exception as e:
                NODE_ADDRESS = "server.duinocoin.com"
                NODE_PORT = 2813
                print('Thread', i,f'{current_time()} : Using default server port and address')
            try:
                soc.connect((str(NODE_ADDRESS), int(NODE_PORT)))
            except Exception as e:
                print('')
            print('Thread', i,f'{current_time()} : Fastest connection found')
            server_version = soc.recv(100).decode()
            print('Thread', i,f'{current_time()} : Server Version: ' + server_version)
            # Mining section
            while True:
                if UseLowerDiff:
                    # Send job request for lower diff
                    soc.send(bytes(
                        "JOB,"
                        + str(username)
                        + ",AVR",
                        encoding="utf8"))
                else:

                    # Send job request
                    soc.send(bytes(
                        "JOB,"
                        + str(username),
                        encoding="utf8"))

                # Receive work
                time.sleep(0.5)
                job = soc.recv(1024).decode().rstrip("\n")
                # Split received data to job and difficulty
                job = job.split(",")
                difficulty = job[2]

                hashingStartTime = time.time()
                base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
                temp_hash = None
                #print (f'{current_time()} : job: ', job)
                for result in range(100 * int(difficulty) + 1):
                    # Calculate hash with difficulty
                    temp_hash = base_hash.copy()
                    temp_hash.update(str(result).encode('ascii'))
                    ducos1 = temp_hash.hexdigest()
                    #print (ducos1)
                    # If hash is even with expected hash result
                    if (job[1] == ducos1):
                        time.sleep(result * sleep)
                        hashingStopTime = time.time()
                        timeDifference = hashingStopTime - hashingStartTime

                        hashrate = result / (timeDifference)
                        if  (hashrate < 232):
                            #140, 178, 219, print ('Thr', str(i).zfill(3), "Uping hashrate", sleep)
                            sleep = sleep * 0.6
                        if (hashrate > 290):
                            sleep = sleep * 1.3
                            #print('Thr', str(i).zfill(3), "Lowering hashrate", sleep)
                        # Send numeric result to the server
                        soc.send(bytes(str(result) + "," + str(
                            hashrate) + "," + "Official AVR miner 3.0" + "," + devicename + "," + "DUCOID" + chipID,
                                       encoding="utf8"))

                        # Get feedback about the result
                        feedback = soc.recv(1024).decode().rstrip("\n")

                        # If result was good
                        if feedback == "GOOD":
                            shares = shares + 1
                            print('Thread', str(i).zfill(3),"user:", username, ":",f'{current_time()} - good |', chipID,
                                  "|",int(hashrate),
                                  "H/s",
                                  "| Diff",
                                  difficulty, "| shrs:", shares )
                            break
                        # If result was incorrect
                        elif feedback != "GOOD":
                            print('Thread', str(i).zfill(3),"user:", username, ":",f'{current_time()} - rjct |', chipID,
                                  "|",
                                  int(hashrate),
                                  "H/s",
                                  "| Diff",
                                  difficulty,"| res:" ,result, feedback )


                        break

        except Exception as e:
            print('Thread', i,f'{current_time()} : Error occured: ' + str(e) + ", restarting in 5s.")
            time.sleep(5)
            os.execl(sys.executable, sys.executable, *sys.argv)

for i in range(threads*len(usernames)):
    th = Thread(target=minerok, args=(i, usernames[i//threads]))
    th.start()
    time.sleep(4)
