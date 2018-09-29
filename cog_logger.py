import logging
import discord
import time
import sys

te = open('abnormal-{}.out'.format(time.strftime("%Y-%m-%d_%H-%M")), encoding='utf-8', mode='w')  # File where you need to keep the logs

class Unbuffered:
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        te.write(data)    # Write the data of stdout here to a text file as well
    def flush(self):
        pass
sys.stdout=Unbuffered(sys.stdout)
sys.stderr=Unbuffered(sys.stderr)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='abnormal-{}.log'.format(time.strftime("%Y-%m-%d_%H-%M")), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
