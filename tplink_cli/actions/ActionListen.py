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

#from .TPLinkPacket import TPLinkPacket, Opcode
#from .ActionTPLinkConnection import ActionTPLinkConnection
#from .Exceptions import ReceiveTimeoutException
import asyncio
from ..Tools import NetTools
from ..TPLinkInterface import TPLinkInterface
from ..MultiCommand import BaseAction
from ..RC4Packet import RC4Packet

class ActionListen(BaseAction):
	async def async_run(self):
		async with TPLinkInterface(self._args.interface) as conn:
			while True:
				rx_pkt = await conn.recvdata()
				rc4_pkt = RC4Packet.deserialize(rx_pkt.data)

				print(rc4_pkt)

	def run(self):
		asyncio.run(self.async_run())
