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

import contextlib
from .Enums import FieldTag
from .Exceptions import DeserializationException
from .TPLinkTypes import get_handler_class

class PacketField():
	def __init__(self, tag: "FieldTag | int", value: "TPLinkRawData"):
		self._tag = tag
		self._value = value

	@property
	def tag(self):
		return self._tag

	@property
	def tag_str(self):
		if isinstance(self.tag, FieldTag):
			return self.tag.name
		else:
			return str(self.tag)

	@property
	def value(self):
		return self._value

	def dump(self, prefix = ""):
		print(f"{prefix}{str(self)}")

	def __bytes__(self):
		tag_bytes = int(self.tag).to_bytes(length = 2, byteorder = "big")
		value = bytes(self.value)
		length_bytes = len(value).to_bytes(length = 2, byteorder = "big")
		return tag_bytes + length_bytes + value

	def __repr__(self):
		return f"{self.tag_str} = {self.value}"

class PacketFields():
	def __init__(self):
		self._fields = [ ]

	def clear(self):
		self._fields = [ ]

	def append(self, field: PacketField):
		self._fields.append(field)

	def append_all(self, fields: list[PacketField]):
		for field in fields:
			self.append(field)

	@classmethod
	def deserialize(cls, payload):
		fields = cls()

		offset = 0
		while True:
			tag = (payload[offset + 0] << 8) | payload[offset + 1]
			if tag == FieldTag.EndOfFields:
				# Exit
				break

			with contextlib.suppress(ValueError):
				tag = FieldTag(tag)

			length = (payload[offset + 2] << 8) | payload[offset + 3]
			value = payload[offset + 4 : offset + 4 + length]
			if len(value) != length:
				raise DeserializationException(f"TLV packet indicated length of {length} bytes, but only {len(value)} bytes available in packet.")
			offset += 4 + length

			handler_class = get_handler_class(tag)
			field = PacketField(tag, handler_class.deserialize(value))
			fields.append(field)

		if offset + 4 != len(payload):
			raise DeserializationException(f"TLV packet has trailing garbage data, length {len(payload)} bytes but finished at offset {offset}.")
		return fields

	def __bytes__(self):
		return b"".join(bytes(field) for field in self._fields) + bytes.fromhex("ffff 0000")

	def __iter__(self):
		return iter(self._fields)

	def __len__(self):
		return len(self._fields)

	def __repr__(self):
		return ", ".join(str(field) for field in self)
