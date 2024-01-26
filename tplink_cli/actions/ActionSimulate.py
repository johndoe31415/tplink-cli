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

import asyncio
import ipaddress
from ..Tools import NetTools
from ..TPLinkInterface import TPLinkInterface
from ..MultiCommand import BaseAction
from ..RC4Packet import RC4Packet
from ..Enums import Opcode, FieldTag
from ..PacketField import PacketField
from ..TPLinkTypes import TPLinkRawData, TPLinkString, TPLinkBool, TPLinkIPv4, TPLinkMAC

class ActionSimulate(BaseAction):
	async def async_run(self):
		async with TPLinkInterface(self._args.interface, act_as_host = False) as conn:
			while True:
				rx_pkt = await conn.recvdata()

				rc4_pkt = RC4Packet.deserialize(rx_pkt.data)
				print(rc4_pkt)

				if rc4_pkt.opcode == Opcode.Discovery:
					# Respond with same packet, but append fields
					rc4_pkt.opcode = Opcode.ResponseData
					rc4_pkt.switch_mac = conn.host_mac
					rc4_pkt.payload.clear()
					rc4_pkt.payload.append_all([
						PacketField(FieldTag.SwitchName, TPLinkString("TL-SG1016PE")),
						PacketField(FieldTag.DeviceDescription, TPLinkString("Simulated Switch")),
						PacketField(FieldTag.MAC, TPLinkMAC(rc4_pkt.switch_mac)),
						PacketField(FieldTag.FirmwareVersion, TPLinkString("1.0.1 Build 20230712 Rel.73926")),
						PacketField(FieldTag.HardwareVersion, TPLinkString("TL-SG1016PE 5.20")),
						PacketField(FieldTag.DHCP, TPLinkBool(False)),
						PacketField(FieldTag.IPAddress, TPLinkIPv4(ipaddress.ip_address("192.168.123.32"))),
						PacketField(FieldTag.SubnetMask, TPLinkIPv4(ipaddress.ip_address("255.255.255.0"))),
						PacketField(FieldTag.GatewayIPAddress, TPLinkIPv4(ipaddress.ip_address("192.168.123.254"))),
						PacketField(13, TPLinkRawData(bytes.fromhex("01"))),
						PacketField(14, TPLinkRawData(bytes.fromhex("00"))),
						PacketField(15, TPLinkRawData(bytes.fromhex("001c0000"))),
						PacketField(FieldTag.DeviceSupportsEncryption, TPLinkBool(True)),
					])
					conn.send(rc4_pkt.serialize(), host = rx_pkt.host, port = rx_pkt.port)
					print(f"Responding to discovery packet towards {rx_pkt.host}:{rx_pkt.port}")
				elif rc4_pkt.opcode == Opcode.SetData:
					pass
				else:
					print("Not understood request:")
					rc4_pkt.dump()

	def run(self):
		asyncio.run(self.async_run())
