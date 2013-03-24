======================
 README for TLE UTILS
======================

We want cron to pull TLEs from Celestrak nightly and store them in the
.../viz/tle/ directory. This has to be done cautiously to avoid
overwriting good files with damaged ones.

Generate a COMBINED.txt file that has all TLEs, with duplications removed.

* get_celestrak_files.py: does both

We maintain a list of Science Mission Directorate mission satellites
by NORAD ID, sinc the names are non-canonical. From this and the
COMBINED file, we gnerate a SMD.txt file which has all the SMD
missions that we can find.  These are the top menu in iSat's listing
of satellite groups.

* gen_smd_tles.py: uses COMBINED file and smd_noradid_tlename.csv


TODO
====

* Cronjob wrapper
* Ensure we put the files in the right dir
* COMBINED is *not* deduped.
