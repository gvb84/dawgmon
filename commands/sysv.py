from . import *

class ListSystemVInitJobsCommand(ShellCommand):
	name = "list_sysvinit_jobs"
	command = "service --status-all"
	desc = "analyze changes in available System V init jobs"
	supported = "linux"

	@staticmethod
	def parse(output=None):
		res = {}
		if not output:
			return res
		lines = output.splitlines()
		for line in lines:
			parts = line.split()
			res[parts[3]] = parts[1]
		return res

	@staticmethod
	def compare(prev, cur):
		anomalies = []
		services = merge_keys_to_list(prev, cur)
		for service in services:
			if service not in prev:	
				anomalies.append(C("sysvinit job %s added" % service))
				continue
			elif service not in cur:
				anomalies.append(C("sysvinit job %s removed" % service))
				continue
			p, c = prev[service], cur[service]
			if p == c:
				continue
			if p == "+" and c == "-":
				s = "stopped"
			elif p =="-" and c == "+":
				s = "started"
			else:
				s = "unknown"
			anomalies.append(C("sysvinit job %s %s" % (service, s)))
		return anomalies
