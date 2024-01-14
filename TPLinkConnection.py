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
import threading
import queue

from Tools import NetTools
from TPLinkPacket import TPLinkPacket
from Exceptions import ReceiveTimeoutException

class TPLinkConnection(object):
	_HOST_PORT = 29809
	_SWITCH_PORT = 29808

	def __init__(self, interface):
		self._interface = interface
		self._host_mac = NetTools.get_mac_address(self._interface)
		self._txsocket = self._create_udp_socket(NetTools.get_primary_ipv4_address(self._interface), self._HOST_PORT)
		self._rxsocket = self._create_udp_socket("0.0.0.0", self._HOST_PORT)
		self._rx_msgs = queue.Queue()
		self._rx_thread = threading.Thread(target = self._receive_thread, daemon = True)
		self._rx_thread.start()

	@staticmethod
	def _create_udp_socket(ip_address, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.bind((ip_address, port))
		return sock

	def _receive_thread(self):
		while True:
			msg = self._rxsocket.recv(4096)
			packet = TPLinkPacket.deserialize(msg)
			self._rx_msgs.put(packet)

	@property
	def host_mac(self):
		return self._host_mac

	def send(self, packet):
		packet = bytes(packet)
		self._txsocket.sendto(packet, ("255.255.255.255", self._SWITCH_PORT))

	def recv(self, timeout = 1.0):
		try:
			return self._rx_msgs.get(timeout = timeout)
		except queue.Empty:
			raise ReceiveTimeoutException(f"Receive timed out after {timeout:.1f} secs.")

	def send_recv(self, packet, recv_timeout = 1.0):
		self.send(packet)
		return self.recv(recv_timeout)

	def close(self):
		self._txsocket.close()
		self._rxsocket.close()
