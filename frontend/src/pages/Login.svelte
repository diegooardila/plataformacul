<script lang="ts">
    import { navigate } from "svelte-routing";
    import { login, logout } from "../lib/services/auth";
    import Input from "../components/ui/Input.svelte";
    import Button from "../components/ui/Button.svelte";

    let username = "";
    let password = "";
    let isLoading = false;
    let errorMessage = "";
    let selectedRole = 3; // 1: Admin, 2: Docente, 3: Estudiante

    async function handleLogin() {
        if (!username || !password) {
            errorMessage = "Por favor ingresa tu correo y contraseña";
            return;
        }

        isLoading = true;
        errorMessage = "";

        try {
            const res = await login(username, password, selectedRole);
            const user = res.user;
            
            // Validar si el rol que el usuario escogió en la interfaz coincide exactamente con su rol en la BD
            let allowed = false;
            
            if (user.role_id === selectedRole) {
                allowed = true; // Logró hacer match correcto
            }

            if (!allowed) {
                errorMessage = "Credenciales Incorrectas. Intenta Cambiar De Rol";
                logout(); // Purgamos el Storage
                return;
            }
            
            // Redirigir basado en el rol de destino seleccionado
            if (selectedRole === 1) {
                navigate("/admin");
            } else if (selectedRole === 2) {
                navigate("/docente");
            } else if (selectedRole === 3) {
                navigate("/estudiante");
            }
        } catch (err) {
            errorMessage = "Correo o contraseña incorrectos";
            console.error(err);
        } finally {
            isLoading = false;
        }
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
            <img src="/img/logo.png" alt="Logo CUL" class="w-48 mt-8 drop-shadow-md" />
        </div>

        <!-- Panel derecho -->
        <div class="md:w-1/2 p-10 flex flex-col justify-center">
            <h2 class="text-2xl font-bold text-gray-700 text-center mb-6">
                Iniciar sesión
            </h2>

            {#if errorMessage}
                <div class="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 border border-red-100 text-center">
                    {errorMessage}
                </div>
            {/if}

            <form class="space-y-5" on:submit|preventDefault={handleLogin}>
                <Input id="username" type="text" bind:value={username} required label="Correo Electrónico" />
                <Input id="password" type="password" bind:value={password} required label="Contraseña" />

                <div>
                    <span class="block text-gray-600 text-sm mb-2 font-medium">Ingresar Destino</span>
                    <div class="grid grid-cols-3 gap-2">
                        <button type="button" class="{selectedRole === 3 ? 'bg-blue-100 text-blue-700 border-blue-500' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'} border rounded-lg py-2 text-sm font-medium transition" on:click={() => selectedRole = 3}>Estudiante</button>
                        <button type="button" class="{selectedRole === 2 ? 'bg-indigo-100 text-indigo-700 border-indigo-500' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'} border rounded-lg py-2 text-sm font-medium transition" on:click={() => selectedRole = 2}>Docente</button>
                        <button type="button" class="{selectedRole === 1 ? 'bg-gray-800 text-gray-100 border-gray-900' : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'} border rounded-lg py-2 text-sm font-medium transition" on:click={() => selectedRole = 1}>Admin</button>
                    </div>
                </div>

                <div class="pt-2">
                    <Button type="submit" disabled={isLoading} fullWidth={true}>
                        {isLoading ? 'Verificando...' : 'Ingresar'}
                    </Button>
                </div>
            </form>
        </div>

    </div>
</div>
