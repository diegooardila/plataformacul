<script>
    import { navigate } from "svelte-routing";

    let username = "";
    let password = "";

    function ingresarEstudiante() {
        // En una app real, aqui iria la autenticacion
        navigate("/estudiante");
    }

    function ingresarDocente() {
        navigate("/docente");
    }

    function ingresarAdmin() {
        navigate("/admin");
    }
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-100 via-blue-50 to-gray-200 flex items-center justify-center p-4">
    <div class="bg-white shadow-xl rounded-xl overflow-hidden flex flex-col md:flex-row w-full max-w-5xl">

        <!-- Panel izquierdo -->
        <div class="md:w-1/2 bg-gray-50 flex flex-col justify-center items-center p-10 text-center">
            <h1 class="text-4xl font-bold text-blue-600 mb-4">
                Sistema Académico
            </h1>
            <p class="text-gray-600 max-w-sm">
                PLATAFORMA DE INSCRIPCIÓN Y CONTROL DE CURSOS ELECTIVOS.
            </p>
            <!-- Note: You might need to move `img/logo-03.jpg` to `public/img` in Vite -->
            <img src="/img/logo.png" alt="Logo CUL" class="w-48 mt-8 drop-shadow-md" />
        </div>

        <!-- Panel derecho -->
        <div class="md:w-1/2 p-10 flex flex-col justify-center">
            <h2 class="text-2xl font-bold text-gray-700 text-center mb-6">
                Iniciar sesión
            </h2>

            <form class="space-y-5" on:submit|preventDefault>
                <div>
                    <label class="block text-gray-600 text-sm mb-1" for="username">Usuario</label>
                    <input id="username" type="text" bind:value={username} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                </div>

                <div>
                    <label class="block text-gray-600 text-sm mb-1" for="password">Contraseña</label>
                    <input id="password" type="password" bind:value={password} class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                </div>

                <div class="space-y-3 pt-2">
                    <button type="button" on:click={ingresarEstudiante} class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition shadow-sm">
                        Ingresar como Estudiante
                    </button>

                    <button type="button" on:click={ingresarDocente} class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg transition shadow-sm">
                        Ingresar como Docente
                    </button>

                    <button type="button" on:click={ingresarAdmin} class="w-full bg-gray-800 hover:bg-gray-900 text-white font-medium py-2 rounded-lg transition shadow-sm">
                        Ingresar como Administrador
                    </button>
                </div>
            </form>
        </div>

    </div>
</div>
