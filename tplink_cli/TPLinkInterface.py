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
import socket
import fcntl
import collections
from .Tools import NetTools
from .Exceptions import ReceiveTimeoutException

class TPLinkProtocol(asyncio.DatagramProtocol):
	RXMsg = collections.namedtuple ("RXMsg", [ "data", "host", "port" ])
	def __init__(self, tplink_interface):
		super().__init__()
		self._tplink_interface = tplink_interface

	def datagram_received(self, data, addr):
		msg = self.RXMsg(data = data, host = addr[0], port = addr[1])
		self._tplink_interface._rx_packet(msg)

class TPLinkInterface():
	_HOST_PORT = 29809
	_SWITCH_PORT = 29808

	def __init__(self, interface = None, act_as_host = True):
		self._interface = interface
		if self._interface is None:
			self._interface = NetTools.get_default_gateway_interface()
		self._act_as_host = act_as_host
		self._host_mac = NetTools.get_mac_address(self._interface)
		self._host_ip = NetTools.get_primary_ipv4_address(self._interface)
		self._txsocket = None
		self._rxsocket = None
		self._rx_queue = asyncio.Queue()

	@property
	def interface(self):
		return self._interface

	@property
	def host_mac(self):
		return self._host_mac

	@property
	def host_ip(self):
		return self._host_ip

	@property
	def local_port(self):
		if self._act_as_host:
			return self._HOST_PORT
		else:
			return self._SWITCH_PORT

	async def __aenter__(self, *args):
		loop = asyncio.get_event_loop()
		(self._endpoint_transport, self._endpoint_protocol) = await loop.create_datagram_endpoint(lambda: TPLinkProtocol(self), sock = self._create_udp_socket("0.0.0.0", self.local_port))
		self._txsocket = self._create_udp_socket(self._host_ip, self.local_port)
		return self

	async def __aexit__(self, *args):
		self._endpoint_transport.close()
		self._txsocket.close()

	def _rx_packet(self, rxmsg: TPLinkProtocol.RXMsg):
		asyncio.run_coroutine_threadsafe(self._rx_queue.put(rxmsg), asyncio.get_event_loop())

	async def recvdata(self, timeout: float | None = None):
		if timeout is not None:
			try:
				return await asyncio.wait_for(self._rx_queue.get(), timeout = timeout)
			except TimeoutError:
				return None
		else:
			return await self._rx_queue.get()

	def send(self, data: bytes, host: str, port: int):
		self._txsocket.sendto(data, (host, port))

	@staticmethod
	def _create_udp_socket(ip_address, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.bind((ip_address, port))
		return sock
