import asyncio
import threading

import requests
import websocket
from blessed import Terminal

term = Terminal()

instance = 'http://localhost:3000'
wss_instance = 'ws://localhost:8080'

uname = input('Enter a username: ')

user_req = requests.get(instance + '/user/' + uname)
if (user_req.status_code == 404):
    promptAnswer = input(
        "That username isn't taken. Would you like to register it? (y/n) ")
    if (not ('y' in promptAnswer)):
        print('Quitting...')
        exit()

    res = requests.post(instance + '/register', json={"name": uname})

    if (not res.ok):
        print('An error occured while trying to register. Please try again.')
        exit()

    user_req = res


current_user = user_req.json()

guildsReq = requests.get(instance + '/guilds/' + current_user['name'])

guilds = guildsReq.json()

current_channel = guilds['data'][0]['channels'][0]
current_server = guilds['data'][0]

msgText = ''


def show_msg_view():
    global msgText
    with term.fullscreen():
        while (True):
            msg = None
            print(term.clear())
            print(msgText)
            with term.location(0, term.height - 1):
                msg = input('[#' + current_channel['name'] + ' in ' +
                            term.bold(current_server['name']) + '] ')
                if (msg.startswith('/')):
                    process_command(msg.replace('/', '').split(' '))
                    break
                requests.post(instance + '/message/' +
                              current_channel['id'] + '/' + current_user['id'], json={'content': msg})
                msgText = msgText + '\n' + \
                    term.goldenrod(
                        term.bold(current_user['name'])) + ': ' + msg
            print(term.clear())
            msg = None


def refresh_msg_view():
    with term.fullscreen():
        print(term.clear())
        print(msgText)
        with term.location(0, term.height - 1):
            print('[#' + current_channel['name'] + ' in ' +
                  term.bold(current_server['name']) + '] ')


def process_command(vals):
    global msgText
    if (vals[0] == 'help'):
        msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Commands') + \
            '\n/help - shows this menu\n/listguilds - list guilds you are in\n/channel - switch channel\n/guild - switch guild\n/joinguild - joins a guild\n/clear - clears message\n /refresh - refreshes messages' + \
            term.bold('\nOnly you can see this.\n')
        show_msg_view()
        return
    if (vals[0] == 'clear'):
        msgText = ''
        show_msg_view()
        return
    if (vals[0] == 'listguilds'):
        guilds_data = requests.get(
            instance + '/guilds/' + current_user['name']).json()['data']
        msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Guilds') + \
            '\n' + "\n".join(map(map_to_guild_name, guilds_data)) + \
            term.bold('\nOnly you can see this.\n')
        show_msg_view()
        return
    if (vals[0] == 'joinguild'):
        try:
            vals[1]
        except:
            msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Error') + \
                '\n' + 'I need to know what guild you want to join. Ask the inviter to run the listguilds command.' + \
                term.bold('\nOnly you can see this.\n')
            show_msg_view()
            return
        new_guild_data = requests.put(
            instance + '/join-guild/' + vals[1], json={'name': current_user['name']})
        if (not new_guild_data.ok):
            msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Error') + \
                '\n' + 'I could not find the guild you were trying to join.' + \
                term.bold('\nOnly you can see this.\n')
        global current_channel
        global current_server
        current_channel = new_guild_data.json()['channels'][0]
        current_server = new_guild_data.json()
        show_msg_view()
        return
    if (vals[0] == 'refresh'):
        msgs_req = requests.get(
            instance + '/messages/' + current_channel['id'])
        msgs = msgs_req.json()['data']
        new_msgs = []
        for msg in msgs:
            if (msg['authorId'] == current_user['id']):
                new_msgs.append(term.goldenrod(
                    current_user['name']) + ': ' + msg['content'])
            else:
                new_msgs.append(msg['author']['name'] + ': ' + msg['content'])
        msgText = "\n".join(new_msgs)
        show_msg_view()
        return
    msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Error') + \
        '\n' + 'That command does not exist.' + \
        term.bold('\nOnly you can see this.\n')
    show_msg_view()
    return


def map_to_guild_name(guild):
    print(guild)
    return guild['name'] + ' - invite: ' + guild['id']


show_msg_view()
