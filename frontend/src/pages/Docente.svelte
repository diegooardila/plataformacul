<script lang="ts">
    import { onMount } from "svelte";
    import { navigate } from "svelte-routing";
    import DataTable from "../components/DataTable.svelte";
    import Badge from "../components/ui/Badge.svelte";
    import Button from "../components/ui/Button.svelte";
    import Card from "../components/ui/Card.svelte";
    import PageHeader from "../components/ui/PageHeader.svelte";
    import { getSession, logout } from "../lib/services/auth";
    import { getCourses } from "../lib/services/courses";
    import { getEnrollments } from "../lib/services/enrollments";
    import { getUsuarios } from "../lib/services/users";

    let currentView = "dashboard";
    let myCourses = [];
    let myStudentsByCourse = {}; // Record<courseId, Student[]>
    let loading = true;
    let selectedCourseForStudents = null;

    let todos = [];
    let newTodoText = "";
    let newTodoCourse = "";

    function addTodo() {
        if (!newTodoText.trim()) return;
        todos = [
            ...todos,
            { id: Date.now(), text: newTodoText, courseId: newTodoCourse, completed: false }
        ];
        newTodoText = "";
        newTodoCourse = "";
        saveTodos();
    }
    
    function toggleTodo(id) {
        todos = todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
        saveTodos();
    }
    
    function deleteTodo(id) {
        todos = todos.filter(t => t.id !== id);
        saveTodos();
    }

    function saveTodos() {
        if (teacherId) {
            localStorage.setItem(`teacher_tasks_${teacherId}`, JSON.stringify(todos));
        }
    }

    let isMobileMenuOpen = false;
    let profilePicUrl = null;

    function handlePhotoUpload(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                profilePicUrl = event.target.result as string;
                if (teacherId) localStorage.setItem(`profile_pic_${teacherId}`, profilePicUrl);
            };
            reader.readAsDataURL(file);
        }
    }

    function removePhoto() {
        profilePicUrl = null;
        if (teacherId) localStorage.removeItem(`profile_pic_${teacherId}`);
    }

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
            const [usersData, coursesData, enrollmentsData] = await Promise.all(
                [getUsuarios(), getCourses(), getEnrollments()],
            );

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
                    6: "Suspendido",
                };
                teacherStatusName = statusMap[teacherStatusId] || "Desconocido";
            } else {
                teacherName = "Sesión Inválida";
                navigate("/");
                return;
            }

            // Load Todos
            if (teacherId) {
                const savedTodos = localStorage.getItem(`teacher_tasks_${teacherId}`);
                if (savedTodos) {
                    try {
                        todos = JSON.parse(savedTodos);
                    } catch(e){}
                }
                const savedPic = localStorage.getItem(`profile_pic_${teacherId}`);
                if (savedPic) profilePicUrl = savedPic;
            }

            // Filter courses
            myCourses = courses.filter((c) => c.teacher_user_id === teacherId);

            // Match students to my courses
            const students = users.filter((u) => u.role_id === 3);

            myCourses.forEach((c) => {
                const enrs = enrollments.filter(
                    (e) => e.course_id === c.course_id,
                );
                myStudentsByCourse[c.course_id] = enrs.map((e) => {
                    const st = students.find(
                        (s) => s.user_id === e.student_user_id,
                    );
                    return st
                        ? st
                        : {
                              user_id: 0,
                              first_name: "Desconocido",
                              last_name: "",
                              identity_document: "",
                          };
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
        selectedCourseForStudents = null;
    }

    function cerrarSesion() {
        logout();
        navigate("/");
    }

    $: tableStudentsByCourse = Object.fromEntries(
        Object.entries(myStudentsByCourse).map(
            ([courseId, students]: [string, any[]]) => [
                courseId,
                students.map((st) => ({
                    ...st,
                    _nombre: `${st.first_name} ${st.last_name}`.trim(),
                })),
            ],
        ),
    );
</script>

<div class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav
        class="bg-indigo-700 text-white flex justify-between items-center p-4 shadow z-30 relative"
    >
        <div class="flex items-center gap-3">
            <button
                on:click={toggleMobileMenu}
                class="md:hidden p-1.5 hover:bg-white/10 rounded transition"
                aria-label="Menú"
            >
                <svg
                    class="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 6h16M4 12h16M4 18h16"
                    /></svg
                >
            </button>
            <svg
                class="w-6 h-6 hidden sm:block"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 14l9-5-9-5-9 5 9 5z"
                /><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"
                /><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 14v7"
                /></svg
            >
            <h1 class="text-lg font-bold">Panel del Docente</h1>
        </div>
        <Button
            on:click={cerrarSesion}
            variant="danger"
            class="px-4 py-1.5 text-sm font-medium"
        >
            Cerrar sesión
        </Button>
    </nav>

    <div class="flex flex-1 items-stretch relative">
        {#if isMobileMenuOpen}
            <button
                class="md:hidden fixed inset-0 w-full h-full bg-black/50 z-40 transition-opacity border-0"
                on:click={toggleMobileMenu}
                aria-label="Cerrar modal"
            ></button>
        {/if}

        {#if teacherStatusId !== 1}
            <div
                class="w-full flex flex-col items-center justify-center p-6 bg-gray-50"
            >
                <div
                    class="bg-red-50 p-10 rounded-2xl w-full max-w-lg text-center border border-red-100 shadow"
                >
                    <svg
                        class="w-20 h-20 text-red-500 mx-auto mb-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        /></svg
                    >
                    <h2 class="text-3xl font-bold text-red-700 mb-2">
                        Acceso Restringido
                    </h2>
                    <p class="text-red-700 font-medium text-base mt-6">
                        El perfil de docente se encuentra en estado <span
                            class="bg-red-200 text-red-800 px-2 py-1 rounded inline-block font-bold"
                            >{teacherStatusName.toUpperCase()}</span
                        >. No cuenta con los permisos necesarios para visualizar
                        la lista de cursos ni gestionar las inscripciones de sus
                        alumnos. Si esto es un error, por favor contacte a
                        soporte o admisiones.
                    </p>
                </div>
            </div>
        {:else}
            <!-- Sidebar -->
            <div
                class="{isMobileMenuOpen
                    ? 'flex'
                    : 'hidden'} md:flex shrink-0 flex-col absolute inset-y-0 left-0 md:relative z-50 w-64 bg-indigo-800 text-white shadow p-5 border-r border-indigo-700 transition-transform duration-300"
            >
                <h2
                    class="font-semibold mb-6 text-xs uppercase tracking-wider text-indigo-300"
                >
                    Menú Docente
                </h2>
                <ul class="space-y-1">
                    <li>
                        <button
                            on:click={() => {
                                setView("dashboard");
                                isMobileMenuOpen = false;
                            }}
                            class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView ===
                            'dashboard'
                                ? 'bg-indigo-600 shadow'
                                : 'hover:bg-indigo-700 text-indigo-100'}"
                            >Inicio</button
                        >
                    </li>
                    <li>
                        <button
                            on:click={() => {
                                setView("mis_cursos");
                                isMobileMenuOpen = false;
                            }}
                            class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView ===
                            'mis_cursos'
                                ? 'bg-indigo-600 shadow'
                                : 'hover:bg-indigo-700 text-indigo-100'}"
                            >Mis Cursos</button
                        >
                    </li>
                    <li>
                        <button
                            on:click={() => {
                                setView("mis_estudiantes");
                                isMobileMenuOpen = false;
                            }}
                            class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView ===
                            'mis_estudiantes'
                                ? 'bg-indigo-600 shadow'
                                : 'hover:bg-indigo-700 text-indigo-100'}"
                            >Estudiantes Inscritos</button
                        >
                    </li>
                    <li>
                        <button
                            on:click={() => {
                                setView("perfil");
                                isMobileMenuOpen = false;
                            }}
                            class="w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition {currentView ===
                            'perfil'
                                ? 'bg-indigo-600 shadow'
                                : 'hover:bg-indigo-700 text-indigo-100'}"
                            >Perfil</button
                        >
                    </li>
                </ul>
            </div>

            <!-- Contenido -->
            <div class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
                {#if loading}
                    <div class="flex h-full items-center justify-center">
                        <p class="text-gray-500 font-medium">
                            Cargando datos del docente...
                        </p>
                    </div>
                {:else if currentView === "dashboard"}
                    <PageHeader title="Bienvenido, {teacherName}" />
                    <Card class="mb-8">
                        <p class="text-gray-600">
                            Este es tu panel de control como Docente. Aquí
                            podrás visualizar las asignaturas a tu cargo y
                            controlar el desarrollo de tus estudiantes.
                        </p>
                    </Card>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
                        <div class="self-start w-full">
                            <Card class="flex items-center justify-between">
                                <div>
                                    <h3 class="text-sm font-semibold text-gray-500">
                                        Cursos Asignados
                                    </h3>
                                    <p
                                        class="text-3xl font-bold text-indigo-700 mt-1"
                                    >
                                        {myCourses.length}
                                    </p>
                                </div>
                                <div
                                    class="p-3 bg-indigo-50 text-indigo-600 rounded-lg"
                                >
                                    <svg
                                        class="w-8 h-8"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        ><path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                                        /></svg
                                    >
                                </div>
                            </Card>
                        </div>

                        <!-- Tareas Pendientes -->
                        <Card class="flex flex-col h-full border-t-4 border-t-indigo-500 shadow-sm relative overflow-hidden group">
                            <div class="absolute inset-x-0 -top-10 h-20 bg-indigo-50 -skew-y-3 opacity-50 z-0 pointer-events-none"></div>
                            <h3 class="text-lg font-bold text-indigo-800 mb-4 flex items-center gap-2 relative z-10">
                                <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                                Recordatorios de Clase
                            </h3>
                            
                            <form on:submit|preventDefault={addTodo} class="flex flex-col gap-2 mb-4 relative z-10 w-full">
                                <div class="flex gap-2 w-full">
                                    <input type="text" bind:value={newTodoText} placeholder="Nueva tarea rápida..." class="flex-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm px-3 py-2 border" required />
                                </div>
                                <div class="flex gap-2">
                                    <select bind:value={newTodoCourse} class="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm px-3 py-1.5 border">
                                        <option value="">General (Sin curso)</option>
                                        {#each myCourses as curso}
                                            <option value={curso.course_id}>{curso.course_name}</option>
                                        {/each}
                                    </select>
                                    <Button type="submit" variant="primary" class="shrink-0 px-3 py-1.5 text-sm whitespace-nowrap">Añadir</Button>
                                </div>
                            </form>

                            <div class="flex-1 overflow-y-auto max-h-60 space-y-2 pr-1 relative z-10">
                                {#if todos.length === 0}
                                    <p class="text-gray-500 text-sm text-center py-6 bg-gray-50 rounded-lg italic border border-dashed border-gray-200">No hay recordatorios pendientes.</p>
                                {:else}
                                    {#each todos as todo (todo.id)}
                                        <div class="flex items-start gap-3 p-3 rounded-lg border {todo.completed ? 'bg-gray-50 border-gray-200 opacity-60 hover:opacity-100' : 'bg-white border-indigo-100 shadow-sm'} transition-all group/item hover:border-indigo-300">
                                            <button on:click={() => toggleTodo(todo.id)} class="mt-0.5 shrink-0 w-5 h-5 rounded border {todo.completed ? 'bg-green-500 border-green-500 text-white' : 'bg-white border-gray-300 text-transparent hover:border-indigo-400'} flex items-center justify-center transition" aria-label="Marcar completada">
                                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                                            </button>
                                            <div class="flex-1 min-w-0">
                                                <p class="text-sm font-medium {todo.completed ? 'text-gray-400 line-through' : 'text-gray-700'} break-words">{todo.text}</p>
                                                {#if todo.courseId}
                                                    {@const course = myCourses.find(c => c.course_id == todo.courseId)}
                                                    {#if course}
                                                        <span class="text-[10px] mt-1.5 inline-block px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-600 border border-indigo-100 font-medium truncate max-w-full" title={course.course_name}>{course.course_name}</span>
                                                    {/if}
                                                {/if}
                                            </div>
                                            <button on:click={() => deleteTodo(todo.id)} class="opacity-0 group-hover/item:opacity-100 shrink-0 text-gray-400 hover:text-red-500 transition p-1 rounded-full hover:bg-red-50" title="Eliminar recordatorio">
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                            </button>
                                        </div>
                                    {/each}
                                {/if}
                            </div>
                        </Card>
                    </div>
                {:else if currentView === "perfil"}
                    <PageHeader title="Mi Perfil" />
                    <div class="max-w-2xl bg-white rounded-xl shadow-sm border border-gray-100 p-8 flex flex-col items-center sm:flex-row sm:items-start gap-8">
                        <div class="flex flex-col items-center shrink-0">
                            <div class="w-32 h-32 rounded-full bg-indigo-50 border-4 border-white shadow-lg overflow-hidden flex items-center justify-center mb-4 relative group">
                                {#if profilePicUrl}
                                    <img src={profilePicUrl} alt="Foto de perfil" class="w-full h-full object-cover" />
                                {:else}
                                    <svg class="w-16 h-16 text-indigo-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
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
                                <p class="text-xl font-bold text-gray-800">{teacherName}</p>
                            </div>
                            <div>
                                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Rol y Estado</h3>
                                <div class="inline-flex items-center mt-1 gap-2">
                                    <span class="relative flex h-3 w-3">
                                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                      <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                    </span>
                                    <Badge color="green" text={teacherStatusName} />
                                    <Badge color="indigo" text="Docente" />
                                </div>
                            </div>
                            <div class="pt-4 border-t border-gray-100">
                                <p class="text-sm text-gray-500">Puedes hacer clic en el avatar para actualizar tu imagen de perfil en forma local.</p>
                            </div>
                        </div>
                    </div>
                {:else if currentView === "mis_cursos"}
                    <PageHeader title="Mis Cursos Asignados" />
                    {#if myCourses.length === 0}
                        <div
                            class="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                        >
                            <p class="text-gray-600">
                                No tienes cursos asignados actualmente.
                            </p>
                        </div>
                    {:else}
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {#each myCourses as curso}
                                <Card
                                    class="border-l-4 border-l-indigo-500 hover:shadow-md transition"
                                >
                                    <h3
                                        class="text-xl font-bold text-indigo-800 mb-2"
                                    >
                                        {curso.course_name}
                                    </h3>
                                    <p class="text-gray-600 text-sm mb-1">
                                        <strong>Código:</strong>
                                        {curso.course_code}
                                    </p>
                                    <p class="text-gray-600 text-sm mb-1">
                                        <strong>Horario:</strong>
                                        {curso.schedule}
                                    </p>
                                    <p class="text-gray-600 text-sm mb-4">
                                        <strong>Estudiantes inscritos:</strong>
                                        {(
                                            myStudentsByCourse[
                                                curso.course_id
                                            ] || []
                                        ).length} / {curso.max_capacity}
                                    </p>
                                    <button
                                        on:click={() => {
                                            selectedCourseForStudents =
                                                curso.course_id;
                                            setView("mis_estudiantes");
                                        }}
                                        class="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition cursor-pointer"
                                        >Ver listado de estudiantes &rarr;</button
                                    >
                                </Card>
                            {/each}
                        </div>
                    {/if}
                {:else if currentView === "mis_estudiantes"}
                    {#if !selectedCourseForStudents}
                        <PageHeader title="Estudiantes por Curso" />
                        {#if myCourses.length === 0}
                            <div
                                class="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                            >
                                <p class="text-gray-600">
                                    No tienes cursos para mostrar estudiantes.
                                </p>
                            </div>
                        {:else}
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {#each myCourses as curso}
                                    <Card
                                        class="border-l-4 border-l-indigo-500 hover:shadow-md transition"
                                    >
                                        <h3
                                            class="text-xl font-bold text-indigo-800 mb-2"
                                        >
                                            {curso.course_name}
                                        </h3>
                                        <p class="text-gray-600 text-sm mb-1">
                                            <strong>Código:</strong>
                                            {curso.course_code}
                                        </p>
                                        <p class="text-gray-600 text-sm mb-4">
                                            <strong
                                                >Estudiantes inscritos:</strong
                                            >
                                            {(
                                                myStudentsByCourse[
                                                    curso.course_id
                                                ] || []
                                            ).length} / {curso.max_capacity}
                                        </p>
                                        <Button
                                            on:click={() =>
                                                (selectedCourseForStudents =
                                                    curso.course_id)}
                                            variant="indigo"
                                            fullWidth={true}
                                            >VER ESTUDIANTES DEL CURSO</Button
                                        >
                                    </Card>
                                {/each}
                            </div>
                        {/if}
                    {:else}
                        {@const curso = myCourses.find(
                            (c) => c.course_id === selectedCourseForStudents,
                        )}
                        <div class="flex items-center gap-4 mb-6">
                            <Button
                                on:click={() =>
                                    (selectedCourseForStudents = null)}
                                variant="secondary"
                                class="!px-2 !py-2 bg-gray-200"
                                title="Volver al listado"
                            >
                                <svg
                                    class="w-5 h-5"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M10 19l-7-7m0 0l7-7m-7 7h18"
                                    /></svg
                                >
                            </Button>
                            <h2 class="text-3xl font-bold text-gray-800">
                                Estudiantes: {curso?.course_name}
                            </h2>
                        </div>
                        <div
                            class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
                        >
                            <div
                                class="bg-indigo-50 px-6 py-4 border-b border-indigo-100 flex justify-between items-center"
                            >
                                <h3 class="text-lg font-bold text-indigo-900">
                                    {curso?.course_name}
                                    <span
                                        class="text-xs font-normal text-indigo-600 bg-white px-2 py-0.5 rounded border border-indigo-200 ml-2"
                                        >{curso?.course_code}</span
                                    >
                                </h3>
                                <span
                                    class="text-sm font-medium text-indigo-700"
                                    >{(
                                        myStudentsByCourse[curso?.course_id] ||
                                        []
                                    ).length} inscritos</span
                                >
                            </div>
                            <div class="p-4">
                                <DataTable
                                    data={tableStudentsByCourse[
                                        curso?.course_id
                                    ] || []}
                                    columns={[
                                        {
                                            key: "identity_document",
                                            label: "Documento",
                                        },
                                        {
                                            key: "_nombre",
                                            label: "Nombre Completo",
                                        },
                                        {
                                            key: "_estado",
                                            label: "Estado",
                                            sortable: false,
                                            center: true,
                                        },
                                    ]}
                                    searchPlaceholder="Buscar estudiante..."
                                    emptyText="Este curso aún no tiene inscripciones"
                                    tableClass="w-full min-w-[500px]"
                                    let:row
                                >
                                    <tr class="hover:bg-gray-50 transition">
                                        <td
                                            class="px-6 py-3 text-gray-800 font-medium"
                                            >{row.identity_document}</td
                                        >
                                        <td class="px-6 py-3 text-gray-600"
                                            >{row._nombre}</td
                                        >
                                        <td class="px-6 py-3 text-center">
                                            <Badge
                                                color="green"
                                                text="Activo"
                                            />
                                        </td>
                                    </tr>
                                </DataTable>
                            </div>
                        </div>
                    {/if}
                {/if}
            </div>
        {/if}
    </div>
</div>
