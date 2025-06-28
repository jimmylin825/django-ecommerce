document.addEventListener('DOMContentLoaded', function () {
  const coverCheckboxes = document.querySelectorAll('input[name$="is_cover"]');

  coverCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener('change', function () {
      if (this.checked) {
        coverCheckboxes.forEach((cb) => {
          if (cb !== this) cb.checked = false;
        });
      }
    });
  });
});
