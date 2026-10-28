// Bo loc kieu Excel: bien moi input text trong hang ".excel-filter-row" thanh
// mot <select> liet ke cac gia tri (da duoc trim) dang xuat hien trong cot tuong ung,
// giup nguoi dung tich chon gia tri co san thay vi phai go tay.
function initExcelFilterTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const filterRow = table.querySelector('.excel-filter-row');
  if (!tbody || !filterRow) return;

  const filterCells = Array.from(filterRow.querySelectorAll('[data-col]'));

  // Doc toan bo du lieu hang hien co de xay danh sach gia tri duy nhat cho tung cot
  const dataRows = Array.from(tbody.querySelectorAll('tr')).filter((row) => !row.classList.contains('no-data-row'));

  filterCells.forEach((cell) => {
    const col = parseInt(cell.dataset.col, 10);
    const existingInput = cell.querySelector('input, select');
    if (existingInput) existingInput.remove();

    const values = new Set();
    dataRows.forEach((row) => {
      const td = row.children[col];
      if (!td) return;
      const text = td.textContent.replace(/\s+/g, ' ').trim();
      if (text) values.add(text);
    });

    const select = document.createElement('select');
    select.className = 'form-select form-select-sm col-filter';
    select.dataset.col = String(col);

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Tất cả --';
    select.appendChild(defaultOption);

    Array.from(values)
      .sort((a, b) => a.localeCompare(b, 'vi'))
      .forEach((value) => {
        const opt = document.createElement('option');
        opt.value = value;
        opt.textContent = value;
        select.appendChild(opt);
      });

    cell.appendChild(select);
  });

  const filters = Array.from(filterRow.querySelectorAll('.col-filter'));

  function applyFilters() {
    const activeFilters = filters
      .map((select) => ({ col: parseInt(select.dataset.col, 10), value: select.value.trim().toLowerCase() }))
      .filter((f) => f.value);

    dataRows.forEach((row) => {
      const cells = row.children;
      const match = activeFilters.every((f) => {
        const cell = cells[f.col];
        if (!cell) return true;
        return cell.textContent.replace(/\s+/g, ' ').trim().toLowerCase() === f.value;
      });
      row.style.display = match ? '' : 'none';
    });
  }

  filters.forEach((select) => select.addEventListener('change', applyFilters));

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
