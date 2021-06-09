from blessed import Terminal
import requests
import asyncio

term = Terminal()

instance = 'http://localhost:3000'

uname = input('Enter a username: ')

if (requests.get(instance + '/user-exists/' + uname).status_code == 204):
    promptAnswer = input(
        "That username isn't taken. Would you like to register it? (y/n) ")
    if (not ('y' in promptAnswer)):
        print('Quitting...')
        exit()

    res = requests.post(instance + '/register', json={"name": uname})

    if (not res.ok):
        print('An error occured while trying to register. Please try again.')
        exit()


currentUser = uname

guildsReq = requests.get(instance + '/guilds/' + currentUser)

guilds = guildsReq.json()

currentChannel = guilds['data'][0]['channels'][0]['name']
currentServer = guilds['data'][0]['name']

msgText = ''


def show_msg_view():
    global msgText
    with term.fullscreen():
        while (True):
            msg = None
            print(term.clear())
            print(msgText)
            with term.location(0, term.height - 1):
                msg = input('[#' + currentChannel + ' in ' +
                            term.bold(currentServer) + '] ')
            if (msg):
                if (msg.startswith('/')):
                    process_command(msg.replace('/', '').split(' '))
                    break
                msgText = msgText + '\n' + \
                    term.goldenrod(term.bold(currentUser)) + ': ' + msg
            print(term.clear())
            msg = None


def refresh_msg_view():
    with term.fullscreen():
        print(term.clear())
        print(msgText)
        with term.location(0, term.height - 1):
            print('[#' + currentChannel + ' in ' +
                  term.bold(currentServer) + '] ')


def process_command(vals):
    global msgTexts
    if (vals[0] == 'help'):
        msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Commands') + \
            '\n/help - shows this menu\n/listguilds - list guilds you are in\n/channel - switch channel\n/guild - switch guild\n/joinguild - joins a guild\n/clear - clears messages' + \
            term.bold('\nOnly you can see this.\n')
        show_msg_view()
    if (vals[0] == 'clear'):
        msgText = ''
        show_msg_view()
    if (vals[0] == 'listguilds'):
        data = requests.get(instance + '/guilds/' + currentUser)
        print(data)
        msgText += term.bold(term.dodgerblue('\n\nClyde[BOT]') + ':\n') + term.bold('Guilds') + \
            '\n/help - shows this menu\n/listguilds - list guilds you are in\n/channel - switch channel\n/guild - switch guild\n/joinguild - joins a guild\n/clear - clears messages' + \
            term.bold('\nOnly you can see this.\n')
        show_msg_view()


asyncio.run(show_msg_view())
