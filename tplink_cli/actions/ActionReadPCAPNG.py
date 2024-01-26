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

import pcapng
import contextlib
from ..MultiCommand import BaseAction
from ..RC4Packet import RC4Packet
from ..Exceptions import DeserializationException

class ActionReadPCAPNG(BaseAction):
	def run(self):
		with open(self._args.filename, "rb") as f:
			for block in pcapng.scanner.FileScanner(f):
				if not isinstance(block, pcapng.blocks.EnhancedPacket):
					continue

				ethertype = block.packet_data[12 : 12 + 2]
				if ethertype != bytes.fromhex("08 00"):
					# Not IPv4.
					continue

				if block.packet_data[0x17] != 17:
					# Not UDP
					continue

				udp_length = int.from_bytes(block.packet_data[38 : 38 + 2], byteorder = "big") - 8
				payload = block.packet_data[42 : 42 + udp_length]

				with contextlib.suppress(DeserializationException):
					rc4_pkt = RC4Packet.deserialize(payload)
					rc4_pkt.dump()
					print()
