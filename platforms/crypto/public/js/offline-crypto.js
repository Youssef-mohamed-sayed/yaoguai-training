/* ============================================================
   offline-crypto.js — small, dependency-free reference
   implementations used ONLY to grade in-browser exercises
   (hex/base64/xor/md5) when the Flask API isn't running.
   These mirror the behaviour of encoding.py / stream_core.py /
   md5_core.py closely enough for teaching + grading, but the
   "real" implementations the lessons teach live in the Python
   project — this file is a convenience, not the source of truth.
   ============================================================ */

const Offline = {
  hexEncode(str) {
    return Array.from(new TextEncoder().encode(str))
      .map((b) => b.toString(16).padStart(2, "0")).join("");
  },
  hexDecode(hex) {
    const clean = hex.replace(/\s+/g, "");
    const bytes = [];
    for (let i = 0; i < clean.length; i += 2) bytes.push(parseInt(clean.substr(i, 2), 16));
    return new TextDecoder().decode(new Uint8Array(bytes));
  },
  b64Encode(str) {
    return btoa(unescape(encodeURIComponent(str)));
  },
  b64Decode(b64) {
    return decodeURIComponent(escape(atob(b64)));
  },
  xor(str, key) {
    const data = new TextEncoder().encode(str);
    const k = new TextEncoder().encode(key);
    const out = new Uint8Array(data.length);
    for (let i = 0; i < data.length; i++) out[i] = data[i] ^ k[i % k.length];
    return Array.from(out).map((b) => b.toString(16).padStart(2, "0")).join("");
  },
  xorFromHex(hexCipher, key) {
    const bytes = [];
    for (let i = 0; i < hexCipher.length; i += 2) bytes.push(parseInt(hexCipher.substr(i, 2), 16));
    const k = new TextEncoder().encode(key);
    const out = bytes.map((b, i) => b ^ k[i % k.length]);
    return new TextDecoder().decode(new Uint8Array(out));
  },
  // Compact MD5 (public-domain style implementation), returns lowercase hex.
  md5(str) {
    function rotl(x, c) { return (x << c) | (x >>> (32 - c)); }
    function toHexLE(n) {
      let s = "";
      for (let i = 0; i < 4; i++) { s += ((n >>> (i * 8)) & 0xff).toString(16).padStart(2, "0"); }
      return s;
    }
    const K = [];
    for (let i = 0; i < 64; i++) K[i] = Math.floor(Math.abs(Math.sin(i + 1)) * 2 ** 32);
    const S = [7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22,
               5,9,14,20,5,9,14,20,5,9,14,20,5,9,14,20,
               4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23,
               6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21];
    let bytes = Array.from(new TextEncoder().encode(str));
    const origLenBits = bytes.length * 8;
    bytes.push(0x80);
    while (bytes.length % 64 !== 56) bytes.push(0);
    for (let i = 0; i < 8; i++) bytes.push((origLenBits / Math.pow(2, 8 * i)) & 0xff);

    let a0 = 0x67452301, b0 = 0xefcdab89, c0 = 0x98badcfe, d0 = 0x10325476;

    for (let chunk = 0; chunk < bytes.length; chunk += 64) {
      const M = [];
      for (let j = 0; j < 16; j++) {
        M[j] = bytes[chunk + j*4] | (bytes[chunk + j*4+1] << 8) |
               (bytes[chunk + j*4+2] << 16) | (bytes[chunk + j*4+3] << 24);
      }
      let [A,B,C,D] = [a0,b0,c0,d0];
      for (let i = 0; i < 64; i++) {
        let F, g;
        if (i < 16)      { F = (B & C) | (~B & D);         g = i; }
        else if (i < 32) { F = (D & B) | (~D & C);         g = (5*i + 1) % 16; }
        else if (i < 48) { F = B ^ C ^ D;                  g = (3*i + 5) % 16; }
        else             { F = C ^ (B | ~D);                g = (7*i) % 16; }
        F = (F + A + K[i] + M[g]) | 0;
        A = D; D = C; C = B;
        B = (B + rotl(F, S[i])) | 0;
      }
      a0 = (a0 + A) | 0; b0 = (b0 + B) | 0; c0 = (c0 + C) | 0; d0 = (d0 + D) | 0;
    }
    return [a0,b0,c0,d0].map(toHexLE).join("");
  },
};

window.Offline = Offline;
