import discord
from datetime import datetime, timedelta
import asyncio
import cog_config

sublist = ['banned words',
           'oversized images',
           'raid alert']

muted = []

def subscribed_to(t):
    nlist = []
    if t & 0b1:
        nlist.append('banned words')
    if t & 0b10:
        nlist.append('oversized images')
    if t & 0b100:
        nlist.append('raid alert')
    if t & 0b1000:
        nlist.append('fourth one')
    return nlist

async def subscribe(client, message, command=None):
    t = cog_config.read('Notifications',message.author.id)
    if len(command) == 1:
        if t:
            t = int(t)
        if not t or t == 0:
            print('{} has no notifications enabled.'.format(message.author.name))
            await client.send_message(message.channel, "{} has no notifications enabled.\nAvaliable subscriptions:\n```\n{}\n```".format(message.author.name,'\n'.join(sublist)))
            return
        nlist = subscribed_to(t)
        print('{} subscribed to:\n{}'.format(message.author.name,'\n'.join(nlist)))
        await client.send_message(message.channel, "{} subscribed to:\n```\n{}\n```\nAvaliable subscriptions:\n```\n{}\n```".format(message.author.name,'\n'.join(nlist),'\n'.join(sublist)))
        return
    a = command[1].split(',')
    if t:
        t = int(t)
    else:
        t = 0
    nlist = []
    for i in a:
        if i.strip() == 'banned words':
            t |= 0b1
            nlist.append('banned words')
        if i.strip() == 'oversized images':
            t |= 0b10
            nlist.append('oversized images')
        if i.strip() == 'raid alert':
            t |= 0b100
            nlist.append('raid alert')
        if i.strip() == 'fourth one':
            t |= 0b1000
            nlist.append('fourth one')
    print('{} subscribed to:\n{}'.format(message.author.name,'\n'.join(nlist)))
    cog_config.write('Notifications',message.author.id, t)
    await client.send_message(message.channel, "{} just subscribed to:\n```\n{}\n```".format(message.author.name,'\n'.join(nlist)))

async def unsubscribe(client, message, command=None):
    t = cog_config.read('Notifications',message.author.id)
    if len(command) == 1:
        if t:
            t = int(t)
        if not t or t == 0:
            print('{} has no notifications enabled.'.format(message.author.name))
            await client.send_message(message.channel, "{} has no notifications enabled.\nAvaliable subscriptions:\n```\n{}\n```".format(message.author.name,'\n'.join(sublist)))
            return
        nlist = subscribed_to(t)
        print('{} subscribed to:\n{}'.format(message.author.name,'\n'.join(nlist)))
        await client.send_message(message.channel, "{} subscribed to:\n```\n{}\n```\nAvaliable subscriptions:\n```\n{}\n```".format(message.author.name,'\n'.join(nlist),'\n'.join(sublist)))
        return
    a = command[1].split(',')
    
    if t:
        t = int(t)
    else:
        t = 0
    nlist = []
    for i in a:
        if i.strip() == 'banned words':
            t &= 0b11111110
            nlist.append('banned words')
        if i.strip() == 'oversized images':
            t &= 0b11111101
            nlist.append('oversized images')
        if i.strip() == 'raid alert':
            t &= 0b11111011
            nlist.append('raid alert')
        if i.strip() == 'fourth one':
            t &= 0b11110111
            nlist.append('fourth one')
    print('{} unsubscribed from:\n{}'.format(message.author.name,'\n'.join(nlist)))
    cog_config.write('Notifications',message.author.id, t)
    await client.send_message(message.channel, "{} unsubscribed from:\n```\n{}\n```".format(message.author.name,'\n'.join(nlist)))

def get_subscribers(mode):
    keys = cog_config.read_keys('Notifications')
    out = []
    if mode == 'banned words':
        for uid in keys:
            if int(cog_config.read('Notifications',uid)) & 0b1:
                out.append(uid)
    elif mode == 'oversized images':
        for uid in keys:
            if int(cog_config.read('Notifications',uid)) & 0b10:
                out.append(uid)
    elif mode == 'raid alert':
        for uid in keys:
            if int(cog_config.read('Notifications',uid)) & 0b100:
                out.append(uid)
    elif mode == 'fourth one':
        for uid in keys:
            if int(cog_config.read('Notifications',uid)) & 0b1000:
                out.append(uid)
    else:
        return None
    return out

async def dispatch(client, mode, message):
    receivers = get_subscribers(mode)
    for i in receivers:
        if i in muted:
            continue
        usr = await client.get_user_info(i)
        await client.send_message(usr, message)
        
async def mute(client, message, command=None):
    muted.append(message.author.id)
    if message.server:
        dest = message.channel
    else:
        dest = message.author
    print('({1.hour:02d}:{1.minute:02d}){0} has muted notifications.'.format(message.author.name, datetime.now()))
    await client.send_message(dest, 'Notifications muted. You will no longer receive notifications.\nUse `unmute` command to unmute notifications.')

async def unmute(client, message, command=None):
    if message.author.id in muted:
        muted.remove(message.author.id)
        if message.server:
            dest = message.channel
        else:
            dest = message.author
        print('({1.hour:02d}:{1.minute:02d}){0} has unmuted notifications.'.format(message.author.name, datetime.now()))
        await client.send_message(dest, 'Notifications unmuted. You will now receive notifications as normal')
