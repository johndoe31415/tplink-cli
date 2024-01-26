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

class RC4():
	def __init__(self, key):
		self._sbox = self._key_schedule(key)
		self._i = 0
		self._j = 0

	def _key_schedule(self, key):
		assert(isinstance(key, bytes))
		sbox = list(range(256))
		j = 0
		for i in range(256):
			j = (j + sbox[i] + key[i % len(key)]) % 256
			(sbox[i], sbox[j]) = (sbox[j], sbox[i])
		return sbox

	def next_byte(self):
		self._i = (self._i + 1) % 256
		self._j = (self._j + self._sbox[self._i]) % 256
		(self._sbox[self._i], self._sbox[self._j]) = (self._sbox[self._j], self._sbox[self._i])
		k = self._sbox[(self._sbox[self._i] + self._sbox[self._j]) % 256]
		return k

	def next_bytes(self, count):
		return bytes(self.next_byte() for i in range(count))

	def crypt(self, data):
		return bytes(srcbyte ^ keybyte for (srcbyte, keybyte) in zip(data, self.next_bytes(len(data))))

if __name__ == "__main__":
	rc4 = RC4(bytes.fromhex("0102030405"))
	assert(rc4.next_bytes(16) == bytes.fromhex("b2 39 63 05  f0 3d c0 27   cc c3 52 4a  0a 11 18 a8"))
	assert(rc4.next_bytes(16) == bytes.fromhex("69 82 94 4f  18 fc 82 d5   89 c4 03 a4  7a 0d 09 19"))
	rc4.next_bytes(240 - 32)
	assert(rc4.next_bytes(16) == bytes.fromhex("28 cb 11 32  c9 6c e2 86   42 1d ca ad  b8 b6 9e ae"))
	assert(rc4.next_bytes(16) == bytes.fromhex("1c fc f6 2b  03 ed db 64   1d 77 df cf  7f 8d 8c 93"))

	rc4 = RC4(bytes.fromhex("1ada31d5cf688221c109163908ebe51debb46227c6cc8b37641910833222772a"))
	rc4.next_bytes(4096)
	assert(rc4.next_bytes(16) == bytes.fromhex("37 0b 1c 1f  e6 55 91 6d   97 fd 0d 47  ca 1d 72 b8"))
