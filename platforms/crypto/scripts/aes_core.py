"""
Manual (educational) AES-128 implementation: SubBytes, ShiftRows, MixColumns,
AddRoundKey, key expansion, 10 rounds. ECB mode with PKCS7 padding, for
teaching the algorithm's internals only - NOT for production use (no IV,
ECB leaks patterns, not constant time).
"""

S_BOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]
INV_S_BOX = [0] * 256
for i, v in enumerate(S_BOX):
    INV_S_BOX[v] = i

RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]


def _xtime(a):
    a <<= 1
    if a & 0x100:
        a ^= 0x11b
    return a & 0xff


def _gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b
        b >>= 1
    return p


def _key_expansion(key16: bytes):
    key_cols = [list(key16[i:i + 4]) for i in range(0, 16, 4)]
    w = key_cols[:]
    for i in range(4, 44):
        temp = w[i - 1][:]
        if i % 4 == 0:
            temp = temp[1:] + temp[:1]
            temp = [S_BOX[b] for b in temp]
            temp[0] ^= RCON[i // 4 - 1]
        w.append([w[i - 4][j] ^ temp[j] for j in range(4)])
    # group into 11 round keys of 16 bytes
    round_keys = []
    for r in range(11):
        cols = w[r * 4:(r + 1) * 4]
        rk = bytearray(16)
        for c in range(4):
            for row in range(4):
                rk[c * 4 + row] = cols[c][row]
        round_keys.append(bytes(rk))
    return round_keys


def _add_round_key(state, round_key):
    return bytes(s ^ k for s, k in zip(state, round_key))


def _sub_bytes(state):
    return bytes(S_BOX[b] for b in state)


def _inv_sub_bytes(state):
    return bytes(INV_S_BOX[b] for b in state)


def _shift_rows(state):
    s = list(state)
    out = [0] * 16
    for row in range(4):
        for col in range(4):
            out[col * 4 + row] = s[((col + row) % 4) * 4 + row]
    return bytes(out)


def _inv_shift_rows(state):
    s = list(state)
    out = [0] * 16
    for row in range(4):
        for col in range(4):
            out[((col + row) % 4) * 4 + row] = s[col * 4 + row]
    return bytes(out)


def _mix_columns(state):
    out = bytearray(16)
    for c in range(4):
        col = state[c * 4:c * 4 + 4]
        out[c * 4 + 0] = _gmul(col[0], 2) ^ _gmul(col[1], 3) ^ col[2] ^ col[3]
        out[c * 4 + 1] = col[0] ^ _gmul(col[1], 2) ^ _gmul(col[2], 3) ^ col[3]
        out[c * 4 + 2] = col[0] ^ col[1] ^ _gmul(col[2], 2) ^ _gmul(col[3], 3)
        out[c * 4 + 3] = _gmul(col[0], 3) ^ col[1] ^ col[2] ^ _gmul(col[3], 2)
    return bytes(out)


def _inv_mix_columns(state):
    out = bytearray(16)
    for c in range(4):
        col = state[c * 4:c * 4 + 4]
        out[c * 4 + 0] = _gmul(col[0], 14) ^ _gmul(col[1], 11) ^ _gmul(col[2], 13) ^ _gmul(col[3], 9)
        out[c * 4 + 1] = _gmul(col[0], 9) ^ _gmul(col[1], 14) ^ _gmul(col[2], 11) ^ _gmul(col[3], 13)
        out[c * 4 + 2] = _gmul(col[0], 13) ^ _gmul(col[1], 9) ^ _gmul(col[2], 14) ^ _gmul(col[3], 11)
        out[c * 4 + 3] = _gmul(col[0], 11) ^ _gmul(col[1], 13) ^ _gmul(col[2], 9) ^ _gmul(col[3], 14)
    return bytes(out)


def _encrypt_block(block16: bytes, round_keys) -> bytes:
    state = _add_round_key(block16, round_keys[0])
    for rnd in range(1, 10):
        state = _sub_bytes(state)
        state = _shift_rows(state)
        state = _mix_columns(state)
        state = _add_round_key(state, round_keys[rnd])
    state = _sub_bytes(state)
    state = _shift_rows(state)
    state = _add_round_key(state, round_keys[10])
    return state


def _decrypt_block(block16: bytes, round_keys) -> bytes:
    state = _add_round_key(block16, round_keys[10])
    for rnd in range(9, 0, -1):
        state = _inv_shift_rows(state)
        state = _inv_sub_bytes(state)
        state = _add_round_key(state, round_keys[rnd])
        state = _inv_mix_columns(state)
    state = _inv_shift_rows(state)
    state = _inv_sub_bytes(state)
    state = _add_round_key(state, round_keys[0])
    return state


def _pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)


def _unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        return data
    return data[:-pad_len]


def aes_encrypt_bytes(data: bytes, key16: bytes) -> bytes:
    round_keys = _key_expansion(key16)
    padded = _pad(data)
    out = bytearray()
    for i in range(0, len(padded), 16):
        out += _encrypt_block(padded[i:i + 16], round_keys)
    return bytes(out)


def aes_decrypt_bytes(data: bytes, key16: bytes) -> bytes:
    round_keys = _key_expansion(key16)
    out = bytearray()
    for i in range(0, len(data), 16):
        out += _decrypt_block(data[i:i + 16], round_keys)
    return _unpad(bytes(out))
