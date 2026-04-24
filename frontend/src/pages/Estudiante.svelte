<script>
    import { navigate } from "svelte-routing";
    import { onMount } from "svelte";

    import { getCourses } from "../lib/services/courses";
    import { createEnrollment, getEnrollments } from "../lib/services/enrollments";
    import { getSession, logout } from "../lib/services/auth";
    import DataTable from "../components/DataTable.svelte";
    import Toast from "../components/ui/Toast.svelte";
    import Card from "../components/ui/Card.svelte";
    import Badge from "../components/ui/Badge.svelte";
    import Button from "../components/ui/Button.svelte";
    import PageHeader from "../components/ui/PageHeader.svelte";

    let currentView = 'dashboard';
    let availableCourses = [];
    let myCourses = [];
    let loading = false;
    
    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    let studentId = null;
    let studentName = "Estudiante";
    let studentStatusId = null;
    let isMobileMenuOpen = false;

    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

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
    <nav class="bg-blue-950 text-white flex justify-between items-center p-4 shadow z-30 relative">
        <div class="flex items-center gap-3">
            <button on:click={toggleMobileMenu} class="md:hidden p-1.5 hover:bg-white/10 rounded transition" aria-label="Menú">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
            <h1 class="text-lg font-bold">Panel del Estudiante</h1>
        </div>
        <Button on:click={cerrarSesion} variant="danger" class="px-4 py-1.5 text-sm">
            Cerrar sesión
        </Button>
    </nav>

    <!-- Toast Message -->
    <Toast message={toastMessage} type={toastType} show={showToast} />

    <div class="flex flex-1 items-stretch relative">
        {#if isMobileMenuOpen}
            <button class="md:hidden fixed inset-0 w-full h-full bg-black/50 z-40 transition-opacity border-0" on:click={toggleMobileMenu} aria-label="Cerrar modal"></button>
        {/if}

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
            <div class="{isMobileMenuOpen ? 'flex' : 'hidden'} md:flex shrink-0 flex-col absolute inset-y-0 left-0 md:relative z-50 w-64 bg-blue-950 text-white shadow p-4 border-r border-blue-900 transition-transform duration-300">
                <h2 class="font-semibold mb-4 text-sm uppercase tracking-wider text-blue-200">Menú</h2>
            <ul class="space-y-2">
                <li><button on:click={() => { setView('dashboard'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2 rounded transition {currentView === 'dashboard' ? 'bg-blue-900 shadow-sm' : 'hover:bg-blue-900'}">Dashboard</button></li>
                <li><button on:click={() => { setView('cursos'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2 rounded transition {currentView === 'cursos' ? 'bg-blue-900 shadow-sm' : 'hover:bg-blue-900'}">Cursos disponibles</button></li>
                <li><button on:click={() => { setView('inscripciones'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2 rounded transition {currentView === 'inscripciones' ? 'bg-blue-900 shadow-sm' : 'hover:bg-blue-900'}">Mis inscripciones</button></li>
                <li><button on:click={() => { setView('perfil'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2 rounded transition {currentView === 'perfil' ? 'bg-blue-900 shadow-sm' : 'hover:bg-blue-900'}">Perfil</button></li>
            </ul>
        </div>

        <!-- Contenido -->
        <div class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
            {#if currentView === 'dashboard'}
                <PageHeader title="Bienvenido/a, {studentName}" />
                <Card class="mb-8">
                    <p class="text-gray-600">"Inscríbete y expande tu increíble conocimiento."</p>
                </Card>

                <h3 class="text-2xl font-bold text-gray-800 mb-4">Mis Cursos Actuales</h3>
                {#if loading}
                    <p class="text-gray-500">Cargando tus cursos...</p>
                {:else if myCourses.length === 0}
                    <div class="bg-blue-50 p-6 rounded-xl border border-blue-100">
                        <p class="text-blue-900">No estás inscrito en ningún curso actualmente. Ve a "Cursos disponibles" para inscribirte.</p>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {#each myCourses as curso}
                            <Card class="border-l-4 border-l-green-500 hover:shadow-md transition relative bg-white">
                                <Badge color="green" text="Inscrito" class="absolute top-4 right-4" />
                                <h3 class="text-xl font-bold text-gray-800 mb-2 pr-16">{curso.course_name}</h3>
                                <p class="text-gray-600 text-sm mb-1"><strong>Código:</strong> {curso.course_code}</p>
                                <p class="text-gray-600 text-sm mb-1"><strong>Horario:</strong> {curso.schedule}</p>
                                <p class="text-gray-600 text-sm mt-4 text-green-600 font-medium">Estado: Activo</p>
                            </Card>
                        {/each}
                    </div>
                {/if}
            {:else if currentView === 'cursos'}
                <PageHeader title="Cursos Disponibles" />
                
                {#if loading}
                    <p class="text-gray-500">Cargando cursos...</p>
                {:else if availableCourses.length === 0}
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <p class="text-gray-600">No hay cursos disponibles en este momento.</p>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {#each availableCourses as curso}
                            <Card class="hover:shadow-md transition">
                                <h3 class="text-xl font-bold text-blue-900 mb-2">{curso.course_name}</h3>
                                <p class="text-gray-600 text-sm mb-1"><strong>Código:</strong> {curso.course_code}</p>
                                <p class="text-gray-600 text-sm mb-1"><strong>Horario:</strong> {curso.schedule}</p>
                                <p class="text-gray-600 text-sm mb-4"><strong>Cupos:</strong> {curso.max_capacity}</p>
                                
                                {#if myCourses.some(mc => mc.course_id === curso.course_id)}
                                    <Button disabled fullWidth={true} class="bg-gray-300 text-gray-500">Ya inscrito</Button>
                                {:else}
                                    <Button on:click={() => tryEnroll(curso.course_id)} variant="primary" fullWidth={true} class="bg-blue-900 hover:bg-blue-800">Inscribirme</Button>
                                {/if}
                            </Card>
                        {/each}
                    </div>
                {/if}
            {:else if currentView === 'inscripciones'}
                <PageHeader title="Historial de Inscripciones" />
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                    <DataTable
                        data={myCourses}
                        columns={[
                            { key: "course_code", label: "Código" },
                            { key: "course_name", label: "Curso" },
                            { key: "schedule", label: "Horario" },
                            { key: "_estado", label: "Estado", sortable: false, center: true },
                        ]}
                        searchPlaceholder="Buscar por código, nombre, horario..."
                        emptyText="Aún no tienes inscripciones activas"
                        tableClass="w-full min-w-[500px]"
                        let:row
                    >
                        <tr class="hover:bg-gray-50 transition">
                            <td class="px-6 py-3 font-medium text-gray-800">{row.course_code}</td>
                            <td class="px-6 py-3 text-gray-600">{row.course_name}</td>
                            <td class="px-6 py-3 text-gray-600">{row.schedule}</td>
                            <td class="px-6 py-3 text-center">
                                <Badge color="green" text="Activa" />
                            </td>
                        </tr>
                    </DataTable>
                </div>
            {:else if currentView === 'perfil'}
                <PageHeader title="Mi Perfil" />
                <div class="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-gray-100 max-w-2xl">
                    <div class="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-6 mb-8">
                        <div class="w-20 h-20 bg-blue-100 text-blue-900 rounded-full flex items-center justify-center text-3xl font-bold uppercase shrink-0">
                            {studentName.charAt(0)}
                        </div>
                        <div>
                            <h3 class="text-2xl font-bold text-gray-800">{studentName}</h3>
                            <p class="text-gray-500 font-medium tracking-wide text-sm mt-1">ESTUDIANTE ACTIVO</p>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="grid grid-cols-1 sm:grid-cols-3 border-b border-gray-50 pb-4 gap-1 sm:gap-4">
                            <span class="text-gray-500 font-medium sm:col-span-1">Nombre de usuario</span>
                            <span class="text-gray-800 font-medium sm:col-span-2">{studentName}</span>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-3 border-b border-gray-50 pb-4 gap-1 sm:gap-4">
                            <span class="text-gray-500 font-medium sm:col-span-1">ID del Sistema</span>
                            <span class="text-gray-800 font-medium sm:col-span-2">{studentId}</span>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
        {/if}
    </div>
</div>
