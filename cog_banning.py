from datetime import datetime
import discord
import asyncio
import re

ban_channel = '279779468204048414' #SCP #ban output channel ID

def stop_mass_mentions(text):
    if text:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    return text

def escape_code_line(text):
    if text:
        text = text.replace("`", "\\`")
    return text

class CaseTemplate:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def find_id(text):
    sr = re.findall('\(.*?\)', text)
    if sr:
        return sr[-1].strip('()')
    return ''
    
def disjoin(text):
    if len(text.split('\n')) != 4:
        return None
    t = text.split('\n')
    t1 = t[0].replace('**','').split(' | ')
    return CaseTemplate(case_number = int(t1[0].split()[1][1:]),
                       ban_type = t1[1].split()[0],
                       user_id = find_id(t[1]),
                       mod_id = find_id(t[2]),
                       reason = (t[3].split(maxsplit=1))[1])

def join(CaseTemplate, User, Mod=None):
    try:
        if CaseTemplate.case_type == 'Ban':
            ctype = 'Ban :hammer:'
        elif CaseTemplate.case_type == 'Unban':
            ctype = 'Unban :lock_with_ink_pen:'
        else:
            ctype = ''
        if CaseTemplate.mod_id:
            if Mod:
                mline = '{}({})'.format(Mod.name,CaseTemplate.mod_id)
            else:
                mline = '{}({})'.format('???',CaseTemplate.mod_id)
        else:
            mline = '\\_\\_\\_'
        if CaseTemplate.reason:
            rline = CaseTemplate.reason
        else:
            rline = 'Type `reason {} <reason> to add a reason.'.format(CaseTemplate.case_number)
    except Exception as e:
        print(e)
        return None
    line = []
    line.append('**Case #{}** | {}'.format(CaseTemplate.case_number, ctype))
    line.append('**User:** {}({})'.format(User.name,CaseTemplate.user_id))
    line.append('**Moderator:** {}'.format(mline))
    line.append('**Reason**: {}'.format(rline))
    return '\n'.join(line)
    

async def ban(client, member):
    print('({1.hour:02d}:{1.minute:02d}){0.name} has been banned from {0.server.name}.'.format(member, datetime.now()))
    case_number = 0
    async for i in client.logs_from(client.get_channel(ban_channel)):
        if (i.content is not None):
            d = disjoin(i.content)
            if d and d.ban_type == 'Ban':
                case_number = d.case_number
                break
            
    ban_message = join(CaseTemplate(case_number = case_number+1,
                                    case_type = 'Ban',
                                    user_id = member.id,
                                    mod_id = '',
                                    reason = ''),
                       member)
    await client.send_message(client.get_channel(ban_channel), escape_code_line(stop_mass_mentions(ban_message)))


async def unban(client, server, user):
    print('({0.hour:02d}:{0.minute:02d}){1.name} has been unbanned from {2.name}.'.format(datetime.now(), user, server))
    case_number = None
    async for i in client.logs_from(client.get_channel(ban_channel), limit=1000):
        if (i.content is not None):
            d = disjoin(i.content)
            if d and d.ban_type == 'Ban':
                if d.user_id == user.id:
                    case_number = d.case_number
                    break
    if not case_number:
        case_number = '?'
    unban_message = join(CaseTemplate(case_number = case_number,
                                      case_type = 'Unban',
                                      user_id = user.id,
                                      mod_id = d.mod_id,
                                      reason = ''),
                         user, Mod=server.get_member(d.mod_id))
    await client.send_message(client.get_channel(ban_channel), escape_code_line(stop_mass_mentions(unban_message)))

async def reason(client, message, command=None):
    if len(command) <= 1:
        await client.send_message(message.channel, '```\n'+command[0]+' <case_number> <reason>\n```')
        return
    reason_command = command[1].split(' ', maxsplit=1)
    if len(reason_command) >= 1:
        case_message = None
        async for i in client.logs_from(client.get_channel(ban_channel)):
            if (i.content is not None):
                d = disjoin(i.content)
                if d:
                    if int(reason_command[0]) == d.case_number:
                        case_message = i
                        break
        if not case_message:
            await client.send_message(message.channel, 'No case {} found'.format(reason_command[0]))
            return
        if len(reason_command) < 2:
            reason_command.append('')
        
        case_message_new = case_message.content.split('\n')
        case_message_new[2] = '**Moderator:** {0.name}({0.id})'.format(message.author)
        case_message_new[3] = '**Reason:** {0}'.format(reason_command[1])
        print('({1.hour:02d}:{1.minute:02d}){0.author.name} has claimed the case #{2}'.format(message, datetime.now(), d.case_number))
        print('Case #{0}; Reason: {1}'.format(d.case_number, reason_command[1]))
        await client.edit_message(case_message, escape_code_line(stop_mass_mentions('\n'.join(case_message_new))))
        await client.send_message(message.channel, 'Case {} claimed'.format(reason_command[0]))
    else:
        await client.send_message(message.channel, '```\n'+command[0]+' <case_number> <reason>\n```')

