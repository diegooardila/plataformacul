<script lang="ts">
    import { onMount } from "svelte";
    import { getEnrollments, createEnrollment, deleteEnrollment, type EnrollmentCreate } from "../lib/services/enrollments";
    import { getCourses } from "../lib/services/courses";
    import { getUsuarios } from "../lib/services/users";

    let enrollments = [];
    let students = [];
    let courses = [];
    
    let loading = true;
    let deletingEnrollmentId = null;
    let isEnrollmentModalOpen = false;
    let isDeleteModalOpen = false;
    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    // Form data
    let form = {
        student_user_id: null,
        course_id: null,
        registration_date: new Date().toISOString().split('T')[0],
        status_id: 1
    };

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        loading = true;
        try {
            const [enrollData, courseData, userData] = await Promise.all([
                getEnrollments(),
                getCourses(),
                getUsuarios()
            ]);
            enrollments = enrollData || [];
            courses = courseData || [];
            students = (userData || []).filter(u => u.role_id === 3); // Role 3 = Estudiante
        } catch (err) {
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function openModal() {
        form = {
            student_user_id: students.length > 0 ? students[0].user_id : null,
            course_id: courses.length > 0 ? courses[0].course_id : null,
            registration_date: new Date().toISOString().split('T')[0],
            status_id: 1
        };
        isEnrollmentModalOpen = true;
    }

    function closeModal() {
        isEnrollmentModalOpen = false;
    }

    function openDeleteModal(enrollmentId) {
        deletingEnrollmentId = enrollmentId;
        isDeleteModalOpen = true;
    }

    function closeDeleteModal() {
        isDeleteModalOpen = false;
        deletingEnrollmentId = null;
    }

    function displayToast(message, type) {
        toastMessage = message;
        toastType = type;
        showToast = true;
        setTimeout(() => { showToast = false; }, 3000);
    }

    async function saveEnrollment() {
        if (!form.student_user_id || !form.course_id) {
            displayToast("Debes seleccionar un estudiante y un curso válido.", "error");
            return;
        }
        
        const selectedStudent = students.find(s => s.user_id === parseInt(form.student_user_id as any));
        if (selectedStudent && selectedStudent.status_id !== 1) {
            const statusMap = {
                1: "Activo",
                2: "Inactivo",
                3: "Pendiente",
                4: "Finalizado",
                5: "Cancelado",
                6: "Suspendido"
            };
            const estadoTexto = statusMap[selectedStudent.status_id] || "Desconocido";
            displayToast(`Estudiante Con Proceso En Estado ${estadoTexto}, Acérquese A Admisiones.`, "error");
            return;
        }

        const body: EnrollmentCreate = {
            student_user_id: parseInt(form.student_user_id as any),
            course_id: parseInt(form.course_id as any),
            registration_date: new Date().toISOString(), // Backend expect a typical ISO datetime string, or date string
            status_id: parseInt(form.status_id as any),
        };

        try {
            await createEnrollment(body);
            closeModal();
            displayToast("Inscripción exitosa", "success");
            await loadData();
        } catch (err) {
            console.error(err);
            displayToast("Error al procesar la inscripción", "error");
        }
    }

    async function confirmDelete() {
        try {
            await deleteEnrollment(deletingEnrollmentId);
            closeDeleteModal();
            displayToast("Inscripción eliminada correctamente", "success");
            await loadData();
        } catch (err) {
            console.error(err);
            displayToast("Error al cancelar la inscripción", "error");
            closeDeleteModal();
        }
    }

    function getStudentName(id) {
        const s = students.find(s => s.user_id === id);
        return s ? `${s.first_name} ${s.last_name}` : "Desconocido";
    }

    function getCourseName(id) {
        const c = courses.find(c => c.course_id === id);
        return c ? c.course_name : "Desconocido";
    }

    function getCourseCode(id) {
        const c = courses.find(c => c.course_id === id);
        return c ? c.course_code : "N/A";
    }
</script>

<div class="flex-1">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
            <h2 class="text-2xl font-bold text-gray-800">Gestión de Inscripciones</h2>
            <p class="text-gray-500 text-sm mt-1">Revisa y matricula estudiantes en los cursos disponibles.</p>
        </div>
        <button on:click={openModal} class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium shadow transition flex items-center gap-2 cursor-pointer">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/></svg>
            Nueva Inscripción
        </button>
    </div>

    {#if showToast}
        <div class="fixed top-20 right-5 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-50 transition-all {toastType === 'success' ? 'bg-green-600' : 'bg-red-600'}">
            {toastMessage}
        </div>
    {/if}

    <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50 border-b">
                    <tr>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">ID Insc.</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Estudiante</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Curso</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Código</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Fecha</th>
                        <th class="text-center px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Acciones</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                    {#if loading}
                        <tr><td colspan="6" class="px-4 py-8 text-center text-gray-500">Cargando inscripciones...</td></tr>
                    {:else if enrollments.length === 0}
                        <tr><td colspan="6" class="px-4 py-8 text-center text-gray-500">No se encontraron inscripciones.</td></tr>
                    {:else}
                        {#each enrollments as en}
                            <tr class="hover:bg-gray-50 transition">
                                <td class="px-4 py-3 font-medium text-gray-800">{en.enrollment_id}</td>
                                <td class="px-4 py-3 text-gray-600 font-medium">{getStudentName(en.student_user_id)}</td>
                                <td class="px-4 py-3 text-gray-600">{getCourseName(en.course_id)}</td>
                                <td class="px-4 py-3 text-gray-600">{getCourseCode(en.course_id)}</td>
                                <td class="px-4 py-3 text-gray-600 text-center font-medium">{new Date(en.registration_date).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                                <td class="px-4 py-3">
                                    <div class="flex justify-center flex-wrap gap-2">
                                        <button on:click={() => openDeleteModal(en.enrollment_id)} class="text-xs bg-red-100 text-red-700 hover:bg-red-200 px-3 py-1.5 rounded transition font-medium" title="Cancelar inscripción">
                                            Cancelar
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Modal Crear -->
    {#if isEnrollmentModalOpen}
        <div class="fixed inset-0 z-40 flex items-center justify-center">
            <button class="absolute inset-0 bg-black/50" on:click={closeModal} aria-label="Cerrar modal"></button>
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-y-auto">
                <div class="flex justify-between items-center p-6 border-b border-gray-100">
                    <h3 class="text-xl font-bold text-gray-800">Matricular Estudiante</h3>
                    <button on:click={closeModal} class="text-gray-400 hover:text-gray-600 transition"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
                </div>
                <form on:submit|preventDefault={saveEnrollment} class="p-6">
                    <div class="space-y-4">
                        <div class="space-y-1">
                            <label class="block text-sm font-medium text-gray-700">Estudiante</label>
                            <select bind:value={form.student_user_id} required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none cursor-pointer">
                                {#each students as st}
                                    <option value={st.user_id}>{st.first_name} {st.last_name} ({st.identity_document})</option>
                                {/each}
                            </select>
                        </div>
                        <div class="space-y-1">
                            <label class="block text-sm font-medium text-gray-700">Curso a Matricular</label>
                            <select bind:value={form.course_id} required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none cursor-pointer">
                                {#each courses as c}
                                    <option value={c.course_id}>{c.course_name} ({c.course_code})</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                    <div class="mt-8 flex justify-end gap-3 pt-5 border-t border-gray-100">
                        <button type="button" on:click={closeModal} class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition">Cerrar</button>
                        <button type="submit" class="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md rounded-lg transition">Inscribir</button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    <!-- Modal Confirmar Cancelar -->
    {#if isDeleteModalOpen}
        <div class="fixed inset-0 z-40 flex items-center justify-center">
            <button class="absolute inset-0 bg-black/50" on:click={closeDeleteModal} aria-label="Cerrar modal"></button>
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6 text-center">
                <div class="mx-auto w-14 h-14 bg-orange-100 rounded-full flex items-center justify-center mb-4">
                    <svg class="w-7 h-7 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                </div>
                <h3 class="text-lg font-bold text-gray-800 mb-2">Cancelar Inscripción</h3>
                <p class="text-gray-500 text-sm mb-6">¿Estás seguro que deseas remover al estudiante de este curso? Esto no se puede deshacer.</p>
                <div class="flex justify-center gap-3">
                    <button on:click={closeDeleteModal} class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition">Volver</button>
                    <button on:click={confirmDelete} class="px-5 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg shadow-sm transition">Sí, Cancelar</button>
                </div>
            </div>
        </div>
    {/if}
</div>
