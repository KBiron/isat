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
    smdcsv = csv.DictReader(smd_noradid_tlename)
    for row in smdcsv:
        smd_noradid[    row['noradid']]  = row['tlename']
        smd_noradid[int(row['noradid'])] = row['tlename']

# TODO:
# * If COMBINED has dupes, so will output SMD file :-(
# * Sort output by tle name

with open(SMD_PATH, 'w') as smd_tles_out:
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
                if name != smd_noradid[noradid]: # fails on missing leading zeros
                    logging.warning('Mismatch TLE names SMD=%s COMBINED=%s' %
                                    (smd_noradid[noradid], name))
                smd_tles_out.write(name)
                smd_tles_out.write(tle1)
                smd_tles_out.write(tle2)
