#!/usr/bin/env python
# -*- coding=utf-8 -*-

from sys import path, argv, exit
import datetime
import unicodedata
from os.path import expanduser, getmtime, exists
from subprocess import Popen, PIPE
import json
import re

home = expanduser('~')

from pystickies.pystickies import parseStickies
from workflow import Workflow

OSX_NINE_DATABASE_FILE = home + '/Library/StickiesDatabase'

def get_db_path():
    return OSX_NINE_DATABASE_FILE

def main(wf):
    filename = u'database_cache.txt'
    update_flag = False
    stickies = []
    if exists(filename):
        mtime = getmtime(filename)
        lastupdate = datetime.datetime.fromtimestamp(mtime)
        if lastupdate < datetime.datetime.now() - datetime.timedelta(minutes=1):
            update_flag = True 
    else:
        update_flag = True

    if update_flag:
        f = open(filename, 'w')
        db_path = get_db_path()
        rtfs = parseStickies(db_path)
        for rtf in rtfs:
            pr = Popen(["textutil", "-convert", "txt", "-stdin","-stdout"],
                stdout=PIPE,
                stderr=PIPE,
                stdin=PIPE)
            (out, error) = pr.communicate(rtf)
            out = unicodedata.normalize('NFC', out.decode('utf-8'))
            stickies.append(out)
        json.dump(stickies, f)
    else:
        f = open(filename)
        stickies = json.load(f)
    query = unicodedata.normalize('NFC', argv[1].decode('utf-8'))
    item_isset = False
    if query == u"clear":
        wf.add_item(
                u'CLEAR CACHED DATABASE',
                arg=u'clear',
                valid=True)
        item_isset = True

    query = re.compile(query, re.IGNORECASE)
    for stickie in stickies:
        m = query.search(stickie)
        if m:
            index = m.start(0)
            title = stickie[:50]
            arg = stickie[:26]
            start_offset = 23
            end_offset = 65
            start = index - start_offset if index > start_offset else 0
            end = start + end_offset if len(stickie) > start + end_offset else len(stickie)
            subtitle = stickie[start:end].replace('\n','')
            wf.add_item(title, subtitle, arg=arg, valid=True)
            item_isset = True
    if item_isset is False:
        wf.add_item(u'No Item')
    wf.send_feedback()

if __name__ == '__main__':
    if len(argv) != 2:
        exit()

    wf = Workflow()
    exit(wf.run(main))
