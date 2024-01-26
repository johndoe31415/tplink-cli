#	tplink-cli - Command line interface for TP-LINK smart switches
#	Copyright (C) 2017-2024 Johannes Bauer
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

import socket
import fcntl
import re
import subprocess
import asyncio
from .MACAddress import MACAddress

class NetTools(object):
	_IP_IPV4_ADDR_REGEX = re.compile(r"\s*inet (?P<addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(?P<subnet>\d{1,2})")
	@classmethod
	def get_mac_address(cls, ifname):
		SIOCGIFHWADDR = 0x8927
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		fd = s.fileno()
		ifname = ifname.encode().ljust(256, b"\x00")
		info = fcntl.ioctl(fd, SIOCGIFHWADDR,  ifname)
		mac = info[18 : 18 + 6]
		return MACAddress(mac)

	@classmethod
	def get_primary_ipv4_address(cls, ifname):
		stdout = subprocess.check_output([ "ip", "-4", "addr", "show", ifname, "label", ifname ]).decode("ascii")
		rematch = cls._IP_IPV4_ADDR_REGEX.search(stdout)
		if rematch is None:
			raise ValueError(f"Unable to determine IPv4 address of interface {ifname}.")
		rematch = rematch.groupdict()
		return rematch["addr"]

	@classmethod
	def get_default_gateway_interface(cls):
		with open("/proc/net/route") as f:
			for (lineno, line) in enumerate(f, 1):
				if lineno == 1:
					continue
				line = line.rstrip("\n").split("\t")
				interface = line[0]
				flags = int(line[3], 16)
				if (flags & 3) == 3:
					# Unicast, Gateway
					return interface
		raise ValueError("Unable to determine the interface pointing to a default gateway.")
