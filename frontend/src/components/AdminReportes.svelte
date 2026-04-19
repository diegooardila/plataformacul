<script lang="ts">
    import { onMount } from "svelte";
    import { getUsuarios } from "../lib/services/users";
    import { getCourses } from "../lib/services/courses";
    import { getEnrollments } from "../lib/services/enrollments";

    let loading = true;

    let totalActivos = 0;
    let totalEstudiantes = 0;
    let totalDocentes = 0;

    let totalCursos = 0;
    let totalCuposOfrecidos = 0;

    let totalInscripciones = 0;
    let topCursoNombre = "N/A";
    let topCursoInscripciones = 0;

    onMount(async () => {
        try {
            const [users, courses, enrollments] = await Promise.all([
                getUsuarios(),
                getCourses(),
                getEnrollments(),
            ]);

            const usrs = users || [];
            const crs = courses || [];
            const enrs = enrollments || [];

            totalActivos = usrs.filter((u) => u.status_id === 1).length;
            totalEstudiantes = usrs.filter((u) => u.role_id === 3).length;
            totalDocentes = usrs.filter((u) => u.role_id === 2).length;

            totalCursos = crs.length;
            totalCuposOfrecidos = crs.reduce(
                (sum, c) => sum + c.max_capacity,
                0,
            );

            totalInscripciones = enrs.length;

            // Encontrar curso con más inscripciones
            if (crs.length > 0 && enrs.length > 0) {
                const countMap = {};
                enrs.forEach((e) => {
                    countMap[e.course_id] = (countMap[e.course_id] || 0) + 1;
                });

                let maxCount = 0;
                let maxId = null;
                for (const [cId, count] of Object.entries(countMap)) {
                    if (count > maxCount) {
                        maxCount = count as number;
                        maxId = parseInt(cId);
                    }
                }

                if (maxId) {
                    const bestCourse = crs.find((c) => c.course_id === maxId);
                    if (bestCourse) {
                        topCursoNombre = bestCourse.course_name;
                        topCursoInscripciones = maxCount;
                    }
                }
            }
        } catch (error) {
            console.error("Error generando reportes", error);
        } finally {
            loading = false;
        }
    });
</script>

<div class="flex-1">
    <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-800">
            Reportes y Estadísticas
        </h2>
        <p class="text-gray-500 text-sm mt-1">
            Visión general del estado actual del sistema académico.
        </p>
    </div>

    {#if loading}
        <div class="flex items-center justify-center p-12">
            <p class="text-gray-500 font-medium">Calculando métricas...</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <!-- Metrica Usuarios -->
            <div
                class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between"
            >
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-gray-500 font-semibold text-sm">
                        Total Usuarios Activos
                    </h3>
                    <div class="p-2 bg-blue-50 rounded-lg text-blue-600">
                        <svg
                            class="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                            /></svg
                        >
                    </div>
                </div>
                <div>
                    <p class="text-3xl font-bold text-gray-800 mb-1">
                        {totalActivos}
                    </p>
                    <div class="flex text-sm text-gray-500 gap-4 mt-2">
                        <span
                            ><strong class="text-gray-700"
                                >{totalEstudiantes}</strong
                            > Estudiantes</span
                        >
                        <span
                            ><strong class="text-gray-700"
                                >{totalDocentes}</strong
                            > Docentes</span
                        >
                    </div>
                </div>
            </div>

            <!-- Metrica Cursos -->
            <div
                class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between"
            >
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-gray-500 font-semibold text-sm">
                        Cursos Habilitados
                    </h3>
                    <div class="p-2 bg-purple-50 rounded-lg text-purple-600">
                        <svg
                            class="w-6 h-6"
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
                </div>
                <div>
                    <p class="text-3xl font-bold text-gray-800 mb-1">
                        {totalCursos}
                    </p>
                    <p class="text-sm text-gray-500 mt-2">
                        Capacidad total: <strong class="text-gray-700"
                            >{totalCuposOfrecidos}</strong
                        > cupos general
                    </p>
                </div>
            </div>

            <!-- Metrica Inscripciones -->
            <div
                class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between"
            >
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-gray-500 font-semibold text-sm">
                        Total Inscripciones
                    </h3>
                    <div class="p-2 bg-green-50 rounded-lg text-green-600">
                        <svg
                            class="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            /></svg
                        >
                    </div>
                </div>
                <div>
                    <p class="text-3xl font-bold text-gray-800 mb-1">
                        {totalInscripciones}
                    </p>
                    <div class="mt-2 text-sm">
                        <span class="text-gray-500"
                            >Curso más popular:
                        </span><span class="font-semibold text-gray-700"
                            >{topCursoNombre}</span
                        >
                        <span
                            class="text-xs bg-green-100 text-green-800 px-1.5 rounded"
                            >{topCursoInscripciones} matriculados</span
                        >
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <div
        class="w-full overflow-hidden rounded-xl shadow-sm border border-gray-100 bg-white"
    >
        <iframe
            title="gestionCursosCUL"
            width="100%"
            height="700"
            src="https://app.powerbi.com/reportEmbed?reportId=8966942f-e3ca-4cc8-a31c-7070054c0250&autoAuth=true&ctid=740be6bd-fd36-470e-94d9-0f0c777fadb9"
            frameborder="0"
            allowFullScreen="true"
            style="min-height: 700px;"
        >
        </iframe>
    </div>
</div>
