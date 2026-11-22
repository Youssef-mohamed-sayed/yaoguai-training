/* ============================================================
   registry.js — single source of truth for course structure.
   Order here IS the pedagogical path: Data -> Encoding ->
   Encryption (symmetric -> asymmetric) -> Hashing -> password
   hashing -> cracking/CTF. Every topic found in the slides is
   listed, even ones without a fully written lesson yet
   (implemented:false) — the dashboard shows these as "drafting"
   rather than silently dropping them. All 16 are implemented as of
   this revision; the flag stays in place for any future addition.
   ============================================================ */

const COURSE = [
  // ---------------- ENCODING ----------------
  { id:"hex", order:1, category:"encoding", title:"Hexadecimal", native:"十六進法",
    difficulty:"Beginner", summary:"Turn bytes into readable text and back — the alphabet every other lesson assumes you can read.",
    implemented:true },
  { id:"base64", order:2, category:"encoding", title:"Base64", native:"基数64",
    difficulty:"Beginner", summary:"Pack arbitrary bytes into plain ASCII — how binary data survives being emailed, URLed and JSON'd.",
    implemented:true },
  { id:"ascii", order:3, category:"encoding", title:"ASCII", native:"文字符号",
    difficulty:"Beginner", summary:"The map from the letters you type to the numbers a computer actually stores.",
    implemented:true },
  { id:"url", order:4, category:"encoding", title:"URL Encoding", native:"百分符号化",
    difficulty:"Easy", summary:"Why spaces become %20 — escaping characters a URL isn't allowed to carry raw.",
    implemented:true },

  // ---------------- ENCRYPTION (symmetric -> asymmetric) ----------------
  { id:"xor", order:5, category:"encryption", title:"XOR Cipher", native:"排他的論理和",
    difficulty:"Easy", summary:"The simplest possible cipher — and the one that teaches you why key reuse is fatal.",
    implemented:true },
  { id:"rc4", order:6, category:"encryption", title:"RC4", native:"流密码",
    difficulty:"Intermediate", summary:"A stream cipher that generates an XOR keystream byte-by-byte — and why it's retired.",
    implemented:true },
  { id:"des", order:7, category:"encryption", title:"DES", native:"旧世代暗号",
    difficulty:"Intermediate", summary:"The Feistel network that defined block ciphers for 20 years, broken by its own short key.",
    implemented:true },
  { id:"3des", order:8, category:"encryption", title:"Triple DES", native:"三重旧世代",
    difficulty:"Intermediate", summary:"Patching DES's key size by running it three times — a bridge, not a destination.",
    implemented:true },
  { id:"aes", order:9, category:"encryption", title:"AES", native:"高度暗号標準",
    difficulty:"Advanced", summary:"The block cipher securing almost everything today: state grids, S-boxes and round keys.",
    implemented:true },
  { id:"diffie-hellman", order:10, category:"encryption", title:"Diffie–Hellman", native:"鍵交換",
    difficulty:"Intermediate", summary:"How two strangers agree on a secret key in full view of an eavesdropper — no ciphertext involved.",
    implemented:true },
  { id:"rsa", order:11, category:"encryption", title:"RSA", native:"非対称暗号",
    difficulty:"Advanced", summary:"Public-key encryption built from the difficulty of factoring — and why padding isn't optional.",
    implemented:true },

  // ---------------- HASHING ----------------
  { id:"md5", order:12, category:"hashing", title:"MD5", native:"一方向関数",
    difficulty:"Easy", summary:"A one-way digest you can't run backwards — and the collisions that retired it for security.",
    implemented:true },
  { id:"sha1", order:13, category:"hashing", title:"SHA-1", native:"安全な旧式ハッシュ",
    difficulty:"Easy", summary:"MD5's sturdier sibling, deprecated the same way: collisions, eventually, catch up.",
    implemented:true },
  { id:"sha256", order:14, category:"hashing", title:"SHA-256", native:"現行ハッシュ標準",
    difficulty:"Intermediate", summary:"The hash function behind TLS certificates, Git commits and Bitcoin blocks.",
    implemented:true },
  { id:"bcrypt", order:15, category:"hashing", title:"bcrypt", native:"遅延ハッシュ",
    difficulty:"Intermediate", summary:"Password hashing designed to be slow on purpose — salts, cost factors, and why speed is the enemy here.",
    implemented:true },
  { id:"cracking", order:16, category:"hashing", title:"Cracking Hashes", native:"総当たり攻撃",
    difficulty:"CTF", summary:"John the Ripper, Hashcat and wordlists — turning a leaked hash back into a password.",
    implemented:true, extra:true },
];

function courseById(id){ return COURSE.find(c => c.id === id); }
function courseByCategory(cat){ return COURSE.filter(c => c.category === cat).sort((a,b)=>a.order-b.order); }
function courseOrdered(){ return [...COURSE].sort((a,b)=>a.order-b.order); }
function neighbours(id){
  const ordered = courseOrdered();
  const i = ordered.findIndex(c => c.id === id);
  return { prev: ordered[i-1] || null, next: ordered[i+1] || null };
}

window.COURSE = COURSE;
window.courseById = courseById;
window.courseByCategory = courseByCategory;
window.courseOrdered = courseOrdered;
window.neighbours = neighbours;
