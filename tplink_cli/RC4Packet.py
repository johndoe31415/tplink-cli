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
import dataclasses
from .Enums import Opcode
from .PacketField import PacketFields
from .TPLinkObfuscation import TPLinkObfuscation
from .NamedStruct import NamedStruct
from .Exceptions import DeserializationException
from .MACAddress import MACAddress

@dataclasses.dataclass
class RC4Packet():
	_HEADER_DEFINITION = NamedStruct((
		("B", "version"),
		("B", "opcode"),
		("6s", "switch_mac"),
		("6s", "host_mac"),
		("H", "sequence_number"),
		("I", "error_code"),
		("H", "length"),
		("H", "fragmentation_offset"),
		("H", "flags"),
		("H", "token_id"),
		("I", "checksum"),
	), struct_extra = ">")
	version: int
	opcode: Opcode
	switch_mac: MACAddress
	host_mac: MACAddress
	sequence_number: int
	error_code: int
	length: int | None
	fragmentation_offset: int
	flags: int
	token_id: int
	checksum: int
	payload: PacketFields
	auto_compute_length: bool = dataclasses.field(repr = False, default = True)

	@classmethod
	def deserialize(cls, ciphertext: bytes):
		plaintext = TPLinkObfuscation.deobfuscate(ciphertext)
		return cls.deserialize_plaintext(plaintext)

	@classmethod
	def deserialize_plaintext(cls, plaintext: bytes):
		if len(plaintext) < cls._HEADER_DEFINITION.size:
			raise DeserializationException(f"Unable to deserialize RC4 packet too short for header (length {len(plaintext)} bytes).")

		header = cls._HEADER_DEFINITION.unpack_head(plaintext)
		if len(plaintext) != header.length:
			raise DeserializationException(f"Unable to deserialize RC4 packet, header indicates {header.length} bytes but message was {len(plaintext)} bytes long.")

		field_dict = header._asdict()
		field_dict["opcode"] = Opcode(field_dict["opcode"])
		field_dict["switch_mac"] = MACAddress(field_dict["switch_mac"])
		field_dict["host_mac"] = MACAddress(field_dict["host_mac"])
		payload_data = plaintext[cls._HEADER_DEFINITION.size : ]
		field_dict["payload"] = PacketFields.deserialize(payload_data)
		return cls(**field_dict)

	def dump(self):
		for field in dataclasses.fields(self):
			if not field.repr:
				continue
			name = field.name
			value = getattr(self, name)
			if name != "payload":
				if not isinstance(value, enum.Enum):
					print(f"{name}: {value}")
				else:
					print(f"{name}: {value.name}")
			else:
				print(f"{name}: {len(self.payload)} fields")
				for field_item in value:
					field_item.dump(prefix = "    ")
