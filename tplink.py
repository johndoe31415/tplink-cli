#!/usr/bin/env python3
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

import sys

from MultiCommand import MultiCommand
from ActionTCPDump import ActionTCPDump
from ActionIdentify import ActionIdentify

#msg1 = bytes.fromhex("5d746a047dbeb0b2fb61cbe62ca87fb8422ba2f5d78baeed508f463dc202909aa4ec81c6")
#msg2 = bytes.fromhex("5d763ac3c2324177fb61cbe62ca87fb8422ba2f5d733aeed508f463dc202909a5b1281cc736606650ee8708fe1406926597b1866521ddc46082c330873e2f29d04e942304a2068b48c3a7d2e170f1a90e8f385c8ba32c3f0b7b5afad8ebcdc1b73ce374e8982a7e83ae6edf9cad4c9240da496f322edffa3dc8270b79fc2fc29e1fd8f5b65f82e6d8af3af2f6aef50e6ddc96ff446f1787c498fb7f7")

mc = MultiCommand()

def genparser(parser):
	parser.add_argument("--verbose", action = "store_true", help = "Increase logging verbosity.")
mc.register("tcpdump", "Decode traffic that has been generated by tcpdump", genparser, action = ActionTCPDump)

def genparser(parser):
	parser.add_argument("-i", "--interface", metavar = "ifname", required = True, help = "Specify the network interface that switches should be looked for. Mandatory argument.")
	parser.add_argument("-t", "--timeout", metavar = "secs", type = float, default = "1.0", help = "Default timeout that is waited for switches to respond. Defaults to %(default)s sec.")
	parser.add_argument("--verbose", action = "store_true", help = "Increase logging verbosity.")
mc.register("identify", "Identify all switches on the network", genparser, action = ActionIdentify)

mc.run(sys.argv[1:])





