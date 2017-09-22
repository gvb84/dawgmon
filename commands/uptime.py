from . import *
from datetime import datetime

PARSE_STR = "%Y-%m-%d %H:%M:%S"

class UptimeCommand(ShellCommand):
	name = "uptime"
	command = "uptime -s"
	desc = "show uptime and check if reboot happened"
	supported = "linux"

	@staticmethod
	def parse(output=None):
		if not output:
			return None 
		try:
			return datetime.strptime(output.strip(), PARSE_STR)
		except ValueError:
			return None

	@staticmethod
	def compare(prev, cur):
		scur = cur.strftime(PARSE_STR)
		if not prev:
			return [D("system has been up since %s" % scur)]
		sprev = prev.strftime(PARSE_STR)
		if cur != prev:
			if cur > prev:
				return [W("system rebooted since last check (up since: %s)" % scur)]
			else:
				return [W("time traveling detected as uptime went from %s to %s" % (sprev, scur))]
		else:
			return [D("system didn't reboot since last check (up since: %s)" % scur)]
