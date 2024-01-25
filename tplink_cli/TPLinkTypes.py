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

import dataclasses
from .Enums import FieldTag

@dataclasses.dataclass
class TPLinkRawData():
	value: bytes = bytes()

	@classmethod
	def deserialize(cls, payload):
		return cls(value = payload)

	def __bytes__(self):
		return self.value


@dataclasses.dataclass
class TPLinkString():
	value: str = ""

	@classmethod
	def deserialize(cls, payload):
		return cls(value = payload.decode("ascii").rstrip("\x00"))

	def __bytes__(self):
		return self.value.encode("ascii") + "\x00"


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
#		FieldTag.PortCount:									TPLinkInt,
#		FieldTag.MAC:										TPLinkMAC,
#		FieldTag.DHCP:										TPLinkBool,
#		FieldTag.IPAddress:									TPLinkIPv4,
#		FieldTag.SubnetMask:								TPLinkIPv4,
#		FieldTag.GatewayIPAddress:							TPLinkIPv4,
#		FieldTag.PortSetting:								TPLinkPortSetting,
#		FieldTag.MonitoringPortStatus:						TPLinkPortStatistics,
#		FieldTag.PortMirroringConfig:						TPLinkMirroringConfig,
#		FieldTag.LAGConfiguration:							TPLinkLagConfig,
#		FieldTag.PortBasedVLANStatus:						TPLinkBool,
#		FieldTag.PortBasedVLANConfig:						TPLinkPortBasedVLANConfig,
#		FieldTag.PortBasedVLANPortCount:					TPLinkInt,
#		FieldTag.VLAN802_1Q_Status:							TPLinkBool,
#		FieldTag.VLAN802_1Q_Config:							TPLink802_1Q_VLANConfig,
#		FieldTag.VLAN802_1Q_PortCount:						TPLinkInt,
#		FieldTag.VLAN802_1Q_PVID_Setting:					TPLinkPVIDSetting,
#		FieldTag.MTUVLANSetting:							TPLinkMTUVLANSetting,
#		FieldTag.QoSConfigurationType:						TPLinkQoSPriorityType,
#		FieldTag.QoSConfigurationPortBased:					TPLinkQoSPriority,
#		FieldTag.BandwidthControlIngress:					TPLinkBandwidthControlSetting,
#		FieldTag.BandwidthControlEgress:					TPLinkBandwidthControlSetting,
#		FieldTag.StormControl:								TPLinkStormControl,
#		FieldTag.CableTest:									TPLinkCableTest,
#		FieldTag.LoopPrevention:							TPLinkBool,
#		FieldTag.IGMPSnoopingStatus:						TPLinkBool,
#		FieldTag.IGMPSnooping_ReportMessageSuppression:		TPLinkBool,
#		FieldTag.MulticastIPTable:							TPLinkMulticastIPTable,
	}.get(tag, TPLinkRawData)
