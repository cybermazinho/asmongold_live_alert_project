import serial
import time
import json
import aiohttp
import asyncio
import requests
import socket
import re
import threading
import os

HOST = "irc.twitch.tv"
PORT = 6667
NICK = "your_nick"
PASS = "your_pass"  
CHANNEL = "#zackrawrr"
CHAT_MSG_REGEX = re.compile(r":(.+)!.* PRIVMSG " + CHANNEL + " :(.+)")

channel_name = 'zackrawrr'
wow_name = "name_friend"
asmongoldLive = False
wow_online = False 

def arduino_online(asmongold, wow, message):
    serial_port = serial.Serial('you_serial_port', 9600)
    time.sleep(2)
    send_info = {"asmongold": asmongold, "wow": wow, "message": message}
    json_string = json.dumps(send_info)
    serial_port.write((json_string + '\n').encode())
    print("Asmongold:", asmongold, "WOW:", wow, "Message:", message)
    serial_port.close()

async def wow_info(asmongold):
    global wow_online
    url = f'https://armory.warmane.com/api/character/{wow_name}/Icecrown/summary'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                dates = await res.json()
                wow_online = dates["online"]
                arduino_online(asmongold, dates["online"], "loading...")
    except Exception as e:
        print(f"Error: {e}")

async def check_live():
    global asmongoldLive
    response = requests.get(f'https://www.twitch.tv/{channel_name}')
    if 'isLiveBroadcast' in response.text:
        asmongoldLive = True
        await wow_info(True) 
    else:
        asmongoldLive = True
        await wow_info(False) 

def send_pong(sock):
    sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

def connect_twitch():
    sock = socket.socket()
    sock.connect((HOST, PORT))
    sock.send("PASS {}\r\n".format(PASS).encode("utf-8"))
    sock.send("NICK {}\r\n".format(NICK).encode("utf-8"))
    sock.send("JOIN {}\r\n".format(CHANNEL).encode("utf-8"))
    return sock

def parse_chat_message(msg):
    match = CHAT_MSG_REGEX.match(msg)
    if match:
        username = match.group(1)
        message = match.group(2)
        if len(message) < 18 :
            arduino_online(asmongoldLive, wow_online, message)

def listen_twitch_chat(sock):
    last_message_time = time.time()

    while True:
        resp = sock.recv(2048).decode("utf-8")
        if resp.startswith("PING"):
            send_pong(sock)
        elif "PRIVMSG" in resp:
            current_time = time.time()
            time_since_last_message = current_time - last_message_time

            if time_since_last_message >= 10:
                parse_chat_message(resp)
                last_message_time = current_time

async def main():
    twitch_socket = connect_twitch()
    chat_listener_thread = threading.Thread(target=listen_twitch_chat, args=(twitch_socket,))
    chat_listener_thread.start()
    while True:
        await check_live()
        await asyncio.sleep(60) 

if __name__ == "__main__":
    asyncio.run(main())

