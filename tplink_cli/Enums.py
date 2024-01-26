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

class Opcode(enum.IntEnum):
	Discovery = 0
	RequestData = 1
	ResponseData = 2
	SetData = 3
	AcknowledgeSetData = 4

class FieldTag(enum.IntEnum):
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

	EndOfFields = 0xffff
