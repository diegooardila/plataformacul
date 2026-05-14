<script lang="ts">
    import { onMount } from "svelte";
    import { fade } from "svelte/transition";
    import { navigate } from "svelte-routing";
    import { getSession, logout } from "../lib/services/auth";

    import AdminUsuarios from "../components/AdminUsuarios.svelte";
    import AdminCursos from "../components/AdminCursos.svelte";
    import AdminInscripciones from "../components/AdminInscripciones.svelte";
    import AdminReportes from "../components/AdminReportes.svelte";
    import Button from "../components/ui/Button.svelte";
    import PageHeader from "../components/ui/PageHeader.svelte";
    import Badge from "../components/ui/Badge.svelte";

    let currentView = "usuarios";
    let isMobileMenuOpen = false;

    let adminId = null;
    let adminName = "Administrador";
    let profilePicUrl = null;

    function handlePhotoUpload(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                profilePicUrl = event.target.result as string;
                if (adminId) localStorage.setItem(`profile_pic_${adminId}`, profilePicUrl);
            };
            reader.readAsDataURL(file);
        }
    }

    function removePhoto() {
        profilePicUrl = null;
        if (adminId) localStorage.removeItem(`profile_pic_${adminId}`);
    }

    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

    onMount(() => {
        const session = getSession();
        if (!session.user_id || session.role_id !== 1) {
            navigate("/");
            return;
        }
        adminId = session.user_id;
        adminName = session.user_name || "Administrador";
        const savedPic = localStorage.getItem(`profile_pic_${adminId}`);
        if (savedPic) profilePicUrl = savedPic;
    });

    function cerrarSesion() {
        logout();
        navigate("/");
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
                <li>
                    <button
                        on:click={() => { currentView = "perfil"; isMobileMenuOpen = false; }}
                        class="w-full text-left px-3 py-2 rounded-lg font-medium text-sm transition {currentView === 'perfil' ? 'bg-blue-600 text-white shadow' : 'hover:bg-gray-700 text-gray-300 hover:text-white'}"
                        >Perfil</button>
                </li>
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
            {#key currentView}
                <div in:fade={{ duration: 180 }}>
                    {#if currentView === "usuarios"}
                        <AdminUsuarios />
                    {:else if currentView === "cursos"}
                        <AdminCursos />
                    {:else if currentView === "inscripciones"}
                        <AdminInscripciones />
                    {:else if currentView === "reportes"}
                        <AdminReportes />
                    {:else if currentView === "perfil"}
                        <PageHeader title="Mi Perfil" />
                        <div class="max-w-2xl bg-white rounded-xl shadow-sm border border-gray-100 p-8 flex flex-col items-center sm:flex-row sm:items-start gap-8">
                            <div class="flex flex-col items-center shrink-0">
                                <div class="w-32 h-32 rounded-full bg-blue-50 border-4 border-white shadow-lg overflow-hidden flex items-center justify-center mb-4 relative group">
                                    {#if profilePicUrl}
                                        <img src={profilePicUrl} alt="Foto de perfil" class="w-full h-full object-cover" />
                                    {:else}
                                        <svg class="w-16 h-16 text-blue-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                                    {/if}
                                    <label class="absolute inset-0 bg-black/40 text-white flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                                        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                        <span class="text-xs font-semibold">Cambiar</span>
                                        <input type="file" accept="image/*" class="hidden" on:change={handlePhotoUpload} />
                                    </label>
                                </div>
                                {#if profilePicUrl}
                                    <button on:click={removePhoto} class="mt-2 text-xs font-medium text-red-500 hover:text-red-700 transition">Quitar foto</button>
                                {/if}
                            </div>
                            <div class="flex-1 w-full space-y-4">
                                <div>
                                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Nombre Completo</h3>
                                    <p class="text-xl font-bold text-gray-800">{adminName}</p>
                                </div>
                                <div>
                                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Rol y Estado</h3>
                                    <div class="inline-flex items-center mt-1 gap-2">
                                        <span class="relative flex h-3 w-3">
                                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                          <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                        </span>
                                        <Badge color="green" text="Activo" />
                                        <Badge color="blue" text="Administrador" />
                                    </div>
                                </div>
                                <div class="pt-4 border-t border-gray-100">
                                    <p class="text-sm text-gray-500">Puedes hacer clic en el avatar para actualizar tu imagen de perfil en forma local.</p>
                                </div>
                            </div>
                        </div>
                    {/if}
                </div>
            {/key}
        </main>
    </div>
</div>
