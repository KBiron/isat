#!/usr/bin/env python
# Read list of SMD NORAD IDs and pull corresponding TLEs from
# COMBINED TLE file into separate SMD TLE file.

import csv
import logging
import os

SMD_NORADID_TLENAME = 'smd_noradid_tlename.csv'
COMBINED = 'COMBINED.txt'
SMD = 'SMD.txt'
TLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       '..', 'viz', 'tle'))

COMBINED_PATH = os.path.join(TLE_DIR, COMBINED)
SMD_PATH = os.path.join(TLE_DIR, SMD)

logging.basicConfig(level=logging.INFO)

# We don't really care about the TLE Name, it's a sanity check for humans
# Keep string and int representation to allow sloppy leading zeros.

smd_noradid = {}
with open(SMD_NORADID_TLENAME) as smd_noradid_tlename:
    smdcsv = csv.reader(smd_noradid_tlename)
    for (noradid, tlename) in smdcsv:
        smd_noradid[    noradid ] = tlename
        smd_noradid[int(noradid)] = tlename

# TODO:
# * If COMBINED has dupes, so will output SMD file :-(
# * Sort output by tle name

# PROBLEM:
# Different Celestrak files have different names for the same satellite:
# geo.txt:430:    GOES 12                 
# goes.txt:34:    GOES 12 [B]             
# sarsat.txt:10:  GOES 12                 
# weather.txt:13: GOES 12                 
# Some have [+], [-], [B], [P], [S]
# I don't know what they mean, can't find docs.
# I've also seen: [DASS], [SYLDA], [TETHERED] but assume this is OK.
# This makes it confusing to keep unique sats -- which name is
# correct for the given NORAD ID?

tles = {}
with open(COMBINED_PATH, 'r') as combined:
    while True:
        name = combined.readline()
        if not name.strip():   # read doesn't trip EOF exception
            break
        tle1 = combined.readline()
        tle2 = combined.readline()
        noradid = tle2[2:7]
        logging.debug('Name=%s NORADID="%s"' % (name.strip(), noradid))
        if not noradid:
            raise RuntimeError, 'NoradID from TLE2 nonexistent: %s' % tle2
        if noradid in smd_noradid or int(noradid) in smd_noradid:
            logging.info('COMBINED TLE has SMD NORAD ID: %s' % noradid)
            if name.strip() != smd_noradid[int(noradid)].strip():
                logging.warning('Mismatch TLE names SMD=%s COMBINED=%s' %
                                (smd_noradid[int(noradid)], name.strip()))
            # If we found a dupe by noradid, keep just the first.
            # What's the right way to ignore [+] and other suffixes?
            if noradid in tles:
                logging.warning('Dupe noradid=%s prev=%s name=%s' %
                                (noradid, tles[noradid]['name'].strip(), name.strip()))
            else:
                tles[noradid] = {'name': name, 'tle1': tle1, 'tle2': tle2}

# Output TLEs sorted by name (it's keyed by noradid)

name_tle = {val['name']: {'tle1': val['tle1'],
                   'tle2': val['tle2']} for (noradid, val) in tles.items()}
with open(SMD_PATH, 'w') as smd_tles_out:
    for name in sorted(name_tle):
        smd_tles_out.write(name)
        smd_tles_out.write(name_tle[name]['tle1'])
        smd_tles_out.write(name_tle[name]['tle2'])
