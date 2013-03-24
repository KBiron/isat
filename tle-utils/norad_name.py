#!/usr/bin/python
# Read COMBINED.txt and show only NORADID and NAME
# for inclusion on Science Mission satelites
# Output with TAB so it can be pasted into an Excel spread

import logging

tle = {}
with open('COMBINED.txt') as f:
    while True:
        try:
            name = f.readline().strip()
            if not name:
                break
            tle1 = f.readline()
            tle2 = f.readline()
            tle[name] = tle2[2:7]
        except Exception, e:
            logging.error(e)

for name, id in sorted(tle.items()):
    print '%s,%s' % (id, name)
