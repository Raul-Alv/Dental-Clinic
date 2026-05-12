document.addEventListener('DOMContentLoaded', () => {
  const normalizePath = (path) => {
    if (!path) {
      return '/';
    }

    const compactPath = path.replace(/\/+/g, '/');
    return compactPath.endsWith('/') ? compactPath : `${compactPath}/`;
  };

  const currentPath = normalizePath(window.location.pathname);

  document.querySelectorAll('[data-nav-link]').forEach((link) => {
    const linkPath = normalizePath(new URL(link.href, window.location.origin).pathname);
    const linkDepth = linkPath.split('/').filter(Boolean).length;
    const isSectionLink = linkDepth > 1;
    const isActive = currentPath === linkPath || (isSectionLink && currentPath.startsWith(linkPath));

    link.classList.toggle('is-active', isActive);
  });

  document.querySelectorAll('.alert').forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  const fileInput = document.getElementById('id_rdf_file');
  const dropZone = document.getElementById('file-drop-zone');
  const fileList = document.getElementById('file-list');
  const dropZoneCopy = dropZone ? dropZone.querySelector('p') : null;

  if (!fileInput || !dropZone || !fileList) {
    return;
  }

  const emptyMessage = 'Arrastra el archivo aqui o haz clic para seleccionarlo desde tu equipo.';

  const syncDropZoneState = (filesCount) => {
    const hasFiles = filesCount > 0;

    dropZone.classList.toggle('is-filled', hasFiles);
    if (dropZoneCopy) {
      dropZoneCopy.textContent = hasFiles
        ? `${filesCount} archivo(s) listo(s) para importar.`
        : emptyMessage;
    }
  };

  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.classList.remove('dragover');
    fileInput.files = event.dataTransfer.files;
    updateFileList();
  });

  fileInput.addEventListener('change', updateFileList);

  function updateFileList() {
    fileList.innerHTML = '';
    const files = fileInput.files;

    syncDropZoneState(files.length);

    if (!files.length) {
      return;
    }

    Array.from(files).forEach((file) => {
      const item = document.createElement('li');
      item.className = 'list-group-item d-flex justify-content-between align-items-center';

      const name = document.createElement('span');
      name.textContent = file.name;

      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-sm btn-outline-danger';
      button.textContent = 'Quitar';
      button.addEventListener('click', () => {
        fileInput.value = '';
        fileList.innerHTML = '';
        syncDropZoneState(0);
      });

      item.append(name, button);
      fileList.appendChild(item);
    });
  }

  syncDropZoneState(0);
});
