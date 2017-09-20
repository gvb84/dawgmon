import shlex
import subprocess

class CommandResult:

	@classmethod
	def succeeded(cls):
		raise Exception("not implemented for %s" % str(cls))

class ShellCommandResult(CommandResult):
	def __init__(self, stdout, stderr, retcode):
		super(ShellCommandResult, self).__init__()
		self.stdout = stdout
		self.stderr = stderr
		self.retcode = retcode

	def succeeded(self):
		return self.retcode == 0

class PythonCommandResult:
	def __init__(self):
		super(PythonCommandResult, self).__init__()

class Command:

	@classmethod
	def parse(cls, data):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def compare(cls, prev, cur):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def run(cls):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def canrun(cls):
		raise Exception("not implemented for %s" % str(cls))
	
class ShellCommand(Command):

	def _runProcess(self, cmd):
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = p.communicate()

		# XXX we should probably try and get the system encoding for
		# this instead of defaulting to UTF-8.
		stdout = stdout.decode("utf-8")
		stderr = stderr.decode("utf-8")
		retcode = p.returncode
		return (retcode, stdout, stderr)

	def run(self):
		cmd = shlex.split(self.command)

		# if canrun() was ran before and it returned True it means that
		# the object property _binary was set with the full path to the
		# commandline binary so we will replace that in the commandline
		# string to execute that command and only that one.
		if hasattr(self, "_binary"):
			cmd[0] = self._binary

		ret = self._runProcess(cmd)
		return ShellCommandResult(*ret)

	def canrun(self, ostype=None):
		# check ostype if there's a list of supported OS names specified
		if hasattr(self, "supported"):	
			supported = self.supported
			# convert to list if only one value is being set
			if type(supported) == str:
				supported = [supported]
			if ostype not in supported:
				return False
		# run 'whereis' on the first line in the command and if that
		# output can be validly parsed and returns an actual binary we
		# return True which means that the command most likely can be
		# run and that it will run explicitly with the cached binary
		# filename returned by 'whereis' and ached in self._binary
		binary, *parts = shlex.split(self.command)
		cmd = shlex.split("whereis -b %s" % binary)
		retcode, stdout, stderr = self._runProcess(cmd)
		if retcode != 0 or stdout.find(binary) != 0:
			return False
		stdout = stdout[len(binary):]
		if stdout[0] != ":":
			return False
		binaries = stdout[1:].strip().split()
		if len(binaries) == 0 or len(binaries[0]) == 0:
			return False
		self._binary = binaries[0]
		return True

class PythonCommand(Command):

	@classmethod
	def run():
		pass
	
class ListeningTCPUDPPortsCommand(ShellCommand):
	name = "list_tcpudp_ports"
	desc = "list changes in listening TCP/UDP ports for both IPv4/IPv6"
	command = "netstat --tcp --udp -ln"
	supported = "linux"

if __name__ == "__main__":
	ostype = "linux"
	cmd = ListeningTCPUDPPortsCommand()
	print(cmd.canrun())
	if cmd.canrun("linux"):
		res = cmd.run()
		print(res.succeeded())
		print(res.stdout, res.stderr)


input_1 = \
"""
tcp        0      0 0.0.0.0:1234            0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp6       0      0 ::1:631                 :::*                    LISTEN      -                   """

input_2 = \
"""
tcp        0      0 0.0.0.0:23411           0.0.0.0:*               LISTEN      26433/nc
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   """
