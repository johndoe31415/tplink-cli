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

import random
import enum
import struct
import collections
from .TPLinkObfuscation import TPLinkObfuscation
from .HexDump import HexDump
from .TPLinkTypes import TPLinkData, TPLinkString, TPLinkBool, TPLinkMAC, TPLinkIPv4, TPLinkPortSetting, TPLinkPortStatistics, TPLinkMirroringConfig, TPLinkLagConfig, TPLinkInt, TPLinkPortBasedVLANConfig, TPLink802_1Q_VLANConfig, TPLinkPVIDSetting, TPLinkMTUVLANSetting, TPLinkBandwidthControlSetting, TPLinkQoSPriority, TPLinkQoSPriorityType, TPLinkStormControl, TPLinkCableTest, TPLinkMulticastIPTable

class Opcode(enum.IntEnum):
	Discovery = 0
	RequestData = 1
	ResponseData = 2
	SetData = 3
	AcknowledgeSetData = 4

class FieldType(enum.IntEnum):
	SwitchName = 1
	DeviceDescription = 2
	MAC = 3
	IPAddress = 4
	SubnetMask = 5
	GatewayIPAddress = 6
	FirmwareVersion = 7
	HardwareVersion = 8
	DHCP = 9
	PortCount = 10
	LoginUsername = 512
	LoginPassword = 514
	LoginOldPassword = 513
	LoginNewPassword = 515
	SwitchToRSAEncryption = 528

	BackupConfiguration = 768
	RestoreConfiguration = 769
	RebootSwitch = 773

	FactoryReset = 1280

	AuthTokenId = 2305

	PortSetting = 4096

	IGMPSnoopingStatus = 4352
	IGMPSnooping_ReportMessageSuppression = 4354
	MulticastIPTable = 4353

	LAGConfiguration = 4608

	MonitoringPortStatus = 16384

	CableTest = 16896
	LoopPrevention = 17152

	PortBasedVLANStatus = 8448
	PortBasedVLANConfig = 8449
	PortBasedVLANPortCount = 8450

	VLAN802_1Q_Status = 8704
	VLAN802_1Q_Config = 8705
	VLAN802_1Q_PortCount = 8707

	VLAN802_1Q_PVID_Setting = 8706

	QoSConfigurationType = 12288
	QoSConfigurationPortBased = 12289

	BandwidthControlIngress = 12544
	BandwidthControlEgress = 12545
	StormControl = 12800

	PortMirroringConfig = 16640

	MTUVLANSetting = 8192

class FieldData(object):
	_FIELD_TYPES = {
		FieldType.LoginUsername:							TPLinkString,
		FieldType.LoginPassword:							TPLinkString,
		FieldType.LoginOldPassword:							TPLinkString,
		FieldType.LoginNewPassword:							TPLinkString,
		FieldType.SwitchName:								TPLinkString,
		FieldType.DeviceDescription:						TPLinkString,
		FieldType.FirmwareVersion:							TPLinkString,
		FieldType.HardwareVersion:							TPLinkString,
		FieldType.PortCount:								TPLinkInt,
		FieldType.MAC:										TPLinkMAC,
		FieldType.DHCP:										TPLinkBool,
		FieldType.IPAddress:								TPLinkIPv4,
		FieldType.SubnetMask:								TPLinkIPv4,
		FieldType.GatewayIPAddress:							TPLinkIPv4,
		FieldType.PortSetting:								TPLinkPortSetting,
		FieldType.MonitoringPortStatus:						TPLinkPortStatistics,
		FieldType.PortMirroringConfig:						TPLinkMirroringConfig,
		FieldType.LAGConfiguration:							TPLinkLagConfig,
		FieldType.PortBasedVLANStatus:						TPLinkBool,
		FieldType.PortBasedVLANConfig:						TPLinkPortBasedVLANConfig,
		FieldType.PortBasedVLANPortCount:					TPLinkInt,
		FieldType.VLAN802_1Q_Status:						TPLinkBool,
		FieldType.VLAN802_1Q_Config:						TPLink802_1Q_VLANConfig,
		FieldType.VLAN802_1Q_PortCount:						TPLinkInt,
		FieldType.VLAN802_1Q_PVID_Setting:					TPLinkPVIDSetting,
		FieldType.MTUVLANSetting:							TPLinkMTUVLANSetting,
		FieldType.QoSConfigurationType:						TPLinkQoSPriorityType,
		FieldType.QoSConfigurationPortBased:				TPLinkQoSPriority,
		FieldType.BandwidthControlIngress:					TPLinkBandwidthControlSetting,
		FieldType.BandwidthControlEgress:					TPLinkBandwidthControlSetting,
		FieldType.StormControl:								TPLinkStormControl,
		FieldType.CableTest:								TPLinkCableTest,
		FieldType.LoopPrevention:							TPLinkBool,
		FieldType.IGMPSnoopingStatus:						TPLinkBool,
		FieldType.IGMPSnooping_ReportMessageSuppression:	TPLinkBool,
		FieldType.MulticastIPTable:							TPLinkMulticastIPTable,
	}

	def __init__(self, field_type, field_data):
		self._ftype = field_type
		self._fdata = field_data

	@property
	def ftype(self):
		return self._ftype

	@property
	def ftypename(self):
		if isinstance(self.ftype, enum.IntEnum):
			return self.ftype.name
		else:
			return str(self.ftype)

	@property
	def interpreted_data(self):
		handle_class = self._FIELD_TYPES.get(self.ftype, TPLinkData)
		return handle_class(self.data)

	@property
	def data(self):
		return self._fdata

class TPLinkPacket(object):
	_SEQNO = random.randint(0, 0xffff)
	_TPLinkHeaderStruct = struct.Struct("> B B 6s 6s H I H H H H I")
	_TPLinkHeaderField = collections.namedtuple("TPLinkHeaderField", [ "version", "opcode", "switch_mac", "host_mac", "sequence_number", "error_code", "length", "fragmentation_offset", "flag", "tokenid", "checksum" ])

	def __init__(self, header, fields):
		self._header = header
		self._fields = fields

	@property
	def opcode(self):
		try:
			opcode = Opcode(self._header.opcode)
		except ValueError:
			opcode = self._header.opcode
		return opcode

	@classmethod
	def deserialize(cls, obfuscated_data):
		msg = TPLinkObfuscation.deobfuscate(obfuscated_data)

		header = msg[:cls._TPLinkHeaderStruct.size]
		header = cls._TPLinkHeaderField(*cls._TPLinkHeaderStruct.unpack(header))

		fields = [ ]
		offset = cls._TPLinkHeaderStruct.size
		while offset + 2 < len(msg):
			fieldtype = (msg[offset + 0] << 8) | msg[offset + 1]
			if (fieldtype == 0xffff):
				# Exit
				break
			fieldlen = (msg[offset + 2] << 8) | msg[offset + 3]
			fieldval = msg[offset + 4 : offset + 4 + fieldlen]
			try:
				resolved_type = FieldType(fieldtype)
			except ValueError:
				resolved_type = fieldtype
			fields.append(FieldData(resolved_type, fieldval))
			offset += 4 + fieldlen

		return cls(header, fields)

	@classmethod
	def construct(cls, opcode, switch_mac = None, host_mac = None, tokenid = 0, fields = None):
		assert((switch_mac is None) or (isinstance(switch_mac, bytes) and len(switch_mac) == 6))
		assert((host_mac is None) or (isinstance(host_mac, bytes) and len(host_mac) == 6))
		seqno = cls._SEQNO
		cls._SEQNO = (cls._SEQNO + 1) & 0xffff
		if switch_mac is None:
			switch_mac = bytes(6)
		if host_mac is None:
			host_mac = bytes(6)
		if fields is None:
			fields = [ ]
		field_data_len = sum(len(value) for (key, value) in fields)
		length = cls._TPLinkHeaderStruct.size + 4 * (len(fields) + 1) + field_data_len
		header = cls._TPLinkHeaderField(version = 1, opcode = int(opcode), switch_mac = switch_mac, host_mac = host_mac, sequence_number = seqno, error_code = 0, length = length, fragmentation_offset = 0, flag = 0, tokenid = tokenid, checksum = 0)
		return cls(header, fields)

	def dump(self):
		print(self)
		for field in self._fields:
			print(f"  {field.ftypename}: {field.interpreted_data}")
		print()

	def __bytes__(self):
		result = bytearray(self._TPLinkHeaderStruct.pack(*self._header))
		for field in self._fields:
			key = int(field.ftype)
			result.append((key >> 8) & 0xff)
			result.append((key >> 0) & 0xff)
			result.append((len(field.data) >> 8) & 0xff)
			result.append((len(field.data) >> 0) & 0xff)
			result += field.data
		result += bytes.fromhex("ff ff 00 00")
		return TPLinkObfuscation.obfuscate(result)

	def __repr__(self):
		return "Packet<v%d, op = %s, len = %d>" % (self._header.version, self.opcode, self._header.length)

