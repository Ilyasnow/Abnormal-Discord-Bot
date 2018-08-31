import configparser
from collections import deque
import io

#Create memory file, if none exist
def init():
    try:
        io.open('Abnormal_mem.txt', 'r+', encoding='utf16')
    except FileNotFoundError:
        f = io.open('Abnormal_mem.txt', 'w+', encoding='utf16')
        config = configparser.ConfigParser(allow_no_value=True)
        config['CONFIG'] = {'token': 'put_token_here',
                            'bot': 'True'}
        config['Names'] = {}
        config['Nicks'] = {}
        config['Reminders'] = {}
        config.write(f)

#Write value
def write(section, key, value):
    config = configparser.ConfigParser(allow_no_value=True)
    f = io.open('Abnormal_mem.txt', 'r', encoding='utf16')
    config.read_file(f)
    config[section][key] = value
    f = io.open('Abnormal_mem.txt', 'w', encoding='utf16')
    config.write(f)

#Format names and write to memory
def write_name(uid, name):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_file(io.open('Abnormal_mem.txt', 'r', encoding='utf16'))
    record = deque(read('Names', uid).split('\n'))
    if list(record) == ['']:
        record.clear()
    record.append(name)
    if len(record) > 20:
        record.popleft()
    write('Names', uid, '\n'.join(record))
    
#Format nick and write to memory
def write_nick(uid, nick):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_file(io.open('Abnormal_mem.txt', 'r', encoding='utf16'))
    record = deque(read('Nicks', uid).split('\n'))
    if list(record) == ['']:
        record.clear()
    record.append(nick)
    if len(record) > 20:
        record.popleft()
    write('Nicks', uid, '\n'.join(record))    

#Read value of key in section. Return value or None if failed.
def read(section, key):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_file(io.open('Abnormal_mem.txt', 'r', encoding='utf16'))
    if section in config:
        if key in config[section]:
            return config[section][key]
    return ''
