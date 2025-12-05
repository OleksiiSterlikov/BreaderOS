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
   MAIN
=========================== */
document.addEventListener("DOMContentLoaded", () => {

    /* ==== FOLDER CLICK ==== */
    document.querySelectorAll(".folder").forEach(folder => {
        folder.addEventListener("click", () => {
            const ul = folder.parentNode.querySelector("ul");
            if (!ul) return;

            const wasHidden = ul.classList.contains("hidden");
            closeSiblings(ul);
            ul.classList.toggle("hidden", !wasHidden);
        });
    });

    /* ==== FILE CLICK ==== */
    document.querySelectorAll(".file").forEach(file => {
        file.addEventListener("click", () => {
    
            const iframe = document.getElementById("viewer");
            const src = "/book/" + file.dataset.path;   // <<< ВАЖЛИВО!
            iframe.src = src;
    
            document.querySelectorAll(".file").forEach(f => f.classList.remove("active"));
            file.classList.add("active");
    
            document.getElementById("breadcrumbs").textContent = file.dataset.path;
    
            iframe.onload = () => {
                const doc = iframe.contentDocument;
                if (!doc) return;
    
                doc.body.classList.add("book-page");
                applyThemeToIframe();
                applyFontScale(doc);
            };
        });
    });

    /* ==== THEME TOGGLE ==== */
    const themeToggle = document.getElementById("theme-toggle");

    themeToggle.addEventListener("click", () => {
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
    });

});

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

function applyFontScale(docOverride = null) {
    const iframe = document.getElementById("viewer");
    const doc = docOverride || iframe.contentDocument;

    if (!doc) return;

    doc.body.style.fontSize = (18 * fontScale) + "px";
}
