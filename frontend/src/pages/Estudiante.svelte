<script>
    import { navigate } from "svelte-routing";
    import { onMount } from "svelte";

    import { getCourses } from "../lib/services/courses";
    import { createEnrollment, getEnrollments } from "../lib/services/enrollments";
    import { getSession, logout } from "../lib/services/auth";

    let currentView = 'dashboard';
    let availableCourses = [];
    let myCourses = [];
    let loading = false;
    
    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    // Variables de sesión dinámica
    let studentId = null;
    let studentName = "Estudiante";
    let studentStatusId = null;

    onMount(() => {
        const session = getSession();
        if (session.user_id && session.role_id === 3) {
            studentId = session.user_id;
            studentName = session.user_name || "Estudiante";
            studentStatusId = session.status_id || 1;
            loadCourses();
        } else {
            navigate("/");
        }
    });

    async function loadCourses() {
        loading = true;
        try {
            const [allCourses, allEnrollments] = await Promise.all([
                getCourses(),
                getEnrollments()
            ]);

            availableCourses = allCourses || [];
            
            // Filter enrollments for this student
            const myEnrollments = (allEnrollments || []).filter(e => e.student_user_id === studentId);
            
            // Map the enrollment course_ids to the actual course details
            myCourses = myEnrollments.map(e => availableCourses.find(c => c.course_id === e.course_id)).filter(Boolean);

        } catch (err) {
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function setView(view) {
        currentView = view;
    }

    const statusMap = {
        1: "Activo",
        2: "Inactivo",
        3: "Pendiente",
        4: "Finalizado",
        5: "Cancelado",
        6: "Suspendido"
    };

    function tryEnroll(courseId) {
        if (studentStatusId !== 1) {
            const estadoTexto = statusMap[studentStatusId] || "Desconocido";
            displayToast(`Estudiante Con Proceso En Estado ${estadoTexto}, Acérquese A Admisiones.`, "error");
            return;
        }
        inscribirCurso(courseId);
    }

    function displayToast(message, type) {
        toastMessage = message;
        toastType = type;
        showToast = true;
        setTimeout(() => { showToast = false; }, 3000);
    }

    async function inscribirCurso(courseId) {
        try {
            await createEnrollment({
                student_user_id: studentId,
                course_id: courseId,
                registration_date: new Date().toISOString(),
                status_id: 1 // Activo
            });
            displayToast("¡Inscripción exitosa!", "success");
            await loadCourses(); // Reload so it updates "Mis cursos"
            setView('dashboard'); // Redirect to dashboard to see it
        } catch (err) {
            console.error(err);
            displayToast("Error al inscribirse al curso", "error");
        }
    }

    function cerrarSesion() {
        logout();
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

    <!-- Toast Message -->
    {#if showToast}
        <div class="fixed top-20 right-5 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-50 transition-all {toastType === 'success' ? 'bg-green-600' : 'bg-red-600'}">
            {toastMessage}
        </div>
    {/if}

    <div class="flex flex-1 items-stretch">
        {#if studentStatusId !== 1}
            <div class="w-full flex flex-col items-center justify-center p-6 bg-gray-50">
               <div class="bg-red-50 p-10 rounded-2xl w-full max-w-lg text-center border border-red-100 shadow">
                   <svg class="w-20 h-20 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                   <h2 class="text-3xl font-bold text-red-700 mb-2">Acceso Restringido</h2>
                   <p class="text-red-700 font-medium text-base mt-6">
                       El perfil de estudiante se encuentra en estado <span class="bg-red-200 text-red-800 px-2 py-1 rounded inline-block font-bold">{(statusMap[studentStatusId] || 'Desconocido').toUpperCase()}</span>.
                       No cuenta con los permisos necesarios para visualizar la lista de cursos ni gestionar las inscripciones. Si esto es un error, por favor contacte a soporte o admisiones.
                   </p>
               </div>
            </div>
        {:else}
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
                    Bienvenido/a, {studentName}
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
                                
                                {#if myCourses.some(mc => mc.course_id === curso.course_id)}
                                    <button disabled class="w-full bg-gray-300 text-gray-500 font-medium py-2 rounded-lg cursor-not-allowed">Ya inscrito</button>
                                {:else}
                                    <button on:click={() => tryEnroll(curso.course_id)} class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition cursor-pointer">Inscribirme</button>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/if}
            {:else if currentView === 'inscripciones'}
                <h2 class="text-3xl font-bold text-gray-800 mb-6">Historial de Inscripciones</h2>
                {#if myCourses.length === 0}
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <p class="text-gray-600">Aún no tienes inscripciones activas.</p>
                    </div>
                {:else}
                    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                        <table class="w-full text-sm">
                            <thead class="bg-gray-50 border-b">
                                <tr>
                                    <th class="text-left px-6 py-3 text-gray-600 font-semibold">Código</th>
                                    <th class="text-left px-6 py-3 text-gray-600 font-semibold">Curso</th>
                                    <th class="text-left px-6 py-3 text-gray-600 font-semibold">Horario</th>
                                    <th class="text-center px-6 py-3 text-gray-600 font-semibold">Estado</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                {#each myCourses as curso}
                                    <tr class="hover:bg-gray-50 transition">
                                        <td class="px-6 py-3 font-medium text-gray-800">{curso.course_code}</td>
                                        <td class="px-6 py-3 text-gray-600">{curso.course_name}</td>
                                        <td class="px-6 py-3 text-gray-600">{curso.schedule}</td>
                                        <td class="px-6 py-3 text-center">
                                            <span class="inline-flex items-center gap-1.5 py-1 px-2.5 rounded-full text-xs font-medium bg-green-100 text-green-700">Activa</span>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            {:else if currentView === 'perfil'}
                <h2 class="text-3xl font-bold text-gray-800 mb-6">Mi Perfil</h2>
                <div class="bg-white p-8 rounded-xl shadow-sm border border-gray-100 max-w-2xl">
                    <div class="flex items-center gap-6 mb-8">
                        <div class="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-3xl font-bold uppercase">
                            {studentName.charAt(0)}
                        </div>
                        <div>
                            <h3 class="text-2xl font-bold text-gray-800">{studentName}</h3>
                            <p class="text-gray-500 font-medium tracking-wide text-sm mt-1">ESTUDIANTE ACTIVO</p>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="grid grid-cols-3 border-b border-gray-50 pb-4">
                            <span class="text-gray-500 font-medium">Nombre de usuario</span>
                            <span class="col-span-2 text-gray-800 font-medium">{studentName}</span>
                        </div>
                        <div class="grid grid-cols-3 border-b border-gray-50 pb-4">
                            <span class="text-gray-500 font-medium">ID del Sistema</span>
                            <span class="col-span-2 text-gray-800 font-medium">{studentId}</span>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
        {/if}
    </div>
</div>
