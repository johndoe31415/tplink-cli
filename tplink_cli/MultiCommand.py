#!/usr/bin/python3
#
#	MultiCommand - Provide an openssl-style multi-command abstraction
#	Copyright (C) 2011-2024 Johannes Bauer
#
#	This file is part of pycommon.
#
#	pycommon is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pycommon is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pycommon; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#
#	File UUID 4c6b89d0-ec0c-4b19-80d1-4daba7d80967

import sys
import collections
import textwrap

from .FriendlyArgumentParser import FriendlyArgumentParser
from .PrefixMatcher import PrefixMatcher

class MultiCommand():
	RegisteredCommand = collections.namedtuple("RegisteredCommand", [ "name", "description", "parsergenerator", "action", "aliases", "visible" ])
	ParseResult = collections.namedtuple("ParseResults", [ "cmd", "args" ])

	def __init__(self, description = None, trailing_text = None, run_method = False):
		self._description = description
		self._trailing_text = trailing_text
		self._run_method = run_method
		self._commands = { }
		self._aliases = { }
		self._cmdorder = [ ]

	def register(self, commandname, description, parsergenerator, **kwargs):
		supported_kwargs = set(("aliases", "action", "visible"))
		if len(set(kwargs.keys()) - supported_kwargs) > 0:
			raise ValueError(f"Unsupported kwarg found. Supported: {', '.join(sorted(list(supported_kwargs)))}")

		if (commandname in self._commands) or (commandname in self._aliases):
			raise Exception(f"Command '{commandname}' already registered.")

		aliases = kwargs.get("aliases", [ ])
		action = kwargs.get("action")
		for alias in aliases:
			if (alias in self._commands) or (alias in self._aliases):
				raise Exception(f"Alias '{alias}' already registered.")
			self._aliases[alias] = commandname

		cmd = self.RegisteredCommand(commandname, description, parsergenerator, action, aliases, visible = kwargs.get("visible", True))
		self._commands[commandname] = cmd
		self._cmdorder.append(commandname)

	def _show_syntax(self, msg = None):
		output_file = sys.stderr if (msg is not None) else sys.stdout
		if msg is not None:
			print(f"Error: {msg}", file = output_file)
		print(f"usage: {sys.argv[0]} [command] [options]", file = output_file)
		print(file = output_file)
		if self._description is not None:
			print(self._description, file = output_file)
			print(file = output_file)
		print("Available commands:", file = output_file)
		for commandname in self._cmdorder:
			command = self._commands[commandname]
			if not command.visible:
				continue
			commandname_line = command.name
			for description_line in textwrap.wrap(command.description, width = 56):
				print("    %-15s    %s" % (commandname_line, description_line), file = output_file)
				commandname_line = ""
		print(file = output_file)
		if self._trailing_text is not None:
			for line in textwrap.wrap(self._trailing_text, width = 80):
				print(line, file = output_file)
			print(file = output_file)
		print("Options vary from command to command. To receive further info, type", file = output_file)
		print("    %s [command] --help" % (sys.argv[0]), file = output_file)

	def _show_syntax_cmd(self, cmdname, *args):
		self._show_syntax()
		return 0

	def _raise_error(self, msg, silent = False):
		if silent:
			raise Exception(msg)
		else:
			self._show_syntax(msg)
			sys.exit(1)

	def _getcmdnames(self):
		return set(self._commands.keys()) | set(self._aliases.keys())

	def parse(self, cmdline, silent = False):
		if len(cmdline) < 1:
			self._raise_error("No command supplied.")

		# Check if we can match the command portion
		pm = PrefixMatcher(self._getcmdnames() | set([ "-h", "--help" ]))
		try:
			supplied_cmd = pm.matchunique(cmdline[0])
		except Exception as e:
			self._raise_error("Invalid command supplied: %s" % (str(e)))

		if supplied_cmd in [ "-h", "--help" ]:
			return self.ParseResult(cmd = self.RegisteredCommand(name = "--help", description = None, parsergenerator = None, action = self._show_syntax_cmd, aliases = None, visible = False), args = None)
		elif supplied_cmd in self._aliases:
			supplied_cmd = self._aliases[supplied_cmd]

		command = self._commands[supplied_cmd]
		parser = FriendlyArgumentParser(prog = sys.argv[0] + " " + command.name, description = command.description, add_help = False)
		command.parsergenerator(parser)
		parser.add_argument("--help", action = "help", help = "Show this help page.")
		parser.setsilenterror(silent)
		args = parser.parse_args(cmdline[1:])
		return self.ParseResult(command, args)

	def run(self, cmdline, silent = False):
		parseresult = self.parse(cmdline, silent)
		if parseresult.cmd.action is None:
			raise Exception("Should run command '%s', but no action was registered." % (parseresult.cmd.name))
		result = parseresult.cmd.action(parseresult.cmd.name, parseresult.args)
		if self._run_method:
			result = result.run()
		return result

class BaseAction():
	def __init__(self, cmd, args):
		self._cmd = cmd
		self._args = args

	@property
	def cmd(self):
		return self._cmd

	@property
	def args(self):
		return self._args

	def run(self):
		raise NotImplementedError(self.__class__.__name__)

if __name__ == "__main__":
	mc = MultiCommand(description = "Run multiple export- and importthings", run_method = True)

	class ImportAction(BaseAction):
		def run(self):
			print("Import:", self.cmd, self.args)
			return self.args.returncode

	class ExportAction(BaseAction):
		def run(self):
			print("Export:", self.cmd, self.args)

	def genparser(parser):
		parser.add_argument("-r", "--returncode", metavar = "value", type = int, required = True, help = "Gives the exit code. Mandatory argument.")
		parser.add_argument("-i", "--infile", metavar = "filename", required = True, help = "Specifies the input text file that is to be imported. Mandatory argument.")
		parser.add_argument("-n", "--world", metavar = "name", choices = [ "world", "foo", "bar" ], default = "overworld", help = "Specifies the world name. Possible options are %(choices)s. Default is %(default)s.")
		parser.add_argument("-h", "--hello", action = "store_true", help = "Print 'hello world'")
		parser.add_argument("--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
	mc.register("import", "Import some file from somewhere", genparser, action = ImportAction, aliases = [ "ymport" ])

	def genparser(parser):
		parser.add_argument("-o", "--outfile", metavar = "filename", help = "Specifies the input text file that is to be imported.")
		parser.add_argument("--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
	mc.register("export", "Export some file to somewhere", genparser, action = ExportAction)

	returncode = mc.run(sys.argv[1:])
	sys.exit(returncode or 0)
