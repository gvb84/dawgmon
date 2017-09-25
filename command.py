import shlex, subprocess

class CommandResult:

	@classmethod
	def parse(cls):
		raise Exception("not implemented for %s" % str(cls))

	# called when serializing results for the cache
	@classmethod
	def serialize(cls):
		raise Exception("not implemented for %s" % str(cls))

	# returns True if the command succeeded or False if it failed
	@classmethod
	def succeeded(cls):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def error(cls):
		raise Exception("not implemented for %s" % str(cls))

class ShellCommandResult(CommandResult):
	def __init__(self, cmd, retcode, stdout, stderr):
		super(ShellCommandResult, self).__init__()
		self.cmd = cmd
		self.retcode = retcode
		self.stdout = stdout
		self.stderr = stderr

	def parse(self):
		if not self.succeeded():
			raise Exception("command didn't succeed so cannot parse result")
		return self.cmd.parse(self.stdout)

	def serialize(self):
		return {"cmd":self.cmd.name,"res":(self.retcode, self.stdout, self.stderr)}

	@staticmethod
	def deserialize(cmd, data):
		if not isinstance(cmd, ShellCommand):
			return None
		if type(data) != dict:
			return None
		cmd_name = data["cmd"] if "cmd" in data else None
		if not cmd_name or cmd_name != cmd.name:
			return None
		return ShellCommandResult(cmd, *data["res"])

	def succeeded(self):
		return self.retcode == 0

	def error(self):
		if self.succeeded():
			return ""
		# should use the rewritten command (after the whereis run) for nicer output
		# instead of the one in the code which is self.cmd.command
		return "\n%s\n%s\n" % (self.cmd.command, self.stderr)

class PythonCommandResult:
	def __init__(self):
		super(PythonCommandResult, self).__init__()

	def succeeded(self):
		return False

class Command:

	@classmethod
	def parse(cls):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def compare(cls, prev, cur):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def run(cls):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def canrun(cls, ostype=None):
		raise Exception("not implemented for %s" % str(cls))

	@classmethod
	def deserialize_result(cls, data=None):
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
		return ShellCommandResult(self, *ret)

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

	def deserialize_result(self, data):
		return ShellCommandResult.deserialize(self, data)

class PythonCommand(Command):

	@classmethod
	def run():
		pass
