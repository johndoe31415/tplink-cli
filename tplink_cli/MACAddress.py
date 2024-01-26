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

class MACAddress():
	def __init__(self, mac: bytes):
		assert(isinstance(mac, bytes))
		assert(len(mac) == 6)
		self._mac = mac

	def __lt__(self, other):
		return bytes(self) < bytes(other)

	def __eq__(self, other):
		return bytes(self) == bytes(other)

	def __hash__(self):
		return hash(self._mac)

	def __bytes__(self):
		return self._mac

	def __repr__(self):
		return ":".join(f"{x:02x}" for x in self._mac)
