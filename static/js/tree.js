let fontScale = 1.0;
let activeFileElement = null;
let currentTheme = "light";

function findFileElementByPath(path) {
    return document.querySelector(`.file[data-path="${CSS.escape(path)}"]`);
}

function closeSiblings(currentUl) {
    const parentLi = currentUl.parentNode;
    if (!parentLi) {
        return;
    }

    const parentUl = parentLi.parentNode;
    if (!parentUl) {
        return;
    }

    parentUl.querySelectorAll(":scope > li > ul").forEach((ul) => {
        if (ul !== currentUl) {
            ul.classList.add("hidden");
            const folderButton = ul.parentNode.querySelector(":scope > .folder");
            if (folderButton) {
                folderButton.classList.remove("is-open");
                updateFolderIcon(folderButton, false);
            }
        }
    });
}

function escapeHtml(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function createNode(item) {
    const li = document.createElement("li");
    li.className = "tree-node";

    if (item.is_dir) {
        li.innerHTML = `
            <button class="tree-item folder" type="button" data-path="${escapeHtml(item.fullpath)}">
                <span class="tree-icon" aria-hidden="true">▸</span>
                <span class="tree-label">${escapeHtml(item.name)}</span>
            </button>
            <ul class="hidden"></ul>
        `;
    } else {
        li.innerHTML = `
            <button class="tree-item file" type="button" data-path="${escapeHtml(item.fullpath)}">
                <span class="tree-icon" aria-hidden="true">•</span>
                <span class="tree-label">${escapeHtml(item.name)}</span>
            </button>
        `;
    }

    return li;
}

function updateFolderIcon(folderButton, isOpen) {
    const icon = folderButton.querySelector(".tree-icon");
    if (!icon) {
        return;
    }
    icon.textContent = isOpen ? "▾" : "▸";
}

function setViewerEmptyState(isVisible) {
    const emptyState = document.getElementById("viewer-empty");
    if (!emptyState) {
        return;
    }
    emptyState.classList.toggle("hidden", !isVisible);
}

function setBreadcrumbs(text) {
    const breadcrumbs = document.getElementById("breadcrumbs");
    if (breadcrumbs) {
        breadcrumbs.textContent = text;
    }
}

async function loadFolder(ul, path) {
    ul.innerHTML = `<li class="tree-loading">Loading...</li>`;

    try {
        const res = await fetch(`/api/folder?path=${encodeURIComponent(path)}`);
        if (!res.ok) {
            throw new Error("Folder request failed");
        }

        const items = await res.json();
        ul.innerHTML = "";

        if (!items.length) {
            ul.innerHTML = `<li class="tree-empty">Папка порожня</li>`;
            return;
        }

        items.forEach((item) => ul.appendChild(createNode(item)));
        attachHandlers(ul);
    } catch (_error) {
        ul.innerHTML = `<li class="tree-empty">Не вдалося завантажити вміст папки</li>`;
    }
}

function markActiveFile(fileElement) {
    if (activeFileElement && activeFileElement !== fileElement) {
        activeFileElement.classList.remove("is-active");
    }

    activeFileElement = fileElement;
    if (activeFileElement) {
        activeFileElement.classList.add("is-active");
    }
}

function attachHandlers(root) {
    root.querySelectorAll(".folder").forEach((folder) => {
        if (folder.dataset.bound === "true") {
            return;
        }

        folder.dataset.bound = "true";
        folder.onclick = async () => {
            const ul = folder.parentNode.querySelector("ul");
            if (!ul) {
                return;
            }

            const wasHidden = ul.classList.contains("hidden");
            closeSiblings(ul);

            if (!ul.dataset.loaded) {
                await loadFolder(ul, folder.dataset.path);
                ul.dataset.loaded = "true";
            }

            ul.classList.toggle("hidden", !wasHidden);
            folder.classList.toggle("is-open", wasHidden);
            updateFolderIcon(folder, wasHidden);
        };
    });

    root.querySelectorAll(".file").forEach((file) => {
        if (file.dataset.bound === "true") {
            return;
        }

        file.dataset.bound = "true";
        file.onclick = () => {
            markActiveFile(file);
            openFile(file.dataset.path);
            closeSidebarOnMobile();
        };
    });
}

function buildBookUrl(path) {
    const encodedPath = path
        .split("/")
        .map((part) => encodeURIComponent(part))
        .join("/");
    return "/book/" + encodedPath;
}

function applyThemeToIframe() {
    const iframe = document.getElementById("viewer");
    const doc = iframe.contentDocument;
    if (!doc || !doc.head || !doc.body) {
        return;
    }

    const oldStyle = doc.getElementById("reader-theme-style");
    if (oldStyle) {
        oldStyle.remove();
    }

    const style = doc.createElement("style");
    style.id = "reader-theme-style";

    if (currentTheme === "dark") {
        style.textContent = `
            html, body { background: #0f151d !important; color: #eef2f6 !important; }
            * { color: inherit; }
            body {
                max-width: 940px;
                margin: 0 auto !important;
                padding: 36px 24px 48px !important;
                font-family: "Avenir Next", "Segoe UI Variable", "Trebuchet MS", sans-serif !important;
                line-height: 1.75 !important;
            }
            img, table, video, iframe, object, embed { max-width: 100% !important; height: auto !important; }
            table { border-collapse: collapse !important; }
            th, td { border: 1px solid rgba(255, 255, 255, 0.12) !important; padding: 10px !important; }
            a { color: #ffb08f !important; }
        `;
    } else {
        style.textContent = `
            html, body { background: #ffffff !important; color: #1f2933 !important; }
            * { color: inherit; }
            body {
                max-width: 940px;
                margin: 0 auto !important;
                padding: 36px 24px 48px !important;
                font-family: "Avenir Next", "Segoe UI Variable", "Trebuchet MS", sans-serif !important;
                line-height: 1.75 !important;
            }
            img, table, video, iframe, object, embed { max-width: 100% !important; height: auto !important; }
            table { border-collapse: collapse !important; }
            th, td { border: 1px solid rgba(31, 41, 51, 0.14) !important; padding: 10px !important; }
            a { color: #b6502e !important; }
        `;
    }

    doc.head.appendChild(style);
}

function applyFontScale(docOverride = null) {
    const iframe = document.getElementById("viewer");
    const doc = docOverride || iframe.contentDocument;
    if (!doc || !doc.body) {
        return;
    }

    doc.body.style.fontSize = `${18 * fontScale}px`;
}

async function updatePageNavigation(currentPath) {
    const prevBtn = document.getElementById("nav-prev");
    const nextBtn = document.getElementById("nav-next");

    if (!prevBtn || !nextBtn) {
        return;
    }

    prevBtn.disabled = true;
    nextBtn.disabled = true;
    prevBtn.onclick = null;
    nextBtn.onclick = null;

    try {
        const res = await fetch(`/api/navigation?path=${encodeURIComponent(currentPath)}`);
        if (!res.ok) {
            return;
        }

        const navigation = await res.json();

        if (navigation.prev) {
            prevBtn.disabled = false;
            prevBtn.onclick = () => openFile(navigation.prev);
        }

        if (navigation.next) {
            nextBtn.disabled = false;
            nextBtn.onclick = () => openFile(navigation.next);
        }
    } catch (_error) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
    }
}

function openFile(path) {
    const iframe = document.getElementById("viewer");
    if (!iframe) {
        return;
    }

    markActiveFile(findFileElementByPath(path));
    setViewerEmptyState(false);
    setBreadcrumbs(path);
    iframe.src = buildBookUrl(path);

    iframe.onload = async () => {
        const doc = iframe.contentDocument;
        if (!doc) {
            return;
        }

        applyThemeToIframe();
        applyFontScale(doc);
        await updatePageNavigation(path);
    };
}

function setTheme(themeName) {
    const body = document.body;
    body.classList.remove("theme-light", "theme-dark");
    body.classList.add(`theme-${themeName}`);
    currentTheme = themeName;
    applyThemeToIframe();
}

function openSidebar() {
    document.body.classList.add("sidebar-open");
}

function closeSidebarOnMobile() {
    if (window.innerWidth <= 880) {
        document.body.classList.remove("sidebar-open");
    }
}

function attachGlobalControls() {
    const inc = document.getElementById("font-inc");
    const dec = document.getElementById("font-dec");
    const themeToggle = document.getElementById("theme-toggle");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarClose = document.getElementById("sidebar-close");

    if (inc) {
        inc.onclick = () => {
            fontScale = Math.min(2.2, fontScale + 0.1);
            applyFontScale();
        };
    }

    if (dec) {
        dec.onclick = () => {
            fontScale = Math.max(0.7, fontScale - 0.1);
            applyFontScale();
        };
    }

    if (themeToggle) {
        themeToggle.onclick = () => {
            setTheme(currentTheme === "dark" ? "light" : "dark");
        };
    }

    if (sidebarToggle) {
        sidebarToggle.onclick = () => openSidebar();
    }

    if (sidebarClose) {
        sidebarClose.onclick = () => document.body.classList.remove("sidebar-open");
    }

    window.addEventListener("resize", () => {
        if (window.innerWidth > 880) {
            document.body.classList.remove("sidebar-open");
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    attachGlobalControls();
    attachHandlers(document);
    setTheme("light");
    setViewerEmptyState(true);
});
