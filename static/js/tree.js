/* ===========================
   CLOSE SIBLINGS
=========================== */
function closeSiblings(currentUl) {
    const parentLi = currentUl.parentNode;
    const parentUl = parentLi.parentNode;

    parentUl.querySelectorAll(":scope > li > ul").forEach(ul => {
        if (ul !== currentUl) ul.classList.add("hidden");
    });
}

/* ===========================
   CREATE NODE (HTML)
=========================== */
function createNode(item) {
    const li = document.createElement("li");

    if (item.is_dir) {
        li.innerHTML = `
            <div class="folder" data-path="${item.fullpath}">${item.name}</div>
            <ul class="hidden" id="node-${item.fullpath.replace(/\//g, '_')}"></ul>
        `;
    } else {
        li.innerHTML = `
            <div class="file"
                 data-file="/book/${item.fullpath}"
                 data-path="${item.fullpath}">
                📄 ${item.name}
            </div>
        `;
    }

    return li;
}

/* ===========================
   LAZY LOAD FOLDER
=========================== */
async function loadFolder(ul, path) {
    ul.innerHTML = `<li>Loading...</li>`; // temporary

    const res = await fetch(`/api/folder?path=${encodeURIComponent(path)}`);
    const items = await res.json();

    ul.innerHTML = "";
    items.forEach(item => {
        ul.appendChild(createNode(item));
    });

    attachHandlers(ul); // bind events to new nodes
}

/* ===========================
   ATTACH EVENT HANDLERS
=========================== */
function attachHandlers(rootElement) {

    /* ---- FOLDER CLICK ---- */
    rootElement.querySelectorAll(".folder").forEach(folder => {
        folder.onclick = async () => {

            const path = folder.dataset.path;
            const ul = folder.parentNode.querySelector("ul");

            if (!ul) return;

            const wasHidden = ul.classList.contains("hidden");

            closeSiblings(ul);

            // lazy-load only when first open
            if (ul.dataset.loaded !== "true") {
                await loadFolder(ul, path);
                ul.dataset.loaded = "true";
            }

            ul.classList.toggle("hidden", !wasHidden);
        };
    });

    /* ---- FILE CLICK ---- */
    rootElement.querySelectorAll(".file").forEach(file => {
        file.onclick = () => {
            const iframe = document.getElementById("viewer");
            const src = "/book/" + file.dataset.path;
            iframe.src = src;

            document.querySelectorAll(".file").forEach(f => f.classList.remove("active"));
            file.classList.add("active");

            document.getElementById("breadcrumbs").textContent = file.dataset.path;

            iframe.onload = () => {
                const doc = iframe.contentDocument;
                if (!doc) return;

                // Remove restrictive CSP
                doc.querySelectorAll('meta[http-equiv="Content-Security-Policy"]').forEach(el => el.remove());

                // Fix video relative paths
                doc.querySelectorAll("video source").forEach(src => {
                    let url = src.getAttribute("src");
                    if (!url.startsWith("/book/")) {
                        const base = "/book/" + file.dataset.path.replace(/[^\/]+$/, "");
                        src.setAttribute("src", base + url);
                    }
                });

                doc.body.classList.add("book-page");
                applyThemeToIframe();
                applyFontScale(doc);
            };
        };
    });
}

/* ===========================
   APPLY THEME TO IFRAME
=========================== */
function applyThemeToIframe() {
    const iframe = document.getElementById("viewer");
    const doc = iframe.contentDocument;

    if (!doc) return;

    let oldStyle = doc.getElementById("dark-style");
    if (oldStyle) oldStyle.remove();

    const style = doc.createElement("style");
    style.id = "dark-style";

    if (document.body.classList.contains("theme-dark")) {
        style.textContent = `
            body {
                background: #1a1a1a !important;
                color: #e0e0e0 !important;
            }
            * {
                color: #e0e0e0 !important;
                background: transparent !important;
            }
            img {
                max-width: 100%;
                height: auto;
            }
        `;
    } else {
        style.textContent = `
            body {
                background: white !important;
                color: black !important;
            }
            * {
                color: black !important;
                background: transparent !important;
            }
        `;
    }

    doc.head.appendChild(style);
}

/* ===========================
   FONT CONTROL
=========================== */
let fontScale = 1.0;

document.getElementById("font-inc").addEventListener("click", () => {
    fontScale += 0.1;
    applyFontScale();
});

document.getElementById("font-dec").addEventListener("click", () => {
    fontScale = Math.max(0.6, fontScale - 0.1);
    applyFontScale();
});
/* ===========================
   CHANGE FONT SIZE
=========================== */
function applyFontScale(docOverride = null) {
    const iframe = document.getElementById("viewer");
    const doc = docOverride || iframe.contentDocument;

    if (!doc) return;

    doc.body.style.fontSize = (18 * fontScale) + "px";
}

/* ===========================
   THEME COLOR
=========================== */
function attachGlobalControls() {
    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        themeToggle.onclick = () => {
            const body = document.body;

            if (body.classList.contains("theme-dark")) {
                body.classList.remove("theme-dark");
                body.classList.add("theme-light");
                themeToggle.textContent = "🌙";
            } else {
                body.classList.remove("theme-light");
                body.classList.add("theme-dark");
                themeToggle.textContent = "☀️";
            }
            applyThemeToIframe();
        };
    }

    const inc = document.getElementById("font-inc");
    const dec = document.getElementById("font-dec");

    if (inc) inc.onclick = () => {
        fontScale += 0.1;
        applyFontScale();
    };

    if (dec) dec.onclick = () => {
        fontScale = Math.max(0.6, fontScale - 0.1);
        applyFontScale();
    };
}

document.addEventListener("DOMContentLoaded", () => {
    attachHandlers(document);
    attachGlobalControls();
});
