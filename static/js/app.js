/* HelpDesk Pro — shared page behaviour. No framework, no dependencies.
   Everything here improves a page that already works without it. */
(function () {
  'use strict';

  // ── Dropdown menus (notifications, account) ──────────────────────
  var openMenu = null;

  function closeMenu() {
    if (!openMenu) return;
    openMenu.button.setAttribute('aria-expanded', 'false');
    openMenu.panel.hidden = true;
    openMenu = null;
  }

  document.querySelectorAll('[data-menu]').forEach(function (button) {
    var panel = document.getElementById(button.getAttribute('aria-controls'));
    if (!panel) return;
    button.addEventListener('click', function (event) {
      event.stopPropagation();
      var wasOpen = openMenu && openMenu.button === button;
      closeMenu();
      if (wasOpen) return;
      panel.hidden = false;
      button.setAttribute('aria-expanded', 'true');
      openMenu = { button: button, panel: panel };
    });
  });

  document.addEventListener('click', function (event) {
    if (openMenu && !openMenu.panel.contains(event.target)) closeMenu();
  });

  // ── Navigation on small screens ──────────────────────────────────
  var band = document.getElementById('band');
  var navToggle = document.querySelector('[data-nav-toggle]');
  if (band && navToggle) {
    navToggle.addEventListener('click', function () {
      var open = band.toggleAttribute('data-nav-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (openMenu) { var button = openMenu.button; closeMenu(); button.focus(); }
    if (band && band.hasAttribute('data-nav-open')) {
      band.removeAttribute('data-nav-open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });

  // ── Dismissible alerts ───────────────────────────────────────────
  document.querySelectorAll('[data-dismiss]').forEach(function (button) {
    button.addEventListener('click', function () {
      var alert = button.closest('.alert');
      if (alert) alert.remove();
    });
  });

  // ── Confirm before a destructive link or button ──────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (event) {
      if (!window.confirm(el.getAttribute('data-confirm'))) event.preventDefault();
    });
  });

  // ── Bulk selection on the ticket table ───────────────────────────
  var bulk = document.querySelector('[data-bulk]');
  if (bulk) {
    var selectAll = document.querySelector('[data-select-all]');
    var boxes = Array.prototype.slice.call(document.querySelectorAll('[data-select-row]'));
    var count = bulk.querySelector('[data-bulk-count]');
    var apply = bulk.querySelector('[data-bulk-apply]');

    var refresh = function () {
      var chosen = boxes.filter(function (box) { return box.checked; }).length;
      if (count) {
        count.textContent = chosen
          ? chosen + (chosen === 1 ? ' ticket selected' : ' tickets selected')
          : 'Tick tickets below, then choose an action.';
      }
      if (apply) apply.disabled = chosen === 0;
      if (selectAll) {
        selectAll.checked = chosen > 0 && chosen === boxes.length;
        selectAll.indeterminate = chosen > 0 && chosen < boxes.length;
      }
    };

    if (selectAll) {
      selectAll.addEventListener('change', function () {
        boxes.forEach(function (box) { box.checked = selectAll.checked; });
        refresh();
      });
    }
    boxes.forEach(function (box) { box.addEventListener('change', refresh); });
    refresh();
  }

  // ── Subcategories follow the chosen category ─────────────────────
  var form = document.querySelector('form[data-subcategory-url]');
  if (form) {
    var category = form.querySelector('#id_category');
    var sub = form.querySelector('#id_subcategory');
    var url = form.getAttribute('data-subcategory-url');
    var placeholder = '<option value="">Choose a category first</option>';

    var load = function (keep) {
      if (!category.value) { sub.innerHTML = placeholder; sub.disabled = true; return; }
      sub.disabled = true;
      fetch(url + '?category=' + encodeURIComponent(category.value), { credentials: 'same-origin' })
        .then(function (response) { return response.text(); })
        .then(function (html) {
          sub.innerHTML = html;
          if (keep) sub.value = keep;
          sub.disabled = false;
        })
        .catch(function () { sub.disabled = false; });
    };

    if (category && sub) {
      category.addEventListener('change', function () { load(null); });
      // After a failed submit the chosen subcategory must survive the reload.
      load(sub.value || null);
    }
  }

  // ── Tooltips for elements that explain themselves on hover/focus ─
  var tip = null;

  function showTip(el) {
    var text = el.getAttribute('data-tip');
    if (!text) return;
    if (!tip) {
      tip = document.createElement('div');
      tip.className = 'tip';
      tip.setAttribute('role', 'tooltip');
      document.body.appendChild(tip);
    }
    tip.textContent = text;
    tip.hidden = false;
    var box = el.getBoundingClientRect();
    var own = tip.getBoundingClientRect();
    // Beside the element when there is room, so the tip covers part of its
    // own row instead of the row above or below; otherwise above, then below.
    var left = box.left - own.width - 10;
    var top = box.top + (box.height - own.height) / 2;
    if (left < 8) {
      left = Math.min(Math.max(8, box.left), window.innerWidth - own.width - 8);
      top = box.top - own.height - 8;
      if (top < 8) top = box.bottom + 8;
    }
    top = Math.min(Math.max(8, top), window.innerHeight - own.height - 8);
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  }

  function hideTip() { if (tip) tip.hidden = true; }

  document.querySelectorAll('[data-tip]').forEach(function (el) {
    el.addEventListener('mouseenter', function () { showTip(el); });
    el.addEventListener('mouseleave', hideTip);
    el.addEventListener('focus', function () { showTip(el); });
    el.addEventListener('blur', hideTip);
  });
  window.addEventListener('scroll', hideTip, { passive: true });
})();
