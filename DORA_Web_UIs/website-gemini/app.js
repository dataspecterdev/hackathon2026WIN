(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const messagesEl = $("messages");
  const composerEl = $("composer");
  const inputEl = $("composer-input");
  const sendBtn = $("composer-send");
  const healthDot = $("health-dot");
  const newChatBtn = $("new-chat");
  const chatListEl = $("chat-list");
  const chatTitleEl = $("chat-title");
  const modelPill = $("model-pill");
  const sidebarEl = $("sidebar");
  const backdropEl = $("backdrop");
  const menuBtn = $("menu-btn");

  const uploadForm = $("upload-form");
  const uploadPackageIdInput = $("upload-package-id");
  const uploadFilesInput = $("upload-files");
  const uploadDrop = $("upload-drop");
  const uploadDropText = $("upload-drop-text");
  const uploadSubmitBtn = $("upload-submit");
  const uploadStatusEl = $("upload-status");

  let busy = false;
  let knownPackages = [];
  let lastUploadedPackage = null;

  // ------------------------------------------------------------- storage --

  const STORE_KEY = "dora_chats_v1";
  const ACTIVE_KEY = "dora_active_chat_v1";
  const MAX_CHATS = 30;

  function loadStore() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORE_KEY));
      if (raw && Array.isArray(raw.order) && raw.chats) return raw;
    } catch {
      /* corrupted store — start fresh */
    }
    return { order: [], chats: {} };
  }

  let store = loadStore();
  let activeId = localStorage.getItem(ACTIVE_KEY);

  function saveStore() {
    // Oldest chats fall off so localStorage can't grow without bound.
    while (store.order.length > MAX_CHATS) {
      const dropped = store.order.pop();
      delete store.chats[dropped];
    }
    localStorage.setItem(STORE_KEY, JSON.stringify(store));
    localStorage.setItem(ACTIVE_KEY, activeId || "");
  }

  function createChat() {
    const chat = {
      id: crypto.randomUUID(),
      title: null,
      createdAt: Date.now(),
      messages: [],
    };
    store.chats[chat.id] = chat;
    store.order.unshift(chat.id);
    activeId = chat.id;
    saveStore();
    return chat;
  }

  function activeChat() {
    if (!activeId || !store.chats[activeId]) {
      if (store.order.length > 0) {
        activeId = store.order[0];
      } else {
        return createChat();
      }
    }
    return store.chats[activeId];
  }

  function removeChat(id) {
    delete store.chats[id];
    store.order = store.order.filter((c) => c !== id);
    if (activeId === id) activeId = store.order[0] || null;
    if (!activeId) createChat();
    saveStore();
    renderChatList();
    renderMessages();
  }

  // -------------------------------------------------- markdown rendering --

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function inline(s) {
    return escapeHtml(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }

  const BADGES = {
    FLAG: "badge-flag",
    NO_FLAG: "badge-ok",
    Critical: "badge-critical",
    High: "badge-high",
    Medium: "badge-medium",
    Low: "badge-low",
    Info: "badge-info",
  };

  function cellHtml(text) {
    if (Object.prototype.hasOwnProperty.call(BADGES, text)) {
      return `<span class="badge ${BADGES[text]}">${escapeHtml(text.replace("_", " "))}</span>`;
    }
    return inline(text);
  }

  function isTableBlock(lines) {
    if (lines.length < 2) return false;
    if (!lines[0].includes("|")) return false;
    return /^\s*\|?[\s:-]+\|[\s:|-]+$/.test(lines[1]);
  }

  function renderTable(lines) {
    const split = (row) =>
      row.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
    const header = split(lines[0]);
    const bodyRows = lines.slice(2).map(split);
    let html = "<div class='table-scroll'><table><thead><tr>";
    header.forEach((h) => (html += `<th>${inline(h)}</th>`));
    html += "</tr></thead><tbody>";
    bodyRows.forEach((row, i) => {
      html += `<tr style="--i:${i}">`;
      row.forEach((c) => (html += `<td>${cellHtml(c)}</td>`));
      html += "</tr>";
    });
    html += "</tbody></table></div>";
    return html;
  }

  function renderMarkdownish(text) {
    const blocks = text.split(/\n{2,}/);
    return blocks
      .map((block) => {
        const lines = block.split("\n").filter((l) => l.length > 0);
        if (lines.length === 0) return "";
        if (isTableBlock(lines)) return renderTable(lines);
        if (lines[0].startsWith("### ")) {
          const rest = lines.slice(1);
          const restHtml = rest.length ? `<p>${rest.map(inline).join("<br>")}</p>` : "";
          return `<h3>${inline(lines[0].slice(4))}</h3>${restHtml}`;
        }
        const firstBullet = lines.findIndex((l) => l.startsWith("- "));
        if (firstBullet !== -1 && lines.slice(firstBullet).every((l) => l.startsWith("- "))) {
          const intro = lines.slice(0, firstBullet);
          const items = lines.slice(firstBullet);
          const introHtml = intro.length ? `<p>${intro.map(inline).join("<br>")}</p>` : "";
          return (
            introHtml +
            "<ul>" +
            items.map((l) => `<li>${inline(l.slice(2))}</li>`).join("") +
            "</ul>"
          );
        }
        return `<p>${inline(block).replace(/\n/g, "<br>")}</p>`;
      })
      .join("");
  }

  // ------------------------------------------------------- dom rendering --

  function fmtTime(ts) {
    return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function fmtDay(ts) {
    const d = new Date(ts);
    const today = new Date();
    if (d.toDateString() === today.toDateString()) return "Today";
    today.setDate(today.getDate() - 1);
    if (d.toDateString() === today.toDateString()) return "Yesterday";
    return d.toLocaleDateString([], { month: "short", day: "numeric" });
  }

  function msgNode(m, animate) {
    const wrap = document.createElement("div");
    wrap.className = `msg msg-${m.role}${m.error ? " msg-error" : ""}${animate ? " msg-enter" : ""}`;

    const roleEl = document.createElement("div");
    roleEl.className = "msg-role";
    roleEl.textContent =
      (m.role === "user" ? "You" : "DORA") + (m.ts ? ` · ${fmtTime(m.ts)}` : "");
    wrap.appendChild(roleEl);

    const bodyEl = document.createElement("div");
    bodyEl.className = "msg-body";
    if (m.role === "assistant" && !m.error) {
      bodyEl.innerHTML = renderMarkdownish(m.text);
    } else {
      bodyEl.textContent = m.text;
    }
    wrap.appendChild(bodyEl);

    if (m.csvUrl) {
      const bar = document.createElement("div");
      bar.className = "msg-actions";
      const link = document.createElement("a");
      link.className = "btn-download";
      link.href = m.csvUrl;
      link.textContent = "Download CSV — submission schema (15 fields)";
      bar.appendChild(link);
      wrap.appendChild(bar);
    }

    if (m.suggestions && m.suggestions.length > 0) {
      const bar = document.createElement("div");
      bar.className = "suggestions";
      m.suggestions.forEach((s, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "chip chip-suggest";
        b.style.setProperty("--i", i);
        b.textContent = s;
        b.addEventListener("click", () => {
          inputEl.value = s;
          autosize();
          inputEl.focus();
        });
        bar.appendChild(b);
      });
      wrap.appendChild(bar);
    }

    if (m.trace && m.trace.length > 0) {
      const details = document.createElement("details");
      details.className = "trace";
      const summary = document.createElement("summary");
      summary.textContent = `${m.trace.length} rule verdict${m.trace.length === 1 ? "" : "s"} — audit trail`;
      details.appendChild(summary);
      const list = document.createElement("div");
      list.className = "trace-list";
      m.trace.forEach((t) => {
        const item = document.createElement("div");
        item.className = "trace-item";
        const toolEl = document.createElement("div");
        toolEl.className = "trace-tool";
        toolEl.textContent = t.tool;
        const io = document.createElement("pre");
        io.className = "trace-io";
        io.textContent = t.input
          ? `input:  ${JSON.stringify(t.input)}\noutput: ${JSON.stringify(t.output)}`
          : JSON.stringify(t.output, null, 1);
        item.appendChild(toolEl);
        item.appendChild(io);
        list.appendChild(item);
      });
      details.appendChild(list);
      wrap.appendChild(details);
    }

    return wrap;
  }

  function typingNode() {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-assistant msg-enter";
    const roleEl = document.createElement("div");
    roleEl.className = "msg-role";
    roleEl.textContent = "DORA";
    wrap.appendChild(roleEl);
    const bodyEl = document.createElement("div");
    bodyEl.className = "msg-body typing";
    for (let i = 0; i < 3; i++) {
      const d = document.createElement("span");
      d.className = "typing-dot";
      bodyEl.appendChild(d);
    }
    wrap.appendChild(bodyEl);
    return wrap;
  }

  function heroNode() {
    const hero = document.createElement("div");
    hero.className = "hero msg-enter";

    const logo = document.createElement("img");
    logo.src = "/deldot-logo.webp";
    logo.alt = "";
    logo.className = "hero-logo";
    hero.appendChild(logo);

    const h = document.createElement("h2");
    h.textContent = "Review a contract package";
    hero.appendChild(h);

    const p = document.createElement("p");
    p.className = "hero-sub";
    p.textContent =
      "Gemini reviews with live function calls into the local review server — uploaded packages included, evidence verified verbatim.";
    hero.appendChild(p);

    if (knownPackages.length > 0) {
      const label = document.createElement("div");
      label.className = "hero-label";
      label.textContent = "Start with a package";
      hero.appendChild(label);

      const chips = document.createElement("div");
      chips.className = "hero-chips";
      knownPackages.forEach((pid, i) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.style.setProperty("--i", i);
        chip.textContent = pid;
        chip.addEventListener("click", () => {
          inputEl.value = `Review ${pid} against all 18 CC criteria.`;
          autosize();
          inputEl.focus();
        });
        chips.appendChild(chip);
      });
      hero.appendChild(chips);
    }

    const label2 = document.createElement("div");
    label2.className = "hero-label";
    label2.textContent = "Sample questions";
    hero.appendChild(label2);

    const examples = document.createElement("div");
    examples.className = "hero-chips";
    SAMPLE_QUESTIONS.forEach((tpl, i) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip chip-soft";
      chip.style.setProperty("--i", i);
      chip.textContent = tpl.replace("{pkg}", "…");
      chip.addEventListener("click", () => {
        const pkg = tpl.includes("development labels")
          ? currentDevPackageGuess()
          : currentPackageGuess();
        inputEl.value = tpl.replace("{pkg}", pkg);
        autosize();
        inputEl.focus();
      });
      examples.appendChild(chip);
    });
    hero.appendChild(examples);

    return hero;
  }

  const SAMPLE_QUESTIONS = [
    "Review {pkg} against all 18 CC criteria.",
    "Review {pkg} against CC-04 (Performance and payment bonds).",
    "Review {pkg} against CC-09 (Buy America / BABA applicability).",
    "Which addenda apply to {pkg}, and did any supersede a base clause?",
    "What packages are loaded right now?",
  ];

  function sampleQuestionsFor(pkg) {
    return [
      `Review ${pkg} against all 18 CC criteria.`,
      `Review ${pkg} against CC-04 (Performance and payment bonds).`,
      `Check CC-09 (Buy America / BABA) applicability for ${pkg}.`,
      `Which addenda apply to ${pkg}, and did any supersede a base clause?`,
    ];
  }

  function currentDevPackageGuess() {
    // Scoring only works where labels exist, so prefer a DEV-* package.
    const guess = currentPackageGuess();
    if (guess.startsWith("DEV-")) return guess;
    return knownPackages.find((p) => p.startsWith("DEV-")) || guess;
  }

  function currentPackageGuess() {
    // Latest package mentioned in this chat, else the last upload, else the first known.
    const chat = activeChat();
    for (let i = chat.messages.length - 1; i >= 0; i--) {
      const text = chat.messages[i].text.toUpperCase();
      const hit = knownPackages.find((p) => text.includes(p));
      if (hit) return hit;
    }
    return lastUploadedPackage || knownPackages[0] || "<PACKAGE_ID>";
  }

  function renderMessages() {
    const chat = activeChat();
    messagesEl.innerHTML = "";
    if (chat.messages.length === 0) {
      messagesEl.appendChild(heroNode());
    } else {
      chat.messages.forEach((m) => messagesEl.appendChild(msgNode(m, false)));
    }
    chatTitleEl.textContent = chat.title || "New review";
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderChatList() {
    chatListEl.innerHTML = "";
    if (store.order.length === 0) {
      const empty = document.createElement("p");
      empty.className = "chat-list-empty";
      empty.textContent = "No reviews yet.";
      chatListEl.appendChild(empty);
      return;
    }
    store.order.forEach((id) => {
      const chat = store.chats[id];
      if (!chat) return;
      const item = document.createElement("div");
      item.className = `chat-item${id === activeId ? " active" : ""}`;
      item.setAttribute("role", "button");
      item.tabIndex = 0;

      const main = document.createElement("div");
      main.className = "chat-item-main";
      const title = document.createElement("div");
      title.className = "chat-item-title";
      title.textContent = chat.title || "New review";
      const meta = document.createElement("div");
      meta.className = "chat-item-meta";
      meta.textContent = `${fmtDay(chat.createdAt)} · ${chat.messages.length} message${chat.messages.length === 1 ? "" : "s"}`;
      main.appendChild(title);
      main.appendChild(meta);
      item.appendChild(main);

      const del = document.createElement("button");
      del.className = "chat-item-del";
      del.type = "button";
      del.setAttribute("aria-label", "Delete chat");
      del.textContent = "×";
      del.addEventListener("click", (e) => {
        e.stopPropagation();
        removeChat(id);
      });
      item.appendChild(del);

      const open = () => {
        activeId = id;
        saveStore();
        renderChatList();
        renderMessages();
        closeSidebar();
      };
      item.addEventListener("click", open);
      item.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          open();
        }
      });
      chatListEl.appendChild(item);
    });
  }

  function pushMessage(m) {
    const chat = activeChat();
    const hadNone = chat.messages.length === 0;
    chat.messages.push(m);
    if (!chat.title && m.role === "user") {
      chat.title = m.text.length > 42 ? m.text.slice(0, 42) + "…" : m.text;
      chatTitleEl.textContent = chat.title;
    }
    saveStore();
    if (hadNone) messagesEl.innerHTML = "";
    const node = msgNode(m, true);
    messagesEl.appendChild(node);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    renderChatList();
    return node;
  }

  // ------------------------------------------------------------ api calls --

  async function loadHealth() {
    try {
      const resp = await fetch("/api/health");
      const data = await resp.json();
      healthDot.classList.remove("ok", "bad");
      healthDot.classList.add(data.model_key_configured ? "ok" : "bad");
      healthDot.title = data.model_key_configured
        ? `Connected — ${data.backend} backend`
        : data.backend === "ces"
          ? "No Google Cloud credentials on the server"
          : "GOOGLE_API_KEY is not set on the server";
      if (data.model) {
        modelPill.hidden = false;
        modelPill.textContent =
          data.backend === "rules" ? "deterministic rules" : data.model;
        modelPill.title = data.model;
      }
    } catch {
      healthDot.classList.add("bad");
      healthDot.title = "Server unreachable";
    }
  }

  async function loadPackages() {
    try {
      const resp = await fetch("/api/packages");
      const data = await resp.json();
      knownPackages = data.packages || [];
      if (activeChat().messages.length === 0) renderMessages();
    } catch {
      knownPackages = [];
    }
  }

  async function sendMessage(text) {
    busy = true;
    sendBtn.disabled = true;

    pushMessage({ role: "user", text, ts: Date.now() });
    const typing = typingNode();
    messagesEl.appendChild(typing);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: activeChat().id, message: text }),
      });
      const data = await resp.json();
      typing.remove();

      if (!resp.ok) {
        pushMessage({
          role: "assistant",
          text: data.detail || "Request failed.",
          error: true,
          ts: Date.now(),
        });
        return;
      }

      pushMessage({
        role: "assistant",
        text: data.reply || "(empty response)",
        csvUrl: data.csv_url || null,
        trace: data.trace || [],
        ts: Date.now(),
      });
    } catch (err) {
      typing.remove();
      pushMessage({
        role: "assistant",
        text: `Network error: ${err}`,
        error: true,
        ts: Date.now(),
      });
    } finally {
      busy = false;
      sendBtn.disabled = false;
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }
  }

  // -------------------------------------------------------------- upload --

  function setUploadStatus(text, kind) {
    uploadStatusEl.hidden = !text;
    uploadStatusEl.textContent = text;
    uploadStatusEl.className = `upload-status${kind ? ` ${kind}` : ""}`;
  }

  function describeSelectedFiles(fileList) {
    if (!fileList || fileList.length === 0) {
      uploadDropText.textContent = "Choose package folder…";
      uploadSubmitBtn.disabled = true;
      return;
    }
    const files = Array.from(fileList);
    const pdfCount = files.filter((f) => f.name.toLowerCase().endsWith(".pdf")).length;
    const hasMetadata = files.some((f) => f.name === "Project_Metadata.json");
    const folderName = files[0].webkitRelativePath
      ? files[0].webkitRelativePath.split("/")[0]
      : null;

    const label = folderName || (files.length === 1 ? files[0].name : `${files.length} files`);
    uploadDropText.textContent = hasMetadata
      ? `${label} — ${pdfCount} PDF${pdfCount === 1 ? "" : "s"}`
      : `${label} — ⚠ no Project_Metadata.json found`;

    if (folderName && !uploadPackageIdInput.value.trim()) {
      uploadPackageIdInput.value = folderName.replace(/[^A-Za-z0-9_-]/g, "-").slice(0, 64);
    }
    uploadSubmitBtn.disabled = false;
  }

  uploadFilesInput.addEventListener("change", () => {
    describeSelectedFiles(uploadFilesInput.files);
  });

  ["dragover", "dragenter"].forEach((evt) =>
    uploadDrop.addEventListener(evt, (e) => {
      e.preventDefault();
      uploadDrop.classList.add("dragover");
    })
  );
  ["dragleave", "dragend"].forEach((evt) =>
    uploadDrop.addEventListener(evt, () => uploadDrop.classList.remove("dragover"))
  );
  uploadDrop.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadDrop.classList.remove("dragover");
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadFilesInput.files = e.dataTransfer.files;
      describeSelectedFiles(uploadFilesInput.files);
    }
  });

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileList = uploadFilesInput.files;
    if (!fileList || fileList.length === 0) return;

    uploadSubmitBtn.disabled = true;
    setUploadStatus("Uploading and parsing…", "busy");

    const form = new FormData();
    form.append("package_id", uploadPackageIdInput.value.trim());
    Array.from(fileList).forEach((f) => form.append("files", f));

    try {
      const resp = await fetch("/api/packages/upload", { method: "POST", body: form });
      const data = await resp.json();

      if (!resp.ok) {
        setUploadStatus(data.detail || "Upload failed.", "bad");
        uploadSubmitBtn.disabled = false;
        return;
      }

      setUploadStatus(
        `Loaded ${data.package_id} — ${data.documents.length} document(s), ${data.clauses_extracted} clause(s).`,
        "ok"
      );
      uploadForm.reset();
      describeSelectedFiles(null);
      lastUploadedPackage = data.package_id;
      await loadPackages();
      pushMessage({
        role: "assistant",
        text:
          `Uploaded and parsed **${data.package_id}** (${data.project_title}): ` +
          `${data.documents.length} document(s), ${data.clauses_extracted} clause(s) resolved ` +
          `to checklist headings. Here are some questions you can ask about it:`,
        suggestions: sampleQuestionsFor(data.package_id),
        ts: Date.now(),
      });
    } catch (err) {
      setUploadStatus(`Network error: ${err}`, "bad");
      uploadSubmitBtn.disabled = false;
    }
  });

  // -------------------------------------------------------------- events --

  function autosize() {
    inputEl.style.height = "auto";
    inputEl.style.height = `${Math.min(inputEl.scrollHeight, 160)}px`;
  }

  composerEl.addEventListener("submit", (e) => {
    e.preventDefault();
    if (busy) return;
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    autosize();
    sendMessage(text);
  });

  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      composerEl.requestSubmit();
    }
  });
  inputEl.addEventListener("input", autosize);

  newChatBtn.addEventListener("click", () => {
    if (busy) return;
    // Reuse the current chat if it's still empty rather than stacking blanks.
    if (activeChat().messages.length === 0) {
      renderMessages();
      closeSidebar();
      return;
    }
    createChat();
    renderChatList();
    renderMessages();
    closeSidebar();
    inputEl.focus();
  });

  function closeSidebar() {
    sidebarEl.classList.remove("open");
    backdropEl.classList.remove("show");
  }

  menuBtn.addEventListener("click", () => {
    sidebarEl.classList.toggle("open");
    backdropEl.classList.toggle("show", sidebarEl.classList.contains("open"));
  });
  backdropEl.addEventListener("click", closeSidebar);

  // ---------------------------------------------------------------- boot --

  renderChatList();
  renderMessages();
  loadHealth();
  loadPackages();
})();
