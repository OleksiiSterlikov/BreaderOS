console.log("TREE.JS LOADED", Date.now());

/* ======================================================
   УТИЛІТИ
====================================================== */

// закривати всі інші папки на цьому рівні
function closeSiblings(currentUl) {
    const parentLi = currentUl.parentNode;
    if (!parentLi) return;

    const parentUl = parentLi.parentNode;
    if (!parentUl) return;

    parentUl.querySelectorAll(":scope > li > ul").forEach(ul => {
        if (ul !== currentUl) ul.classList.add("hidden");
    });
}

/* ======================================================
   HTML генерація
====================================================== */

function createNode(item) {
    const li = document.createElement("li");

    if (item.is_dir) {
        li.innerHTML = `
            <div class="folder" data-path="${item.fullpath}">
                📁 ${item.name}
            </div>
            <ul class="hidden" id="node-${item.fullpath.replace(/\//g, "_")}"></ul>
        `;
    } else {
        li.innerHTML = `
            <div class="file" data-path="${item.fullpath}">
                📄 ${item.name}
            </div>
        `;
    }

    return li;
}

/* ======================================================
   LAZY LOAD
====================================================== */

async function loadFolder(ul, path) {
    ul.innerHTML = `<li>Loading...</li>`;

    const res = await fetch(`/api/folder?path=${encodeURIComponent(path)}`);
    const items = await res.json();

    ul.innerHTML = "";
    items.forEach(item => ul.appendChild(createNode(item)));

    attachHandlers(ul); // підключаємо події до нових елементів
}

/* ======================================================
   ПІДКЛЮЧЕННЯ ОБРОБНИКІВ
====================================================== */

function attachHandlers(root) {

    /* ---------- КЛІК ПО ПАПЦІ ---------- */
    root.querySelectorAll(".folder").forEach(folder => {
        folder.onclick = async () => {
            const path = folder.dataset.path;
            const ul = folder.parentNode.querySelector("ul");

            const wasHidden = ul.classList.contains("hidden");

            closeSiblings(ul);

            // lazy-load (один раз)
            if (!ul.dataset.loaded) {
                await loadFolder(ul, path);
                ul.dataset.loaded = "true";
            }

            ul.classList.toggle("hidden", !wasHidden);
        };
    });

    /* ---------- КЛІК ПО ФАЙЛУ ---------- */
    root.querySelectorAll(".file").forEach(file => {
        file.onclick = () => openFile(file.dataset.path);
    });
}

/* ======================================================
   ВІДКРИТТЯ ФАЙЛУ В IFRAME
====================================================== */

function openFile(path) {
    const iframe = document.getElementById("viewer");
    iframe.src = "/book/" + path;

    // breadcrumbs
    document.getElementById("breadcrumbs").textContent = path;

    iframe.onload = () => {
        const doc = iframe.contentDocument;
        if (!doc) return;

        // тема
        applyThemeToIframe();

        // шрифт
        applyFontScale(doc);

        // навігація кнопками
        insertPageNavigation(doc, path);
    };
}

/* ======================================================
   КНОПКИ НАВІГАЦІЇ (← →)
====================================================== */

function insertPageNavigation(doc, currentPath) {
    if (!window.BookPages) return;

    const idx = window.BookPages.indexOf(currentPath);

    const nav = doc.createElement("div");
    nav.style.cssText = `
        width: 100%;
        display: flex;
        justify-content: space-between;
        margin-top: 40px;
        padding: 20px 0;
        border-top: 1px solid #888;
        font-size: 20px;
    `;

    const prevBtn = doc.createElement("button");
    prevBtn.textContent = "⬅ Попередня";

    const nextBtn = doc.createElement("button");
    nextBtn.textContent = "Наступна ➡";

    nav.append(prevBtn, nextBtn);
    doc.body.appendChild(nav);

    // previous
    if (idx > 0) {
        prevBtn.onclick = () => openFile(window.BookPages[idx - 1]);
    } else {
        prevBtn.disabled = true;
    }

    // next
    if (idx < window.BookPages.length - 1) {
        nextBtn.onclick = () => openFile(window.BookPages[idx + 1]);
    } else {
        nextBtn.disabled = true;
    }
}

/* ======================================================
   ТЕМИ
====================================================== */
function applyThemeToIframe() {
    const iframe = document.getElementById("viewer");
    const doc = iframe.contentDocument;
    if (!doc) return;

    const old = doc.getElementById("dark-style");
    if (old) old.remove();

    const style = doc.createElement("style");
    style.id = "dark-style";

    if (document.body.classList.contains("theme-dark")) {
        style.textContent = `
            body { background:#1a1a1a !important; color:#e0e0e0 !important; }
            * { color:#e0e0e0 !important; background:transparent !important; }
        `;
    } else {
        style.textContent = `
            body { background:white !important; color:black !important; }
            * { color:black !important; background:transparent !important; }
        `;
    }

    doc.head.appendChild(style);
}

/* ======================================================
   МАСШТАБ ШРИФТУ
====================================================== */

let fontScale = 1.0;

function applyFontScale(docOverride = null) {
    const iframe = document.getElementById("viewer");
    const doc = docOverride || iframe.contentDocument;
    if (!doc) return;

    doc.body.style.fontSize = (18 * fontScale) + "px";
}

function attachGlobalControls() {
    document.getElementById("font-inc").onclick = () => {
        fontScale += 0.1;
        applyFontScale();
    };

    document.getElementById("font-dec").onclick = () => {
        fontScale = Math.max(0.6, fontScale - 0.1);
        applyFontScale();
    };

    document.getElementById("theme-toggle").onclick = () => {
        const body = document.body;
        const btn = document.getElementById("theme-toggle");

        if (body.classList.contains("theme-dark")) {
            body.classList.replace("theme-dark", "theme-light");
            btn.textContent = "🌙";
        } else {
            body.classList.replace("theme-light", "theme-dark");
            btn.textContent = "☀️";
        }
        applyThemeToIframe();
    };
}

/* ======================================================
   ІНІЦІАЛІЗАЦІЯ
====================================================== */

document.addEventListener("DOMContentLoaded", () => {
    attachGlobalControls();
    attachHandlers(document); // підключаємо обробники до вже існуючих вузлів
});
