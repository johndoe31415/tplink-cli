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

import ipaddress
import dataclasses
from .Enums import FieldTag
from .MACAddress import MACAddress

@dataclasses.dataclass
class TPLinkRawData():
	value: bytes = bytes()

	@classmethod
	def deserialize(cls, payload):
		return cls(value = payload)

	def __bytes__(self):
		return self.value

	def __repr__(self):
		if len(self.value) == 0:
			return f"TPLinkRawData<>"
		else:
			return f"TPLinkRawData<{len(self.value)}: {self.value.hex()}>"

@dataclasses.dataclass
class TPLinkString():
	value: str = ""

	@classmethod
	def deserialize(cls, payload):
		return cls(value = payload.decode("ascii").rstrip("\x00"))

	def __bytes__(self):
		if len(self.value) == 0:
			return bytes()
		else:
			return self.value.encode("ascii") + bytes(1)

@dataclasses.dataclass
class TPLinkInt():
	value: int = 0

	@classmethod
	def deserialize(cls, payload):
		TODO
		print(payload)
		return cls(value = int.from_bytes(payload, byteorder = "big"))

	def __bytes__(self):
		TODO
		return self.value.encode("ascii") + "\x00"


@dataclasses.dataclass
class TPLinkBigint():
	value: int = 0

	@classmethod
	def deserialize(cls, payload):
		return cls(value = int.from_bytes(payload[2 :], byteorder = "little"))

	def __bytes__(self):
		# Stored as short limbs with a redundant prefix indicating the limb
		# count
		limb_count = (self.value.bit_length() + 15) // 16
		byte_count = limb_count * 2
		return limb_count.to_bytes(byteorder = "big", length = 2) + self.value.to_bytes(byteorder = "little", length = byte_count)


@dataclasses.dataclass
class TPLinkBool():
	value: bool = False

	@classmethod
	def deserialize(cls, payload):
		return cls(value = (len(payload) > 0) and (payload[0] != 0))

	def __bytes__(self):
		return bytes([ int(self.value) ])

@dataclasses.dataclass
class TPLinkMAC():
	value: MACAddress = MACAddress(bytes(6))

	@classmethod
	def deserialize(cls, payload):
		return cls(value = MACAddress(payload))

	def __bytes__(self):
		return bytes(self.value)

@dataclasses.dataclass
class TPLinkPVIDSetting():
	port: int = 0
	pvid: int = 0

	@classmethod
	def deserialize(cls, payload):
		if len(payload) == 0:
			# For requests of this field, it's empty
			return cls()
		return cls(port = payload[0], pvid = int.from_bytes(payload[1 : 4], byteorder = "big"))

	def __bytes__(self):
		return self.port.to_bytes(byteorder = "big", length = 1) + self.pvid.to_bytes(byteorder = "big", length = 3)

@dataclasses.dataclass
class TPLinkIPv4():
	value: ipaddress.IPv4Address

	@classmethod
	def deserialize(cls, payload):
		return cls(value = ipaddress.IPv4Address(payload))

	def __bytes__(self):
		return self.value.packed

def get_handler_class(tag):
	return {
		FieldTag.LoginUsername:								TPLinkString,
		FieldTag.LoginPassword:								TPLinkString,
		FieldTag.LoginOldPassword:							TPLinkString,
		FieldTag.LoginNewPassword:							TPLinkString,
		FieldTag.SwitchName:								TPLinkString,
		FieldTag.DeviceDescription:							TPLinkString,
		FieldTag.FirmwareVersion:							TPLinkString,
		FieldTag.HardwareVersion:							TPLinkString,
		FieldTag.PortCount:									TPLinkInt,
		FieldTag.DeviceSupportsEncryption:					TPLinkBool,
		FieldTag.MAC:										TPLinkMAC,
		FieldTag.DHCP:										TPLinkBool,
		FieldTag.IPAddress:									TPLinkIPv4,
		FieldTag.SubnetMask:								TPLinkIPv4,
		FieldTag.GatewayIPAddress:							TPLinkIPv4,
#		FieldTag.PortSetting:								TPLinkPortSetting,
#		FieldTag.MonitoringPortStatus:						TPLinkPortStatistics,
#		FieldTag.PortMirroringConfig:						TPLinkMirroringConfig,
#		FieldTag.LAGConfiguration:							TPLinkLagConfig,
		FieldTag.PortBasedVLANStatus:						TPLinkBool,
#		FieldTag.PortBasedVLANConfig:						TPLinkPortBasedVLANConfig,
		FieldTag.PortBasedVLANPortCount:					TPLinkInt,
		FieldTag.VLAN802_1Q_Status:							TPLinkBool,
#		FieldTag.VLAN802_1Q_Config:							TPLink802_1Q_VLANConfig,
		FieldTag.VLAN802_1Q_PortCount:						TPLinkInt,
		FieldTag.VLAN802_1Q_PVID_Setting:					TPLinkPVIDSetting,
#		FieldTag.MTUVLANSetting:							TPLinkMTUVLANSetting,
#		FieldTag.QoSConfigurationType:						TPLinkQoSPriorityType,
#		FieldTag.QoSConfigurationPortBased:					TPLinkQoSPriority,
#		FieldTag.BandwidthControlIngress:					TPLinkBandwidthControlSetting,
#		FieldTag.BandwidthControlEgress:					TPLinkBandwidthControlSetting,
#		FieldTag.StormControl:								TPLinkStormControl,
#		FieldTag.CableTest:									TPLinkCableTest,
		FieldTag.LoopPrevention:							TPLinkBool,
		FieldTag.IGMPSnoopingStatus:						TPLinkBool,
		FieldTag.IGMPSnooping_ReportMessageSuppression:		TPLinkBool,
#		FieldTag.MulticastIPTable:							TPLinkMulticastIPTable,
		FieldTag.SwitchToRSAEncryption:						TPLinkBigint,
	}.get(tag, TPLinkRawData)
