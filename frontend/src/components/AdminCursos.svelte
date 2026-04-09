<script lang="ts">
    import { onMount } from "svelte";
    import { getCourses, createCourse, updateCourse, deleteCourse, type CourseCreate } from "../lib/services/courses";
    import { getUsuarios } from "../lib/services/users";

    let courses = [];
    let teachers = [];
    let loading = true;
    let editingCourseId = null;
    let deletingCourseId = null;
    let isCourseModalOpen = false;
    let isDeleteModalOpen = false;
    let toastMessage = "";
    let toastType = "success";
    let showToast = false;

    // Form data
    let form = {
        course_code: "",
        course_name: "",
        max_capacity: 30,
        schedule: "",
        teacher_user_id: null,
        clasroom: 1,
        period_id: 1,
        status: 1
    };

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        loading = true;
        try {
            const [coursesData, usersData] = await Promise.all([
                getCourses(),
                getUsuarios()
            ]);
            courses = coursesData || [];
            teachers = (usersData || []).filter(u => u.role_id === 2); // Role 2 = Docente
        } catch (err) {
            console.error(err);
        } finally {
            loading = false;
        }
    }

    function openModal() {
        editingCourseId = null;
        form = {
            course_code: "",
            course_name: "",
            max_capacity: 30,
            schedule: "",
            teacher_user_id: teachers.length > 0 ? teachers[0].user_id : null,
            clasroom: 1,
            period_id: 1,
            status: 1
        };
        isCourseModalOpen = true;
    }

    function openEditModal(course) {
        editingCourseId = course.course_id;
        form = {
            course_code: course.course_code,
            course_name: course.course_name,
            max_capacity: course.max_capacity,
            schedule: course.schedule,
            teacher_user_id: course.teacher_user_id,
            clasroom: course.clasroom,
            period_id: course.period_id,
            status: course.status
        };
        isCourseModalOpen = true;
    }

    function closeModal() {
        isCourseModalOpen = false;
        editingCourseId = null;
    }

    function openDeleteModal(courseId) {
        deletingCourseId = courseId;
        isDeleteModalOpen = true;
    }

    function closeDeleteModal() {
        isDeleteModalOpen = false;
        deletingCourseId = null;
    }

    function displayToast(message, type) {
        toastMessage = message;
        toastType = type;
        showToast = true;
        setTimeout(() => { showToast = false; }, 3000);
    }

    async function saveCourse() {
        const body: CourseCreate = {
            course_code: form.course_code,
            course_name: form.course_name,
            max_capacity: parseInt(form.max_capacity as any),
            schedule: form.schedule,
            teacher_user_id: form.teacher_user_id ? parseInt(form.teacher_user_id as any) : null,
            clasroom: parseInt(form.clasroom as any),
            period_id: parseInt(form.period_id as any),
            status: parseInt(form.status as any),
        };

        try {
            if (editingCourseId) {
                await updateCourse(editingCourseId, body);
            } else {
                await createCourse(body);
            }

            closeModal();
            displayToast(
                editingCourseId ? "Curso actualizado correctamente" : "Curso creado correctamente",
                "success"
            );
            await loadData();
        } catch (err) {
            console.error(err);
            displayToast("Error al guardar el curso", "error");
        }
    }

    async function confirmDelete() {
        try {
            await deleteCourse(deletingCourseId);
            closeDeleteModal();
            displayToast("Curso eliminado correctamente", "success");
            await loadData();
        } catch (err) {
            console.error(err);
            displayToast("Error al eliminar el curso (asegúrate que no tenga estudiantes inscritos)", "error");
            closeDeleteModal();
        }
    }

    function getTeacherName(id) {
        const t = teachers.find(t => t.user_id === id);
        return t ? `${t.first_name} ${t.last_name}` : "-";
    }
</script>

<div class="flex-1">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
            <h2 class="text-2xl font-bold text-gray-800">Gestión de Cursos</h2>
            <p class="text-gray-500 text-sm mt-1">Crear, editar y eliminar cursos del sistema asignando docentes.</p>
        </div>
        <button on:click={openModal} class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium shadow transition flex items-center gap-2 cursor-pointer">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Nuevo Curso
        </button>
    </div>

    <!-- Toast Message -->
    {#if showToast}
        <div class="fixed top-20 right-5 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-50 transition-all {toastType === 'success' ? 'bg-green-600' : 'bg-red-600'}">
            {toastMessage}
        </div>
    {/if}

    <!-- Tabla Cursos -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead class="bg-gray-50 border-b">
                    <tr>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Código</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Nombre</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Horario</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Cupo</th>
                        <th class="text-left px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Docente</th>
                        <th class="text-center px-4 py-3 text-gray-600 font-semibold whitespace-nowrap">Acciones</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                    {#if loading}
                        <tr><td colspan="6" class="px-4 py-8 text-center text-gray-500">Cargando cursos...</td></tr>
                    {:else if courses.length === 0}
                        <tr><td colspan="6" class="px-4 py-8 text-center text-gray-500">No se encontraron cursos registados.</td></tr>
                    {:else}
                        {#each courses as course}
                            <tr class="hover:bg-gray-50 transition">
                                <td class="px-4 py-3 font-medium text-gray-800">{course.course_code}</td>
                                <td class="px-4 py-3 font-medium text-gray-800">{course.course_name}</td>
                                <td class="px-4 py-3 text-gray-600">{course.schedule}</td>
                                <td class="px-4 py-3 text-gray-600">{course.max_capacity}</td>
                                <td class="px-4 py-3 text-gray-600">{getTeacherName(course.teacher_user_id)}</td>
                                <td class="px-4 py-3">
                                    <div class="flex justify-center gap-2">
                                        <button on:click={() => openEditModal(course)} class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition" title="Editar">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                                        </button>
                                        <button on:click={() => openDeleteModal(course.course_id)} class="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition" title="Eliminar">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
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

    <!-- Modals -->
    {#if isCourseModalOpen}
        <div class="fixed inset-0 z-40 flex items-center justify-center">
            <button class="absolute inset-0 bg-black/50" on:click={closeModal} aria-label="Cerrar modal"></button>
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-xl mx-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center p-6 border-b border-gray-100">
                    <h3 class="text-xl font-bold text-gray-800">{editingCourseId ? 'Editar Curso' : 'Nuevo Curso'}</h3>
                    <button on:click={closeModal} class="text-gray-400 hover:text-gray-600 transition"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
                </div>
                <form on:submit|preventDefault={saveCourse} class="p-6">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                        <div class="space-y-1 sm:col-span-1">
                            <label class="block text-sm font-medium text-gray-700">Código</label>
                            <input bind:value={form.course_code} type="text" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none"/>
                        </div>
                        <div class="space-y-1 sm:col-span-1">
                            <label class="block text-sm font-medium text-gray-700">Nombre</label>
                            <input bind:value={form.course_name} type="text" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none"/>
                        </div>
                        <div class="space-y-1 sm:col-span-1">
                            <label class="block text-sm font-medium text-gray-700">Horario</label>
                            <input bind:value={form.schedule} type="text" required placeholder="Ej: Lunes 8-10am" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none"/>
                        </div>
                        <div class="space-y-1 sm:col-span-1">
                            <label class="block text-sm font-medium text-gray-700">Cupo Máximo</label>
                            <input bind:value={form.max_capacity} type="number" required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none"/>
                        </div>
                        <div class="space-y-1 sm:col-span-2">
                            <label class="block text-sm font-medium text-gray-700">Docente Asignado</label>
                            <select bind:value={form.teacher_user_id} required class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition outline-none cursor-pointer">
                                {#each teachers as teacher}
                                    <option value={teacher.user_id}>{teacher.first_name} {teacher.last_name}</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                    <div class="mt-8 flex justify-end gap-3 pt-5 border-t border-gray-100">
                        <button type="button" on:click={closeModal} class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition">Cancelar</button>
                        <button type="submit" class="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-md rounded-lg transition">Guardar</button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    {#if isDeleteModalOpen}
        <div class="fixed inset-0 z-40 flex items-center justify-center">
            <button class="absolute inset-0 bg-black/50" on:click={closeDeleteModal} aria-label="Cerrar modal"></button>
            <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6 text-center">
                <div class="mx-auto w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mb-4">
                    <svg class="w-7 h-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </div>
                <h3 class="text-lg font-bold text-gray-800 mb-2">Eliminar Curso</h3>
                <p class="text-gray-500 text-sm mb-6">Esta acción no se puede deshacer. Asegúrate de que no haya estudiantes inscritos en este curso antes de eliminarlo.</p>
                <div class="flex justify-center gap-3">
                    <button on:click={closeDeleteModal} class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition">Cancelar</button>
                    <button on:click={confirmDelete} class="px-5 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg shadow-sm transition">Eliminar</button>
                </div>
            </div>
        </div>
    {/if}
</div>
