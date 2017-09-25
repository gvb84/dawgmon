import os, subprocess
from datetime import datetime

DATE_PARSE_STR = "%Y-%m-%d %H:%M:%S.%f"

# return a list with unique and sorted set of keys of dictionary d1 and d2
def merge_keys_to_list(d1, d2):
	ret = list(set(list(d1.keys()) + list(d2.keys())))	
	ret.sort()
	return ret

# if subsecs is True we return mili/micro seconds too otherwise just seconds
def ts_to_str(timestamp, subsecs=True):
	return None if not timestamp else timestamp.strftime(DATE_PARSE_STR if subsecs else DATE_PARSE_STR[:-3])

# if subsecs is True we convert mili/micro seconds too otherwise the input
# string is assumed to only contain maximum second precision
def str_to_ts(s, subsecs=True):
	return None if not s else datetime.strptime(s, DATE_PARSE_STR if subsecs else DATE_PARSE_STR[:-3])

def get_osname():
	retcode, stdout, stderr = run_command(["uname", "-s"])
	if retcode != 0:
		raise Exception("cannot get OS name (uname -s failed)")
	lines = stdout.splitlines()
	if len(lines) != 1 or len(lines[0]) == 0:
		raise Exception("uname -s returned invalid and unexpected output")
	return lines[0].lower()

def run_command(cmd):
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()

	# XXX we should probably try and get the system encoding for
	# this instead of defaulting to UTF-8.
	stdout = stdout.decode("utf-8")
	stderr = stderr.decode("utf-8")
	retcode = p.returncode
	return (retcode, stdout, stderr)
