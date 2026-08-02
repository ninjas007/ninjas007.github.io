const MENU_URL = "data/menu.json";
const NAVBAR_BRAND_TEXT = "MONOSPACE DEV";

function normalizeMenuHref(href) {
	const [pathPart, hashPart] = String(href || "index.html").split("#");
	return {
		path: (pathPart || "index.html").replace(/^\.\/+/, "").toLowerCase(),
		hash: hashPart ? `#${hashPart}` : "",
	};
}

function isMenuActive(href) {
	const currentPath =
		window.location.pathname.split("/").filter(Boolean).pop()?.toLowerCase() ||
		"index.html";
	const currentHash = window.location.hash;
	const target = normalizeMenuHref(href);

	if (currentPath !== target.path) return false;
	if (!target.hash) return true;
	return currentHash === target.hash;
}

function renderNavbarMenu(menus) {
	const nav = document.querySelector(".navbar-menu");
	const brand = document.querySelector(".navbar-brand");
	if (brand) {
		brand.textContent = NAVBAR_BRAND_TEXT;
	}
	if (!nav) return;

	nav.innerHTML = menus
		.map((menu) => {
			const active = isMenuActive(menu.href);
			return `<li><a href="${menu.href}"${active ? ' aria-current="page"' : ""}>${menu.title}</a></li>`;
		})
		.join("");

	nav.addEventListener("click", (event) => {
		if (!event.target.closest("a")) return;
		nav.classList.remove("open");
		nav.classList.remove("active");
	});
}

function renderFooterMenu(menus) {
	const footer = document.querySelector(".menubar-footer");
	if (!footer) return;

	footer.innerHTML = menus
		.map((menu) => {
			const active = isMenuActive(menu.href);
			return `<a href="${menu.href}">
				<button class="btn-menubar">
					<i class="${menu.icon} ${active ? "text-info" : ""}" style="width: 24px; height: 24px; font-size: 20px"></i>
					<span class="${active ? "text-info" : ""}" style="font-size: 10px">${menu.title}</span>
				</button>
			</a>`;
		})
		.join("");
}

async function getMenus() {
	try {
		const res = await fetch(MENU_URL, { cache: "no-store" });
		if (!res.ok) throw new Error("Failed to load menu.json");
		const menus = await res.json();
		renderNavbarMenu(menus);
		renderFooterMenu(menus);
	} catch (error) {
		console.error(error);
	}
}

getMenus();
