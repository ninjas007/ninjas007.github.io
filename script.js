
function getMenus() {
    $.ajax({
        dataType: "json",
        url: "data/menu.json",
        success: function (menus) {
            let html = ``;
            let page = window.location.pathname;
            $.each(menus, function (index, menu) {
                html += `<a href="${menu.href}">
                <button class="btn-menubar">
                    <i class="${menu.icon} ${page == `/${menu.href}` ? 'text-info' : ''}" style="width: 24px; height: 24px; font-size: 20px"></i>
                    <span class="${page == `/${menu.href}` ? 'text-info' : ''}" style="font-size: 10px">${menu.title}</span>
                </button>
                </a>`
            });

            $('.menubar-footer').html(`${html}`);
        }
    });
}

getMenus();