from . import *

class CheckProcessessCommand(ShellCommand):
	name = "list_processes"
	command = "ps aux"
	desc = "monitors changes in the running processes (mostly for debugging)"

	@staticmethod
	def parse(output=None):
		res = {}
		if not output:
			return res
		lines = output.splitlines()
		# ignore the first header line of the output
		for line in lines[1:]:
			parts = line.split()
			user, pid = parts[0:2]
			pid = int(pid)
			cmd = parts[10]	

			# start will be HH:MM if started same day, MmmDD if different day
			# but same year and simply year if started a different year
			start = parts[8]
			res[pid] = (cmd, user, start)
		return res

	@staticmethod
	def compare(prev, cur):
		anomalies = []
		processes = merge_keys_to_list(prev, cur)
		for process in processes:
			if process not in prev:
				anomalies.append(D("process %i (%s) started" % (process, cur[process][0])))
				continue
			elif process not in cur:
				anomalies.append(D("process %i (%s) stopped" % (process, prev[process][0])))
				continue
			p, c = prev[process], cur[process]
			if p[0] != c[0]:
				anomalies.append(D("process %i changed from %s to %s" % (process, p[0], c[0])))
			elif p[1] != c[1]:
				anomalies.append(D("owner of process %i changed from %s to %s" % (process, p[1], c[1]))) 
		return anomalies
