<script>
    import { onMount } from "svelte";
    import { fly } from "svelte/transition";
    import { navigate } from "svelte-routing";

    import DataTable from "../components/DataTable.svelte";
    import Badge from "../components/ui/Badge.svelte";
    import Button from "../components/ui/Button.svelte";
    import Card from "../components/ui/Card.svelte";
    import PageHeader from "../components/ui/PageHeader.svelte";
    import Toast from "../components/ui/Toast.svelte";
    import { getSession, logout } from "../lib/services/auth";
    import { getCourses } from "../lib/services/courses";
    import {
        createEnrollment,
        getEnrollments,
    } from "../lib/services/enrollments";

    let currentView = "dashboard";
    let availableCourses = [];
    let myCourses = [];
    let loading = false;

    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    let studentId = null;
    let studentName = "Estudiante";
    let studentStatusId = 1;
    let isMobileMenuOpen = false;
    let profilePicUrl = null;

    function handlePhotoUpload(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                profilePicUrl = event.target.result;
                if (studentId && typeof profilePicUrl === "string") {
                    localStorage.setItem(
                        `profile_pic_${studentId}`,
                        profilePicUrl,
                    );
                }
            };
            reader.readAsDataURL(file);
        }
    }

    function removePhoto() {
        profilePicUrl = null;
        if (studentId) localStorage.removeItem(`profile_pic_${studentId}`);
    }

    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

    onMount(() => {
        const session = getSession();
        if (session.user_id && session.role_id === 3) {
            studentId = session.user_id;
            studentName = session.user_name || "Estudiante";
            studentStatusId = session.status_id || 1;
            const savedPic = localStorage.getItem(`profile_pic_${studentId}`);
            if (savedPic) profilePicUrl = savedPic;
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
                getEnrollments(),
            ]);

            availableCourses = allCourses || [];

            // Filter enrollments for this student
            const myEnrollments = (allEnrollments || []).filter(
                (e) => e.student_user_id === studentId,
            );

            // Map the enrollment course_ids to the actual course details
            myCourses = myEnrollments
                .map((e) =>
                    availableCourses.find((c) => c.course_id === e.course_id),
                )
                .filter(Boolean);
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
        6: "Suspendido",
    };

    function tryEnroll(courseId) {
        if (studentStatusId !== 1) {
            const estadoTexto = statusMap[studentStatusId] || "Desconocido";
            displayToast(
                `Estudiante Con Proceso En Estado ${estadoTexto}, Acérquese A Admisiones.`,
                "error",
            );
            return;
        }
        inscribirCurso(courseId);
    }

    function displayToast(message, type) {
        toastMessage = message;
        toastType = type;
        showToast = true;
        setTimeout(() => {
            showToast = false;
        }, 3000);
    }

    async function inscribirCurso(courseId) {
        try {
            await createEnrollment({
                student_user_id: studentId,
                course_id: courseId,
                registration_date: new Date().toISOString(),
                status_id: 1, // Activo
            });
            displayToast("¡Inscripción exitosa!", "success");
            await loadCourses(); // Reload so it updates "Mis cursos"
            setView("dashboard"); // Redirect to dashboard to see it
        } catch (err) {
            console.error(err);
            displayToast(err.message || "Error al inscribirse al curso", "error");
        }
    }

    function cerrarSesion() {
        logout();
        navigate("/");
    }
</script>

<div class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav
        class="bg-blue-950 text-white flex justify-between items-center p-4 shadow z-30 relative"
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
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            /></svg>
            <h1 class="text-lg font-bold">Panel del Estudiante</h1>
        </div>
        <Button
            on:click={cerrarSesion}
            variant="danger"
            class="px-4 py-1.5 text-sm"
        >
            Cerrar sesión
        </Button>
    </nav>

    <!-- Toast Message -->
    <Toast message={toastMessage} type={toastType} show={showToast} />

    <div class="flex flex-1 items-stretch relative">
        {#if isMobileMenuOpen}
            <button
                class="md:hidden fixed inset-0 w-full h-full bg-black/50 z-40 transition-opacity border-0"
                on:click={toggleMobileMenu}
                aria-label="Cerrar modal"
            ></button>
        {/if}

        {#if studentStatusId !== 1}
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
                        El perfil de estudiante se encuentra en estado <span
                            class="bg-red-200 text-red-800 px-2 py-1 rounded inline-block font-bold"
                            >{(
                                statusMap[studentStatusId] || "Desconocido"
                            ).toUpperCase()}</span
                        >. No cuenta con los permisos necesarios para visualizar
                        la lista de cursos ni gestionar las inscripciones. Si
                        esto es un error, por favor contacte a soporte o
                        admisiones.
                    </p>
                </div>
            </div>
        {:else}
            <!-- Sidebar -->
            <div
                class="{isMobileMenuOpen
                    ? 'flex'
                    : 'hidden'} md:flex shrink-0 flex-col absolute inset-y-0 left-0 md:relative z-50 w-64 bg-blue-950 text-white shadow p-4 border-r border-blue-900 transition-transform duration-300"
            >
                <h2
                    class="font-semibold mb-4 text-sm uppercase tracking-wider text-blue-200"
                >
                    Menú
                </h2>
                <ul class="space-y-1">
                    <li>
                        <button
                            on:click={() => { setView("dashboard"); isMobileMenuOpen = false; }}
                            class="w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center gap-2.5 text-sm {currentView === 'dashboard' ? 'bg-blue-900 shadow-sm border-l-2 border-l-blue-300 font-semibold' : 'hover:bg-blue-900/60 text-blue-100'}"
                        >
                            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                            Dashboard
                        </button>
                    </li>
                    <li>
                        <button
                            on:click={() => { setView("cursos"); isMobileMenuOpen = false; }}
                            class="w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center gap-2.5 text-sm {currentView === 'cursos' ? 'bg-blue-900 shadow-sm border-l-2 border-l-blue-300 font-semibold' : 'hover:bg-blue-900/60 text-blue-100'}"
                        >
                            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                            Cursos disponibles
                        </button>
                    </li>
                    <li>
                        <button
                            on:click={() => { setView("inscripciones"); isMobileMenuOpen = false; }}
                            class="w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center gap-2.5 text-sm {currentView === 'inscripciones' ? 'bg-blue-900 shadow-sm border-l-2 border-l-blue-300 font-semibold' : 'hover:bg-blue-900/60 text-blue-100'}"
                        >
                            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>
                            Mis inscripciones
                        </button>
                    </li>
                    <li>
                        <button
                            on:click={() => { setView("perfil"); isMobileMenuOpen = false; }}
                            class="w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center gap-2.5 text-sm {currentView === 'perfil' ? 'bg-blue-900 shadow-sm border-l-2 border-l-blue-300 font-semibold' : 'hover:bg-blue-900/60 text-blue-100'}"
                        >
                            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                            Perfil
                        </button>
                    </li>
                </ul>
            </div>

            <!-- Contenido -->
            <div class="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
                {#key currentView}
                <div in:fly={{ y: 10, duration: 220 }}>
                {#if currentView === "dashboard"}
                    <PageHeader title="Bienvenido/a, {studentName}" />
                    <Card class="mb-8">
                        <div class="flex items-center justify-between flex-wrap gap-3">
                            <p class="text-gray-600">
                                "Inscríbete y expande tu increíble conocimiento."
                            </p>
                            {#if myCourses.length > 0}
                                <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 text-sm font-medium border border-blue-100">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                                    {myCourses.length} {myCourses.length === 1 ? 'curso inscrito' : 'cursos inscritos'}
                                </span>
                            {/if}
                        </div>
                    </Card>

                    <h3 class="text-2xl font-bold text-gray-800 mb-4">
                        Mis Cursos Actuales
                    </h3>
                    {#if loading}
                        <div class="flex items-center gap-3 text-gray-500 py-4">
                            <svg class="animate-spin w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                            <span>Cargando cursos...</span>
                        </div>
                    {:else if myCourses.length === 0}
                        <div
                            class="bg-blue-50 p-6 rounded-xl border border-blue-100"
                        >
                            <p class="text-blue-900">
                                No estás inscrito en ningún curso actualmente.
                                Ve a "Cursos disponibles" para inscribirte.
                            </p>
                        </div>
                    {:else}
                        <div
                            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        >
                            {#each myCourses as curso}
                                <Card
                                    class="border-l-4 border-l-green-500 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 relative bg-white"
                                >
                                    <Badge
                                        color="green"
                                        text="Inscrito"
                                        class="absolute top-4 right-4"
                                    />
                                    <h3
                                        class="text-xl font-bold text-gray-800 mb-2 pr-16"
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
                                    <p
                                        class="text-gray-600 text-sm mt-4 text-green-600 font-medium"
                                    >
                                        Estado: Activo
                                    </p>
                                </Card>
                            {/each}
                        </div>
                    {/if}
                {:else if currentView === "cursos"}
                    <PageHeader title="Cursos Disponibles" />

                    {#if loading}
                        <div class="flex items-center gap-3 text-gray-500 py-4">
                            <svg class="animate-spin w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                            <span>Cargando cursos...</span>
                        </div>
                    {:else if availableCourses.length === 0}
                        <div
                            class="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                        >
                            <p class="text-gray-600">
                                No hay cursos disponibles en este momento.
                            </p>
                        </div>
                    {:else}
                        <div
                            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        >
                            {#each availableCourses as curso}
                                <Card class="hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
                                    <h3
                                        class="text-xl font-bold text-blue-900 mb-2"
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
                                        <strong>Cupos:</strong>
                                        {curso.max_capacity}
                                    </p>

                                    {#if myCourses.some((mc) => mc.course_id === curso.course_id)}
                                        <Button
                                            disabled
                                            fullWidth={true}
                                            class="bg-gray-300 text-gray-500"
                                            >Ya inscrito</Button
                                        >
                                    {:else}
                                        <Button
                                            on:click={() =>
                                                tryEnroll(curso.course_id)}
                                            variant="primary"
                                            fullWidth={true}
                                            class="bg-blue-900 hover:bg-blue-800"
                                            >Inscribirme</Button
                                        >
                                    {/if}
                                </Card>
                            {/each}
                        </div>
                    {/if}
                {:else if currentView === "inscripciones"}
                    <PageHeader title="Historial de Inscripciones" />
                    <div
                        class="bg-white rounded-xl shadow-sm border border-gray-100 p-4"
                    >
                        <DataTable
                            data={myCourses}
                            columns={[
                                { key: "course_code", label: "Código" },
                                { key: "course_name", label: "Curso" },
                                { key: "schedule", label: "Horario" },
                                {
                                    key: "_estado",
                                    label: "Estado",
                                    sortable: false,
                                    center: true,
                                },
                            ]}
                            searchPlaceholder="Buscar por código, nombre, horario..."
                            emptyText="Aún no tienes inscripciones activas"
                            tableClass="w-full min-w-[500px]"
                            let:row
                        >
                            <tr class="hover:bg-gray-50 transition">
                                <td class="px-6 py-3 font-medium text-gray-800"
                                    >{row.course_code}</td
                                >
                                <td class="px-6 py-3 text-gray-600"
                                    >{row.course_name}</td
                                >
                                <td class="px-6 py-3 text-gray-600"
                                    >{row.schedule}</td
                                >
                                <td class="px-6 py-3 text-center">
                                    <Badge color="green" text="Activa" />
                                </td>
                            </tr>
                        </DataTable>
                    </div>
                {:else if currentView === "perfil"}
                    <PageHeader title="Mi Perfil" />
                    <div
                        class="max-w-2xl bg-white rounded-xl shadow-sm border border-gray-100 p-8 flex flex-col items-center sm:flex-row sm:items-start gap-8"
                    >
                        <div class="flex flex-col items-center shrink-0">
                            <div
                                class="w-32 h-32 rounded-full bg-blue-50 border-4 border-white shadow-lg overflow-hidden flex items-center justify-center mb-4 relative group"
                            >
                                {#if profilePicUrl}
                                    <img
                                        src={profilePicUrl}
                                        alt="Foto de perfil"
                                        class="w-full h-full object-cover"
                                    />
                                {:else}
                                    <svg
                                        class="w-16 h-16 text-blue-300"
                                        fill="currentColor"
                                        viewBox="0 0 24 24"
                                        ><path
                                            d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
                                        /></svg
                                    >
                                {/if}
                                <label
                                    class="absolute inset-0 bg-black/40 text-white flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                                >
                                    <svg
                                        class="w-6 h-6 mb-1"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                        ><path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                                        ></path><path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                                        ></path></svg
                                    >
                                    <span class="text-xs font-semibold"
                                        >Cambiar</span
                                    >
                                    <input
                                        type="file"
                                        accept="image/*"
                                        class="hidden"
                                        on:change={handlePhotoUpload}
                                    />
                                </label>
                            </div>
                            {#if profilePicUrl}
                                <button
                                    on:click={removePhoto}
                                    class="mt-2 text-xs font-medium text-red-500 hover:text-red-700 transition"
                                    >Quitar foto</button
                                >
                            {/if}
                        </div>
                        <div class="flex-1 w-full space-y-4">
                            <div>
                                <h3
                                    class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
                                >
                                    Nombre Completo
                                </h3>
                                <p class="text-xl font-bold text-gray-800">
                                    {studentName}
                                </p>
                            </div>
                            <div>
                                <h3
                                    class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
                                >
                                    Rol y Estado
                                </h3>
                                <div
                                    class="inline-flex items-center mt-1 gap-2"
                                >
                                    <span class="relative flex h-3 w-3">
                                        <span
                                            class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
                                        ></span>
                                        <span
                                            class="relative inline-flex rounded-full h-3 w-3 bg-green-500"
                                        ></span>
                                    </span>
                                    <Badge
                                        color="green"
                                        text={statusMap[studentStatusId] ||
                                            "Desconocido"}
                                    />
                                    <Badge color="blue" text="Estudiante" />
                                </div>
                            </div>
                            <div class="pt-4 border-t border-gray-100">
                                <p class="text-sm text-gray-500">
                                    Puedes hacer clic en el avatar para
                                    actualizar tu imagen de perfil en forma
                                    local.
                                </p>
                            </div>
                        </div>
                    </div>
                {/if}
                </div>
                {/key}
            </div>
        {/if}
    </div>
</div>
