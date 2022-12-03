#	tplink-cli - Command line interface for TP-LINK smart switches
#	Copyright (C) 2017-2022 Johannes Bauer
#
#	This file is part of tplink-cli.
#
#	tplink-cli is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	tplink-cli is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with tplink-cli; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import re
import sys
from TPLinkPacket import TPLinkPacket

class PacketDumper(object):
	_WIRESHARK_RE = re.compile("^[0-9a-f]{4}  (?P<hex>[0-9a-f]{2} .*)  ")
	_TCPDUMP_RE = re.compile("	0x[0-9a-f]{4}:\s+(?P<hex>.{39})")
	def __init__(self):
		self._data = bytearray()

	def _show_packet(self):
		if len(self._data) == 0:
			return
		packet = TPLinkPacket.deserialize(self._data[28:])
		packet.dump()
		self._data = bytearray()

	def _parse_tcpdump_line(self, line):
		result = self._TCPDUMP_RE.match(line)
		if not result:
			self._show_packet()
		else:
			result = result.groupdict()
			new_data = bytes.fromhex(result["hex"])
			self._data += new_data
			if len(new_data) != 16:
				self._show_packet()

	def parse_tcpdump_stdin(self):
		for line in sys.stdin:
#			print("LINE", line)
			self._parse_tcpdump_line(line)
