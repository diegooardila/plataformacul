<script lang="ts">
    import { onMount } from "svelte";
    import { navigate } from "svelte-routing";
    import { getSession, logout } from "../lib/services/auth";

    import AdminUsuarios from "../components/AdminUsuarios.svelte";
    import AdminCursos from "../components/AdminCursos.svelte";
    import AdminInscripciones from "../components/AdminInscripciones.svelte";
    import AdminReportes from "../components/AdminReportes.svelte";
    import Button from "../components/ui/Button.svelte";

    let currentView = "usuarios";
    let isMobileMenuOpen = false;

    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

    onMount(() => {
        const session = getSession();
        if (!session.user_id || session.role_id !== 1) {
            navigate("/");
        }
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
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
            {#if currentView === "usuarios"}
                <AdminUsuarios />
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
