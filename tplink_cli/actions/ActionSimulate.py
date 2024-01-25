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
from .TPLinkPacket import TPLinkPacket, Opcode, FieldData, FieldType
from .TPLinkTypes import TPLinkString
from .ActionTPLinkConnection import ActionTPLinkConnection
from .Exceptions import ReceiveTimeoutException
from .Tools import NetTools

class ActionSimulate(ActionTPLinkConnection):
	def _run_action(self):
		interface_ip = NetTools.get_primary_ipv4_address(self._args.interface)
		my_mac_address = NetTools.get_mac_address(self._args.interface)

		fields =  [
			#(FieldType.SwitchName, TPLinkString("foobar")),
			(FieldType.SwitchName, b"foobar"),
		]
		answer = TPLinkPacket.xconstruct(opcode = Opcode.ResponseData, switch_mac = my_mac_address, host_mac = my_mac_address, seqno = 1234, fields = fields)
		answer.dump()
		jfdofd


		rxsd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		rxsd.bind(("255.255.255.255", 29808))

		txsd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		txsd.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		txsd.bind((interface_ip, 29808))

		while True:
			(msg, (peer_ip, peer_port)) = rxsd.recvfrom(1024)
			decrypted = TPLinkPacket.deserialize(msg)
			decrypted.dump()

			fields = [
					FieldData(FieldType.SwitchName, TPLinkString("Dings Switch")),
			]
			answer = TPLinkPacket.xconstruct(opcode = Opcode.ResponseData, switch_mac = my_mac_address, host_mac = my_mac_address, seqno = decrypted._header.sequence_number, fields = fields)
			answer.dump()
			print(answer)
			print(decrypted._header)
			print("RX", decrypted)

			#if peer_ip == interface_ip:

