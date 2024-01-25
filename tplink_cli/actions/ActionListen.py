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
from ..Tools import NetTools
from ..MultiCommand import BaseAction

class ActionListen(BaseAction):
	def run(self):
		interface = self.args.interface or NetTools.get_default_gateway_interface()
		ip_address = NetTools.get_primary_ipv4_address(interface)
		print(interface, ip_address)
