import discord
from threading import Timer
import asyncio
import random

raid_quotes = ['Raid! Maybe. Probably not.',
               'Suspicious people joining.',
               'High probability of raid.',
               'Anyone here? Raid incoming.']

timers = {}
timers_q = {}

#long raider timer
def empty_f(member):
    del timers[member]

#short raider timer
def empty_f_q(member):
    del timers_q[member]

#when someone joins start both timers for them
async def on_join(client, member):
    timers[member] = Timer(300,empty_f,[member])
    timers_q[member] = Timer(30,empty_f_q,[member])
    timers[member].start()
    timers_q[member].start()
    print('%%%debug%%% cog_raid_alert on_join()')
    if len(timers_q) > 1:
        print('Raid alert! Raiders: {0}'.format(', '.join([i.name for i in list(timers_q.keys())])))
        await client.send_message(client.get_channel('477269419765006345'), ':smiling_imp: '+random.choice(raid_quotes)+'\nPossible raiders: {0}'.format(', '.join([i.mention for i in list(timers_q.keys())])))
    elif len(timers) > 2:
        print('Raid alert! Raiders: {0}'.format(', '.join([i.name for i in list(timers.keys())])))
        await client.send_message(client.get_channel('477269419765006345'), ':smiling_imp: '+random.choice(raid_quotes)+'\nPossible raiders: {0}'.format(', '.join([i.mention for i in list(timers.keys())])))

#when someone leaves, stop their timer
def on_remove(member):
    print('%%%debug%%% cog_raid_alert on_remove()')
    if member in timers_q:
        timers_q[member].cancel()
        del timers_q[member]
    if member in timers:
        timers[member].cancel()
        del timers[member]

#on exit cancel every timer
def cancel():
    if timers:
        for i in timers.values():
            i.cancel()
    if timers_q:
        for i in timers_q.values():
            i.cancel()



