import discord
import os
import feedparser
from datetime import datetime
from threading import Timer, Thread
from derpibooru import Search, sort
import urbandictionary as ud
import time
import winsound
import asyncio

TOKEN = ""
client = discord.Client()

COMMAND_PREFIX = '`' #prefix used in `commands
DERPI_FILTER = 'safe AND score.gte:100 AND NOT meme' #additional filter for every derpi request
EQD_FEED_ENABLED = True
DERPIBOORU_ENABLED = True

timers = [] #list of Timers for raid detection
timers_q = [] #list of short Timers for raid detection
joined_users = [] #debug

authorized_servers = [''] #EQD
commands_channels = ['']  #channels for `commands
authorized_channels = [''] #ponyville and #manehattan IDs
log_channel = '' #log output channel ID
ban_channel = '' #ban output channel ID
eqd_feed_channel = '' #channel for eqd feed
art_commands = [''] #channels for derpi commands
img_filter = ['.jpg', '.jpeg', '.png', '.gif', 'imgur.com', 'deviantart.com',
              'instagram.com', 'youtube.com', 'twitter.com', 'youtu.be']
banned_words = ['fag', 'nigg', 'milf',
                'cunt', 'retard', 'autis', 'aryanne', 'nibba', 'ni**', 'fa**ot']
dir_path = os.path.dirname(os.path.realpath(__file__))
notification_sound = os.path.join(dir_path,'typewriter_click_quiet.wav') #alert sound. File with this name should be present in the same directory as this script (.wav only)

print('Starting...')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    global loop_timer
    if not loop_timer.is_alive():
        loop_f()

@client.event
async def on_member_join(member):
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} joined server {0.server.name}.'.format(member, datetime.now()))
        if member.avatar_url:
            member_avatar_url = member.avatar_url
        else:
            member_avatar_url = member.default_avatar_url
        em = discord.Embed(title=':white_check_mark:', description=member.mention+'\nJoined the server {}'.format(member.server.name), colour=0x40EE40)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member), icon_url=member_avatar_url)
        em.add_field(name='User created on:', value=member.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((datetime.now() - member.created_at).days), inline=False)
        em.set_thumbnail(url=member_avatar_url)
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_member_remove(member):
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} left server {0.server.name}.'.format(member, datetime.now()))
        if member.avatar_url:
            member_avatar_url = member.avatar_url
        else:
            member_avatar_url = member.default_avatar_url
        em = discord.Embed(title=':x:', description=member.mention+'\nLeft the server {}'.format(member.server.name), colour=0xEE4040)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member), icon_url=member_avatar_url)
        em.add_field(name='User created on:', value=member.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((datetime.now() - member.created_at).days), inline=False)
        em.set_thumbnail(url=member_avatar_url)
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_member_update(member_before, member_after):
    if True:
        if member_before.server.id in authorized_servers:
            if member_after.avatar_url:
                member_a_avatar_url = member_after.avatar_url
            else:
                member_a_avatar_url = member_after.default_avatar_url
            if member_before.avatar_url:
                member_b_avatar_url = member_before.avatar_url
            else:
                member_b_avatar_url = member_before.default_avatar_url
            em = discord.Embed(title=':information_source:', description=member_after.mention, colour=0xEE40EE)
            em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_a_avatar_url)
            em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
            
            if set(member_before.roles) - set(member_after.roles): #lost roles
                print('({1.hour:02d}:{1.minute:02d}){0.name} has lost roles in {0.server.name}.'.format(member_before, datetime.now()))
                roles_dif = ', '.join(i.name for i in (set(member_before.roles) - set(member_after.roles)))
                #for role in (set(member_before.roles) - set(member_after.roles)):
                #    roles_dif += role.name + ', '
                #roles_dif = roles_dif[:-2]
                print(roles_dif)
                em.title=':flag_black:'
                em.add_field(name='Lost role(s):', value=roles_dif, inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)
                
            if set(member_after.roles) - set(member_before.roles): #got roles
                print('({1.hour:02d}:{1.minute:02d}){0.name} got new roles in {0.server.name}.'.format(member_before, datetime.now()))
                roles_dif = ', '.join(i.name for i in (set(member_after.roles) - set(member_before.roles)))
                #for role in (set(member_after.roles) - set(member_before.roles)):
                #    roles_dif += role.name + ', '
                #roles_dif = roles_dif[:-2]
                print(roles_dif)
                em.title=':flag_white:'
                em.add_field(name='Got new role(s)', value=roles_dif, inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)
                
            if member_before.name != member_after.name: #name change
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their name.'.format(member_before, datetime.now()))
                print('{0.name} to {1.name}'.format(member_before, member_after))
                em.colour=0x80A0EE
                em.add_field(name='New name', value='`{0.name}` changed to `{1.name}`'.format(member_before, member_after), inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)
                
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
                em.add_field(name='New nickname', value='`{0.nick}` changed to `{1.nick}`'.format(member_before, member_after), inline=False)
                await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_member_ban(member):
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} has been banned from {0.server.name}.'.format(member, datetime.now()))
        ban_number = 0
        async for i in client.logs_from(client.get_channel(ban_channel)):
            if (i.content is not None) and (len(i.content.split())>2):
                if (i.content.split()[1])[0] == '#':
                    ban_number = int(i.content.split()[1][1:-2])
                    break
        ban_message = '**Case #{1}** | Ban :hammer:\n**User:** {0.name}({0.id})\n**Moderator:** \\_\\_\\_\n**Reason**: Type \\`reason {1} <reason> to add a reason.'.format(member, ban_number+1)
        await client.send_message(client.get_channel(ban_channel), stop_mass_mentions(ban_message))
        
@client.event
async def on_message_delete(message):
    if not message.server:
        return
    if message.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.author.name}\'s message has been deleted from #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
        print('\"{0.author.name}:{0.content}\"'.format(message))
        if message.author.avatar_url:
            member_avatar_url = message.author.avatar_url
        else:
            member_avatar_url = message.author.default_avatar_url
        em = discord.Embed(title=':wastebasket:', description=message.author.mention, colour=0xFE8800)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(message.author), icon_url=member_avatar_url)
        em.add_field(name='Deleted message from #{0.channel.name}'.format(message), value=':page_facing_up: **Message:**\n{0.content}'.format(message), inline = False)
        attachments_text = ''
        first_attachment = ''
        if message.attachments:
            for attachment in message.attachments:
                attachments_text += '{}[:link:]({}) '.format(attachment.get('filename'), attachment.get('proxy_url'))
                if not first_attachment:
                    first_attachment = attachment
            if attachments_text:
                em.add_field(name='Attachments:', value=attachments_text)
                em.set_thumbnail(url=first_attachment.get('proxy_url'))
        if message.embeds:
            em.add_field(name='Embeds:', value=':white_check_mark:')
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_message_edit(before, after):
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
            print('\"{0.author.name}:{0.content}\"'.format(before))
            em.title=':pushpin:'
            em.colour=0x88FFFF
            em.add_field(name='Message has been pinned in #{0.channel.name}'.format(before), value='{0.author.name}: {0.content}'.format(before), inline=False)
        elif before.pinned and not after.pinned: #message unpinned
            print('({1.hour:02d}:{1.minute:02d}){0.author.name}\'s message was unpinned in #{0.channel.name} at {0.server.name}.'.format(before, datetime.now()))
            print('\"{0.author.name}:{0.content}\"'.format(before))
            em.title=':round_pushpin:'
            em.colour=0x88FFFF
            em.add_field(name='Message has been unpinned in #{0.channel.name}'.format(before), value='{0.author.name}: {0.content}'.format(before), inline=False)
        else: #message edited
            print('({1.hour:02d}:{1.minute:02d}){0.author.name} edited message from #{0.channel.name} at {0.server.name}.'.format(before, datetime.now()))
            print('Before:\"{0.author.name}:{0.content}\"\n After:\"{1.author.name}:{1.content}\"'.format(before, after))
            em.title=':pencil2:'
            em.description=before.author.mention
            em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(before.author), icon_url=member_avatar_url)
            em.add_field(name='Edited message in #{0.channel.name}'.format(before), value=':page_facing_up: **Message before:**\n{0.content}\n:pencil: **Message after:**\n{1.content}'.format(before, after), inline=False)
        attachments_text = ''
        first_attachment = ''
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
    if message.server is not None: #not DMs
        if message.server.id in authorized_servers:
            global DERPIBOORU_ENABLED
            global EQD_FEED_ENABLED
            
            if message.channel.id in art_commands:
                if message.content.startswith(COMMAND_PREFIX):
                    command = message.content.split(' ' , maxsplit=1)
            
                    if command[0] == COMMAND_PREFIX+'ponyr':
                        if not DERPIBOORU_ENABLED:
                            return
                        if len(command) == 1:
                            derpi_query = ''
                        else:
                            derpi_query = command[1] + ' AND '
                        print('({1.hour:02d}:{1.minute:02d}) Ponyr with tags:"{0}"'.format(derpi_query+DERPI_FILTER, datetime.now()))
                        for image in Search().sort_by(sort.RANDOM).query(derpi_query+DERPI_FILTER):
                            await client.send_message(message.channel, image.url)
                            break
                        
                    if command[0] == COMMAND_PREFIX+'pony':
                        if not DERPIBOORU_ENABLED:
                            return
                        if len(command) == 1:
                            derpi_query = ''
                        else:
                            derpi_query = command[1] + ' AND '
                        print('({1.hour:02d}:{1.minute:02d}) Pony with tags:"{0}"'.format(derpi_query+DERPI_FILTER, datetime.now()))
                        for image in Search().query(derpi_query+DERPI_FILTER):
                            await client.send_message(message.channel, image.url)
                            break
            
            if message.channel.id in commands_channels:
                if message.content.startswith(COMMAND_PREFIX):
                    command = message.content.split(' ' , maxsplit=1)

                    if command[0] == COMMAND_PREFIX+'togglederpi':
                        DERPIBOORU_ENABLED = not DERPIBOORU_ENABLED
                        if DERPIBOORU_ENABLED:
                            await client.send_message(message.channel, 'Derpibooru commands are now enabled')
                        else:
                            await client.send_message(message.channel, 'Derpibooru commands are now disabled')

                    if command[0] == COMMAND_PREFIX+'togglefeed':
                        EQD_FEED_ENABLED = not EQD_FEED_ENABLED
                        if EQD_FEED_ENABLED:
                            await client.send_message(message.channel, 'EQD feed is now enabled')
                        else:
                            await client.send_message(message.channel, 'EQD feed is now disabled')

                    if command[0] == COMMAND_PREFIX+'urban':
                        if len(command) == 1:
                            return
                        print('({0.hour:02d}:{0.minute:02d}) Urban for word "{1}"'.format(datetime.now(), command[1]))
                        defs = ud.define(command[1])
                        em = discord.Embed(title=defs[0].word, description=defs[0].definition)
                        em.add_field(name='Example', value=defs[0].example)
                        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                        await client.send_message(message.channel, em)

                    if command[0] == COMMAND_PREFIX+'ping':
                        print('({0.hour:02d}:{0.minute:02d}) pong'.format(datetime.now()))
                        await client.send_message(message.channel, 'pong')
                        
                    if command[0] == COMMAND_PREFIX+'reason':
                        if len(command) == 1:
                            return
                        reason_command = command[1].split(' ', maxsplit=1)
                        if len(reason_command) >= 2:
                            async for i in client.logs_from(client.get_channel(ban_channel)):
                                if (i.content is not None) and (len(i.content.split())>2):
                                    if (i.content.split()[1])[0] == '#':
                                        ban_number = int(i.content.split()[1][1:-2])
                                        if int(reason_command[0]) == ban_number:
                                            ban_message = i
                                            break
                            if not ban_message:
                                return
                            ban_message_new = ban_message.content.split('\n')
                            ban_message_new[2] = '**Moderator:** {0.name}({0.id})'.format(message.author)
                            ban_message_new[3] = '**Reason:** {0}'.format(reason_command[1])
                            print('({1.hour:02d}:{1.minute:02d}){0.author.name} has claimed the ban #{2}'.format(message, datetime.now(), ban_number))
                            print('Case #{0}; Reason: {1}'.format(ban_number, reason_command[1]))
                            await client.edit_message(ban_message, stop_mass_mentions('\n'.join(ban_message_new)))
                            
                    if command[0] == COMMAND_PREFIX+'userinfo':
                        if len(command) == 1:
                            userinfo_command = message.author.id
                        else:
                            userinfo_command = command [1]
                        print('({1.hour:02d}:{1.minute:02d}){0.author.name} used `userinfo command'.format(message, datetime.now()))
                        print('\"{0.author.name}:{0.content}\"'.format(message))
                        if userinfo_command.isdecimal():
                            user = message.server.get_member(userinfo_command)
                        elif (userinfo_command.strip('<>@!')).isdecimal():
                            user = message.server.get_member(userinfo_command.strip('<>@!'))
                        else:
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
                        
                    if command[0] == COMMAND_PREFIX+'serverinfo':
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


                

                
    if message.server is not None:
        if message.server.id in authorized_servers:
            for i in banned_words:
                if i in message.content.lower():
                    winsound.PlaySound(notification_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    if message.author.nick is None:
                        print('({1.hour:02d}:{1.minute:02d}){0.author.name} said banned word in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                        print('\"{0.author.name}:{0.content}\"'.format(message))
                    else:
                        print('({1.hour:02d}:{1.minute:02d}){0.author.nick}({0.author.name}) said banned word in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                        print('\"{0.author.nick}:{0.content}\"'.format(message))
                    break
            #if not message.author.bot:
            if message.channel.id in authorized_channels:
                if message.attachments is not None:
                    for i in message.attachments:
                        if i is not None:
                            try:
                                if(i.get('width') is not None) and (i.get('height') > 128):
                                    if i.get('width') > 400:
                                        if (i.get('height')*0.75) < 128:
                                            break
                                    winsound.PlaySound(notification_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
                                    if message.author.nick is None:
                                        print('({3.hour:02d}:{3.minute:02d}){0.author.name} posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('width'),i.get('height'),datetime.now()))
                                    else:
                                        print('({3.hour:02d}:{3.minute:02d}){0.author.nick}({0.author.name}) posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('width'),i.get('height'),datetime.now()))
                                    break
                            except AttributeError:
                                print('({1.hour:02d}:{1.minute:02d}){0.author.nick}({0.author.name}) posted weird embed in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                                break
                if message.embeds is not None:
                    for i in message.embeds:
                        if i is not None:
                            if(i.get('thumbnail').get('width') is not None) and (i.get('thumbnail').get('height') > 128):
                                winsound.PlaySound(notification_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
                                if message.author.nick is None:
                                    print('({3.hour:02d}:{3.minute:02d}){0.author.name} posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('thumbnail').get('width'),i.get('thumbnail').get('height'),datetime.now()))
                                else:
                                    print('({3.hour:02d}:{3.minute:02d}){0.author.nick}({0.author.name}) posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(message, i.get('thumbnail').get('width'),i.get('thumbnail').get('height'),datetime.now()))
                                break
                if message.author.bot:
                    winsound.PlaySound(notification_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    print('({1.hour:02d}:{1.minute:02d})(Bot){0.author.name} is rampaging in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                for j in img_filter:
                    if ('://' in message.content.lower()) and (j in message.content.lower()):
                        if message.author.nick is None:
                            print('({1.hour:02d}:{1.minute:02d}){0.author.name} posted an image link in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                        else:
                            print('({1.hour:02d}:{1.minute:02d}){0.author.nick}({0.author.name}) posted an image link in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                        break
                        msg_emb = message
                        time.sleep(2.5)
                        msg_emb = get_message(msg_emb.channel, msg_emb.id)
                        if msg_emb.embeds is not None:
                            for i in msg_emb.embeds:
                                if i is not None:
                                    if(i.get('thumbnail').get('width') is not None) and (i.get('thumbnail').get('height') > 128):
                                        winsound.PlaySound(notification_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
                                        if message.author.nick is None:
                                            print('({3.hour:02d}:{3.minute:02d}){0.author.name} posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(msg_emb, i.get('thumbnail').get('width'),i.get('thumbnail').get('height'),datetime.now()))
                                        else:
                                            print('({3.hour:02d}:{3.minute:02d}){0.author.nick}({0.author.name}) posted a picture({1}x{2}) in #{0.channel.name} at {0.server.name}.'.format(msg_emb, i.get('thumbnail').get('width'),i.get('thumbnail').get('height'),datetime.now()))
                                        break
            if 'https://discord.gg/' in message.content.lower():
                winsound.PlaySound(notification_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
                if message.author.nick is None:
                    print('({1.hour:02d}:{1.minute:02d}){0.author.name} posted invite link in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                    print('\"{0.author.name}:{0.content}\"'.format(message))
                else:
                    print('({1.hour:02d}:{1.minute:02d}){0.author.nick}({0.author.name}) posted invite link in #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
                    print('\"{0.author.nick}:{0.coart_commandsntent}\"'.format(message))

def stop_mass_mentions(text):
    text = text.replace("@everyone", "@\u200beveryone")
    text = text.replace("@here", "@\u200bhere")
    return text

last_posted_time = None

async def EQD_feed_poster():
    await client.wait_until_ready()
    while not client.is_closed:
        print('({0.hour:02d}:{0.minute:02d})Checking EQD feed...'.format(datetime.now()))
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
	
def loop_f():
    print('{0.hour:02d}:{0.minute:02d}\t-----------------------------------------------------------------------'.format(datetime.now()))
    global loop_timer
    loop_timer = Timer(3600,loop_f)
    loop_timer.start()
    
loop_timer = Timer(0,loop_f)

client.loop.create_task(EQD_feed_poster())
print('Run() begins...')
client.run(TOKEN, bot=True) #True for real bot accounts, False for selfbots

print('Exit.')
loop_timer.cancel()
client.close()
