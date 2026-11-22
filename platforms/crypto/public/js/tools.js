/* ============================================================
   tools.js — CyberChef-style workbench. Every operation calls the
   Flask API through CryptoAPI (js/api.js); nothing is computed here.
   ============================================================ */

const T = CryptoAPI;
const KEY  = { id: "key",  label: "Key",  placeholder: "secret key" };
const asText = (v) => Array.isArray(v) ? v.join(", ") : (typeof v === "boolean" ? String(v) : v);

/* Each tool: modes[] with run(input, params) -> API promise, and endpoint text. */
const TOOLS = [
  { group: "Encoding" },
  { id: "hex", name: "Hexadecimal", desc: "Bytes as base-16 text. Encoding only — no secret.",
    modes: [
      { name: "Encode", endpoint: "/api/encoding/hex/encode", run: (i) => T.encoding.hexEncode(i) },
      { name: "Decode", endpoint: "/api/encoding/hex/decode", run: (i) => T.encoding.hexDecode(i.replace(/\s+/g, "")) } ] },
  { id: "base64", name: "Base64", desc: "Binary-safe text encoding. Encoding only — no secret.",
    modes: [
      { name: "Encode", endpoint: "/api/encoding/base64/encode", run: (i) => T.encoding.b64Encode(i) },
      { name: "Decode", endpoint: "/api/encoding/base64/decode", run: (i) => T.encoding.b64Decode(i.trim()) } ] },
  { id: "ascii", name: "ASCII codes", desc: "Characters as decimal codes, e.g. 72, 105.",
    modes: [
      { name: "Encode", endpoint: "/api/encoding/ascii/encode", run: (i) => T.encoding.asciiEncode(i) },
      { name: "Decode", endpoint: "/api/encoding/ascii/decode", run: (i) => T.encoding.asciiDecode(i.trim().split(/[\s,]+/).filter(Boolean).join(",")) } ] },
  { id: "url", name: "URL encoding", desc: "Percent-encoding used in web addresses.",
    modes: [
      { name: "Encode", endpoint: "/api/encoding/url/encode", run: (i) => T.encoding.urlEncode(i) },
      { name: "Decode", endpoint: "/api/encoding/url/decode", run: (i) => T.encoding.urlDecode(i) } ] },

  { group: "Encryption" },
  { id: "xor", name: "XOR", desc: "Repeating-key XOR. Ciphertext is Base64.", params: [KEY],
    modes: [
      { name: "Encrypt", endpoint: "/api/encryption/xor", run: (i, p) => T.encryption.xor(i, p.key) },
      { name: "Decrypt", endpoint: "/api/decryption/xor", run: (i, p) => T.decryption.xor(i.trim(), p.key) } ] },
  { id: "rc4", name: "RC4", desc: "Stream cipher. Ciphertext is Base64.", params: [KEY],
    modes: [
      { name: "Encrypt", endpoint: "/api/encryption/rc4", run: (i, p) => T.encryption.rc4(i, p.key) },
      { name: "Decrypt", endpoint: "/api/decryption/rc4", run: (i, p) => T.decryption.rc4(i.trim(), p.key) } ] },
  { id: "des", name: "DES", desc: "56-bit block cipher. The key is padded or cut to 8 bytes. Ciphertext is Base64.", params: [KEY],
    modes: [
      { name: "Encrypt", endpoint: "/api/encryption/des", run: (i, p) => T.encryption.des(i, p.key) },
      { name: "Decrypt", endpoint: "/api/decryption/des", run: (i, p) => T.decryption.des(i.trim(), p.key) } ] },
  { id: "3des", name: "Triple DES", desc: "DES applied three times. Leave key 3 empty to reuse key 1.",
    params: [ { id: "key1", label: "Key 1", placeholder: "first key" }, { id: "key2", label: "Key 2", placeholder: "second key" }, { id: "key3", label: "Key 3 (optional)", placeholder: "third key", optional: true } ],
    modes: [
      { name: "Encrypt", endpoint: "/api/encryption/3des", run: (i, p) => T.encryption.des3(i, p.key1, p.key2, p.key3 || undefined) },
      { name: "Decrypt", endpoint: "/api/decryption/3des", run: (i, p) => T.decryption.des3(i.trim(), p.key1, p.key2, p.key3 || undefined) } ] },
  { id: "aes", name: "AES-128", desc: "Modern block cipher. The key is padded or cut to 16 bytes. Ciphertext is Base64.", params: [KEY],
    modes: [
      { name: "Encrypt", endpoint: "/api/encryption/aes", run: (i, p) => T.encryption.aes(i, p.key) },
      { name: "Decrypt", endpoint: "/api/decryption/aes", run: (i, p) => T.decryption.aes(i.trim(), p.key) } ] },
  { id: "rsa", name: "RSA", desc: "Public-key demo. Generate a key pair, then encrypt with (e, n) and decrypt with (d, n). Keep messages short.",
    custom: "rsa",
    params: [ { id: "n", label: "n (modulus)", placeholder: "click Generate keys", area: true }, { id: "e", label: "e (public exponent)", placeholder: "65537" }, { id: "d", label: "d (private exponent)", placeholder: "needed to decrypt", area: true } ],
    modes: [
      { name: "Encrypt", endpoint: "/api/encryption/rsa", run: (i, p) => T.encryption.rsa(i, p.e, p.n) },
      { name: "Decrypt", endpoint: "/api/decryption/rsa", run: (i, p) => T.decryption.rsa(i.trim(), p.d, p.n) } ] },

  { group: "Hashing" },
  { id: "md5", name: "MD5", desc: "128-bit digest. Broken for security — fine for learning.",
    modes: [ { name: "Hash", endpoint: "/api/hashing/md5", run: (i) => T.hashing.md5(i) } ] },
  { id: "sha1", name: "SHA-1", desc: "160-bit digest. Deprecated.",
    modes: [ { name: "Hash", endpoint: "/api/hashing/sha1", run: (i) => T.hashing.sha1(i) } ] },
  { id: "sha256", name: "SHA-256", desc: "256-bit digest used by TLS, Git and Bitcoin.",
    modes: [ { name: "Hash", endpoint: "/api/hashing/sha256", run: (i) => T.hashing.sha256(i) } ] },
  { id: "bcrypt", name: "bcrypt", desc: "Slow, salted password hashing. Use Verify to check a password against a hash.",
    modes: [
      { name: "Hash", endpoint: "/api/hashing/bcrypt", params: [ { id: "rounds", label: "Cost (4–14)", placeholder: "12", type: "number", value: "10", min: 4, max: 14 } ],
        run: (i, p) => T.hashing.bcryptHash(i, parseInt(p.rounds || "10", 10)) },
      { name: "Verify", endpoint: "/api/hashing/bcrypt/verify", params: [ { id: "hash", label: "bcrypt hash", placeholder: "$2b$10$…", area: true } ],
        run: (i, p) => T.hashing.bcryptVerify(i, (p.hash || "").trim()).then(ok => ok ? "✓ match — the password fits this hash" : "✗ no match") } ] },

  { group: "Cracking" },
  { id: "crack", name: "Crack a hash", custom: "crack",
    desc: "Tries words from the sample wordlist against the hash, looks it up in Hashes.com's crowd-sourced database, or automatically identifies unknown hash algorithms.",
    modes: [
      { name: "Crack (sample wordlist)", endpoint: "/api/crack/wordlist",
        params: [ { id: "hash_type", label: "Hash type", type: "select", options: [["md5","MD5"],["sha1","SHA-1"],["sha256","SHA-256"]] } ],
        run: (i, p) => T.crack.wordlist(i.trim(), p.hash_type)
        .then(r => r.cracked
          ? `✓ cracked after trying ${r.tried} word${r.tried === 1 ? "" : "s"}\n\npassword: ${r.password}`
          : `✗ not in this app's ${r.tried}-word sample list.\nTry the Hashes.com mode above, or a full wordlist with John/Hashcat.`) },
      { name: "Crack (Hashes.com)", endpoint: "/api/hashescom",
        params: [ { id: "hashescom_key", label: "Hashes.com API key", value: "750f5602dc5aed7bad2d960011df4790", placeholder: "750f5602dc5aed7bad2d960011df4790", persist: true } ],
        run: (i, p) => T.crack.hashescom(i.trim(), p.hashescom_key || "750f5602dc5aed7bad2d960011df4790")
          .then(r => r.cracked
            ? `✓ found in Hashes.com's database\n\npassword: ${r.password}\nalgorithm: ${r.algorithm}${r.salt ? `\nsalt: ${r.salt}` : ""}`
            : "✗ not found in Hashes.com's database.\nThat only rules out hashes someone has already cracked before — it says nothing about a genuinely strong, never-leaked password.") },
      { name: "Identify algorithm", endpoint: "/api/hashescom/identify",
        run: (i) => T.crack.hashescomIdentify(i.trim(), true)
          .then(r => r.algorithms && r.algorithms.length
            ? `Identified Algorithm(s):\n\n${r.algorithms.map((a, idx) => `  ${idx + 1}. ${a}`).join("\n")}`
            : "Could not identify algorithm — hash format unrecognised by Hashes.com.") },
    ] },

  { group: "File Crypto" },
  { id: "file-encrypt", name: "File Encrypt", custom: "file-encrypt",
    desc: "Upload a .txt file and encrypt it. DES: download the encrypted file and remember your key. Hybrid RSA+DES: a random session key is generated, encrypted with your RSA public key, and bundled separately — you need your private key (d) to decrypt later.",
    modes: [] },
  { id: "file-decrypt", name: "File Decrypt", custom: "file-decrypt",
    desc: "Upload an encrypted file and recover the original. DES: provide the same key used to encrypt. Hybrid: provide the encrypted session key, your RSA private exponent d, and modulus n.",
    modes: [] },
];

const $ = (id) => document.getElementById(id);
const els = { list: $("tools-list"), title: $("tool-title"), desc: $("tool-desc"), modes: $("mode-switch"),
  input: $("input"), output: $("output"), params: $("params"), msg: $("msg"), endpoint: $("endpoint"), run: $("run-btn") };
const state = { tool: null, mode: 0, values: {} };
const byId = (id) => TOOLS.find(t => t.id === id);

function setMsg(text, kind){ els.msg.textContent = text || ""; els.msg.className = "tool-msg" + (kind ? " " + kind : ""); }

function buildList(){
  els.list.innerHTML = "";
  TOOLS.forEach(t => {
    if (t.group){ const h = document.createElement("div"); h.className = "tools-group"; h.textContent = t.group; els.list.appendChild(h); return; }
    const a = document.createElement("a"); a.href = "#" + t.id; a.textContent = t.name; a.dataset.id = t.id;
    els.list.appendChild(a);
  });
}

function currentParams(){
  const t = state.tool;
  if (!t) return [];
  const m = (t.modes && t.modes.length) ? t.modes[state.mode] : null;
  return [...(t.params || []), ...(m && m.params ? m.params : [])];
}

function renderFileEncryptUI() {
  els.params.innerHTML = "";
  els.params.style.display = "";

  const cat = state.fileEncCat || "encrypt"; // "encrypt", "encode", "hash"
  const encAlgo = state.fileEncAlgo || "des";
  const encodeAlgo = state.fileEncodeAlgo || "base64";
  const hashAlgo = state.fileHashAlgo || "sha256";

  const container = document.createElement("div");
  container.className = "param-full";
  container.style.display = "flex";
  container.style.flexDirection = "column";
  container.style.gap = "16px";
  container.style.width = "100%";

  // 1. Category Switch
  const catWrap = document.createElement("div");
  const catLabel = document.createElement("label");
  catLabel.textContent = "Operation Category";
  catLabel.style.display = "block";
  catLabel.style.marginBottom = "6px";
  catLabel.style.fontSize = "12.5px";
  catLabel.style.color = "var(--paper-dim)";

  const catSwitch = document.createElement("div");
  catSwitch.className = "mode-switch";
  catSwitch.setAttribute("role", "tablist");

  const catButtons = [
    { id: "encrypt", label: "Encryption" },
    { id: "encode", label: "Encoding" },
    { id: "hash", label: "Hashing" },
  ];

  catButtons.forEach(c => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = c.label;
    btn.className = cat === c.id ? "on" : "";
    btn.addEventListener("click", () => {
      state.fileEncCat = c.id;
      renderFileEncryptUI();
    });
    catSwitch.appendChild(btn);
  });

  catWrap.append(catLabel, catSwitch);
  container.appendChild(catWrap);

  // 2. Algorithm Selector
  const algoWrap = document.createElement("div");
  const algoLabel = document.createElement("label");
  algoLabel.textContent = "Algorithm";
  algoLabel.style.display = "block";
  algoLabel.style.marginBottom = "6px";
  algoLabel.style.fontSize = "12.5px";
  algoLabel.style.color = "var(--paper-dim)";

  const algoSwitch = document.createElement("div");
  algoSwitch.className = "mode-switch";
  algoSwitch.style.flexWrap = "wrap";
  algoSwitch.setAttribute("role", "tablist");

  let activeAlgo = encAlgo;
  let algoList = [];

  if (cat === "encrypt") {
    activeAlgo = encAlgo;
    algoList = [
      { id: "des", label: "DES" },
      { id: "aes", label: "AES-128" },
      { id: "3des", label: "Triple DES" },
      { id: "rc4", label: "RC4" },
      { id: "xor", label: "XOR" },
      { id: "hybrid", label: "Hybrid RSA+DES" },
    ];
  } else if (cat === "encode") {
    activeAlgo = encodeAlgo;
    algoList = [
      { id: "base64", label: "Base64" },
      { id: "hex", label: "Hexadecimal" },
      { id: "ascii", label: "ASCII codes" },
      { id: "url", label: "URL encoding" },
    ];
  } else {
    activeAlgo = hashAlgo;
    algoList = [
      { id: "md5", label: "MD5" },
      { id: "sha1", label: "SHA-1" },
      { id: "sha256", label: "SHA-256" },
      { id: "bcrypt", label: "bcrypt" },
    ];
  }

  algoList.forEach(a => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = a.label;
    btn.className = activeAlgo === a.id ? "on" : "";
    btn.addEventListener("click", () => {
      if (cat === "encrypt") state.fileEncAlgo = a.id;
      else if (cat === "encode") state.fileEncodeAlgo = a.id;
      else state.fileHashAlgo = a.id;
      renderFileEncryptUI();
    });
    algoSwitch.appendChild(btn);
  });

  algoWrap.append(algoLabel, algoSwitch);
  container.appendChild(algoWrap);

  // 3. File Input
  const fileWrap = document.createElement("div");
  const fileLabel = document.createElement("label");
  fileLabel.textContent = "Select file to process (max 1 MB)";
  fileLabel.style.display = "block";
  fileLabel.style.marginBottom = "6px";
  fileLabel.style.fontSize = "12.5px";
  fileLabel.style.color = "var(--paper-dim)";

  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.id = "file-upload";
  fileInput.accept = ".txt,*/*";

  const fileInfo = document.createElement("div");
  fileInfo.style.fontSize = "13px";
  fileInfo.style.marginTop = "4px";
  fileInfo.style.color = "var(--paper-dim)";

  fileInput.addEventListener("change", () => {
    const f = fileInput.files[0];
    if (f) {
      fileInfo.textContent = `Selected: ${f.name} (${(f.size / 1024).toFixed(1)} KB)`;
      fileInfo.style.color = "var(--ok, #4ade80)";
    } else {
      fileInfo.textContent = "";
    }
  });

  fileWrap.append(fileLabel, fileInput, fileInfo);
  container.appendChild(fileWrap);

  // 4. Algorithm-specific input fields
  if (cat === "encrypt") {
    if (activeAlgo === "des") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (DES 8-byte key)</label>
      <input type="text" id="file-key" placeholder="e.g. secret8k" spellcheck="false" value="${state.fileDesKey || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileDesKey = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "aes") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (AES 16-byte key)</label>
      <input type="text" id="file-key" placeholder="e.g. secret16bytekey!" spellcheck="false" value="${state.fileAesKey || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileAesKey = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "3des") {
      const w = document.createElement("div");
      w.style.display = "grid";
      w.style.gridTemplateColumns = "repeat(auto-fit, minmax(200px, 1fr))";
      w.style.gap = "10px";
      w.innerHTML = `
        <div><label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Key 1</label>
        <input type="text" id="file-k1" placeholder="first key" spellcheck="false" value="${state.file3DesK1 || ""}"></div>
        <div><label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Key 2</label>
        <input type="text" id="file-k2" placeholder="second key" spellcheck="false" value="${state.file3DesK2 || ""}"></div>
        <div><label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Key 3 (optional)</label>
        <input type="text" id="file-k3" placeholder="optional third key" spellcheck="false" value="${state.file3DesK3 || ""}"></div>
      `;
      w.querySelector("#file-k1").addEventListener("input", (e) => { state.file3DesK1 = e.target.value; });
      w.querySelector("#file-k2").addEventListener("input", (e) => { state.file3DesK2 = e.target.value; });
      w.querySelector("#file-k3").addEventListener("input", (e) => { state.file3DesK3 = e.target.value; });
      container.appendChild(w);
    } else if (activeAlgo === "rc4") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (RC4 stream key)</label>
      <input type="text" id="file-key" placeholder="stream cipher key" spellcheck="false" value="${state.fileRc4Key || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileRc4Key = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "xor") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (XOR key)</label>
      <input type="text" id="file-key" placeholder="repeating xor key" spellcheck="false" value="${state.fileXorKey || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileXorKey = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "hybrid") {
      const w = document.createElement("div");
      w.style.display = "flex";
      w.style.flexDirection = "column";
      w.style.gap = "10px";
      w.innerHTML = `
        <div>
          <label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">RSA Modulus (n) — generate with RSA tool</label>
          <textarea id="file-rsa-n" rows="2" placeholder="paste RSA modulus n (decimal integer)" spellcheck="false">${state.fileRsaN || ""}</textarea>
        </div>
        <div>
          <label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">RSA Public Exponent (e)</label>
          <input type="text" id="file-rsa-e" placeholder="65537" spellcheck="false" value="${state.fileRsaE || "65537"}">
          <div style="font-size:12px;margin-top:4px;color:var(--paper-dim)">💡 Tip: Switch to the RSA tool in the sidebar to generate a 256-bit or 512-bit key pair.</div>
        </div>
      `;
      w.querySelector("#file-rsa-n").addEventListener("input", (e) => { state.fileRsaN = e.target.value; });
      w.querySelector("#file-rsa-e").addEventListener("input", (e) => { state.fileRsaE = e.target.value; });
      container.appendChild(w);
    }
  } else if (cat === "encode") {
    const info = document.createElement("div");
    info.style.fontSize = "12.5px";
    info.style.color = "var(--paper-dim)";
    info.textContent = `ℹ️ ${activeAlgo.toUpperCase()} encoding transforms raw file bytes into text representation. No secret key needed.`;
    container.appendChild(info);
  } else {
    // Hashing
    if (activeAlgo === "bcrypt") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Cost Factor / Rounds (4–14)</label>
      <input type="number" id="file-rounds" min="4" max="14" value="${state.fileBcryptRounds || "10"}" style="max-width:140px">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileBcryptRounds = inp.value; });
      container.appendChild(w);
    } else {
      const info = document.createElement("div");
      info.style.fontSize = "12.5px";
      info.style.color = "var(--paper-dim)";
      info.textContent = `ℹ️ Computes a cryptographic checksum (${activeAlgo.toUpperCase()}) for data integrity auditing. No key required.`;
      container.appendChild(info);
    }
  }

  // 5. Action Button & Status
  const actionRow = document.createElement("div");
  actionRow.style.display = "flex";
  actionRow.style.alignItems = "center";
  actionRow.style.gap = "14px";
  actionRow.style.flexWrap = "wrap";
  actionRow.style.marginTop = "6px";

  const runBtn = document.createElement("button");
  runBtn.type = "button";
  runBtn.className = "btn btn-primary";
  runBtn.textContent = cat === "hash" ? "Compute Hash" : (cat === "encode" ? "Encode & Download" : "Encrypt & Download");

  const statusSpan = document.createElement("span");
  statusSpan.className = "tool-msg";

  actionRow.append(runBtn, statusSpan);
  container.appendChild(actionRow);

  // 6. Result Card (for Hybrid key output or Hash output)
  const resultCard = document.createElement("div");
  resultCard.id = "file-result-card";
  resultCard.style.display = "none";
  resultCard.style.flexDirection = "column";
  resultCard.style.gap = "8px";
  resultCard.style.padding = "14px";
  resultCard.style.border = "1px solid var(--line)";
  resultCard.style.marginTop = "10px";

  container.appendChild(resultCard);

  // Run Handler
  runBtn.addEventListener("click", async () => {
    resultCard.style.display = "none";
    resultCard.innerHTML = "";
    statusSpan.textContent = "";
    statusSpan.className = "tool-msg";

    const file = fileInput.files[0];
    if (!file) {
      statusSpan.textContent = "Choose a file first.";
      statusSpan.className = "tool-msg bad";
      return;
    }
    if (file.size > 1024 * 1024) {
      statusSpan.textContent = "File too large (max 1 MB).";
      statusSpan.className = "tool-msg bad";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("action", cat);
    formData.append("algo", activeAlgo);

    if (cat === "encrypt") {
      if (activeAlgo === "des") {
        const k = (state.fileDesKey || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "aes") {
        const k = (state.fileAesKey || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "3des") {
        const k1 = (state.file3DesK1 || "").trim();
        const k2 = (state.file3DesK2 || "").trim();
        const k3 = (state.file3DesK3 || "").trim();
        if (!k1 || !k2) { statusSpan.textContent = "Fill in: Key 1 and Key 2"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key1", k1);
        formData.append("key2", k2);
        if (k3) formData.append("key3", k3);
      } else if (activeAlgo === "rc4") {
        const k = (state.fileRc4Key || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "xor") {
        const k = (state.fileXorKey || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "hybrid") {
        const n = (state.fileRsaN || "").trim();
        const e = (state.fileRsaE || "65537").trim();
        if (!n || !e) { statusSpan.textContent = "Fill in: n and e"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("n", n);
        formData.append("e", e);
      }
    } else if (cat === "hash") {
      if (activeAlgo === "bcrypt") {
        formData.append("rounds", (state.fileBcryptRounds || "10").trim());
      }
    }

    runBtn.disabled = true;
    statusSpan.textContent = cat === "hash" ? "Computing hash…" : "Processing…";
    statusSpan.className = "tool-msg";

    try {
      const res = await T.file.transform(formData);

      if (cat === "hash") {
        statusSpan.textContent = `✓ ${res.algo.toUpperCase()} hash computed successfully.`;
        statusSpan.className = "tool-msg ok";

        resultCard.style.display = "flex";
        resultCard.innerHTML = `
          <div style="font-size:12.5px;color:var(--paper-dim);font-weight:600">
            ${res.algo.toUpperCase()} Hash:
          </div>
          <textarea id="file-hash-out" readonly rows="2" style="font-family:monospace;font-size:13px"></textarea>
          <div style="display:flex;gap:10px;flex-wrap:wrap">
            <button type="button" class="btn btn-ghost btn-sm" id="copy-file-hash-btn">Copy Hash</button>
            <button type="button" class="btn btn-ghost btn-sm" id="dl-checksum-btn">Download Checksum File</button>
          </div>
        `;
        const hashArea = resultCard.querySelector("#file-hash-out");
        hashArea.value = res.hash;

        resultCard.querySelector("#copy-file-hash-btn").addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(res.hash);
            statusSpan.textContent = "✓ Hash copied to clipboard.";
            statusSpan.className = "tool-msg ok";
          } catch (_) {
            hashArea.select();
            document.execCommand("copy");
            statusSpan.textContent = "✓ Hash copied.";
            statusSpan.className = "tool-msg ok";
          }
        });

        resultCard.querySelector("#dl-checksum-btn").addEventListener("click", () => {
          const checksumText = `${res.hash}  ${res.filename}\n`;
          const blob = new Blob([checksumText], { type: "text/plain;charset=utf-8" });
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = `${res.filename}.${res.algo}`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(a.href);
        });

      } else if (cat === "encrypt" && activeAlgo === "hybrid") {
        const blob = new Blob([res.encrypted_file_b64], { type: "text/plain;charset=utf-8" });
        const downloadName = (res.original_filename || file.name) + ".hybrid.enc";
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = downloadName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);

        statusSpan.textContent = `✓ File encrypted and downloaded: ${downloadName}`;
        statusSpan.className = "tool-msg ok";

        resultCard.style.display = "flex";
        resultCard.innerHTML = `
          <div style="font-size:12.5px;color:var(--paper-dim);font-weight:600">
            Encrypted session key (RSA-wrapped DES key):
          </div>
          <div style="font-size:12px;color:var(--paper-dim)">
            Save this key! You will need it along with your private exponent <code>d</code> and modulus <code>n</code> to decrypt the file.
          </div>
          <textarea id="file-hybrid-key-out" readonly rows="2" style="font-family:monospace;font-size:13px"></textarea>
          <div>
            <button type="button" class="btn btn-ghost btn-sm" id="copy-session-key-btn">Copy key</button>
          </div>
        `;
        const keyArea = resultCard.querySelector("#file-hybrid-key-out");
        keyArea.value = res.encrypted_key;
        resultCard.querySelector("#copy-session-key-btn").addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(res.encrypted_key);
            statusSpan.textContent = "✓ Encrypted session key copied to clipboard.";
            statusSpan.className = "tool-msg ok";
          } catch (_) {
            keyArea.select();
            document.execCommand("copy");
            statusSpan.textContent = "✓ Encrypted session key copied.";
            statusSpan.className = "tool-msg ok";
          }
        });
      } else {
        // Normal file download
        statusSpan.textContent = `✓ File processed and downloaded: ${res.filename || "file"}`;
        statusSpan.className = "tool-msg ok";
      }
    } catch (err) {
      statusSpan.textContent = err.message || "Operation failed.";
      statusSpan.className = "tool-msg bad";
    } finally {
      runBtn.disabled = false;
    }
  });

  els.params.appendChild(container);
}

function renderFileDecryptUI() {
  els.params.innerHTML = "";
  els.params.style.display = "";

  const cat = state.fileDecCat || "decrypt"; // "decrypt", "decode", "verify"
  const decAlgo = state.fileDecAlgo || "des";
  const decodeAlgo = state.fileDecodeAlgo || "base64";
  const verifyAlgo = state.fileVerifyAlgo || "sha256";

  const container = document.createElement("div");
  container.className = "param-full";
  container.style.display = "flex";
  container.style.flexDirection = "column";
  container.style.gap = "16px";
  container.style.width = "100%";

  // 1. Category Switch
  const catWrap = document.createElement("div");
  const catLabel = document.createElement("label");
  catLabel.textContent = "Operation Category";
  catLabel.style.display = "block";
  catLabel.style.marginBottom = "6px";
  catLabel.style.fontSize = "12.5px";
  catLabel.style.color = "var(--paper-dim)";

  const catSwitch = document.createElement("div");
  catSwitch.className = "mode-switch";
  catSwitch.setAttribute("role", "tablist");

  const catButtons = [
    { id: "decrypt", label: "Decryption" },
    { id: "decode", label: "Decoding" },
    { id: "verify", label: "Hash Verify" },
  ];

  catButtons.forEach(c => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = c.label;
    btn.className = cat === c.id ? "on" : "";
    btn.addEventListener("click", () => {
      state.fileDecCat = c.id;
      renderFileDecryptUI();
    });
    catSwitch.appendChild(btn);
  });

  catWrap.append(catLabel, catSwitch);
  container.appendChild(catWrap);

  // 2. Algorithm Selector
  const algoWrap = document.createElement("div");
  const algoLabel = document.createElement("label");
  algoLabel.textContent = "Algorithm";
  algoLabel.style.display = "block";
  algoLabel.style.marginBottom = "6px";
  algoLabel.style.fontSize = "12.5px";
  algoLabel.style.color = "var(--paper-dim)";

  const algoSwitch = document.createElement("div");
  algoSwitch.className = "mode-switch";
  algoSwitch.style.flexWrap = "wrap";
  algoSwitch.setAttribute("role", "tablist");

  let activeAlgo = decAlgo;
  let algoList = [];

  if (cat === "decrypt") {
    activeAlgo = decAlgo;
    algoList = [
      { id: "des", label: "DES" },
      { id: "aes", label: "AES-128" },
      { id: "3des", label: "Triple DES" },
      { id: "rc4", label: "RC4" },
      { id: "xor", label: "XOR" },
      { id: "hybrid", label: "Hybrid RSA+DES" },
    ];
  } else if (cat === "decode") {
    activeAlgo = decodeAlgo;
    algoList = [
      { id: "base64", label: "Base64" },
      { id: "hex", label: "Hexadecimal" },
      { id: "ascii", label: "ASCII codes" },
      { id: "url", label: "URL encoding" },
    ];
  } else {
    activeAlgo = verifyAlgo;
    algoList = [
      { id: "md5", label: "MD5" },
      { id: "sha1", label: "SHA-1" },
      { id: "sha256", label: "SHA-256" },
      { id: "bcrypt", label: "bcrypt" },
    ];
  }

  algoList.forEach(a => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = a.label;
    btn.className = activeAlgo === a.id ? "on" : "";
    btn.addEventListener("click", () => {
      if (cat === "decrypt") state.fileDecAlgo = a.id;
      else if (cat === "decode") state.fileDecodeAlgo = a.id;
      else state.fileVerifyAlgo = a.id;
      renderFileDecryptUI();
    });
    algoSwitch.appendChild(btn);
  });

  algoWrap.append(algoLabel, algoSwitch);
  container.appendChild(algoWrap);

  // 3. File Input
  const fileWrap = document.createElement("div");
  const fileLabel = document.createElement("label");
  fileLabel.textContent = cat === "verify" ? "Select file to verify checksum" : "Select encrypted or encoded file to restore";
  fileLabel.style.display = "block";
  fileLabel.style.marginBottom = "6px";
  fileLabel.style.fontSize = "12.5px";
  fileLabel.style.color = "var(--paper-dim)";

  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.id = "file-upload-dec";
  fileInput.accept = ".enc,.des.enc,.aes.enc,.b64,.hex,.ascii,.url,*/*";

  const fileInfo = document.createElement("div");
  fileInfo.style.fontSize = "13px";
  fileInfo.style.marginTop = "4px";
  fileInfo.style.color = "var(--paper-dim)";

  fileInput.addEventListener("change", () => {
    const f = fileInput.files[0];
    if (f) {
      fileInfo.textContent = `Selected: ${f.name} (${(f.size / 1024).toFixed(1)} KB)`;
      const origInp = document.getElementById("file-dec-orig-name");
      if (origInp && !origInp.value.trim()) {
        let suggested = f.name;
        const suffixes = [".des.enc", ".aes.enc", ".3des.enc", ".rc4.enc", ".xor.enc", ".hybrid.enc", ".b64", ".hex", ".ascii", ".url", ".enc"];
        for (const s of suffixes) {
          if (suggested.endsWith(s)) {
            suggested = suggested.slice(0, -s.length);
            break;
          }
        }
        origInp.value = suggested;
        state.fileDecOrigName = suggested;
      }
    } else {
      fileInfo.textContent = "";
    }
  });

  fileWrap.append(fileLabel, fileInput, fileInfo);
  container.appendChild(fileWrap);

  // 4. Algorithm-specific input fields
  if (cat === "decrypt") {
    if (activeAlgo === "des") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (DES key)</label>
      <input type="text" id="file-dec-key" placeholder="same key used for encryption" spellcheck="false" value="${state.fileDecDesKey || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileDecDesKey = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "aes") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (AES 16-byte key)</label>
      <input type="text" id="file-dec-key" placeholder="same key used for encryption" spellcheck="false" value="${state.fileDecAesKey || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileDecAesKey = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "3des") {
      const w = document.createElement("div");
      w.style.display = "grid";
      w.style.gridTemplateColumns = "repeat(auto-fit, minmax(200px, 1fr))";
      w.style.gap = "10px";
      w.innerHTML = `
        <div><label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Key 1</label>
        <input type="text" id="file-dec-k1" placeholder="first key" spellcheck="false" value="${state.fileDec3DesK1 || ""}"></div>
        <div><label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Key 2</label>
        <input type="text" id="file-dec-k2" placeholder="second key" spellcheck="false" value="${state.fileDec3DesK2 || ""}"></div>
        <div><label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Key 3 (optional)</label>
        <input type="text" id="file-dec-k3" placeholder="optional third key" spellcheck="false" value="${state.fileDec3DesK3 || ""}"></div>
      `;
      w.querySelector("#file-dec-k1").addEventListener("input", (e) => { state.fileDec3DesK1 = e.target.value; });
      w.querySelector("#file-dec-k2").addEventListener("input", (e) => { state.fileDec3DesK2 = e.target.value; });
      w.querySelector("#file-dec-k3").addEventListener("input", (e) => { state.fileDec3DesK3 = e.target.value; });
      container.appendChild(w);
    } else if (activeAlgo === "rc4") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (RC4 key)</label>
      <input type="text" id="file-dec-key" placeholder="same key used for encryption" spellcheck="false" value="${state.fileDecRc4Key || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileDecRc4Key = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "xor") {
      const w = document.createElement("div");
      w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Secret Key (XOR key)</label>
      <input type="text" id="file-dec-key" placeholder="same key used for encryption" spellcheck="false" value="${state.fileDecXorKey || ""}">`;
      const inp = w.querySelector("input");
      inp.addEventListener("input", () => { state.fileDecXorKey = inp.value; });
      container.appendChild(w);
    } else if (activeAlgo === "hybrid") {
      const w = document.createElement("div");
      w.style.display = "flex";
      w.style.flexDirection = "column";
      w.style.gap = "10px";
      w.innerHTML = `
        <div>
          <label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Encrypted Session Key (decimal string from encrypt)</label>
          <textarea id="file-dec-session-key" rows="2" placeholder="paste encrypted session key" spellcheck="false">${state.fileDecSessionKey || ""}</textarea>
        </div>
        <div>
          <label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">RSA Private Exponent (d)</label>
          <textarea id="file-dec-d" rows="2" placeholder="paste RSA private exponent d" spellcheck="false">${state.fileDecD || ""}</textarea>
        </div>
        <div>
          <label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">RSA Modulus (n)</label>
          <textarea id="file-dec-n" rows="2" placeholder="paste RSA modulus n" spellcheck="false">${state.fileDecN || ""}</textarea>
        </div>
      `;
      w.querySelector("#file-dec-session-key").addEventListener("input", (e) => { state.fileDecSessionKey = e.target.value; });
      w.querySelector("#file-dec-d").addEventListener("input", (e) => { state.fileDecD = e.target.value; });
      w.querySelector("#file-dec-n").addEventListener("input", (e) => { state.fileDecN = e.target.value; });
      container.appendChild(w);
    }
  } else if (cat === "decode") {
    const info = document.createElement("div");
    info.style.fontSize = "12.5px";
    info.style.color = "var(--paper-dim)";
    info.textContent = `ℹ️ Reverses ${activeAlgo.toUpperCase()} encoding back to the original file bytes.`;
    container.appendChild(info);
  } else {
    // Hash Verify
    const w = document.createElement("div");
    w.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Expected ${activeAlgo.toUpperCase()} Checksum / Hash</label>
    <input type="text" id="file-expected-hash" placeholder="paste expected hash here" spellcheck="false" value="${state.fileExpectedHash || ""}">`;
    const inp = w.querySelector("input");
    inp.addEventListener("input", () => { state.fileExpectedHash = inp.value; });
    container.appendChild(w);
  }

  // Original Filename input (for decrypt & decode)
  if (cat !== "verify") {
    const origWrap = document.createElement("div");
    origWrap.innerHTML = `<label style="display:block;margin-bottom:6px;font-size:12.5px;color:var(--paper-dim)">Original Filename (to save as)</label>
    <input type="text" id="file-dec-orig-name" placeholder="notes.txt" spellcheck="false" value="${state.fileDecOrigName || ""}">`;
    origWrap.querySelector("input").addEventListener("input", (e) => { state.fileDecOrigName = e.target.value; });
    container.appendChild(origWrap);
  }

  // 5. Action Button & Status
  const actionRow = document.createElement("div");
  actionRow.style.display = "flex";
  actionRow.style.alignItems = "center";
  actionRow.style.gap = "14px";
  actionRow.style.flexWrap = "wrap";
  actionRow.style.marginTop = "6px";

  const runBtn = document.createElement("button");
  runBtn.type = "button";
  runBtn.className = "btn btn-primary";
  runBtn.textContent = cat === "verify" ? "Verify Checksum" : (cat === "decode" ? "Decode & Download" : "Decrypt & Download");

  const statusSpan = document.createElement("span");
  statusSpan.className = "tool-msg";

  actionRow.append(runBtn, statusSpan);
  container.appendChild(actionRow);

  // Run Handler
  runBtn.addEventListener("click", async () => {
    statusSpan.textContent = "";
    statusSpan.className = "tool-msg";

    const file = fileInput.files[0];
    if (!file) {
      statusSpan.textContent = "Choose a file first.";
      statusSpan.className = "tool-msg bad";
      return;
    }
    if (file.size > 1024 * 1024) {
      statusSpan.textContent = "File too large (max 1 MB).";
      statusSpan.className = "tool-msg bad";
      return;
    }

    const origNameInput = document.getElementById("file-dec-orig-name");
    const origName = (origNameInput ? origNameInput.value : "").trim() || "restored_file.txt";

    const formData = new FormData();
    formData.append("file", file);
    formData.append("action", cat);
    formData.append("algo", activeAlgo);
    formData.append("original_filename", origName);

    if (cat === "decrypt") {
      if (activeAlgo === "des") {
        const k = (state.fileDecDesKey || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "aes") {
        const k = (state.fileDecAesKey || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "3des") {
        const k1 = (state.fileDec3DesK1 || "").trim();
        const k2 = (state.fileDec3DesK2 || "").trim();
        const k3 = (state.fileDec3DesK3 || "").trim();
        if (!k1 || !k2) { statusSpan.textContent = "Fill in: Key 1 and Key 2"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key1", k1);
        formData.append("key2", k2);
        if (k3) formData.append("key3", k3);
      } else if (activeAlgo === "rc4") {
        const k = (state.fileDecRc4Key || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "xor") {
        const k = (state.fileDecXorKey || "").trim();
        if (!k) { statusSpan.textContent = "Fill in: Key"; statusSpan.className = "tool-msg bad"; return; }
        formData.append("key", k);
      } else if (activeAlgo === "hybrid") {
        const encKey = (state.fileDecSessionKey || "").trim();
        const d = (state.fileDecD || "").trim();
        const n = (state.fileDecN || "").trim();
        if (!encKey || !d || !n) {
          statusSpan.textContent = "Fill in: Encrypted session key, d, and n";
          statusSpan.className = "tool-msg bad";
          return;
        }
        formData.append("encrypted_key", encKey);
        formData.append("d", d);
        formData.append("n", n);
      }
    } else if (cat === "verify") {
      const exp = (state.fileExpectedHash || "").trim();
      if (!exp) {
        statusSpan.textContent = "Fill in: Expected checksum / hash";
        statusSpan.className = "tool-msg bad";
        return;
      }
      formData.append("expected_hash", exp);
    }

    runBtn.disabled = true;
    statusSpan.textContent = cat === "verify" ? "Verifying checksum…" : "Processing…";
    statusSpan.className = "tool-msg";

    try {
      const res = await T.file.transform(formData);
      if (cat === "verify") {
        if (res.match) {
          statusSpan.textContent = `✓ Checksum Match! The file matches the expected ${res.algo.toUpperCase()} hash.`;
          statusSpan.className = "tool-msg ok";
        } else {
          statusSpan.textContent = `✗ Checksum Mismatch! Actual file hash: ${res.actual_hash || "(different)"}`;
          statusSpan.className = "tool-msg bad";
        }
      } else {
        statusSpan.textContent = `✓ File restored and downloaded: ${res.filename || origName}`;
        statusSpan.className = "tool-msg ok";
      }
    } catch (err) {
      statusSpan.textContent = err.message || "Operation failed.";
      statusSpan.className = "tool-msg bad";
    } finally {
      runBtn.disabled = false;
    }
  });

  els.params.appendChild(container);
}

function renderParams(){
  const defs = currentParams();
  els.params.innerHTML = "";
  els.params.style.display = (defs.length || state.tool.custom === "rsa") ? "" : "none";
  defs.forEach(p => {
    const wrap = document.createElement("div"); wrap.className = "param";
    const lab = document.createElement("label"); lab.textContent = p.label; lab.htmlFor = "p-" + p.id;
    let inp;
    if (p.type === "select"){
      inp = document.createElement("select"); inp.id = "p-" + p.id;
      p.options.forEach(([v, l]) => { const o = document.createElement("option"); o.value = v; o.textContent = l; inp.appendChild(o); });
      inp.value = state.values[p.id] != null ? state.values[p.id] : p.options[0][0];
      state.values[p.id] = inp.value;
      inp.addEventListener("change", () => { state.values[p.id] = inp.value; });
    } else {
      inp = document.createElement(p.area ? "textarea" : "input");
      inp.id = "p-" + p.id; inp.placeholder = p.placeholder || ""; inp.spellcheck = false;
      if (!p.area) inp.type = p.type || "text";
      if (p.min != null) inp.min = p.min; if (p.max != null) inp.max = p.max;
      if (p.area) inp.rows = 2;
      // "persist" params (e.g. a Hashes.com API key) are remembered in this
      // browser between visits, so the person doesn't retype it every time.
      const owner = window.CryptoAPI.auth.getUser();
      const storageKey = p.persist && owner ? `yaoguai:tool:${owner.id}:${p.id}` : null;
      const stored = storageKey ? localStorage.getItem(storageKey) : null;
      inp.value = state.values[p.id] != null ? state.values[p.id] : (stored || p.value || "");
      if (stored != null) state.values[p.id] = stored;
      inp.addEventListener("input", () => {
        state.values[p.id] = inp.value;
        const currentOwner = window.CryptoAPI.auth.getUser();
        if (storageKey && currentOwner && currentOwner.id === owner.id)
          localStorage.setItem(storageKey, inp.value);
      });
    }
    wrap.append(lab, inp); els.params.appendChild(wrap);
  });
  if (state.tool.custom === "rsa"){
    const row = document.createElement("div"); row.className = "param param-full";
    const bits = document.createElement("select"); bits.id = "rsa-bits";
    [[128, "128-bit (instant)"], [256, "256-bit"], [512, "512-bit"], [1024, "1024-bit (slow)"]].forEach(([v, l]) => { const o = document.createElement("option"); o.value = v; o.textContent = l; if (v === 256) o.selected = true; bits.appendChild(o); });
    const b = document.createElement("button"); b.className = "btn btn-ghost btn-sm"; b.type = "button"; b.textContent = "Generate keys";
    b.addEventListener("click", async () => {
      b.disabled = true; setMsg("Generating keys…");
      try {
        const k = await T.encryption.rsaGenerateKeys(parseInt(bits.value, 10));
        ["n", "e", "d"].forEach(f => { state.values[f] = String(k[f]); const el = $("p-" + f); if (el) el.value = String(k[f]); });
        setMsg("Key pair generated.", "ok");
      } catch (err){ setMsg(err.message, "bad"); }
      b.disabled = false;
    });
    row.append(bits, b); els.params.appendChild(row);
  }
}

function renderModes(){
  els.modes.innerHTML = "";
  els.modes.style.display = state.tool.modes.length > 1 ? "" : "none";
  state.tool.modes.forEach((m, i) => {
    const b = document.createElement("button"); b.type = "button"; b.textContent = m.name;
    b.className = i === state.mode ? "on" : ""; b.setAttribute("role", "tab");
    b.addEventListener("click", () => { state.mode = i; renderModes(); renderParams(); renderMeta(); });
    els.modes.appendChild(b);
  });
}

function renderMeta(){
  const m = state.tool.modes[state.mode];
  els.endpoint.textContent = "POST " + m.endpoint;
  els.run.textContent = m.name === "Hash" ? "Hash" : (m.name === "Identify algorithm" ? "Identify" : m.name);
  $("input-label").textContent = (state.tool.id === "bcrypt" && m.name === "Verify") ? "Password"
    : (state.tool.id === "crack" && m.name === "Identify algorithm") ? "Hash to identify"
    : state.tool.id === "crack" ? "Hash to crack" : "Input";
  els.input.placeholder = (state.tool.id === "crack" && m.name === "Identify algorithm")
    ? "paste any unknown hash (e.g. 5f4dcc3b5aa765d61d8327deb882cf99 or $2y$10$…)"
    : state.tool.id === "crack" ? "paste a hash, e.g. 5f4dcc3b5aa765d61d8327deb882cf99" : "Type or paste text here…";
}

function selectTool(id){
  const t = byId(id) || byId("hex");
  state.tool = t; state.mode = 0; state.values = {};
  els.title.textContent = t.name; els.desc.textContent = t.desc;
  els.list.querySelectorAll("a").forEach(a => a.classList.toggle("current", a.dataset.id === t.id));
  els.output.value = ""; setMsg("");

  const isFileTool = t.id === "file-encrypt" || t.id === "file-decrypt";
  els.input.style.display = isFileTool ? "none" : "";
  const inLab = $("input-label");
  if (inLab) inLab.style.display = isFileTool ? "none" : "";
  const actions = document.querySelector(".tool-actions");
  if (actions) actions.style.display = isFileTool ? "none" : "";
  const outHead = document.querySelector(".out-head");
  if (outHead) outHead.style.display = isFileTool ? "none" : "";
  els.output.style.display = isFileTool ? "none" : "";

  if (t.id === "file-encrypt") {
    els.modes.style.display = "none";
    renderFileEncryptUI();
  } else if (t.id === "file-decrypt") {
    els.modes.style.display = "none";
    renderFileDecryptUI();
  } else {
    renderModes();
    renderParams();
    renderMeta();
  }
}

async function run(){
  if (!state.tool || state.tool.id === "file-encrypt" || state.tool.id === "file-decrypt") return;
  const t = state.tool, m = t.modes[state.mode];
  if (!m) return;
  const input = els.input.value;
  if (!input){ setMsg("Enter some input first.", "bad"); return; }
  const params = {};
  currentParams().forEach(p => { params[p.id] = (state.values[p.id] != null ? state.values[p.id] : (p.value || "")).toString(); });
  const missing = currentParams().filter(p => !p.optional && p.id !== "rounds" && !params[p.id].trim());
  if (missing.length){ setMsg("Fill in: " + missing.map(p => p.label).join(", "), "bad"); return; }
  els.run.disabled = true; setMsg("Working…");
  try {
    const res = await m.run(input, params);
    els.output.value = asText(res); setMsg("Done.", "ok");
  } catch (err){
    els.output.value = ""; setMsg(err.message || "Request failed.", "bad");
  }
  els.run.disabled = false;
}

async function checkApi(){
  const chip = $("api-status");
  try { await T.hashing.md5("ping"); chip.textContent = "API: online"; }
  catch (e){ chip.textContent = "API: offline"; }
}

buildList();
selectTool(location.hash.slice(1));
window.addEventListener("hashchange", () => selectTool(location.hash.slice(1)));
els.run.addEventListener("click", run);
els.input.addEventListener("keydown", (e) => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") run(); });
$("use-btn").addEventListener("click", () => { if (els.output.value){ els.input.value = els.output.value; els.output.value = ""; setMsg("Output moved to input."); } });
$("clear-btn").addEventListener("click", () => { els.input.value = ""; els.output.value = ""; setMsg(""); });
$("copy-btn").addEventListener("click", async () => {
  if (!els.output.value) return;
  try { await navigator.clipboard.writeText(els.output.value); setMsg("Copied.", "ok"); }
  catch (e){ els.output.select(); document.execCommand("copy"); setMsg("Copied.", "ok"); }
});
checkApi();

document.querySelectorAll(".continue-link[data-copy]").forEach(a => {
  a.addEventListener("click", async () => {
    const text = els.input.value;
    if (!text) return;
    try { await navigator.clipboard.writeText(text); } catch (e) { /* clipboard not available — link still opens */ }
  });
});
