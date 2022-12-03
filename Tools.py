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

import socket
import fcntl

class NetTools(object):
	@classmethod
	def get_mac_address(cls, ifname):
		SIOCGIFHWADDR = 0x8927
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		fd = s.fileno()
		ifname = ifname.encode().ljust(256, b"\x00")
		info = fcntl.ioctl(fd, SIOCGIFHWADDR,  ifname)
		mac = info[18 : 18 + 6]
		return mac

	@classmethod
	def get_primary_ipv4_address(cls, ifname):
#		return "172.16.0.131"
		return "192.168.1.2"
