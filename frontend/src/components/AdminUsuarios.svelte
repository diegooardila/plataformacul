<script lang="ts">
    import { onMount } from "svelte";
    import {
        getUsuarios,
        getUsuario,
        createUsuario,
        updateUsuario,
        deleteUsuario,
    } from "../lib/services/users";
    import type { UserCreate } from "../lib/services/users";

    import DataTable from "./DataTable.svelte";
    import Input from "./ui/Input.svelte";
    import Select from "./ui/Select.svelte";
    import Button from "./ui/Button.svelte";
    import Toast from "./ui/Toast.svelte";
    import Modal from "./ui/Modal.svelte";
    import Badge from "./ui/Badge.svelte";
    import PageHeader from "./ui/PageHeader.svelte";

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
        "1": "bg-green-100 text-green-700",
        "2": "bg-red-100 text-red-700",
        "3": "bg-yellow-100 text-yellow-800",
        "4": "bg-blue-100 text-blue-700",
        "5": "bg-gray-100 text-gray-700",
        "6": "bg-orange-100 text-orange-700",
    };

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

    onMount(async () => {
        await loadUsers();
    });

    async function loadUsers() {
        loading = true;
        try {
            const data = await getUsuarios();
            users = data || [];
        } catch (err) {
            console.error(err);
            users = [];
        } finally {
            loading = false;
        }
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
            password_hash: "",
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
        setTimeout(() => { showToast = false; }, duration);
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
                editingUserId ? "Usuario actualizado correctamente" : "Usuario creado correctamente",
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

<div class="flex-1">
    <PageHeader title="Gestión de Usuarios" subtitle="Crear, editar y eliminar usuarios del sistema">
        <svelte:fragment slot="action">
            <Button on:click={openModal} variant="primary" class="px-5 py-2.5 shadow">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                Nuevo Usuario
            </Button>
        </svelte:fragment>
    </PageHeader>

    <Toast message={toastMessage} type={toastType} show={showToast} />

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
</div>
