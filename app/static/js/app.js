// =========================================================================
// GESTIÓN DE NOTIFICACIONES (TOAST)
// =========================================================================
function showToast(message, isError = false) {
    const toastEl = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastMessage');
    toastBody.textContent = message;
    toastEl.className = `toast align-items-center text-white border-0 ${isError ? 'bg-danger' : 'bg-success'}`;
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();
}

// =========================================================================
// MÓDULO SQL SERVER: USUARIOS
// =========================================================================
let modalUsuarioInstance = null;

function abrirModalUsuario(usuario = null) {
    if (!modalUsuarioInstance) {
        modalUsuarioInstance = new bootstrap.Modal(document.getElementById('modalUsuario'));
    }
    const form = document.getElementById('formUsuario');
    form.reset();
    if (usuario) {
        document.getElementById('modalUsuarioTitulo').textContent = 'Editar Usuario';
        document.getElementById('usuarioId').value = usuario.id;
        document.getElementById('usuarioNombre').value = usuario.nombre;
        document.getElementById('usuarioEmail').value = usuario.email;
        document.getElementById('usuarioRol').value = usuario.rol;
        document.getElementById('usuarioDepartamento').value = usuario.departamento || '';
    } else {
        document.getElementById('modalUsuarioTitulo').textContent = 'Nuevo Usuario';
        document.getElementById('usuarioId').value = '';
    }
    modalUsuarioInstance.show();
}

async function cargarUsuarios() {
    const tbody = document.getElementById('tablaUsuariosBody');
    const filtroRol = document.getElementById('filtroRolSql').value;
    try {
        let url = '/api/sql/usuarios';
        if (filtroRol) url += `?rol=${encodeURIComponent(filtroRol)}`;
        const res = await fetch(url);
        const data = await res.json();
        
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-secondary">No se encontraron usuarios registrados.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(u => {
            let badgeClass = 'badge-role-estudiante';
            if (u.rol === 'Administrador') badgeClass = 'badge-role-admin';
            else if (u.rol === 'Docente') badgeClass = 'badge-role-docente';

            return `
                <tr>
                    <td class="fw-bold text-secondary">#${u.id}</td>
                    <td class="fw-semibold text-white">${u.nombre}</td>
                    <td><a href="mailto:${u.email}" class="text-decoration-none text-info small">${u.email}</a></td>
                    <td><span class="badge ${badgeClass} px-2 py-1">${u.rol}</span></td>
                    <td class="text-light small">${u.departamento || 'Sin asignar'}</td>
                    <td class="text-secondary small">${u.fecha_registro || '-'}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick='abrirModalUsuario(${JSON.stringify(u)})' title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="eliminarUsuario(${u.id})" title="Eliminar">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">Error al cargar usuarios desde SQL Server: ${err.message}</td></tr>`;
    }
}

async function guardarUsuario(e) {
    e.preventDefault();
    const id = document.getElementById('usuarioId').value;
    const payload = {
        nombre: document.getElementById('usuarioNombre').value.trim(),
        email: document.getElementById('usuarioEmail').value.trim(),
        rol: document.getElementById('usuarioRol').value,
        departamento: document.getElementById('usuarioDepartamento').value.trim()
    };

    try {
        let res;
        if (id) {
            res = await fetch(`/api/sql/usuarios/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch('/api/sql/usuarios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error en la operación');

        showToast(id ? 'Usuario actualizado exitosamente' : 'Usuario creado exitosamente');
        modalUsuarioInstance.hide();
        cargarUsuarios();
    } catch (err) {
        showToast(err.message, true);
    }
}

async function eliminarUsuario(id) {
    if (!confirm('¿Estás seguro de eliminar este usuario de SQL Server?')) return;
    try {
        const res = await fetch(`/api/sql/usuarios/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al eliminar');
        showToast('Usuario eliminado de SQL Server');
        cargarUsuarios();
    } catch (err) {
        showToast(err.message, true);
    }
}

// =========================================================================
// MÓDULO MONGODB: SUBIDA Y VISUALIZACIÓN DE FICHEROS
// =========================================================================
let modalSubidaInstance = null;
let modalEditarDocInstance = null;

function abrirModalSubida() {
    if (!modalSubidaInstance) {
        modalSubidaInstance = new bootstrap.Modal(document.getElementById('modalSubida'));
    }
    document.getElementById('formSubida').reset();
    document.getElementById('subidaAutor').value = 'hector@campuscloud.edu.mx';
    modalSubidaInstance.show();
}

function abrirModalEditarDocumento(doc) {
    if (!modalEditarDocInstance) {
        modalEditarDocInstance = new bootstrap.Modal(document.getElementById('modalEditarDocumento'));
    }
    document.getElementById('editDocId').value = doc.id;
    document.getElementById('editDocTitulo').value = doc.titulo;
    document.getElementById('editDocCategoria').value = doc.categoria || 'Académico';
    document.getElementById('editDocAutor').value = doc.autor_email;
    document.getElementById('editDocDescripcion').value = doc.descripcion || '';
    modalEditarDocInstance.show();
}

async function actualizarDocumentoMongo(e) {
    e.preventDefault();
    const id = document.getElementById('editDocId').value;
    const payload = {
        titulo: document.getElementById('editDocTitulo').value.trim(),
        categoria: document.getElementById('editDocCategoria').value,
        autor_email: document.getElementById('editDocAutor').value.trim(),
        descripcion: document.getElementById('editDocDescripcion').value.trim()
    };

    try {
        const res = await fetch(`/api/mongo/documentos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al actualizar documento');

        showToast('Metadatos de documento actualizados en MongoDB');
        modalEditarDocInstance.hide();
        cargarDocumentos();
    } catch (err) {
        showToast(err.message, true);
    }
}

async function cargarDocumentos() {
    const tbody = document.getElementById('tablaDocumentosBody');
    try {
        const res = await fetch('/api/mongo/documentos');
        const data = await res.json();

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-secondary">No hay documentos registrados en MongoDB.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(d => {
            let iconClass = 'bi-file-earmark-text text-light';
            if (d.tipo_archivo === 'PDF') iconClass = 'bi-file-earmark-pdf-fill text-danger';
            else if (d.tipo_archivo === 'Excel') iconClass = 'bi-file-earmark-excel-fill text-success';
            else if (d.tipo_archivo === 'Word') iconClass = 'bi-file-earmark-word-fill text-primary';
            else if (d.tipo_archivo === 'Imagen') iconClass = 'bi-file-earmark-image-fill text-warning';
            else if (d.tipo_archivo === 'Código/Texto') iconClass = 'bi-file-earmark-code-fill text-info';

            // Botón de visualización si tiene archivo físico
            let btnVer = '';
            if (d.file_url) {
                btnVer = `
                    <a href="${d.file_url}" target="_blank" class="btn btn-sm btn-outline-info me-1" title="Ver / Descargar archivo">
                        <i class="bi bi-eye-fill"></i> Ver
                    </a>
                `;
            }

            return `
                <tr>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <i class="bi ${iconClass} fs-5"></i>
                            <span class="fw-semibold text-white">${d.titulo}</span>
                        </div>
                    </td>
                    <td><span class="badge bg-secondary-subtle text-light border px-2 py-1">${d.tipo_archivo}</span></td>
                    <td><span class="badge bg-info-subtle text-info border border-info-subtle px-2 py-1">${d.categoria}</span></td>
                    <td class="text-secondary small">${d.autor_email}</td>
                    <td class="text-light small text-truncate" style="max-width: 220px;" title="${d.descripcion || ''}">${d.descripcion || '-'}</td>
                    <td class="text-white small">${d.tamanio_kb} KB</td>
                    <td class="text-secondary small">${d.fecha_subida || '-'}</td>
                    <td class="text-end">
                        ${btnVer}
                        <button class="btn btn-sm btn-outline-warning me-1" onclick='abrirModalEditarDocumento(${JSON.stringify(d)})' title="Editar metadatos">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="eliminarDocumento('${d.id}')" title="Eliminar">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Error al cargar documentos desde MongoDB: ${err.message}</td></tr>`;
    }
}

async function subirArchivosReales(e) {
    e.preventDefault();
    const inputArchivos = document.getElementById('inputArchivos');
    if (!inputArchivos.files || inputArchivos.files.length === 0) {
        showToast('Selecciona al menos un archivo para subir', true);
        return;
    }

    const btn = document.getElementById('btnSubir');
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Subiendo...`;

    const formData = new FormData();
    for (const file of inputArchivos.files) {
        formData.append('files', file);
    }
    formData.append('categoria', document.getElementById('subidaCategoria').value);
    formData.append('autor_email', document.getElementById('subidaAutor').value.trim());
    formData.append('descripcion', document.getElementById('subidaDescripcion').value.trim());

    try {
        const res = await fetch('/api/mongo/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al subir los archivos');

        showToast(data.message || 'Archivos subidos exitosamente a MongoDB');
        modalSubidaInstance.hide();
        cargarDocumentos();
    } catch (err) {
        showToast(err.message, true);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-upload me-1"></i> Subir Archivos`;
    }
}

async function eliminarDocumento(id) {
    if (!confirm('¿Estás seguro de eliminar este documento y su archivo físico de MongoDB?')) return;
    try {
        const res = await fetch(`/api/mongo/documentos/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al eliminar');
        showToast('Documento y archivo eliminados de MongoDB');
        cargarDocumentos();
    } catch (err) {
        showToast(err.message, true);
    }
}

// =========================================================================
// MÓDULO RESPALDOS CLOUD (SILO S3 & SCHEDULER)
// =========================================================================
async function cargarRespaldos() {
    const tbody = document.getElementById('tablaRespaldosBody');
    if (!tbody) return;
    try {
        const res = await fetch('/api/backups');
        const data = await res.json();

        if (!data.files || data.files.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-secondary">No hay respaldos almacenados en SILO S3 todavía.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.files.map(f => {
            const isSql = f.engine.includes('SQL Server');
            const badgeClass = isSql ? 'bg-primary-subtle text-primary border border-primary-subtle' : 'bg-success-subtle text-success border border-success-subtle';
            const iconClass = isSql ? 'bi-database' : 'bi-hdd-stack';

            return `
                <tr>
                    <td class="fw-semibold text-white">
                        <i class="bi bi-file-earmark-zip text-warning me-2"></i>${f.filename}
                    </td>
                    <td>
                        <span class="badge ${badgeClass} px-2 py-1">
                            <i class="bi ${iconClass} me-1"></i>${f.engine}
                        </span>
                    </td>
                    <td class="text-info font-monospace small">${f.size_human}</td>
                    <td class="text-secondary small">${f.timestamp}</td>
                    <td><code class="text-secondary small">${f.key}</code></td>
                    <td class="text-end">
                        <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">
                            <i class="bi bi-check2-circle me-1"></i>En S3
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Error al consultar SILO S3: ${err.message}</td></tr>`;
    }
}

async function dispararRespaldoManual() {
    const btn = document.getElementById('btnEjecutarBackup');
    const terminalContainer = document.getElementById('terminalContainer');
    const terminalLog = document.getElementById('terminalLog');

    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Ejecutando respaldo en el agente...`;
    
    terminalContainer.style.display = 'block';
    terminalLog.textContent = 'Iniciando respaldo en contenedor backup-scheduler...\nEjecutando /scripts/backup-semanal.sh...\nEsperando conexión y subida a SILO S3...';

    try {
        const res = await fetch('/api/backups/manual', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            terminalLog.textContent = data.output || 'Respaldo ejecutado con éxito.';
            showToast('¡Respaldo de SQL Server y MongoDB completado y subido a S3!');
        } else {
            terminalLog.textContent = (data.output || '') + '\n' + (data.error || 'Error al ejecutar el respaldo');
            showToast('Hubo un error al ejecutar el respaldo.', true);
        }
        await cargarRespaldos();
    } catch (err) {
        terminalLog.textContent += `\nError de red: ${err.message}`;
        showToast(`Error al contactar con la API: ${err.message}`, true);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-lightning-charge-fill me-1"></i> Ejecutar Respaldo Manual Ahora`;
    }
}

// =========================================================================
// INICIALIZACIÓN AL CARGAR LA PÁGINA
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
    cargarUsuarios();
    cargarDocumentos();
    cargarRespaldos();

    // Recargar tabla de respaldos automáticamente al cambiar a la pestaña de Respaldos
    const backupTab = document.getElementById('backup-tab');
    if (backupTab) {
        backupTab.addEventListener('shown.bs.tab', () => {
            cargarRespaldos();
        });
    }
});
