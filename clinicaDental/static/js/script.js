document.addEventListener('DOMContentLoaded', () => {
  // —————— 1) Resaltar pestaña activa en el menú ——————
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });

  // —————— 2) Auto-ocultar alertas tras 5 segundos ——————
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      if (window.jQuery) {
        $(alert).fadeOut();
      } else {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
      }
    }, 5000);
  });

  // —————— 3) Zona de Drag & Drop (solo si existe) ——————
  const fileInput = document.getElementById('id_rdf_file');
const dropZone  = document.getElementById('file-drop-zone');
  const fileList  = document.getElementById('file-list');

  if (fileInput && dropZone && fileList) {
    // Click abre diálogo
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & drop
    dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });
    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      fileInput.files = e.dataTransfer.files;
      updateFileList();
    });

    // Cambio manual
    fileInput.addEventListener('change', updateFileList);

    function updateFileList() {
      fileList.innerHTML = '';
      const files = fileInput.files;
      if (!files.length) return;

      Array.from(files).forEach(file => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';

        const nameSpan = document.createElement('span');
        nameSpan.textContent = file.name;

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-outline-danger';
        btn.textContent = 'Eliminar';
        btn.addEventListener('click', () => {
          fileInput.value = '';
          fileList.innerHTML = '';
        });

        li.append(nameSpan, btn);
        fileList.appendChild(li);
      });
    }
  }
});
