<script lang="ts">
    import { onMount } from "svelte";
    import { navigate } from "svelte-routing";
    import { getSession, logout } from "../lib/services/auth";

    import {
        getUsuarios,
        getUsuario,
        createUsuario,
        updateUsuario,
        deleteUsuario,
    } from "../lib/services/users";
    import type { UserCreate } from "../lib/services/users";

    import AdminCursos from "../components/AdminCursos.svelte";
    import AdminInscripciones from "../components/AdminInscripciones.svelte";
    import AdminReportes from "../components/AdminReportes.svelte";
    import DataTable from "../components/DataTable.svelte";
    import Input from "../components/ui/Input.svelte";
    import Select from "../components/ui/Select.svelte";
    import Button from "../components/ui/Button.svelte";
    import Toast from "../components/ui/Toast.svelte";
    import Modal from "../components/ui/Modal.svelte";
    import Badge from "../components/ui/Badge.svelte";
    import PageHeader from "../components/ui/PageHeader.svelte";

    let currentView = "usuarios";
    let isMobileMenuOpen = false;

    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

    onMount(() => {
        const session = getSession();
        if (!session.user_id || session.role_id !== 1) {
            navigate("/");
            return;
        }
        loadUsers();
    });

    let users = [];
    let loading = true;

    const userColumns = [
        { key: "user_id", label: "ID" },
        { key: "identity_document", label: "Documento" },
        { key: "_nombre", label: "Nombre Completo" },
        { key: "email", label: "Email" },
        { key: "_rol", label: "Rol" },
        { key: "_facultad", label: "Facultad" },
        { key: "_estado", label: "Estado" },
        { key: "_x", label: "Acciones", sortable: false, center: true },
    ];

    const userSearchFn = (row: any, q: string): boolean => {
        const lq = q.toLowerCase();
        return (
            String(row.user_id).includes(lq) ||
            (row.identity_document || "").toLowerCase().includes(lq) ||
            row._nombre.toLowerCase().includes(lq) ||
            (row.email || "").toLowerCase().includes(lq) ||
            row._rol.toLowerCase().includes(lq) ||
            row._facultad.toLowerCase().includes(lq) ||
            row._estado.toLowerCase().includes(lq)
        );
    };

    $: tableUsers = users.map(u => ({
        ...u,
        _nombre: [u.first_name, u.middle_name, u.last_name, u.second_last_name].filter(Boolean).join(" "),
        _rol: roleMap[String(u.role_id)] || String(u.role_id),
        _facultad: facultyMap[String(u.faculty_id)] || String(u.faculty_id),
        _estado: statusMap[String(u.status_id)] || String(u.status_id),
    }));
    let editingUserId = null;
    let deletingUserId = null;
    let isUserModalOpen = false;
    let isDeleteModalOpen = false;
    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    const statusMap = {
        "1": "Activo",
        "2": "Inactivo",
        "3": "Pendiente",
        "4": "Finalizado",
        "5": "Cancelado",
        "6": "Suspendido",
    };

    const facultyMap = {
        "1": "Ingeniería de Sistemas",
        "2": "Medicina",
        "3": "Derecho",
        "4": "Administración de Empresas",
        "5": "Arquitectura",
        "6": "Psicología",
        "7": "Economía",
        "8": "Comunicación Social",
        "9": "Biología",
        "10": "Matemáticas",
    };

    const roleMap = {
        "1": "Administrador",
        "2": "Docente",
        "3": "Estudiante",
    };

    const statusColorMap = {
        "1": "bg-green-100 text-green-700", // Activo
        "2": "bg-red-100 text-red-700", // Inactivo
        "3": "bg-yellow-100 text-yellow-800", // Pendiente
        "4": "bg-blue-100 text-blue-700", // Finalizado
        "5": "bg-gray-100 text-gray-700", // Cancelado
        "6": "bg-orange-100 text-orange-700", // Suspendido
    };

    // Form data
    let form = {
        identity_document: "",
        first_name: "",
        middle_name: "",
        last_name: "",
        second_last_name: "",
        email: "",
        password_hash: "",
        role_id: 1,
        faculty_id: null,
        status_id: 1,
    };
    console.log("Admin.svelte cargado");

    onMount(() => {
        console.log("onMount ejecutado");
        loadUsers();
    });

    async function loadUsers() {
        loading = true;
        try {
            const data = await getUsuarios();
            console.log("Respuesta API:", data);
            users = data || [];
        } catch (err) {
            console.error(err);
            users = [];
        } finally {
            loading = false;
        }
    }

    function cerrarSesion() {
        logout();
        navigate("/");
    }

    function openModal() {
        editingUserId = null;
        form = {
            identity_document: "",
            first_name: "",
            middle_name: "",
            last_name: "",
            second_last_name: "",
            email: "",
            password_hash: "",
            role_id: 1,
            faculty_id: null,
            status_id: 1,
        };
        isUserModalOpen = true;
    }

    function openEditModal(user) {
        editingUserId = user.user_id;
        form = {
            identity_document: user.identity_document,
            first_name: user.first_name,
            middle_name: user.middle_name || "",
            last_name: user.last_name,
            second_last_name: user.second_last_name || "",
            email: user.email,
            password_hash: "", // Leave empty unless modifying
            role_id: user.role_id,
            faculty_id: user.faculty_id || null,
            status_id: user.status_id,
        };
        isUserModalOpen = true;
    }

    $: if (!isUserModalOpen && editingUserId !== null) editingUserId = null;

    function closeModal() {
        isUserModalOpen = false;
        editingUserId = null;
    }

    function openDeleteModal(userId) {
        deletingUserId = userId;
        isDeleteModalOpen = true;
    }

    $: if (!isDeleteModalOpen && deletingUserId !== null) deletingUserId = null;

    function closeDeleteModal() {
        isDeleteModalOpen = false;
        deletingUserId = null;
    }

    function displayToast(message, type) {
        toastMessage = message;
        toastType = type;
        showToast = true;
        const duration = type === "error" ? 6000 : 3000;
        setTimeout(() => {
            showToast = false;
        }, duration);
    }

    async function saveUser() {
        const body: UserCreate = {
            identity_document: form.identity_document,
            first_name: form.first_name,
            middle_name: form.middle_name || null,
            last_name: form.last_name,
            second_last_name: form.second_last_name || null,
            email: form.email,
            password_hash: form.password_hash,
            // @ts-ignore
            role_id: parseInt(form.role_id),
            faculty_id: form.faculty_id ? parseInt(form.faculty_id) : null,
            // @ts-ignore
            status_id: parseInt(form.status_id),
        };

        try {
            if (editingUserId) {
                // 👇 obtener usuario actual si no hay password
                if (!body.password_hash) {
                    const current = await getUsuario(editingUserId);
                    body.password_hash = current.password_hash;
                }

                await updateUsuario(editingUserId, body);
            } else {
                await createUsuario(body);
            }

            closeModal();
            displayToast(
                editingUserId
                    ? "Usuario actualizado correctamente"
                    : "Usuario creado correctamente",
                "success",
            );

            loadUsers();
        } catch (err) {
            console.error(err);
            displayToast("Error al guardar el usuario", "error");
        }
    }

    async function confirmDelete() {
        try {
            await deleteUsuario(deletingUserId);

            closeDeleteModal();
            displayToast("Usuario eliminado correctamente", "success");
            loadUsers();
        } catch (err: any) {
            console.error(err);
            const msg = err?.message || "Error al eliminar el usuario";
            displayToast(msg, "error");
            closeDeleteModal();
        }
    }
</script>

<div class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="bg-gray-800 text-white flex justify-between items-center px-6 py-3 shadow-lg sticky top-0 z-30">
        <div class="flex items-center gap-3">
            <button on:click={toggleMobileMenu} class="md:hidden p-1.5 hover:bg-white/10 rounded transition" aria-label="Menú">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
            <svg class="w-7 h-7 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                />
            </svg>
            <h1 class="text-lg font-bold">Panel Administrador</h1>
        </div>
        <Button on:click={cerrarSesion} variant="danger" class="px-4 py-1.5 text-sm font-medium">
            Cerrar sesión
        </Button>
    </nav>

    <div class="flex flex-1 items-stretch relative">
        {#if isMobileMenuOpen}
            <button class="md:hidden fixed inset-0 w-full h-full bg-black/50 z-40 transition-opacity border-0" on:click={toggleMobileMenu} aria-label="Cerrar modal"></button>
        {/if}

        <!-- Sidebar -->
        <aside class="{isMobileMenuOpen ? 'flex' : 'hidden'} md:flex shrink-0 flex-col absolute inset-y-0 left-0 md:relative z-50 w-64 bg-gray-800 border-r border-gray-700 shadow-md p-5 transition-transform duration-300">
            <h2 class="font-semibold text-gray-400 text-xs uppercase tracking-wider mb-4">
                Administración
            </h2>
            <ul class="space-y-1">
                <li>
                    <button
                        on:click={() => { currentView = "usuarios"; isMobileMenuOpen = false; }}
                        class="w-full text-left px-3 py-2 rounded-lg font-medium text-sm transition {currentView === 'usuarios' ? 'bg-blue-600 text-white shadow' : 'hover:bg-gray-700 text-gray-300 hover:text-white'}"
                        >Gestionar Usuarios</button>
                </li>
                <li>
                    <button
                        on:click={() => { currentView = "cursos"; isMobileMenuOpen = false; }}
                        class="w-full text-left px-3 py-2 rounded-lg font-medium text-sm transition {currentView === 'cursos' ? 'bg-blue-600 text-white shadow' : 'hover:bg-gray-700 text-gray-300 hover:text-white'}"
                        >Gestionar Cursos</button>
                </li>
                <li>
                    <button
                        on:click={() => { currentView = "inscripciones"; isMobileMenuOpen = false; }}
                        class="w-full text-left px-3 py-2 rounded-lg font-medium text-sm transition {currentView === 'inscripciones' ? 'bg-blue-600 text-white shadow' : 'hover:bg-gray-700 text-gray-300 hover:text-white'}"
                        >Gestionar Inscripciones</button>
                </li>
                <li>
                    <button
                        on:click={() => { currentView = "reportes"; isMobileMenuOpen = false; }}
                        class="w-full text-left px-3 py-2 rounded-lg font-medium text-sm transition {currentView === 'reportes' ? 'bg-blue-600 text-white shadow' : 'hover:bg-gray-700 text-gray-300 hover:text-white'}"
                        >Reportes</button>
                </li>
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0 overflow-x-hidden">
            {#if currentView === "usuarios"}
                <!-- Header -->
                <PageHeader title="Gestión de Usuarios" subtitle="Crear, editar y eliminar usuarios del sistema">
                    <svelte:fragment slot="action">
                        <Button on:click={openModal} variant="primary" class="px-5 py-2.5 shadow">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                            Nuevo Usuario
                        </Button>
                    </svelte:fragment>
                </PageHeader>

                <!-- Toast Message -->
                <Toast message={toastMessage} type={toastType} show={showToast} />

                <!-- Tabla de usuarios -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                    <DataTable
                        data={tableUsers}
                        columns={userColumns}
                        {loading}
                        searchFn={userSearchFn}
                        searchPlaceholder="Buscar por nombre, email, rol..."
                        loadingText="Cargando usuarios..."
                        emptyText="No se encontraron usuarios"
                        tableClass="w-full min-w-[1000px]"
                        let:row
                    >
                        <tr class="border-b hover:bg-gray-50 transition">
                            <td class="px-4 py-3 text-gray-700 font-medium">{row.user_id}</td>
                            <td class="px-4 py-3 text-gray-600">{row.identity_document}</td>
                            <td class="px-4 py-3 text-gray-600">{row._nombre}</td>
                            <td class="px-4 py-3 text-gray-600">{row.email}</td>
                            <td class="px-4 py-3">
                                <Badge color="purple" text={row._rol} />
                            </td>
                            <td class="px-4 py-3 text-gray-600">{row._facultad}</td>
                            <td class="px-4 py-3">
                                <Badge class={statusColorMap[String(row.status_id).trim()] || 'bg-gray-100 text-gray-700'} color="none" text={row._estado} />
                            </td>
                            <td class="px-4 py-3 text-center">
                                <div class="flex justify-center gap-2">
                                    <button
                                        on:click={() => openEditModal(row)}
                                        class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                                        title="Editar"
                                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                                        </svg>
                                    </button>
                                    <button
                                        on:click={() => openDeleteModal(row.user_id)}
                                        class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition"
                                        title="Eliminar"
                                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                        </svg>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </DataTable>
                </div>

                <!-- Modal Crear/Editar -->
                <Modal bind:isOpen={isUserModalOpen} title={editingUserId ? "Editar Usuario" : "Nuevo Usuario"} maxWidth="max-w-2xl">
                    <form class="p-6 space-y-4" on:submit|preventDefault={saveUser}>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input id="id_doc" required bind:value={form.identity_document} label="Documento de Identidad" />
                            <Input id="email" type="email" required bind:value={form.email} label="Email" />
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input id="fname" required bind:value={form.first_name} label="Primer Nombre" />
                            <Input id="mname" bind:value={form.middle_name} label="Segundo Nombre" />
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input id="lname" required bind:value={form.last_name} label="Primer Apellido" />
                            <Input id="slname" bind:value={form.second_last_name} label="Segundo Apellido" />
                        </div>
                        <div>
                            <Input id="pass" type="password" required={!editingUserId} placeholder={editingUserId ? "Dejar vacío para mantener la actual" : ""} bind:value={form.password_hash} label="Contraseña" />
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Select id="role_id" required bind:value={form.role_id} label="Rol" options={[
                                {value: 1, label: 'Administrador'},
                                {value: 2, label: 'Docente'},
                                {value: 3, label: 'Estudiante'}
                            ]} />
                            <Select id="fac_id" required bind:value={form.faculty_id} label="Facultad" options={[
                                {value: 1, label: 'Ingeniería de Sistemas'},
                                {value: 2, label: 'Medicina'},
                                {value: 3, label: 'Derecho'},
                                {value: 4, label: 'Administración de Empresas'},
                                {value: 5, label: 'Arquitectura'},
                                {value: 6, label: 'Psicología'},
                                {value: 7, label: 'Economía'},
                                {value: 8, label: 'Comunicación Social'},
                                {value: 9, label: 'Biología'},
                                {value: 10, label: 'Matemáticas'}
                            ]} />
                            <Select id="status_id" required bind:value={form.status_id} label="Estado" options={[
                                {value: 1, label: 'Activo'},
                                {value: 2, label: 'Inactivo'},
                                {value: 3, label: 'Pendiente'},
                                {value: 4, label: 'Finalizado'},
                                {value: 5, label: 'Cancelado'},
                                {value: 6, label: 'Suspendido'}
                            ]} />
                        </div>
                        <div class="flex justify-end gap-3 pt-4 border-t mt-6">
                            <Button type="button" on:click={closeModal} variant="secondary">Cancelar</Button>
                            <Button type="submit" variant="primary">Guardar</Button>
                        </div>
                    </form>
                </Modal>

                <!-- Modal Confirmar Eliminar -->
                <Modal bind:isOpen={isDeleteModalOpen} title="Eliminar Usuario" maxWidth="max-w-md">
                    <div class="px-6 py-4 pb-6 text-center">
                        <div class="mx-auto w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mb-4">
                            <svg class="w-7 h-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </div>
                        <p class="text-gray-500 text-sm mb-6">
                            Esta acción no se puede deshacer. El usuario será eliminado permanentemente.
                        </p>
                        <div class="flex justify-center gap-3">
                            <Button on:click={closeDeleteModal} variant="secondary">Cancelar</Button>
                            <Button on:click={confirmDelete} variant="danger">Eliminar</Button>
                        </div>
                    </div>
                </Modal>
            {:else if currentView === "cursos"}
                <AdminCursos />
            {:else if currentView === "inscripciones"}
                <AdminInscripciones />
            {:else if currentView === "reportes"}
                <AdminReportes />
            {/if}
        </main>
    </div>
</div>
