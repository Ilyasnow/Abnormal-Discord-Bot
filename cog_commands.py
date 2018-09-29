from datetime import datetime
import discord
import cog_config

def ihateyou(text):
    if text:
        text = text.replace("`", "\\`")
        text = text.replace("`", "\\`")
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
        text = text.replace("<", "<u200b")
    return text

def nobigcode(text):
    if text:
        text = text.replace("```", "`​`​`")
    return text

async def names(client, message, command=None):
    if len(command) == 1:
        userinfo_command = message.author.id
    else:
        userinfo_command = command [1]
    print('({1.hour:02d}:{1.minute:02d}){0.author.name} used `names command'.format(message, datetime.now()))
    if userinfo_command.isdecimal():
        user = message.server.get_member(userinfo_command)
    elif (userinfo_command.strip('<>@!')).isdecimal():
        user = message.server.get_member(userinfo_command.strip('<>@!'))
    else:
        user = message.server.get_member_named(userinfo_command)
    if not user:
        await client.send_message(message.channel, 'User not found.\nUse \`names <id/mention/name> to get recorded names of user.')
        return
    if user.avatar_url:
        user_avatar_url = user.avatar_url
    else:
        user_avatar_url = user.default_avatar_url
    em = discord.Embed(title=':information_source: User info', colour=user.colour)
    em.set_author(name='User: @{0.name}#{0.discriminator} - {0.id}'.format(user))
    em.set_thumbnail(url=user_avatar_url)
    em.add_field(name='User:', value=user.mention, inline=True)
    em.set_footer(text='{0} at UTC/GMT+0'.format(datetime.utcnow()))
    names = ', '.join(reversed(cog_config.read('Names', user.id).split('\n')))
    nicks = ', '.join(reversed(cog_config.read('Nicks', user.id).split('\n')))
    if not names:
        names = 'None has been recorded'
    if not nicks:
        nicks = 'None has been recorded'
    em.add_field(name='Names:', value="```\n{}\n```".format(nobigcode(names)), inline=False)
    em.add_field(name='Nicks:', value="```\n{}\n```".format(nobigcode(nicks)), inline=False)
    await client.send_message(message.channel, embed=em)
