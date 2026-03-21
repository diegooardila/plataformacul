<script>
    import { navigate } from "svelte-routing";
    import { onMount } from "svelte";

    let currentView = 'dashboard';
    let availableCourses = [];
    let myCourses = [];
    let loading = false;

    // For demonstration, use a fixed student ID (User 3)
    const studentId = 3;

    onMount(() => {
        loadCourses();
    });

    async function loadCourses() {
        loading = true;
        try {
            // Fetch all courses
            const resCourses = await fetch(`/get_courses`);
            let allCourses = [];
            if (resCourses.ok) {
                const data = await resCourses.json();
                allCourses = data.resultado || [];
                availableCourses = allCourses;
            }

            // Fetch enrollments for the current student
            const resEnrollments = await fetch(`/get_enrollments`);
            if (resEnrollments.ok) {
                const data = await resEnrollments.json();
                const enrollments = data.resultado || [];
                
                // Filter enrollments for this student
                const myEnrollments = enrollments.filter(e => e.student_user_id === studentId);
                
                // Map the enrollment course_ids to the actual course details
                myCourses = myEnrollments.map(e => allCourses.find(c => c.course_id === e.course_id)).filter(Boolean);
            }

        } catch (err) {
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function setView(view) {
        currentView = view;
    }

    function cerrarSesion() {
        navigate("/");
    }
</script>

<div class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navbar -->
    <div class="bg-blue-700 text-white flex justify-between items-center p-4 shadow z-10 relative">
        <h1 class="text-lg font-bold">Panel del Estudiante</h1>
        <button on:click={cerrarSesion} class="bg-red-500 hover:bg-red-600 text-white px-4 py-1.5 rounded transition shadow-sm cursor-pointer">
            Cerrar sesión
        </button>
    </div>

    <div class="flex flex-1 items-stretch">
        <!-- Sidebar -->
        <div class="w-64 bg-blue-700 text-white shadow p-4 hidden md:block">
            <h2 class="font-semibold mb-4 text-sm uppercase tracking-wider text-blue-200">Menú</h2>
            <ul class="space-y-2">
                <li><button on:click={() => setView('dashboard')} class="w-full text-left px-3 py-2 rounded transition {currentView === 'dashboard' ? 'bg-blue-600 shadow-sm' : 'hover:bg-blue-600'}">Dashboard</button></li>
                <li><button on:click={() => setView('cursos')} class="w-full text-left px-3 py-2 rounded transition {currentView === 'cursos' ? 'bg-blue-600 shadow-sm' : 'hover:bg-blue-600'}">Cursos disponibles</button></li>
                <li><button on:click={() => setView('inscripciones')} class="w-full text-left px-3 py-2 rounded transition {currentView === 'inscripciones' ? 'bg-blue-600 shadow-sm' : 'hover:bg-blue-600'}">Mis inscripciones</button></li>
                <li><button on:click={() => setView('perfil')} class="w-full text-left px-3 py-2 rounded transition {currentView === 'perfil' ? 'bg-blue-600 shadow-sm' : 'hover:bg-blue-600'}">Perfil</button></li>
            </ul>
        </div>

        <!-- Contenido -->
        <div class="flex-1 p-6 sm:p-10">
            {#if currentView === 'dashboard'}
                <h2 class="text-3xl font-bold text-gray-800 mb-6">
                    Bienvenido Estudiante
                </h2>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
                    <p class="text-gray-600">"Inscríbete y expande tu increíble conocimiento."</p>
                </div>

                <h3 class="text-2xl font-bold text-gray-800 mb-4">Mis Cursos Actuales</h3>
                {#if loading}
                    <p class="text-gray-500">Cargando tus cursos...</p>
                {:else if myCourses.length === 0}
                    <div class="bg-blue-50 p-6 rounded-xl border border-blue-100">
                        <p class="text-blue-800">No estás inscrito en ningún curso actualmente. Ve a "Cursos disponibles" para inscribirte.</p>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {#each myCourses as curso}
                            <div class="bg-white p-6 rounded-xl shadow border-l-4 border-green-500 hover:shadow-md transition relative">
                                <span class="absolute top-4 right-4 bg-green-100 text-green-800 text-xs font-semibold px-2.5 py-0.5 rounded">Inscrito</span>
                                <h3 class="text-xl font-bold text-gray-800 mb-2 pr-16">{curso.course_name}</h3>
                                <p class="text-gray-600 text-sm mb-1"><strong>Código:</strong> {curso.course_code}</p>
                                <p class="text-gray-600 text-sm mb-1"><strong>Horario:</strong> {curso.schedule}</p>
                                <p class="text-gray-600 text-sm mt-4 text-green-600 font-medium">Estado: Activo</p>
                            </div>
                        {/each}
                    </div>
                {/if}
            {:else if currentView === 'cursos'}
                <h2 class="text-3xl font-bold text-gray-800 mb-6">
                    Cursos Disponibles
                </h2>
                
                {#if loading}
                    <p class="text-gray-500">Cargando cursos...</p>
                {:else if availableCourses.length === 0}
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <p class="text-gray-600">No hay cursos disponibles en este momento.</p>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {#each availableCourses as curso}
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                                <h3 class="text-xl font-bold text-blue-800 mb-2">{curso.course_name}</h3>
                                <p class="text-gray-600 text-sm mb-1"><strong>Código:</strong> {curso.course_code}</p>
                                <p class="text-gray-600 text-sm mb-1"><strong>Horario:</strong> {curso.schedule}</p>
                                <p class="text-gray-600 text-sm mb-4"><strong>Cupos:</strong> {curso.max_capacity}</p>
                                <button class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition cursor-pointer">Inscribirme</button>
                            </div>
                        {/each}
                    </div>
                {/if}
            {:else if currentView === 'inscripciones'}
                <h2 class="text-3xl font-bold text-gray-800 mb-6">Mis Inscripciones</h2>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <p class="text-gray-600">Aún no tienes inscripciones activas.</p>
                </div>
            {:else if currentView === 'perfil'}
                <h2 class="text-3xl font-bold text-gray-800 mb-6">Mi Perfil</h2>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <p class="text-gray-600">Aquí verás tu información personal.</p>
                </div>
            {/if}
        </div>
    </div>
</div>
