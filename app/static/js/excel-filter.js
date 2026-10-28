// Bo loc kieu Excel nang cao: moi cot co the la:
//  - "text": o nhap tu do, loc theo kieu "chua chuoi" (vd: Ho ten, SDT, Noi o, Que quan)
//  - "date": chon khoang ngay (tu - den), loc theo gia tri ngay hien thi dd/mm/yyyy trong o
//  - "multiselect": dropdown co o tim kiem + tich chon nhieu gia tri co san trong cot do
function initExcelFilterTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const filterRow = table.querySelector('.excel-filter-row');
  if (!tbody || !filterRow) return;

  const dataRows = Array.from(tbody.querySelectorAll('tr')).filter((row) => !row.classList.contains('no-data-row'));
  const filterCells = Array.from(filterRow.querySelectorAll('[data-col]'));
  const state = {};

  function getCellText(row, col) {
    const td = row.children[col];
    if (!td) return '';
    return td.textContent.replace(/\s+/g, ' ').trim();
  }

  function parseDisplayDate(text) {
    const m = text.match(/(\d{2})\/(\d{2})\/(\d{4})/);
    if (!m) return null;
    return new Date(parseInt(m[3], 10), parseInt(m[2], 10) - 1, parseInt(m[1], 10));
  }

  function applyFilters() {
    dataRows.forEach((row) => {
      let visible = true;
      for (const colKey in state) {
        const f = state[colKey];
        const col = parseInt(colKey, 10);
        const text = getCellText(row, col);

        if (f.kind === 'text') {
          if (f.value && !text.toLowerCase().includes(f.value)) {
            visible = false;
            break;
          }
        } else if (f.kind === 'date') {
          if (f.from || f.to) {
            const d = parseDisplayDate(text);
            if (!d) {
              visible = false;
              break;
            }
            if (f.from && d < f.from) {
              visible = false;
              break;
            }
            if (f.to && d > f.to) {
              visible = false;
              break;
            }
          }
        } else if (f.kind === 'multiselect') {
          if (f.values && f.values.size > 0 && !f.values.has(text)) {
            visible = false;
            break;
          }
        }
      }
      row.style.display = visible ? '' : 'none';
    });
  }

  function closeAllMenus(except) {
    document.querySelectorAll('.excel-multiselect-menu.show').forEach((menu) => {
      if (menu !== except) menu.classList.remove('show');
    });
  }

  function positionMenu(btn, menu) {
    const rect = btn.getBoundingClientRect();
    const menuWidth = Math.max(rect.width, 220);
    let left = rect.left;
    if (left + menuWidth > window.innerWidth - 10) {
      left = Math.max(10, window.innerWidth - menuWidth - 10);
    }
    menu.style.minWidth = menuWidth + 'px';
    menu.style.top = rect.bottom + 4 + 'px';
    menu.style.left = left + 'px';
  }

  filterCells.forEach((cell) => {
    const col = parseInt(cell.dataset.col, 10);
    const kind = cell.dataset.kind || 'multiselect';
    cell.innerHTML = '';

    if (kind === 'text') {
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'form-control form-control-sm col-filter';
      input.placeholder = 'Nhập để tìm...';
      input.addEventListener('input', () => {
        state[col] = { kind: 'text', value: input.value.trim().toLowerCase() };
        applyFilters();
      });
      cell.appendChild(input);
      state[col] = { kind: 'text', value: '' };
    } else if (kind === 'date') {
      const wrap = document.createElement('div');
      wrap.className = 'excel-date-range';

      const from = document.createElement('input');
      from.type = 'date';
      from.className = 'form-control form-control-sm col-filter';
      from.title = 'Từ ngày';

      const to = document.createElement('input');
      to.type = 'date';
      to.className = 'form-control form-control-sm col-filter';
      to.title = 'Đến ngày';

      function update() {
        const fromVal = from.value ? new Date(from.value + 'T00:00:00') : null;
        const toVal = to.value ? new Date(to.value + 'T23:59:59') : null;
        state[col] = { kind: 'date', from: fromVal, to: toVal };
        applyFilters();
      }
      from.addEventListener('change', update);
      to.addEventListener('change', update);

      wrap.appendChild(from);
      wrap.appendChild(to);
      cell.appendChild(wrap);
      state[col] = { kind: 'date', from: null, to: null };
    } else {
      const values = new Set();
      dataRows.forEach((row) => {
        const t = getCellText(row, col);
        if (t) values.add(t);
      });
      const sortedValues = Array.from(values).sort((a, b) => a.localeCompare(b, 'vi'));
      const selected = new Set();

      const wrapper = document.createElement('div');
      wrapper.className = 'excel-multiselect';

      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-sm btn-outline-secondary w-100 text-truncate excel-multiselect-btn';
      btn.textContent = 'Tất cả';

      const menu = document.createElement('div');
      menu.className = 'excel-multiselect-menu';

      const searchBox = document.createElement('input');
      searchBox.type = 'text';
      searchBox.className = 'form-control form-control-sm mb-2';
      searchBox.placeholder = 'Tìm giá trị...';

      const listWrap = document.createElement('div');
      listWrap.className = 'excel-multiselect-list';

      function updateButtonLabel() {
        if (selected.size === 0) btn.textContent = 'Tất cả';
        else if (selected.size === 1) btn.textContent = Array.from(selected)[0];
        else btn.textContent = 'Đã chọn (' + selected.size + ')';
      }

      function renderList(filterText) {
        listWrap.innerHTML = '';
        const ft = (filterText || '').toLowerCase();
        sortedValues
          .filter((v) => !ft || v.toLowerCase().includes(ft))
          .forEach((v) => {
            const id = 'ms_' + col + '_' + Math.random().toString(36).slice(2, 9);
            const item = document.createElement('div');
            item.className = 'form-check';
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.className = 'form-check-input';
            cb.id = id;
            cb.checked = selected.has(v);
            cb.addEventListener('change', () => {
              if (cb.checked) selected.add(v);
              else selected.delete(v);
              updateButtonLabel();
              state[col] = { kind: 'multiselect', values: selected };
              applyFilters();
            });
            const label = document.createElement('label');
            label.className = 'form-check-label small';
            label.htmlFor = id;
            label.textContent = v;
            item.appendChild(cb);
            item.appendChild(label);
            listWrap.appendChild(item);
          });
        if (!listWrap.children.length) {
          const empty = document.createElement('div');
          empty.className = 'text-muted small px-1';
          empty.textContent = 'Không có giá trị phù hợp.';
          listWrap.appendChild(empty);
        }
      }

      searchBox.addEventListener('input', () => renderList(searchBox.value));
      renderList('');

      const footer = document.createElement('div');
      footer.className = 'd-flex justify-content-between mt-2 pt-2 border-top';
      const clearBtn = document.createElement('button');
      clearBtn.type = 'button';
      clearBtn.className = 'btn btn-sm btn-link p-0';
      clearBtn.textContent = 'Bỏ chọn tất cả';
      clearBtn.addEventListener('click', () => {
        selected.clear();
        renderList(searchBox.value);
        updateButtonLabel();
        state[col] = { kind: 'multiselect', values: selected };
        applyFilters();
      });
      footer.appendChild(clearBtn);

      menu.appendChild(searchBox);
      menu.appendChild(listWrap);
      menu.appendChild(footer);

      wrapper.appendChild(btn);
      wrapper.appendChild(menu);
      cell.appendChild(wrapper);

      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = menu.classList.contains('show');
        closeAllMenus();
        if (!isOpen) {
          menu.classList.add('show');
          positionMenu(btn, menu);
          searchBox.value = '';
          renderList('');
          searchBox.focus();
        }
      });
      menu.addEventListener('click', (e) => e.stopPropagation());

      state[col] = { kind: 'multiselect', values: selected };
    }
  });

  document.addEventListener('click', () => closeAllMenus());
  window.addEventListener(
    'scroll',
    () => {
      document.querySelectorAll('.excel-multiselect-menu.show').forEach((menu) => {
        const wrapper = menu.closest('.excel-multiselect');
        if (!wrapper) return;
        positionMenu(wrapper.querySelector('.excel-multiselect-btn'), menu);
      });
    },
    true
  );

  applyFilters();

  // An/hien hang bo loc, nho trang thai qua localStorage theo id bang
  const toggleBtn = document.getElementById('toggleFilterRowBtn');
  const storageKey = tableId + '_filterRowHidden';
  function applyVisibility() {
    const hidden = localStorage.getItem(storageKey) === '1';
    filterRow.style.display = hidden ? 'none' : '';
  }
  applyVisibility();
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const hiddenNow = filterRow.style.display === 'none';
      filterRow.style.display = hiddenNow ? '' : 'none';
      localStorage.setItem(storageKey, hiddenNow ? '0' : '1');
    });
  }
}
