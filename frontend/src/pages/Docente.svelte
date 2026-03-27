<script>
    import { navigate } from "svelte-routing";

    function cerrarSesion() {
        navigate("/");
    }
</script>

<div class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navbar -->
    <div class="bg-indigo-600 text-white flex justify-between items-center p-4 shadow">
        <h1 class="text-lg font-bold">Panel del Docente</h1>
        <button on:click={cerrarSesion} class="bg-red-500 hover:bg-red-600 text-white px-4 py-1.5 rounded transition shadow-sm">
            Cerrar sesión
        </button>
    </div>

    <div class="flex flex-1">
        <!-- Sidebar -->
        <div class="w-64 bg-indigo-600 text-white h-auto sm:h-[calc(100vh-60px)] shadow p-4 hidden md:block">
            <h2 class="font-semibold mb-4 text-sm uppercase tracking-wider text-blue-200">Menú</h2>
            <ul class="space-y-2">
                <li><button class="w-full text-left px-3 py-2 rounded hover:bg-blue-600 transition">Cursos asignados</button></li>
                <li><button class="w-full text-left px-3 py-2 rounded hover:bg-blue-600 transition">Estudiantes inscritos</button></li>
                <li><button class="w-full text-left px-3 py-2 rounded hover:bg-blue-600 transition">Calificaciones</button></li>
                <li><button class="w-full text-left px-3 py-2 rounded hover:bg-blue-600 transition">Perfil</button></li>
            </ul>
        </div>

        <!-- Contenido -->
        <div class="flex-1 p-6 sm:p-10">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">
                Bienvenido Docente
            </h2>
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <p class="text-gray-600">Aquí podrás ver los cursos asignados y gestionar las calificaciones de tus estudiantes.</p>
            </div>
        </div>
    </div>
</div>
