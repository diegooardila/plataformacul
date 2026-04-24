<script lang="ts">
    import { navigate } from "svelte-routing";
    import { onMount } from "svelte";
    import { getCourses } from "../lib/services/courses";
    import { getEnrollments } from "../lib/services/enrollments";
    import { getUsuarios } from "../lib/services/users";
    import { getSession, logout } from "../lib/services/auth";
    import DataTable from "../components/DataTable.svelte";

    let currentView = 'dashboard';
    let myCourses = [];
    let myStudentsByCourse = {}; // Record<courseId, Student[]>
    let loading = true;

    let isMobileMenuOpen = false;
    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

    // For demonstration, fetch all teachers and pick the first one as mock logged in user.
    let teacherId = null;
    let teacherName = "";
    let teacherStatusId = 1;
    let teacherStatusName = "";

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        loading = true;
        try {
            const [usersData, coursesData, enrollmentsData] = await Promise.all([
                getUsuarios(),
                getCourses(),
                getEnrollments()
            ]);

            const users = usersData || [];
            const courses = coursesData || [];
            const enrollments = enrollmentsData || [];

            // Obtener datos del Storage
            const session = getSession();
            if (session.user_id && session.role_id === 2) {
                teacherId = session.user_id;
                teacherName = session.user_name || "Docente";
                teacherStatusId = session.status_id || 1;
                
                const statusMap = {
                    1: "Activo",
                    2: "Inactivo",
                    3: "Pendiente",
                    4: "Finalizado",
                    5: "Cancelado",
                    6: "Suspendido"
                };
                teacherStatusName = statusMap[teacherStatusId] || "Desconocido";
            } else {
                teacherName = "Sesión Inválida";
                navigate('/');
                return;
            }

            // Filter courses
            myCourses = courses.filter(c => c.teacher_user_id === teacherId);

            // Match students to my courses
            const students = users.filter(u => u.role_id === 3);
            
            myCourses.forEach(c => {
                const enrs = enrollments.filter(e => e.course_id === c.course_id);
                myStudentsByCourse[c.course_id] = enrs.map(e => {
                    const st = students.find(s => s.user_id === e.student_user_id);
                    return st ? st : { user_id: 0, first_name: "Desconocido", last_name: "", identity_document: "" };
                });
            });

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
        logout();
        navigate("/");
    }

    $: tableStudentsByCourse = Object.fromEntries(
        Object.entries(myStudentsByCourse).map(([courseId, students]: [string, any[]]) => [
            courseId,
            students.map(st => ({
                ...st,
                _nombre: `${st.first_name} ${st.last_name}`.trim(),
            })),
        ])
    );
</script>

<div class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="bg-indigo-700 text-white flex justify-between items-center p-4 shadow z-30 relative">
        <div class="flex items-center gap-3">
            <button on:click={toggleMobileMenu} class="md:hidden p-1.5 hover:bg-white/10 rounded transition" aria-label="Menú">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
            <svg class="w-6 h-6 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v7"/></svg>
            <h1 class="text-lg font-bold">Panel del Docente</h1>
        </div>
        <button on:click={cerrarSesion} class="bg-red-500 hover:bg-red-600 text-white px-4 py-1.5 rounded transition shadow-sm cursor-pointer text-sm font-medium">
            Cerrar sesión
        </button>
    </nav>

    <div class="flex flex-1 items-stretch relative">
        {#if isMobileMenuOpen}
            <button class="md:hidden fixed inset-0 w-full h-full bg-black/50 z-40 transition-opacity border-0" on:click={toggleMobileMenu} aria-label="Cerrar modal"></button>
        {/if}

        {#if teacherStatusId !== 1}
            <div class="w-full flex flex-col items-center justify-center p-6 bg-gray-50">
               <div class="bg-red-50 p-10 rounded-2xl w-full max-w-lg text-center border border-red-100 shadow">
                   <svg class="w-20 h-20 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                   <h2 class="text-3xl font-bold text-red-700 mb-2">Acceso Restringido</h2>
                   <p class="text-red-700 font-medium text-base mt-6">
                       El perfil de docente se encuentra en estado <span class="bg-red-200 text-red-800 px-2 py-1 rounded inline-block font-bold">{teacherStatusName.toUpperCase()}</span>.
                       No cuenta con los permisos necesarios para visualizar la lista de cursos ni gestionar las inscripciones de sus alumnos. Si esto es un error, por favor contacte a soporte o admisiones.
                   </p>
               </div>
            </div>
        {:else}
            <!-- Sidebar -->
            <div class="{isMobileMenuOpen ? 'flex' : 'hidden'} md:flex shrink-0 flex-col absolute inset-y-0 left-0 md:relative z-50 w-64 bg-indigo-800 text-white shadow p-5 h-full border-r border-indigo-700 transition-transform duration-300">
                <h2 class="font-semibold mb-6 text-xs uppercase tracking-wider text-indigo-300">Menú Docente</h2>
                <ul class="space-y-1">
                <li><button on:click={() => { setView('dashboard'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView === 'dashboard' ? 'bg-indigo-600 shadow' : 'hover:bg-indigo-700 text-indigo-100'}">Inicio</button></li>
                <li><button on:click={() => { setView('mis_cursos'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView === 'mis_cursos' ? 'bg-indigo-600 shadow' : 'hover:bg-indigo-700 text-indigo-100'}">Mis Cursos</button></li>
                <li><button on:click={() => { setView('mis_estudiantes'); isMobileMenuOpen = false; }} class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView === 'mis_estudiantes' ? 'bg-indigo-600 shadow' : 'hover:bg-indigo-700 text-indigo-100'}">Estudiantes Inscritos</button></li>
            </ul>
        </div>

        <!-- Contenido -->
        <div class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0 overflow-x-hidden">
            {#if loading}
                <div class="flex h-full items-center justify-center">
                    <p class="text-gray-500 font-medium">Cargando datos del docente...</p>
                </div>
            {:else}
                {#if currentView === 'dashboard'}
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">Bienvenido, {teacherName}</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
                        <p class="text-gray-600">Este es tu panel de control como Docente. Aquí podrás visualizar las asignaturas a tu cargo y controlar el desarrollo de tus estudiantes.</p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                            <div>
                                <h3 class="text-sm font-semibold text-gray-500">Cursos Asignados</h3>
                                <p class="text-3xl font-bold text-indigo-700 mt-1">{myCourses.length}</p>
                            </div>
                            <div class="p-3 bg-indigo-50 text-indigo-600 rounded-lg">
                                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                            </div>
                        </div>
                    </div>

                {:else if currentView === 'mis_cursos'}
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">Mis Cursos Asignados</h2>
                    {#if myCourses.length === 0}
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-600">No tienes cursos asignados actualmente.</p>
                        </div>
                    {:else}
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {#each myCourses as curso}
                                <div class="bg-white p-6 rounded-xl shadow border-l-4 border-indigo-500 hover:shadow-md transition">
                                    <h3 class="text-xl font-bold text-indigo-800 mb-2">{curso.course_name}</h3>
                                    <p class="text-gray-600 text-sm mb-1"><strong>Código:</strong> {curso.course_code}</p>
                                    <p class="text-gray-600 text-sm mb-1"><strong>Horario:</strong> {curso.schedule}</p>
                                    <p class="text-gray-600 text-sm mb-4"><strong>Estudiantes inscritos:</strong> {(myStudentsByCourse[curso.course_id] || []).length} / {curso.max_capacity}</p>
                                    <button on:click={() => setView('mis_estudiantes')} class="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition">Ver listado de estudiantes &rarr;</button>
                                </div>
                            {/each}
                        </div>
                    {/if}

                {:else if currentView === 'mis_estudiantes'}
                    <h2 class="text-3xl font-bold text-gray-800 mb-6">Estudiantes por Curso</h2>
                    {#if myCourses.length === 0}
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <p class="text-gray-600">No tienes cursos para mostrar estudiantes.</p>
                        </div>
                    {:else}
                        <div class="space-y-8">
                            {#each myCourses as curso}
                                <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                                    <div class="bg-indigo-50 px-6 py-4 border-b border-indigo-100 flex justify-between items-center">
                                        <h3 class="text-lg font-bold text-indigo-900">{curso.course_name} <span class="text-xs font-normal text-indigo-600 bg-white px-2 py-0.5 rounded border border-indigo-200 ml-2">{curso.course_code}</span></h3>
                                        <span class="text-sm font-medium text-indigo-700">{(myStudentsByCourse[curso.course_id] || []).length} inscritos</span>
                                    </div>
                                    <div class="p-4">
                                        <DataTable
                                            data={tableStudentsByCourse[curso.course_id] || []}
                                            columns={[
                                                { key: "identity_document", label: "Documento" },
                                                { key: "_nombre", label: "Nombre Completo" },
                                                { key: "_estado", label: "Estado", sortable: false, center: true },
                                            ]}
                                            searchPlaceholder="Buscar estudiante..."
                                            emptyText="Este curso aún no tiene inscripciones"
                                            tableClass="w-full min-w-[500px]"
                                            let:row
                                        >
                                            <tr class="hover:bg-gray-50 transition">
                                                <td class="px-6 py-3 text-gray-800 font-medium">{row.identity_document}</td>
                                                <td class="px-6 py-3 text-gray-600">{row._nombre}</td>
                                                <td class="px-6 py-3 text-center">
                                                    <span class="inline-flex items-center gap-1.5 py-1 px-2.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                                        <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span> Activo
                                                    </span>
                                                </td>
                                            </tr>
                                        </DataTable>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                {/if}
            {/if}
        </div>
        {/if}
    </div>
</div>
