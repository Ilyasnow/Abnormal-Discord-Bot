import discord
import os 
from datetime import datetime
from threading import Timer, Thread
#from derpibooru import Search, sort
import time
import winsound
import asyncio

TOKEN = "" #Your token
client = discord.Client()
timers = [] #list of Timers for raid detection
timers_q = [] #list of short Timers for raid detection
joined_users = [] #debug

authorized_servers = ['87583189161226240', #EQD
                      '475881818755956736',#SCP
                      '280418753236172811']#ASS
commands_channels = ['280418753236172811', #ASS #channel ID for `reason and `ponyr
                     '477269419765006345'] #SCP
authorized_channels = ['280418753236172811']#ASS #ponyville and #manehattan IDs
log_channel = '477236874948116481' #SCP #log output channel ID
ban_channel = '477236874948116481' #SCP #ban output channel ID
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
        em = discord.Embed(title=':white_check_mark:\nJoined the server {}'.format(member.server.name), colour=0x40EE40)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member), icon_url=member.avatar_url)
        em.add_field(name='User created on:', value=member.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((datetime.now() - member.created_at).days))
        em.set_thumbnail(url=member.avatar_url)
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_member_remove(member):
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} left server {0.server.name}.'.format(member, datetime.now()))
        em = discord.Embed(title=':x:\nLeft the server {}'.format(member.server.name), colour=0xEE4040)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member), icon_url=member.avatar_url)
        em.set_thumbnail(url=member.avatar_url)
        em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
        await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_member_update(member_before, member_after):
    #for i in authorized_servers:
        #if member_before in client.get_server(i).members:
    if True:
        if member_before.server.id in authorized_servers:
            #print('({1.hour:02d}:{1.minute:02d}){0.name} user update in {0.server.name}.'.format(member_before, datetime.now()))
            if set(member_before.roles) - set(member_after.roles):
                print('({1.hour:02d}:{1.minute:02d}){0.name} has lost roles in {0.server.name}.'.format(member_before, datetime.now()))
                roles_dif = ''
                for role in (set(member_before.roles) - set(member_after.roles)):
                    roles_dif += role.name + ', '
                roles_dif = roles_dif[:-2]
                print(roles_dif)
                em = discord.Embed(title=':flag_black:\nLost roles', description=roles_dif, colour=0xEE40EE)
                em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_after.avatar_url)
                em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                await client.send_message(client.get_channel(log_channel), embed=em)
            if set(member_after.roles) - set(member_before.roles):
                print('({1.hour:02d}:{1.minute:02d}){0.name} got new roles in {0.server.name}.'.format(member_before, datetime.now()))
                roles_dif = ''
                for role in (set(member_after.roles) - set(member_before.roles)):
                    roles_dif += role.name + ', '
                roles_dif = roles_dif[:-2]
                print(roles_dif)
                em = discord.Embed(title=':flag_white:\nGot new roles', description=roles_dif, colour=0xEE40EE)
                em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_after.avatar_url)
                em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                await client.send_message(client.get_channel(log_channel), embed=em)
            if member_before.name != member_after.name:
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their name.'.format(member_before, datetime.now()))
                print('{0.name} to {1.name}'.format(member_before, member_after))
                em = discord.Embed(title=':information_source:\nNew name', description='`{0.name}` changed to `{1.name}`'.format(member_before, member_after), colour=0x80A0EE)
                em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_after.avatar_url)
                em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                await client.send_message(client.get_channel(log_channel), embed=em)
            if member_before.avatar != member_after.avatar:
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their avatar.'.format(member_before, datetime.now()))
                em = discord.Embed(title=':information_source:\nNew avatar', colour=0x80A0EE)
                em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_after.avatar_url)
                em.set_image(url=member_after.avatar_url)
                em.set_thumbnail(url=member_before.avatar_url)
                em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                await client.send_message(client.get_channel(log_channel), embed=em)
            if member_before.nick != member_after.nick:
                print('({1.hour:02d}:{1.minute:02d}){0.name} has changed their nickname in {0.server.name}.'.format(member_before, datetime.now()))
                print('{0.name} changed to {1.nick}'.format(member_before, member_after))
                em = discord.Embed(title=':information_source:\nNew nickname', description='`{0.nick}` changed to `{1.nick}`'.format(member_before, member_after), colour=0x80A0EE)
                em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(member_after), icon_url=member_after.avatar_url)
                em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                await client.send_message(client.get_channel(log_channel), embed=em)

@client.event
async def on_member_ban(member):
    if member.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.name} has been banned from {0.server.name}.'.format(member, datetime.now()))
        #ban_messages = yield from client.logs_from(client.get_channel(ban_channel))
        #for i in ban_messages:
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
    if message.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.author.name}\'s message has been deleted from #{0.channel.name} at {0.server.name}.'.format(message, datetime.now()))
        print('\"{0.author.name}:{0.content}\"'.format(message))
        em = discord.Embed(title=':wastebasket:\nDeleted message from #{0.channel.name}'.format(message),description=':page_facing_up: **Message:**\n{0.content}'.format(message), colour=0xFEF888)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(message.author), icon_url=message.author.avatar_url)
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
    if (after.channel.id in log_channel) or after.author.bot:
        return
    if not before.embeds and after.embeds:
        return
    if before.server.id in authorized_servers:
        print('({1.hour:02d}:{1.minute:02d}){0.author.name} edited message from #{0.channel.name} at {0.server.name}.'.format(before, datetime.now()))
        print('Before:\"{0.author.name}:{0.content}\"\n After:\"{1.author.name}:{1.content}\"'.format(before, after))
        em = discord.Embed(title=':pencil2:\nEdited message in #{0.channel.name}'.format(before),description=':page_facing_up: **Message before:**\n{0.content}\n:pencil: **Message after:**\n{1.content}'.format(before, after), colour=0xFEF888)
        em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(before.author), icon_url=before.author.avatar_url) 
        attachments_text = ''
        first_attachment = ''
        #if (type(before.attachments) is dict and type(after.attachments) is dict) or (type(before.attachments) != type(after.attachments)) or (set(before.attachments) != set(after.attachments)):
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
    #if message.server is not None:
    #    if message.server.id in authorized_servers:
    #        if message.channel.id in commands_channels:
    #            if message.content.startswith('`ponyr '):
    #                params = Search().sort_by(sort.RANDOM).limit(1).parameters
    #                random_image = Search(**params).query(message.content[6:])
    #                await client.send_message(message.channel,'Random image with tags "{0}":\n{1}'.format(message.content[6:],random_image.large))
    #                print('({1.hour:02d}:{1.minute:02d}) Ponyr with tags:"{0}"'.format(message.content[6:], datetime.now()))
    if message.server is not None:
        if message.server.id in authorized_servers:
            if message.channel.id in commands_channels:
                if message.content.startswith('`reason '):
                    command = message.content.split()
                    #ban_messages = yield from client.logs_from(client.get_channel(ban_channel))
                    #for i in ban_messages:
                    if len(command) >= 3:
                        async for i in client.logs_from(client.get_channel(ban_channel)):
                            if (i.content is not None) and (len(i.content.split())>2):
                                if (i.content.split()[1])[0] == '#':
                                    ban_number = int(i.content.split()[1][1:-2])
                                    if int(command[1]) == ban_number:
                                        ban_message = i
                                        break
                        ban_message_new = ban_message.content.split('\n')
                        ban_message_new[2] = '**Moderator:** {0.name}({0.id})'.format(message.author)
                        ban_message_new[3] = '**Reason:** {0}'.format(' '.join(command[2:]))
                        print('({1.hour:02d}:{1.minute:02d}){0.author.name} hast claimed the ban #{2}'.format(message, datetime.now(), ban_number))
                        print('Case #{0}; Reason: {1}'.format(ban_number, " ".join(command[2:])))
                        await client.edit_message(ban_message, stop_mass_mentions('\n'.join(ban_message_new)))
                if message.content.startswith('`userinfo'):
                    command = message.content.split(maxsplit=1)
                    if len(command) >= 2:
                        print('({1.hour:02d}:{1.minute:02d}){0.author.name} used `userinfo command'.format(message, datetime.now()))
                        print('\"{0.author.name}:{0.content}\"'.format(message))
                        if message.server.get_member(command[1]) or message.server.get_member_named(command[1]):
                            if command[1].isdecimal():
                                user = message.server.get_member(command[1])
                            elif (command[1].strip('<>@')).isdecimal():
                                user = message.server.get_member(command[1].strip('<>@'))
                            else user = message.server.get_member_named(command[1])
                            if message.server.get_member(command[1]):
                                user = message.server.get_member(command[1])
                            else:
                                user = message.server.get_member_named(command[1])
                            if not user:
                            await client.send_message(client.get_channel(log_channel), 'User not found.\nUse `\`userinfo <id/mention/name>` to get info about user.')
                            em = discord.Embed(title=':information_source: User info', colour=user.colour)
                            em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(user))
                            em.set_thumbnail(url=user.avatar_url)
                            if user.nick:
                                em.add_field(name='Nickname:', value=user.nick)
                            em.add_field(name="User created on:", value=user.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((message.timestamp - user.created_at).days))
                            em.add_field(name="User joined on:", value=user.joined_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((message.timestamp - user.joined_at).days))
                            em.add_field(name="Roles:", value=", ".join([x.name for x in user.roles if x.name != "@everyone"]), inline=False)
                            em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                            await client.send_message(client.get_channel(log_channel), embed=em)
                if message.content.startswith('`serverinfo'):
                    print('({1.hour:02d}:{1.minute:02d}){0.author.name} used `serverinfo command'.format(message, datetime.now()))
                    print('\"{0.author.name}:{0.content}\"'.format(message))
                    em = discord.Embed(title=':information_source: Server info', colour=0x80A0EE)
                    em.set_author(name=message.server.name + ' - ' + message.server.id)
                    em.set_thumbnail(url=message.server.icon_url)
                    em.add_field(name='Members:', value=message.server.member_count)
                    em.add_field(name='Owner:(temp)', value=message.author.mention)
                    ver_levels = {'none':'None - No criteria set.',
                                  'low':'Low - Member must have a verified email on their Discord account.',
                                  'medium':'Medium - Member must have a verified email and be registered on Discord for more than five minutes.',
                                  'high':'High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the server itself for more than ten minutes.',
                                  'table_flip':'High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the server itself for more than ten minutes.'}
                    em.add_field(name='Verification level:', value=ver_levels.get(message.server.verification_level), inline=False)
                    em.add_field(name='Created on:', value=message.server.created_at.strftime("%d %b %Y %H:%M") + ' ({} days ago)'.format((message.timestamp - message.server.created_at).days))
                    em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
                    await client.send_message(client.get_channel(log_channel), embed=em)
                            
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
                    print('\"{0.author.nick}:{0.content}\"'.format(message))

def stop_mass_mentions(text):
    text = text.replace("@everyone", "@\u200beveryone")
    text = text.replace("@here", "@\u200bhere")
    return text
	
def loop_f():
    print('{0.hour:02d}:{0.minute:02d}\t-----------------------------------------------------------------------'.format(datetime.now()))
    global loop_timer
    loop_timer = Timer(3600,loop_f)
    loop_timer.start()
    
loop_timer = Timer(0,loop_f)

print('Run() begins...')
client.run(TOKEN, bot=True) #True for real bot accounts, False for selfbots

print('Exit.')
loop_timer.cancel()
client.close()
