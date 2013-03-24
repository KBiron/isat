#!/usr/bin/env python
# Pull each Celestrak TLE file and save a local copy.
# Also save a combined (but deduped) .txt file.
# Finally save a file of Science Mission Directorate satellites.

# TODO:
# - If Celestrak ever adds or changes filenames we're screwed.
# - Is there a way to find this list of files? or is it static?

import csv
import logging
import os
import urllib2

CELESTRAC_BASE_URL = "http://www.celestrak.com/NORAD/elements/"
SMD_NORADID_TLENAME = 'smd_noradid_tlename.csv'
ALL_FNAME = 'ALL.txt'
SMD_FNAME = 'SMD.txt'
TLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       '..', 'viz', 'tle'))

ALL_PATH = os.path.join(TLE_DIR, ALL_FNAME)
SMD_PATH = os.path.join(TLE_DIR, SMD_FNAME)

logging.basicConfig(level=logging.INFO)

files = {
    "tle-new.txt": "Last 30 Days' Launches",
    "stations.txt": "Space Stations",
    "visual.txt": "100 (or so) Brightest",
    "1999-025.txt": "FENGYUN 1C Debris",
    "iridium-33-debris.txt": "IRIDIUM 33 Debris",
    "cosmos-2251-debris.txt": "COSMOS 2251 Debris",
    "weather.txt": "Weather",
    "noaa.txt": "NOAA",
    "goes.txt": "GOES",
    "resource.txt": "Earth Resources",
    "sarsat.txt": "Search & Rescue (SARSAT)",
    "dmc.txt": "Disaster Monitoring",
    "tdrss.txt": "Tracking and Data Relay Satellite",
    "geo.txt": "Geostationary",
    "intelsat.txt": "Intelsat",
    "gorizont.txt": "Gorizont",
    "raduga.txt": "Raduga",
    "molniya.txt": "Molniya",
    "iridium.txt": "Iridium",
    "orbcomm.txt": "Orbcomm",
    "globalstar.txt": "Globalstar",
    "amateur.txt": "Amateur Radio",
    "x-comm.txt": "Experimental",
    "other-comm.txt": "Other",
    "gps-ops.txt": "GPS Operational",
    "glo-ops.txt": "Glonass Operational",
    "galileo.txt": "Galileo",
    "sbas.txt": "Satellite-Based Augmentation System (WAAS/EGNOS/MSAS)",
    "nnss.txt": "Navy Navigation Satellite System (NNSS)",
    "musson.txt": "Russian LEO Navigation",
    "science.txt": "Space & Earth Science",
    "geodetic.txt": "Geodetic",
    "engineering.txt": "Engineering",
    "education.txt": "Education",
    "military.txt": "Miscellaneous Military",
    "radar.txt": "Radar Calibration",
    "cubesat.txt": "CubeSats",
    "other.txt": "Other",
}

# Get the list of NORAD IDs for SMD Missions.
# We don't really care about the TLE Name, it's a sanity check for humans
# Keep string and int representation to allow sloppy leading zeros.

smd_noradid = {}
with open(SMD_NORADID_TLENAME) as smd_noradid_tlename:
    smdcsv = csv.reader(smd_noradid_tlename)
    for (noradid, tlename) in smdcsv:
        smd_noradid[    noradid ] = tlename
        smd_noradid[int(noradid)] = tlename

# Read each TLE file from Celestrak, write to disk, keep in dict for deduping.

all_tles = {}
smd_tles = {}

def write_tle_file(tles, path):
    """Output TLEs sorted by name (tles is a dict keyed by noradid).
    """
    # Key by name so we can sort on it.
    name_tle = {val['name']: {'tle1': val['tle1'],
                              'tle2': val['tle2']}
                for (noradid, val) in tles.items()}
    with open(path, 'w') as tles_out:
        for name in sorted(name_tle):
            tles_out.write(name)
            tles_out.write(name_tle[name]['tle1'])
            tles_out.write(name_tle[name]['tle2'])

for fname, description in files.items():
    logging.info('Downloading from Celestrak: %s' % fname)
    response = urllib2.urlopen(CELESTRAC_BASE_URL + fname)
    tle_lines = response.readlines()
    # Just write verbatim, no alphabet or dedupe
    with open(os.path.join(TLE_DIR, fname), 'w') as out:
        out.writelines(tle_lines)
    while True:
        try:
            name = tle_lines.pop(0)
        except IndexError, e:
            break
        tle1 = tle_lines.pop(0)
        tle2 = tle_lines.pop(0)
        noradid = tle2[2:7]
        logging.debug('Name=%s NORADID="%s"' % (name.strip(), noradid))
        if not noradid:
            raise RuntimeError, 'NoradID from TLE2 nonexistent: %s' % tle2

        # If we found a dupe by noradid, keep just the first found.
        # What's the right way to ignore [+] and other suffixes?

        if noradid in all_tles:
            logging.debug('Ignoring dupe noradid=%s prev=%s name=%s' %
                            (noradid, all_tles[noradid]['name'].strip(),
                             name.strip()))
            continue
        all_tles[noradid] = {'name': name, 'tle1': tle1, 'tle2': tle2}

        # If we've got a SMD NORAD ID, keep it; warn on name change

        if noradid in smd_noradid or int(noradid) in smd_noradid:
            smd_tles[noradid] = all_tles[noradid] # from above
            logging.info('Found SMD: %s %s' % (noradid, name.strip()))
            if name.strip() != smd_noradid[int(noradid)].strip():
                logging.warning('Mismatch TLE names SMD=%s ALL=%s' %
                                (smd_noradid[int(noradid)].strip(),
                                 name.strip()))


write_tle_file(all_tles, ALL_PATH)
write_tle_file(smd_tles, SMD_PATH)

