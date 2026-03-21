<script>
    import { onMount } from 'svelte';
    import { navigate } from "svelte-routing";

    let users = [];
    let loading = true;
    let editingUserId = null;
    let deletingUserId = null;

    let isUserModalOpen = false;
    let isDeleteModalOpen = false;

    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    const statusMap = {
        '1': 'Activo',
        '2': 'Inactivo',
        '3': 'Pendiente',
        '4': 'Finalizado',
        '5': 'Cancelado',
        '6': 'Suspendido'
    };

    const roleMap = {
        '1': 'Administrador',
        '2': 'Docente',
        '3': 'Estudiante'
    };

    const statusColorMap = {
        '1': 'bg-green-100 text-green-700',   // Activo
        '2': 'bg-red-100 text-red-700',       // Inactivo
        '3': 'bg-yellow-100 text-yellow-800', // Pendiente
        '4': 'bg-blue-100 text-blue-700',     // Finalizado
        '5': 'bg-gray-100 text-gray-700',     // Cancelado
        '6': 'bg-orange-100 text-orange-700'  // Suspendido
    };


    // Form data
    let form = {
        identity_document: '',
        first_name: '',
        middle_name: '',
        last_name: '',
        second_last_name: '',
        email: '',
        password_hash: '',
        role_id: 1,
        faculty_id: null,
        status_id: 1
    };

    onMount(() => {
        loadUsers();
    });

    async function loadUsers() {
        loading = true;
        try {
            // Because of our Vite proxy, this will resolve to the backend API properly
            const res = await fetch(`/get_usuarios`);
            if (!res.ok) {
                if (res.status === 404) {
                    users = [];
                    return;
                }
                throw new Error('Error al cargar usuarios');
            }
            const data = await res.json();
            users = data.resultado || [];
        } catch (err) {
            console.error(err);
            users = [];
        } finally {
            loading = false;
        }
    }

    function cerrarSesion() {
        navigate("/");
    }

    function openModal() {
        editingUserId = null;
        form = {
            identity_document: '',
            first_name: '',
            middle_name: '',
            last_name: '',
            second_last_name: '',
            email: '',
            password_hash: '',
            role_id: 1,
            faculty_id: null,
            status_id: 1
        };
        isUserModalOpen = true;
    }

    function openEditModal(user) {
        editingUserId = user.user_id;
        form = {
            identity_document: user.identity_document,
            first_name: user.first_name,
            middle_name: user.middle_name || '',
            last_name: user.last_name,
            second_last_name: user.second_last_name || '',
            email: user.email,
            password_hash: '', // Leave empty unless modifying
            role_id: user.role_id,
            faculty_id: user.faculty_id || null,
            status_id: user.status_id
        };
        isUserModalOpen = true;
    }

    function closeModal() {
        isUserModalOpen = false;
        editingUserId = null;
    }

    function openDeleteModal(userId) {
        deletingUserId = userId;
        isDeleteModalOpen = true;
    }

    function closeDeleteModal() {
        isDeleteModalOpen = false;
        deletingUserId = null;
    }

    function displayToast(message, type) {
        toastMessage = message;
        toastType = type;
        showToast = true;
        setTimeout(() => { showToast = false; }, 3000);
    }

    async function saveUser() {
        const body = {
            identity_document: form.identity_document,
            first_name: form.first_name,
            middle_name: form.middle_name || null,
            last_name: form.last_name,
            second_last_name: form.second_last_name || null,
            email: form.email,
            password_hash: form.password_hash,
            role_id: parseInt(form.role_id),
            faculty_id: form.faculty_id ? parseInt(form.faculty_id) : null,
            status_id: parseInt(form.status_id)
        };

        try {
            let res;
            if (editingUserId) {
                if (!body.password_hash) {
                    const current = await fetch(`/get_usuario/${editingUserId}`);
                    const currentData = await current.json();
                    body.password_hash = currentData.password_hash;
                }
                res = await fetch(`/update_usuario/${editingUserId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
            } else {
                res = await fetch(`/create_usuario/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
            }

            if (!res.ok) throw new Error('Error al guardar');

            closeModal();
            displayToast(editingUserId ? 'Usuario actualizado correctamente' : 'Usuario creado correctamente', 'success');
            loadUsers();
        } catch (err) {
            console.error(err);
            displayToast('Error al guardar el usuario', 'error');
        }
    }

    async function confirmDelete() {
        try {
            const res = await fetch(`/delete_usuario/${deletingUserId}`, { method: 'DELETE' });
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Error al eliminar');
            }
            closeDeleteModal();
            displayToast('Usuario eliminado correctamente', 'success');
            loadUsers();
        } catch (err) {
            console.error(err);
            displayToast(err.message || 'Error al eliminar el usuario', 'error');
            closeDeleteModal();
        }
    }
</script>

<div class="bg-gray-100 min-h-screen">
    <!-- Navbar -->
    <nav class="bg-gray-800 text-white flex justify-between items-center px-6 py-3 shadow-lg sticky top-0 z-10">
        <div class="flex items-center gap-3">
            <svg class="w-7 h-7 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <h1 class="text-lg font-bold">Panel Administrador</h1>
        </div>
        <button on:click={cerrarSesion} class="bg-red-500 hover:bg-red-600 px-4 py-1.5 rounded text-sm font-medium transition cursor-pointer">
            Cerrar sesión
        </button>
    </nav>

    <div class="flex">
        <!-- Sidebar -->
        <aside class="w-64 bg-gray-800 border-r border-gray-700 min-h-[calc(100vh-60px)] shadow-md p-5 hidden md:block">
            <h2 class="font-semibold text-gray-400 text-xs uppercase tracking-wider mb-4">Administración</h2>
            <ul class="space-y-1">
                <li><button class="w-full text-left px-3 py-2 rounded-lg bg-blue-600 text-white font-medium text-sm shadow">Gestionar Usuarios</button></li>
                <li><button class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white text-sm transition">Gestionar Cursos</button></li>
                <li><button class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white text-sm transition">Gestionar Inscripciones</button></li>
                <li><button class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white text-sm transition">Reportes</button></li>
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 p-6 sm:p-8">
            <!-- Header -->
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                <div>
                    <h2 class="text-2xl font-bold text-gray-800">Gestión de Usuarios</h2>
                    <p class="text-gray-500 text-sm mt-1">Crear, editar y eliminar usuarios del sistema</p>
                </div>
                <button on:click={openModal} class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium shadow transition flex items-center gap-2 cursor-pointer">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Nuevo Usuario
                </button>
            </div>

            <!-- Toast Message -->
            {#if showToast}
                <div class="fixed top-20 right-5 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-50 transition-all {toastType === 'success' ? 'bg-green-600' : 'bg-red-600'}">
                    {toastMessage}
                </div>
            {/if}

            <!-- Tabla de usuarios -->
            <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 border-b">
                            <tr>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">ID</th>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Documento</th>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Nombre Completo</th>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Email</th>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Rol</th>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Facultad</th>
                                <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Estado</th>
                                <th class="text-center px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#if loading}
                                <tr><td colspan="8" class="text-center py-10 text-gray-400">Cargando usuarios...</td></tr>
                            {:else if users.length === 0}
                                <tr><td colspan="8" class="text-center py-10 text-gray-400">No se encontraron usuarios</td></tr>
                            {:else}
                                {#each users as u}
                                    <tr class="border-b hover:bg-gray-50 transition">
                                        <td class="px-4 py-3 text-gray-700 font-medium">{u.user_id}</td>
                                        <td class="px-4 py-3 text-gray-600">{u.identity_document}</td>
                                        <td class="px-4 py-3 text-gray-600">{u.first_name} {u.middle_name || ''} {u.last_name} {u.second_last_name || ''}</td>
                                        <td class="px-4 py-3 text-gray-600">{u.email}</td>
                                        <td class="px-4 py-3"><span class="inline-block bg-purple-100 text-purple-700 text-xs font-medium px-2 py-1 rounded-full">{roleMap[String(u.role_id)] || u.role_id}</span></td>
                                        <td class="px-4 py-3 text-gray-600">{u.faculty_id ?? '-'}</td>
                                        <td class="px-4 py-3"><span class="inline-block {statusColorMap[String(u.status_id).trim()] || 'bg-gray-100 text-gray-700'} text-xs font-medium px-2 py-1 rounded-full">{statusMap[String(u.status_id).trim()] || u.status_id}</span></td>
                                        <td class="px-4 py-3 text-center">
                                            <div class="flex justify-center gap-2">
                                                <button on:click={() => openEditModal(u)} class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition" title="Editar">
                                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                                                </button>
                                                <button on:click={() => openDeleteModal(u.user_id)} class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition" title="Eliminar">
                                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                {/each}
                            {/if}
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <!-- Modal Crear/Editar -->
    {#if isUserModalOpen}
        <div class="fixed inset-0 z-40 flex items-center justify-center">
            <div class="absolute inset-0 bg-black/50" on:click={closeModal}></div>
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center px-6 py-4 border-b">
                    <h3 class="text-lg font-bold text-gray-800">{editingUserId ? 'Editar Usuario' : 'Nuevo Usuario'}</h3>
                    <button on:click={closeModal} class="text-gray-400 hover:text-gray-600 cursor-pointer">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                </div>
                <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
                <form class="p-6 space-y-4" on:submit|preventDefault={saveUser}>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="id_doc">Documento de Identidad *</label>
                            <input type="text" id="id_doc" required bind:value={form.identity_document} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="email">Email *</label>
                            <input type="email" id="email" required bind:value={form.email} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="fname">Primer Nombre *</label>
                            <input type="text" id="fname" required bind:value={form.first_name} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="mname">Segundo Nombre</label>
                            <input type="text" id="mname" bind:value={form.middle_name} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="lname">Primer Apellido *</label>
                            <input type="text" id="lname" required bind:value={form.last_name} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="slname">Segundo Apellido</label>
                            <input type="text" id="slname" bind:value={form.second_last_name} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1" for="pass">Contraseña {editingUserId ? '' : '*'}</label>
                        <input type="password" id="pass" required={!editingUserId} placeholder={editingUserId ? "Dejar vacío para mantener la actual" : ""} bind:value={form.password_hash} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="role_id">Rol *</label>
                            <select id="role_id" required bind:value={form.role_id} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
                                <option value={1}>Administrador</option>
                                <option value={2}>Docente</option>
                                <option value={3}>Estudiante</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="fac_id">Facultad *</label>
                            <select id="fac_id" required bind:value={form.faculty_id} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
                                <option value={1}>Ingeniería de Sistemas</option>
                                <option value={2}>Medicina</option>
                                <option value={3}>Derecho</option>
                                <option value={4}>Administración de Empresas</option>
                                <option value={5}>Arquitectura</option>
                                <option value={6}>Psicología</option>
                                <option value={7}>Economía</option>
                                <option value={8}>Comunicación Social</option>
                                <option value={9}>Biología</option>
                                <option value={10}>Matemáticas</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1" for="status_id">Estado *</label>
                            <select id="status_id" required bind:value={form.status_id} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
                                <option value={1}>Activo</option>
                                <option value={2}>Inactivo</option>
                                <option value={3}>Pendiente</option>
                                <option value={4}>Finalizado</option>
                                <option value={5}>Cancelado</option>
                                <option value={6}>Suspendido</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex justify-end gap-3 pt-4 border-t mt-6">
                        <button type="button" on:click={closeModal} class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition cursor-pointer">
                            Cancelar
                        </button>
                        <button type="submit" class="px-5 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow transition cursor-pointer">
                            Guardar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    <!-- Modal Confirmar Eliminar -->
    {#if isDeleteModalOpen}
        <div class="fixed inset-0 z-40 flex items-center justify-center">
            <div class="absolute inset-0 bg-black/50" on:click={closeDeleteModal}></div>
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
                <div class="text-center">
                    <div class="mx-auto w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mb-4">
                        <svg class="w-7 h-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </div>
                    <h3 class="text-lg font-bold text-gray-800 mb-2">Eliminar Usuario</h3>
                    <p class="text-gray-500 text-sm mb-6">Esta acción no se puede deshacer. El usuario será eliminado permanentemente.</p>
                    <div class="flex justify-center gap-3">
                        <button on:click={closeDeleteModal} class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition cursor-pointer">
                            Cancelar
                        </button>
                        <button on:click={confirmDelete} class="px-5 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg shadow transition cursor-pointer">
                            Eliminar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>
