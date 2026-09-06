/* Rangli dropdown: select.color-img-select ni rasmli ro'yxatga aylantiradi */
(function () {
    'use strict';

    function thumbHtml(opt) {
        var img = opt.getAttribute('data-img');
        var code = opt.getAttribute('data-code') || '#ccc';
        if (img) return '<span class="cimg-th" style="background-image:url(\'' + img + '\')"></span>';
        return '<span class="cimg-th" style="background:' + code + '"></span>';
    }

    function enhance(sel) {
        if (sel.dataset.cimgReady) return;
        // nested_admin bo'sh shablon qatorini o'tkazib yuboramiz
        if (sel.name && sel.name.indexOf('__prefix__') !== -1) return;
        sel.dataset.cimgReady = '1';

        var wrap = document.createElement('span');
        wrap.className = 'cimg-wrap';
        sel.parentNode.insertBefore(wrap, sel.nextSibling);

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'cimg-btn';
        var panel = document.createElement('div');
        panel.className = 'cimg-panel';
        wrap.appendChild(btn);
        wrap.appendChild(panel);
        sel.style.display = 'none';

        function addOpt(opt) {
            var d = document.createElement('div');
            d.className = 'cimg-item' + (opt.selected ? ' sel' : '');
            d.innerHTML = (opt.value ? thumbHtml(opt) : '') + '<span>' + opt.text + '</span>';
            d.addEventListener('click', function () {
                sel.value = opt.value;
                sel.dispatchEvent(new Event('change', { bubbles: true }));
                panel.classList.remove('open');
                sync();
            });
            panel.appendChild(d);
        }

        function build() {
            panel.innerHTML = '';
            Array.prototype.forEach.call(sel.children, function (node) {
                if (node.tagName === 'OPTGROUP') {
                    var h = document.createElement('div');
                    h.className = 'cimg-group';
                    h.textContent = node.label;
                    panel.appendChild(h);
                    Array.prototype.forEach.call(node.children, addOpt);
                } else {
                    addOpt(node);
                }
            });
        }

        function sync() {
            var opt = sel.options[sel.selectedIndex];
            btn.innerHTML = (opt && opt.value ? thumbHtml(opt) : '') +
                '<span>' + (opt ? opt.text : '---------') + '</span>' +
                '<i class="cimg-car"></i>';
            build();
        }

        btn.addEventListener('click', function (e) {
            e.preventDefault();
            // boshqa ochiq panellarni yopamiz
            document.querySelectorAll('.cimg-panel.open').forEach(function (p) {
                if (p !== panel) p.classList.remove('open');
            });
            panel.classList.toggle('open');
        });

        // tashqariga bosilsa yopish
        document.addEventListener('click', function (e) {
            if (!wrap.contains(e.target)) panel.classList.remove('open');
        });

        // tashqi o'zgarish (masalan, popup orqali yangi rang qo'shilsa)
        sel.addEventListener('change', sync);
        sync();
    }

    function initAll() {
        document.querySelectorAll('select.color-img-select').forEach(enhance);
    }

    document.addEventListener('DOMContentLoaded', function () {
        initAll();
        // yangi inline qator qo'shilganda ham ishlashi uchun
        if (window.django && window.django.jQuery) {
            window.django.jQuery(document).on('formset:added', function () {
                setTimeout(initAll, 50);
            });
        }
        new MutationObserver(function () { initAll(); })
            .observe(document.body, { childList: true, subtree: true });
    });
})();
