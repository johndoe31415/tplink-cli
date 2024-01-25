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

import enum

def bitlist(value):
	assert(value >= 0)
	result = [ ]
	bit = 0
	while value > 0:
		if value & 0x01:
			result.append(bit)
		bit += 1
		value >>= 1
	return result

def as_int(data):
	return int.from_bytes(data, byteorder = "big")

def as_str(data):
	return data.rstrip(b"\x00").decode()

def as_ip(data):
	return ".".join(str(x) for x in data)

def as_portlist(data):
	return [ bit + 1 for bit in bitlist(as_int(data)) ]

def str_portlist(ports):
	if len(ports) == 0:
		return "none"
	return ", ".join(str(port) for port in sorted(ports))

class TPLinkData(object):
	_EXPECTED_LENGTH_MIN = None
	_EXPECTED_LENGTH_MAX = None

	def __init__(self, data):
		self._data = data

	@property
	def value(self):
		return self._data

	@property
	def str_value(self):
		if isinstance(self.value, bytes):
			return self.value.hex()
		else:
			return str(self.value)

	@property
	def has_value(self):
		if (self._EXPECTED_LENGTH_MIN is not None) and (len(self._data) < self._EXPECTED_LENGTH_MIN):
			return False
		if (self._EXPECTED_LENGTH_MAX is not None) and (len(self._data) > self._EXPECTED_LENGTH_MAX):
			return False
		return True

	def __str__(self):
		if len(self._data) == 0:
			return "No data"
		elif not self.has_value:
			return "Unknown data: %s" % (self._data.hex())
		else:
			return self.str_value

class TPLinkBool(TPLinkData):
	_EXPECTED_LENGTH_MIN = 1
	_EXPECTED_LENGTH_MAX = 1

	@property
	def value(self):
		return bool(self._data[0])

class TPLinkString(TPLinkData):
	_EXPECTED_LENGTH_MIN = 1

	@property
	def value(self):
		return as_str(self._data)

class TPLinkIPv4(TPLinkData):
	_EXPECTED_LENGTH_MIN = 4
	_EXPECTED_LENGTH_MAX = 4

	@property
	def value(self):
		return as_ip(self._data)

class TPLinkMAC(TPLinkData):
	_EXPECTED_LENGTH_MIN = 6
	_EXPECTED_LENGTH_MAX = 6

	@property
	def value(self):
		return ":".join("%02x" % (x) for x in self._data)

class TPLinkPortConfig(enum.IntEnum):
	LinkDown = 0
	Auto = 1
	HalfDuplex10MBit = 2
	FullDuplex10MBit = 3
	HalfDuplex100MBit = 4
	FullDuplex100MBit = 5
	FullDuplex1000MBit = 6

class TPLinkPortSetting(TPLinkData):
	_EXPECTED_LENGTH_MIN = 7
	_EXPECTED_LENGTH_MAX = 7

	@property
	def value(self):
		return {
			"port":		self._data[0],
			"enabled":	bool(self._data[1]),
			"speed_config":	TPLinkPortConfig(self._data[3]),
			"speed_state":	TPLinkPortConfig(self._data[4]),
			"flowctrl_config": bool(self._data[5]),
			"flowctrl_state": bool(self._data[6]),
		}

	@property
	def str_value(self):
		value = self.value
		return "Port%d: %s, speed %s (actual %s), flowcontrol %s (actual %s)" % (value["port"], "Enabled" if value["enabled"] else "Disabled", value["speed_config"].name, value["speed_state"].name, value["flowctrl_config"], value["flowctrl_state"])

class TPLinkPortStatistics(TPLinkData):
	_EXPECTED_LENGTH_MIN = 19
	_EXPECTED_LENGTH_MAX = 19

	@property
	def value(self):
		return {
			"port":		self._data[0],
			"enabled":	bool(self._data[1]),
			"speed_state":	TPLinkPortConfig(self._data[2]),
			"tx_good_pkt": as_int(self._data[3 : 7]),
			"tx_bad_pkt": as_int(self._data[7 : 11]),
			"rx_good_pkt": as_int(self._data[11 : 15]),
			"rx_bad_pkt": as_int(self._data[15 : 19]),
		}

	@property
	def str_value(self):
		value = self.value
		return "Port%d: %s, speed %s. TX %d good, %d bad. RX %d good, %d bad." % (value["port"], "Enabled" if value["enabled"] else "Disabled", value["speed_state"].name, value["tx_good_pkt"], value["tx_bad_pkt"], value["rx_good_pkt"], value["rx_bad_pkt"])


class TPLinkLagConfig(TPLinkData):
	_EXPECTED_LENGTH_MIN = 5
	_EXPECTED_LENGTH_MAX = 5

	@property
	def value(self):
		return {
			"lag_id":			self._data[0],
			"ports":			as_portlist(self._data[1 : 5]),
		}

	@property
	def str_value(self):
		value = self.value
		if len(value["ports"]) == 0:
			return "LAG %d: Disabled" % (value["lag_id"])
		else:
			ports = ", ".join(str(x) for x in value["ports"])
			return "LAG %d: ports %s" % (value["lag_id"], ports)

class TPLinkMirroringConfig(TPLinkData):
	_EXPECTED_LENGTH_MIN = 10
	_EXPECTED_LENGTH_MAX = 10

	@property
	def value(self):
		return {
			"enabled":			bool(self._data[0]),
			"mirroring_dest":	self._data[1],
			"ingress_src":		as_portlist(self._data[2 : 6]),
			"egress_src":		as_portlist(self._data[6 : 10]),
		}

	@property
	def str_value(self):
		value = self.value
		if not value["enabled"]:
			return "Disabled"
		else:
			ingress = ", ".join(str(x) for x in value["ingress_src"]) if (len(value["ingress_src"]) > 0) else "none"
			egress = ", ".join(str(x) for x in value["egress_src"]) if (len(value["egress_src"]) > 0) else "none"
			return "Enabled: Ingress %s + Egress %s -> port %d" % (ingress, egress, value["mirroring_dest"])

class TPLinkMulticastIPTable(TPLinkData):
	_EXPECTED_LENGTH_MIN = 10
	_EXPECTED_LENGTH_MAX = 10

	@property
	def value(self):
		return {
			"ip":		as_ip(self._data[0 : 4]),
			"vlan_id":	as_int(self._data[4 : 6]),
			"ports":	as_portlist(self._data[6 : 10]),
		}

	@property
	def str_value(self):
		value = self.value
		return "IP %s: VLAN %d, Ports %s" % (value["ip"], value["vlan_id"], str_portlist(value["ports"]))

class TPLinkInt(TPLinkData):
	_EXPECTED_LENGTH_MIN = 1

	@property
	def value(self):
		return as_int(self._data)

class TPLinkPortBasedVLANConfig(TPLinkData):
	_EXPECTED_LENGTH_MIN = 5
	_EXPECTED_LENGTH_MAX = 5

	@property
	def value(self):
		return {
			"vlan_id":			self._data[0],
			"ports":			as_portlist(self._data[1 : 5]),
		}

	@property
	def str_value(self):
		value = self.value
		return "VLAN %d: Ports %s" % (value["vlan_id"], str_portlist(value["ports"]))

class TPLink802_1Q_VLANConfig(TPLinkData):
	_EXPECTED_LENGTH_MIN = 10

	@property
	def value(self):
		return {
			"vlan":			as_int(self._data[0 : 2]),
			"member_ports":	as_portlist(self._data[2 : 6]),
			"tagged_ports":	as_portlist(self._data[6 : 10]),
			"name":			as_str(self._data[10:]),
		}

	@property
	def str_value(self):
		value = self.value
		member = str_portlist(value["member_ports"])
		tagged = str_portlist(value["tagged_ports"])
		return "VLAN %d: \"%s\", member ports %s, tagged ports %s" % (value["vlan"], value["name"], member, tagged)

class TPLinkPVIDSetting(TPLinkData):
	_EXPECTED_LENGTH_MIN = 3
	_EXPECTED_LENGTH_MAX = 3

	@property
	def value(self):
		return {
			"port":				self._data[0],
			"pvid":				as_int(self._data[1 : 3]),
		}

	@property
	def str_value(self):
		value = self.value
		return "Port %d: PVID %d" % (value["port"], value["pvid"])

class TPLinkMTUVLANSetting(TPLinkData):
	_EXPECTED_LENGTH_MIN = 2
	_EXPECTED_LENGTH_MAX = 2

	@property
	def value(self):
		return {
			"enabled":			bool(self._data[0]),
			"uplink_port":		self._data[1],
		}

	@property
	def str_value(self):
		value = self.value
		if not value["enabled"]:
			return "Disabled"
		else:
			return "Enabled, uplink port %d" % (value["uplink_port"])


class TPLinkBandwidthControlSetting(TPLinkData):
	_EXPECTED_LENGTH_MIN = 6
	_EXPECTED_LENGTH_MAX = 6

	@property
	def value(self):
		return {
			"port":			self._data[0],
			"enabled":		bool(self._data[1]),
			"rate_kbps":	as_int(self._data[2 : 6]),
		}

	@property
	def str_value(self):
		value = self.value
		if not value["enabled"]:
			return "Port %d: Unlimited" % (value["port"])
		else:
			return "Port %d: %d kbps" % (value["port"], value["rate_kbps"])

class QoSPriority(enum.IntEnum):
	Queue_Priority_Lowest = 0
	Queue_Priority_Normal = 1
	Queue_Priority_Medium = 2
	Queue_Priority_Highest = 3

class QoSPriorityType(enum.IntEnum):
	QoS_Port_Based = 0
	QoS_802_1P_Based = 1
	QoS_DSCP_Based = 2

class TPLinkQoSPriority(TPLinkData):
	_EXPECTED_LENGTH_MIN = 2
	_EXPECTED_LENGTH_MAX = 2

	@property
	def value(self):
		return {
			"port":			self._data[0],
			"priority":		QoSPriority(self._data[1]),
		}

	@property
	def str_value(self):
		value = self.value
		return "Port %d: %s" % (value["port"], value["priority"].name)

class TPLinkQoSPriorityType(TPLinkData):
	_EXPECTED_LENGTH_MIN = 1
	_EXPECTED_LENGTH_MAX = 1

	@property
	def value(self):
		return QoSPriorityType(self._data[0])

	@property
	def str_value(self):
		return self.value.name

class TPLinkStormControl(TPLinkData):
	_EXPECTED_LENGTH_MIN = 9
	_EXPECTED_LENGTH_MAX = 9

	@property
	def value(self):
		return {
			"port":			self._data[0],
			"enabled":		bool(self._data[1]),
			"bc_limit":		bool(self._data[2]),
			"mc_limit":		bool(self._data[3]),
			"ul_limit":		bool(self._data[4]),
			"rate_kbps":	as_int(self._data[5 : 9]),
		}

	@property
	def str_value(self):
		value = self.value
		if not value["enabled"]:
			return "Port %d: Disabled" % (value["port"])
		else:
			limits = [ ]
			limits.append("BC" if value["bc_limit"] else None)
			limits.append("MC" if value["mc_limit"] else None)
			limits.append("UL" if value["ul_limit"] else None)
			limits = [ limit for limit in limits if limit is not None ]
			return "Port %d: %s limited, %d kbps" % (value["port"], ", ".join(limits), value["rate_kbps"])

class TPLinkTestResult(enum.IntEnum):
	Normal = 1
	Open = 2

class TPLinkCableTest(TPLinkData):
	_EXPECTED_LENGTH_MIN = 6
	_EXPECTED_LENGTH_MAX = 6

	@property
	def value(self):
		return {
			"port":				self._data[0],
			"result":			TPLinkTestResult(self._data[1]),
			"fault_distance":	as_int(self._data[2 : 6]),
		}

	@property
	def str_value(self):
		value = self.value
		return "Port %d: %s, fault distance %d" % (value["port"], value["result"].name, value["fault_distance"])

