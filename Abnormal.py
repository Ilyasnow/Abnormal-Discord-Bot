import discord
import os
import feedparser
from datetime import datetime, timedelta
from threading import Timer, Thread
from derpibooru import Search, sort
import urbandictionary as ud
import random
import time
import asyncio
import re

import cog_logger
import cog_raidalert
import cog_config
import cog_commands
import cog_banning
import cog_notifications

cog_config.init()
TOKEN = str(cog_config.read('CONFIG','token'))
if not TOKEN or TOKEN == 'put_token_here':
    print('Please put your token in config file')
    exit(0)
BOT = bool(cog_config.read('CONFIG','bot'))
client = discord.Client()

COMMAND_PREFIX = '`' #prefix used in `commands



DERPI_GENERAL_FILTER = "157099" #SFW NoMeme filter
DERPI_GENERAL_ARTIST_FILTER = "157101" #SFW NoMeme filter with lowered gte score
DERPI_MEME_FILTER = "157100" #SFW Meme only filter

#Global variables
EQD_FEED_ENABLED = True
DERPIBOORU_ENABLED = True
ME_ENABLED = True
MEME_ENABLED = True
MENTION_ENABLED = True

MEME_COOLDOWN = 30      #Cooldown in seconds for pmeme command
MENTION_COOLDOWN = 300  #Cooldown in seconds between responces to a mention
DERPI_COOLDOWN = 0      #Cooldown in seconds for pony and ponyr commands

meme_timer = None
mention_timer = None
derpi_timer = None
undo_posts = []
derpi_undo_posts = []

#Server and channel ID lists
authorized_servers = ['87583189161226240'] #EQD
commands_channels = ['151834220841533440', #staff
                     '303603185514184705'] #botdev #channels for commands
general_channels = ['87583189161226240', #ponyville
                    '187665178303660032']#manehattan
log_channel = '315288534124855317' #log output channel ID
ban_channel = '279779468204048414' #ban output channel ID
eqd_feed_channel = '281947627292065793' #channel for eqd feed
art_commands = ['277885163793285130', #art
                '303603185514184705'] #botdev #channels for derpi commands
meme_commands = ['151838944827277312', #meme
                 '303603185514184705'] #botdev #channels for meme commands
serious_channels = ['200070887091863553',   #staff action tracking
                    '415610659821060097',   #blog action tracking
                    '279779468204048414',   #ban log
                    '315288534124855317',   #chat log
                    '281947627292065793',   #eqd feed
                    '484358854138658827',   #user tracking
                    '319153432189599745']   #trial mod discussion

#Bot quotes for different situations
cooldown_quotes = ['Give it time...','Hold your horses!','Don\'t rush it']
command_off_quotes = ['Sorry, I am not allowed to do that',]
mention_quotes = [':eyes:','Yes?','Who pinged me? :aaaaaaa:']
ball8_quotes = ['Yes','No','Maybe','Perhaps','Indeed','Why not? :shrugsunset:','Of course not!','How dare you... :isee:','Of course!','I don\'t really know :think:','Eh :shrugsunset:',':pffft:']

#List of common banned words
banned_words = ['fag', 'nigg', 'milf', 'cunt', 'nibba']

#Program begins
print('Starting...')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    global loop_timer               #loop that prints milestones every hour
    if not loop_timer.is_alive():   #Probably would be best to replace with bg task
        loop_f()

@client.event
async def on_member_join(member):
    #Event for when user joins the server
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} joined server {0.server.name}.'.format(member, datetime.now()))
        if member.avatar_url:#choosing avatar to display (user or default)
            member_avatar_url = member.avatar_url
        else:
            member_avatar_url = member.default_avatar_url
        #embed creation
        em = discord.Embed(title=':white_check_mark:', description=member.mention+'\nJoined the server {}'.format(member.server.name), colour=0x40EE40)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member), icon_url=member_avatar_url)
        em.add_field(name='User created on:', value=member.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((datetime.now() - member.created_at).days), inline=False)
        em.set_thumbnail(url=member_avatar_url)
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

        await cog_raidalert.on_join(client, member)

@client.event
async def on_member_remove(member):
    #Event for when user leaves the server
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} left server {0.server.name}.'.format(member, datetime.now()))
        if member.avatar_url:#choosing avatar to display (user or default)
            member_avatar_url = member.avatar_url
        else:
            member_avatar_url = member.default_avatar_url
        #embed creation
        em = discord.Embed(title=':x:', description=member.mention+'\nLeft the server {}'.format(member.server.name), colour=0xEE4040)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member), icon_url=member_avatar_url)
        em.add_field(name='User created on:', value=member.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((datetime.now() - member.created_at).days), inline=False)
        em.set_thumbnail(url=member_avatar_url)
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

        cog_raidalert.on_remove(member)

@client.event
async def on_member_update(member_before, member_after):
    #Event for when user updates something within their profile
    if True:
        if member_before.server.id in authorized_servers:
            #await client.request_offline_members(member_before.server)
            if member_after.avatar_url:#choosing avatar to display (user or default)
                member_a_avatar_url = member_after.avatar_url
            else:
                member_a_avatar_url = member_after.default_avatar_url
            if member_before.avatar_url:
                member_b_avatar_url = member_before.avatar_url
            else:
                member_b_avatar_url = member_before.default_avatar_url
            #preemptive embed creation
            em = discord.Embed(title=':information_source:', description=member_after.mention, colour=0xEE40EE)
            em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_a_avatar_url)
            em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
            
            if set(member_before.roles) - set(member_after.roles): #lost roles
                print('({1.hour:02d}:{1.minute:02d}){0.name} has lost roles in {0.server.name}.'.format(member_before, datetime.now()))
                roles_dif = ', '.join(i.name for i in (set(member_before.roles) - set(member_after.roles)))
                print(roles_dif)
                em.title=':flag_black:'
                em.add_field(name='Lost role(s):', value=roles_dif, inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)
                
            if set(member_after.roles) - set(member_before.roles): #got roles
                print('({1.hour:02d}:{1.minute:02d}){0.name} got new roles in {0.server.name}.'.format(member_before, datetime.now()))
                roles_dif = ', '.join(i.name for i in (set(member_after.roles) - set(member_before.roles)))
                print(roles_dif)
                em.title=':flag_white:'
                em.add_field(name='Got new role(s)', value=roles_dif, inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)
                
            if member_before.name != member_after.name: #name change
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their name.'.format(member_before, datetime.now()))
                print('{0.name} to {1.name}'.format(member_before, member_after))
                em.colour=0x80A0EE
                em.add_field(name='New name', value='{0} changed to {1}'.format(escape_code_line(member_before.name), escape_code_line(member_after.name)), inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)

                cog_config.write_name(member_after.id, member_after.name)
                
            if member_before.avatar != member_after.avatar: #avatar change
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their avatar.'.format(member_before, datetime.now()))
                em.description=member_after.mention+'\nNew avatar'
                em.colour=0x80A0EE
                em.set_image(url=member_a_avatar_url)
                em.set_thumbnail(url=member_b_avatar_url)
                await client.send_message(client.get_channel(log_channel), embed=em)
                
            if member_before.nick != member_after.nick: #nickname change
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their nickname in {0.server.name}.'.format(member_before, datetime.now()))
                print('{0.name} changed to {1.nick}'.format(member_before, member_after))
                em.colour=0x80A0EE
                em.add_field(name='New nickname', value='{0} changed to {1}'.format(escape_code_line(member_before.nick), escape_code_line(member_after.nick)), inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)

                if member_after.nick != None:
                    cog_config.write_nick(member_after.id, member_after.nick)


@client.event
async def on_member_ban(member):
    if member.server.id in authorized_servers:
        await cog_banning.ban(client, member)

@client.event
async def on_member_unban(server, user):
    if server.id in authorized_servers:
        await cog_banning.unban(client, server, user)
        
@client.event
async def on_message_delete(message):
    #Event for when any message gets deleted
    if not message.server: #not in DMs
        return
    if message.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.author.name}\'s message has been deleted from #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
        print('\"{0.author.name}:{0.clean_content}\"'.format(message))
        if message.author.avatar_url:
            member_avatar_url = message.author.avatar_url
        else:
            member_avatar_url = message.author.default_avatar_url
        em = discord.Embed(title=':wastebasket:', description=message.author.mention, colour=0xFE8800)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(message.author), icon_url=member_avatar_url)
        if message.timestamp < datetime.utcnow() - timedelta(seconds = 300):
            del_msg = 'Deleted message from #{0.channel.name} from {1}'.format(message, message.timestamp.replace(microsecond=0))
        else:
            del_msg = 'Deleted message from #{0.channel.name}'.format(message)
        em.add_field(name=del_msg, value=':page_facing_up: **Message:**\n{0.content}'.format(message), inline = False)
        attachments_text = ''
        first_attachment = ''
        f_thumbnail = False
        #getting all attachments. Previewing only first
        if message.attachments:
            for attachment in message.attachments:
                attachments_text += '{}[:link:]({}) '.format(attachment.get('filename'), attachment.get('proxy_url'))
                if not first_attachment:
                    first_attachment = attachment
            if attachments_text:
                em.add_field(name='Attachments:', value=attachments_text)
                em.set_thumbnail(url=first_attachment.get('proxy_url'))
                f_thumbnail = True
        if message.embeds:
            #em.add_field(name='Embeds:', value=':white_check_mark:')
            n_embed = 1
            for i in message.embeds:
                if i.get('type') == 'image':
                    em.add_field(name='Embed {}:'.format(n_embed), value=i.get('thumbnail').get('url'), inline = False)
                    n_embed += 1
                    if not f_thumbnail:
                        em.set_thumbnail(url=i.get('thumbnail').get('proxy_url'))
                        f_thumbnail = True
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_message_edit(before, after):
    #Event for message edit. Adding embeds also counts as edit for some reason
    if not before.server or not after.server: #not in DMs
        return
    if (after.channel.id in log_channel) or after.author.bot: #not in log channel and not from a bot
        return
    if not before.embeds and after.embeds: #message with embed usually triggers on_message_edit
        return
    if before.server.id in authorized_servers:
        if before.author.avatar_url:
            member_avatar_url = before.author.avatar_url
        else:
            member_avatar_url = before.author.default_avatar_url
        em = discord.Embed(colour=0xFEF888)
        if not before.pinned and after.pinned: #message pinned
            print('({1.hour:02d}:{1.minute:02d}){0.author.name}\'s message was pinned in #{0.channel.name} at {0.server.name}.'.format(before, datetime.now()))
            print('\"{0.author.name}:{0.clean_content}\"'.format(before))
            em.title=':pushpin:'
            em.colour=0x88FFFF
            em.add_field(name='Message has been pinned in #{0.channel.name}'.format(before), value='{0.author.name}: {0.content}'.format(before), inline=False)
        elif before.pinned and not after.pinned: #message unpinned
            print('({1.hour:02d}:{1.minute:02d}){0.author.name}\'s message was unpinned in #{0.channel.name} at {0.server.name}.'.format(before, datetime.now()))
            print('\"{0.author.name}:{0.clean_content}\"'.format(before))
            em.title=':round_pushpin:'
            em.colour=0x88FFFF
            em.add_field(name='Message has been unpinned in #{0.channel.name}'.format(before), value='{0.author.name}: {0.content}'.format(before), inline=False)
        else: #message edited
            print('({1.hour:02d}:{1.minute:02d}){0.author.name} edited message from #{0.channel.name} at {0.server.name}.'.format(before, datetime.now()))
            print('Before:\"{0.author.name}:{0.clean_content}\"\n After:\"{1.author.name}:{1.clean_content}\"'.format(before, after))
            em.title=':pencil2:'
            em.description=before.author.mention
            em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(before.author), icon_url=member_avatar_url)
            em.add_field(name='Edited message in #{0.channel.name}'.format(before), value=':page_facing_up: **Message before:**\n{0}\n:pencil: **Message after:**\n{1}'.format(escape_code_line(before.content), escape_code_line(after.content)), inline=False)
        attachments_text = ''
        first_attachment = ''
        #getting all attachments. Previewing only first
        if after.attachments:
            for attachment in after.attachments:
                attachments_text += '{}[:link:]({}) '.format(attachment.get('filename'), attachment.get('proxy_url'))
                if not first_attachment:
                    first_attachment = attachment
            if attachments_text:
                em.add_field(name='Attachments:', value=attachments_text)
                em.set_thumbnail(url=first_attachment.get('proxy_url'))
        if before.embeds or after.embeds:
            em.add_field(name='Embeds:', value=':white_check_mark:')
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow())) 
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_message(message):
    #Event for when message gets recieved
    if not message.server: #DMs
        if message.author == client.user:
            return
        if message.content.startswith(COMMAND_PREFIX):
            command = message.content.split(' ' , maxsplit=1)
            
            if command[0] == COMMAND_PREFIX+'mute':
                await cog_notifications.mute(client, message)

            if command[0] == COMMAND_PREFIX+'unmute':
                await cog_notifications.unmute(client, message)
        else:
            print('({1.hour:02d}:{1.minute:02d}){0.author.name} send us a message in DM.'.format(message, datetime.now()))
            print('\"{0.author.name}:{0.clean_content}\"'.format(message))
            #await client.send_message(client.get_channel('303603185514184705'), '{0.author.name}(`{0.author.id}`) send me a message in DM. He said:\n"{0.clean_content}"'.format(message))
    if message.server: #not DMs
        if message.server.id in authorized_servers:
            #Accessing global variables with ability to write
            global DERPIBOORU_ENABLED
            global EQD_FEED_ENABLED
            global MEME_ENABLED
            global ME_ENABLED
            global MENTION_ENABLED
            global undo_posts
            global derpi_undo_posts
            global meme_timer
            global mention_timer
            global derpi_timer

            if message.channel.id in meme_commands: #For commands in meme channel
                if message.content.startswith(COMMAND_PREFIX):
                    command = message.content.split(' ' , maxsplit=1)

                    if command[0] == COMMAND_PREFIX+'undo': #Pmeme undo command. Deletes last pmeme message sender got
                        print('({1.hour:02d}:{1.minute:02d}) undo command by {0}'.format(message.author.name, datetime.now()))
                        for msg, user in reversed(undo_posts):
                            if user == message.author:
                                await client.delete_message(msg)
                                undo_posts.remove((msg, user))
                                #print([i[1] for i in undo_posts])
                                return
                        await client.send_message(message.channel, 'Nothing to undo for you, silly')
                        print('nothing to undo')
                            
                    if command[0] == COMMAND_PREFIX+'pmeme': #Pmeme command. Gets a random derpi image tagged "meme"
                        if not MEME_ENABLED:
                            await client.send_message(message.channel, random.choice(command_off_quotes))
                            return
                        if len(command) == 1:
                            meme_query = ''
                        else:
                            meme_query = command[1]
                        print('({1.hour:02d}:{1.minute:02d}) pmeme command by {0} with tags "{2}"'.format(message.author.name, datetime.now(), meme_query))
                        if meme_timer.is_alive():
                            await client.send_message(message.channel, random.choice(cooldown_quotes))
                            print('pmeme cooldown'.format(datetime.now()))
                            return
                        if message.channel.id not in commands_channels:
                            meme_timer = Timer(MEME_COOLDOWN, empty) #cooldown
                            meme_timer.start()
                        for image in Search().sort_by(sort.RANDOM).query(meme_query).filter(DERPI_MEME_FILTER):
                            msg = await client.send_message(message.channel, image.url)
                            undo_posts.append((msg, message.author))
                            if len(undo_posts) > 10:
                                undo_posts.pop(0)
                            #print(undo_posts)
                            return
                        await client.send_message(message.channel, "I can't find anything")
                        meme_timer.cancel()
                        print('nothing found')
            
            if message.channel.id in art_commands: #For commands in art channel
                if message.content.startswith(COMMAND_PREFIX):
                    command = message.content.split(' ' , maxsplit=1)

                    if command[0] == COMMAND_PREFIX+'undo': #pony undo command. Deletes last ponyr or pony message sender got
                        print('({1.hour:02d}:{1.minute:02d}) undo command by {0}'.format(message.author.name, datetime.now()))
                        for msg, user in reversed(derpi_undo_posts):
                            if user == message.author:
                                await client.delete_message(msg)
                                derpi_undo_posts.remove((msg, user))
                                #print(derpi_undo_posts)
                                return
                        await client.send_message(message.channel, 'Nothing to undo for you, silly')
                        print('nothing to undo')
            
                    if command[0] == COMMAND_PREFIX+'ponyr': #Ponyr command. Gets a random derpi image with or without user tags.
                        if not DERPIBOORU_ENABLED:
                            await client.send_message(message.channel, random.choice(command_off_quotes))
                            return
                        derpi_filter = DERPI_GENERAL_FILTER
                        if len(command) == 1:
                            derpi_query = ''
                        else:
                            derpi_query = command[1]
                            if command[1].find('artist:') != -1:
                                derpi_filter = DERPI_GENERAL_ARTIST_FILTER
                        print('({1.hour:02d}:{1.minute:02d}) Pony with tags:"{0}"'.format(derpi_query, datetime.now()))
                        if derpi_timer.is_alive():
                            await client.send_message(message.channel, random.choice(cooldown_quotes))
                            print('ponyr cooldown'.format(datetime.now()))
                            return
                        if message.channel.id not in commands_channels:
                            derpi_timer = Timer(DERPI_COOLDOWN, empty)
                            derpi_timer.start()
                        for image in Search().sort_by(sort.RANDOM).query(derpi_query).filter(filter_id=derpi_filter):
                            msg = await client.send_message(message.channel, image.url)
                            derpi_undo_posts.append((msg, message.author))
                            if len(derpi_undo_posts) > 10:
                                derpi_undo_posts.pop(0)
                            #print(derpi_undo_posts)
                            return                        
                        await client.send_message(message.channel, "I can't find anything")
                        derpi_timer.cancel()
                        print('nothing found')
                        
                    if command[0] == COMMAND_PREFIX+'pony': #Pony command. Gets newest derpi image with or without user tags.
                        if not DERPIBOORU_ENABLED:
                            await client.send_message(message.channel, random.choice(command_off_quotes))
                            return
                        derpi_filter = DERPI_GENERAL_FILTER
                        if len(command) == 1:
                            derpi_query = ''
                        else:
                            derpi_query = command[1]
                            if command[1].find('artist:') != -1:
                                derpi_filter = DERPI_GENERAL_ARTIST_FILTER
                        print('({1.hour:02d}:{1.minute:02d}) Pony with tags:"{0}"'.format(derpi_query, datetime.now()))
                        if derpi_timer.is_alive():
                            await client.send_message(message.channel, random.choice(cooldown_quotes))
                            print('pony cooldown'.format(datetime.now()))
                            return
                        if message.channel.id not in commands_channels:
                            derpi_timer = Timer(DERPI_COOLDOWN, empty)
                            derpi_timer.start()
                        for image in Search().query(derpi_query).filter(filter_id=derpi_filter):
                            msg = await client.send_message(message.channel, image.url)
                            derpi_undo_posts.append((msg, message.author))
                            if len(derpi_undo_posts) > 10:
                                derpi_undo_posts.pop(0)
                            #print([v.name for v in derpi_undo_posts.values()])
                            return
                        await client.send_message(message.channel, "I can't find anything")
                        derpi_timer.cancel()
                        print('nothing found')
            
            if message.channel.id in commands_channels: #For general (staff) commands. Preferably to add mod user filter
                if message.content.startswith(COMMAND_PREFIX):
                    command = message.content.split(' ' , maxsplit=1)


                    if command[0] == COMMAND_PREFIX+'mute': #Mute command. Mutes sub notifications
                        await cog_notifications.mute(client, message)

                    if command[0] == COMMAND_PREFIX+'unmute': #Unmute command. Unmutes sub notifications
                        await cog_notifications.unmute(client, message)

                    if command[0] == COMMAND_PREFIX+'subscribe': #Subscribe command. Adds your id to the list of recievers of something.
                        await cog_notifications.subscribe(client, message, command)

                    if command[0] == COMMAND_PREFIX+'unsubscribe': #Unsubscribe command. Removes your id form the list of recievers of something.
                        await cog_notifications.unsubscribe(client, message, command)
                        
                    if command[0] == COMMAND_PREFIX+'names': #Names command. Prints the last recorded 20 names and nicknames of a user.
                        await cog_commands.names(client, message, command)
                    
                    if command[0] == COMMAND_PREFIX+'togglemention': #Togglemention command. Enables/disables responce to a mention
                        MENTION_ENABLED = not MENTION_ENABLED
                        if MENTION_ENABLED:
                            await client.send_message(message.channel, 'Reaction to mentions is now enabled')
                        else:
                            await client.send_message(message.channel, 'Reaction to mentions is now disabled')

                    if command[0] == COMMAND_PREFIX+'togglememe': #Togglememe command. Enables/disables pmeme
                        MEME_ENABLED = not MEME_ENABLED
                        if MEME_ENABLED:
                            await client.send_message(message.channel, 'Meme commands are now enabled')
                        else:
                            await client.send_message(message.channel, 'Meme commands are now disabled')

                    if command[0] == COMMAND_PREFIX+'toggleme': #Togglememe command. Enables/disables me
                        ME_ENABLED = not ME_ENABLED
                        if ME_ENABLED:
                            await client.send_message(message.channel, 'Me command is now enabled')
                        else:
                            await client.send_message(message.channel, 'Me command is now disabled')


                    if command[0] == COMMAND_PREFIX+'me': #Me command. Makes bot say the message given in specified channel
                        if not ME_ENABLED:
                            return
                        if len(command) > 1:
                            me_command = command[1].split(' ', maxsplit=1)
                            print('({1.hour:02d}:{1.minute:02d}) me command with args {0}'.format((message.clean_content.split(' ' , maxsplit=1))[1], datetime.now()))
                            me_channel_id = me_command[0].strip('<>#!')
                            if len(me_command) > 1 and me_channel_id.isdecimal() and client.get_channel(me_channel_id) and me_channel_id not in serious_channels:
                                try:
                                    await client.send_typing(client.get_channel(me_channel_id))
                                    await asyncio.sleep(min(len(me_command[1])*0.05*random.uniform(0.8,1.1), 6)) #"Typing..." length formula
                                    await client.send_message(client.get_channel(me_channel_id), stop_mass_mentions(me_command[1]))
                                except discord.errors.Forbidden as e:
                                    await client.send_message(message.channel, 'I can\'t post there')
                                return
                        await client.send_message(message.channel, '```\n'+command[0]+' #channel <text_you_want_me_to_say>\n```')

                    if command[0] == COMMAND_PREFIX+'togglederpi': #Togglederpi command. Enables/disables pony and ponyr
                        DERPIBOORU_ENABLED = not DERPIBOORU_ENABLED
                        if DERPIBOORU_ENABLED:
                            await client.send_message(message.channel, 'Derpibooru commands are now enabled')
                        else:
                            await client.send_message(message.channel, 'Derpibooru commands are now disabled')

                    if command[0] == COMMAND_PREFIX+'togglefeed': #Togglefeed command. Enables/disables feed
                        EQD_FEED_ENABLED = not EQD_FEED_ENABLED
                        if EQD_FEED_ENABLED:
                            await client.send_message(message.channel, 'EQD feed is now enabled')
                        else:
                            await client.send_message(message.channel, 'EQD feed is now disabled')

                    if command[0] == COMMAND_PREFIX+'urban': #Urban command. Gets Urbandictionary definition for the word
                        if len(command) == 1:
                            return
                        print('({0.hour:02d}:{0.minute:02d}){1.author.name} used urban for word "{2}"'.format(datetime.now(), message, command[1]))
                        defs = ud.define(command[1])
                        if not defs:
                            print('Nothing found')
                            await client.send_message(message.channel, 'Nothing found')
                            return
                        n = 0
                        em = discord.Embed(title=defs[n].word, description=defs[n].definition.replace('[', '').replace(']', ''), colour=0x134FE6)
                        em.add_field(name='Example:', value=defs[n].example.replace('[', '').replace(']', ''))
                        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                        await client.send_message(message.channel, embed=em)

                    if command[0] == COMMAND_PREFIX+'urbanr': #UrbanR command. Gets random Urbandictionary word and its definition
                        defs = ud.random()
                        if not defs:
                            print('Urbanr Nothing found')
                            await client.send_message(message.channel, 'Nothing found')
                            return
                        n = 0
                        print('({0.hour:02d}:{0.minute:02d}){1.author.name} used urbanr and got the word "{2}"'.format(datetime.now(), message, defs[n].word))
                        em = discord.Embed(title=defs[n].word, description=defs[n].definition.replace('[', '').replace(']', ''), colour=0x134FE6)
                        em.add_field(name='Example:', value=defs[n].example.replace('[', '').replace(']', ''))
                        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                        await client.send_message(message.channel, embed=em)

                    if command[0] == COMMAND_PREFIX+'ping': #Ping command. Simply replies with pong. Used to check if bot is alive
                        print('({0.hour:02d}:{0.minute:02d}) pong'.format(datetime.now()))
                        await client.send_message(message.channel, 'pong')
                        
                    if command[0] == COMMAND_PREFIX+'reason': #Reason command. Logs the ban in ban channel with given case and reason.
                        await cog_banning.reason(client, message, command)
                            
                    if command[0] == COMMAND_PREFIX+'userinfo': #Userinfo command. Prints information about given user or sender, if no user given
                        if len(command) == 1:
                            userinfo_command = message.author.id
                        else:
                            userinfo_command = command [1]
                        print('({1.hour:02d}:{1.minute:02d}){0.author.name} used `userinfo command'.format(message, datetime.now()))
                        print('\"{0.author.name}:{0.content}\"'.format(message))
                        if userinfo_command.isdecimal():                        #by id
                            user = message.server.get_member(userinfo_command)
                        elif (userinfo_command.strip('<>@!')).isdecimal():      #by ping
                            user = message.server.get_member(userinfo_command.strip('<>@!'))
                        else:                                                   #by name
                            user = message.server.get_member_named(userinfo_command)
                        if not user:
                            await client.send_message(message.channel, 'User not found.\nUse \`userinfo <id/mention/name> to get info about user.')
                            return
                        if user.avatar_url:
                            user_avatar_url = user.avatar_url
                        else:
                            user_avatar_url = user.default_avatar_url
                        em = discord.Embed(title=':information_source: User info', colour=user.colour)
                        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(user))
                        em.set_thumbnail(url=user_avatar_url)
                        em.add_field(name='User:', value=user.mention, inline=True)
                        if user.nick:
                            em.add_field(name='Nickname:', value=user.nick, inline=True)
                        em.add_field(name="User created on:", value=user.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)  '.format((message.timestamp - user.created_at).days), inline=False)
                        em.add_field(name="User joined on:", value=user.joined_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((message.timestamp - user.joined_at).days), inline=False)
                        if len(user.roles) > 1:
                            em.add_field(name="Roles:", value=", ".join([x.name for x in user.roles if x.name != "@everyone"]), inline=False)
                        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                        await client.send_message(message.channel, embed=em)
                        
                    if command[0] == COMMAND_PREFIX+'serverinfo': #Serverinfo command. Prints information about current server
                        print('({1.hour:02d}:{1.minute:02d}){0.author.name} used `serverinfo command'.format(message, datetime.now()))
                        print('\"{0.author.name}:{0.content}\"'.format(message))
                        em = discord.Embed(title=':information_source: Server info', colour=0x80A0EE)
                        em.set_author(name=message.server.name + ' - ' + message.server.id)
                        em.set_thumbnail(url=message.server.icon_url)
                        em.add_field(name='Members:', value=message.server.member_count)
                        em.add_field(name='Owner:', value=message.server.owner.mention)
                        ver_levels = {discord.VerificationLevel.none:'None - No criteria set.',
                                      discord.VerificationLevel.low:'Low - Member must have a verified email on their Discord account.',
                                      discord.VerificationLevel.medium:'Medium - Member must have a verified email and be registered on Discord for more than five minutes.',
                                      discord.VerificationLevel.high:'High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the server itself for more than ten minutes.',
                                      discord.VerificationLevel.table_flip:'High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the server itself for more than ten minutes.'}
                        em.add_field(name='Verification level:', value=ver_levels.get(message.server.verification_level, 'None'), inline=False)
                        em.add_field(name='Created on:', value=message.server.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((message.timestamp - message.server.created_at).days), inline=False)
                        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                        await client.send_message(message.channel, embed=em)


            if message.server.me in message.mentions: #If someone mentions the bot
                if not MENTION_ENABLED:
                    return
                print('({1.hour:02d}:{1.minute:02d}){0.author.name} mentioned bot in {0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                print('\"{0.author.name}:{0.clean_content}\"'.format(message))
                if mention_timer.is_alive():
                    return
                if message.channel.id not in commands_channels:
                    mention_timer = Timer(MENTION_COOLDOWN, empty) #mention cooldown
                    mention_timer.start()

                rand = random.randint(5,15)
                if '?' in message.content:
                    rand_q = emojify(random.choice(ball8_quotes), message.server)
                elif ':boop:' in message.content:
                    rand_q = emojify(':boop:', message.server) + message.author.mention
                    print(rand_q)
                elif ':hugs:' in message.content:
                    rand_q = emojify(':hugs:', message.server) + message.author.mention
                else:
                    rand_q = emojify(random.choice(mention_quotes), message.server)
                print('And we answered in {0} sec with \"{1}\"'.format(rand, rand_q))
                await asyncio.sleep(rand)
                await client.send_message(message.channel, rand_q)
                
    if message.server:
        if message.server.id in authorized_servers:
            if message.channel.id not in serious_channels and message.channel.id != '151834220841533440': #staff
                for i in banned_words:
                    if i in message.content.lower():
                        if message.author.nick is None:
                            print('({1.hour:02d}:{1.minute:02d}){0.author.name} said banned word in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                            print('\"{0.author.name}:{0.content}\"'.format(message))
                            dmsg = '{0.author.name}`({0.author.id})` said banned word in #{0.channel.name} at {0.server.name}.\n\"{0.author.name}:{0.content}\"'.format(message)
                            await cog_notifications.dispatch(client, 'banned words', dmsg)
                        else:
                            print('({1.hour:02d}:{1.minute:02d}){0.author.nick}({0.author.name}) said banned word in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                            print('\"{0.author.nick}:{0.content}\"'.format(message))
                            dmsg = '{0.author.nick}({0.author.name})`({0.author.id})` said banned word in #{0.channel.name} at {0.server.name}.\n\"{0.author.nick}:{0.content}\"'.format(message)
                            await cog_notifications.dispatch(client, 'banned words', dmsg)
                        break
            
            if message.channel.id in general_channels:
                if message.attachments:
                    for i in message.attachments:
                        if i:
                            try:
                                if(i.get('width') is not None) and (i.get('height') > 128):
                                    if i.get('width') > 400:
                                        if (i.get('height')*0.75) < 128:
                                            break
                                    if message.author.nick is None:
                                        dmsg = '{0.author.name}`({0.author.id})` posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('width'),i.get('height'))
                                        print('({0.hour:02d}:{0.minute:02d})'.format(datetime.now())+dmsg)
                                        await cog_notifications.dispatch(client, 'oversized images', dmsg)
                                    else:
                                        dmsg = '{0.author.nick}({0.author.name})`({0.author.id})` posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('width'),i.get('height'))
                                        print('({0.hour:02d}:{0.minute:02d})'.format(datetime.now())+dmsg)
                                        await cog_notifications.dispatch(client, 'oversized images', dmsg)
                                    break
                            except AttributeError:
                                print('({1.hour:02d}:{1.minute:02d}){0.author.name} posted weird embed in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                                break
                if message.embeds:
                    for i in message.embeds:
                        if i.get('type') == 'image':
                            if(i.get('thumbnail').get('width')) and (i.get('thumbnail').get('height') > 128):
                                if i.get('thumbnail').get('width') > 400:
                                        if (i.get('thumbnail').get('height')*0.75) < 128:
                                            break
                                if message.author.nick is None:
                                    dmsg = '{0.author.name}`({0.author.id})` posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('thumbnail').get('width'),i.get('thumbnail').get('height'))
                                    print('({0.hour:02d}:{0.minute:02d})'.format(datetime.now())+dmsg)
                                    await cog_notifications.dispatch(client, 'oversized images', dmsg)
                                else:
                                    dmsg = '{0.author.nick}({0.author.name})`({0.author.id})` posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('thumbnail').get('width'),i.get('thumbnail').get('height'))
                                    print('({0.hour:02d}:{0.minute:02d})'.format(datetime.now())+dmsg)
                                    await cog_notifications.dispatch(client, 'oversized images', dmsg)
                                break

def emojify(text, server):
    sr = re.findall(':.*?:', text)
    for temoji in sr:
        for emoji in server.emojis:
            if emoji.name == temoji.strip(':'):
                text = text.replace(temoji, str(emoji))
                break
    return text

def stop_mass_mentions(text): #Puts invisible character after @ to escape mass pings
    if text:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    return text

def escape_code_line(text):
    if text:
        text = text.replace("`", "\\`")
    return text

last_posted_time = None

async def EQD_feed_poster(): #EQD feed fetcher. Every 10 minutes compares published time of last post on feed with last printed one
    await client.wait_until_ready()
    while not client.is_closed:
        print('({0.hour:02d}:{0.minute:02d})Checking EQD feed.'.format(datetime.now()))
        EQDfeed = feedparser.parse('https://www.equestriadaily.com/feeds/posts/default')
        global last_posted_time
        if not last_posted_time:
            last_posted_time = EQDfeed.entries[0].published
        if last_posted_time < EQDfeed.entries[0].published:
            for post in EQDfeed.entries:
                if last_posted_time >= post.published:
                    break
                print('New EQD post!\n{0.title}'.format(post))
                eqd_feed_message = ':newspaper:\n__***{0.title}***__\n{0.author}\n{0.link}\n{0.published_parsed.tm_year}-{0.published_parsed.tm_mon:02d}-{0.published_parsed.tm_mday:02d} {0.published_parsed.tm_hour:02d}:{0.published_parsed.tm_min:02d} at UTC/GMT+0'.format(post)
                global EQD_FEED_ENABLED
                if EQD_FEED_ENABLED:
                    await client.send_message(client.get_channel(eqd_feed_channel), eqd_feed_message)
        last_posted_time = EQDfeed.entries[0].published
        await asyncio.sleep(600) # task runs every 600 seconds (10 min)
	
def loop_f(): #1 hour loop. Milestone
    print('{0.hour:02d}:{0.minute:02d}\t-----------------------------------------------------------------------'.format(datetime.now()))
    global loop_timer
    loop_timer = Timer(3600,loop_f)
    loop_timer.start()
    
loop_timer = Timer(0,loop_f)

def empty(): #Empty function for cooldowns. There's probably a way without it
    return
    
meme_timer = Timer(0, empty) #initialize meme_timer
meme_timer.start()
mention_timer = Timer(0, empty) #initialize mention_timer
mention_timer.start()
derpi_timer = Timer(0, empty) #initialize derpi_timer
derpi_timer.start()

EQD_feed_task = client.loop.create_task(EQD_feed_poster()) #Background task


print('Run() begins...')

def run_client(client, *args, **kwargs): #Custom client.start shell to allow for autorestart
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(client.start(*args, **kwargs))
        except KeyboardInterrupt:
            print('Exit.')
            meme_timer.cancel()
            loop_timer.cancel()
            EQD_feed_task.cancel()
            loop.run_until_complete(client.close())
            return
        except Exception as e:
            print("Error", e)
        print("Restart in 60 seconds.")
        time.sleep(60)

run_client(client, TOKEN, bot=BOT) #True for real bot accounts, False for selfbots
