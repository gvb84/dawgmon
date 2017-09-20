from . import *

class IsRestartRequiredCommand(ShellCommand):
	name = "needs_restart"
	command = "sh -c 'if test -f /var/run/reboot-required.pkgs ; then cat /var/run/reboot-required.pkgs; fi'"
	desc = "checks whether a reboot is required (Ubuntu-only)"
	supported = "linux"

	@staticmethod
	def parse(output):
		return output

	@staticmethod
	def compare(prev, cur):
		if len(cur) > 0:
			pkgs = cur.splitlines()
			pkgs.sort()
			return [W("reboot required"), D("reboot required because of packages [%s]" % (",".join(pkgs)))]
		return []
