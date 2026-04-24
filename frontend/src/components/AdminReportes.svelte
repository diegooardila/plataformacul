<script lang="ts">
    import { onMount } from "svelte";
    import jsPDF from "jspdf";
    import autoTable from "jspdf-autotable";
    import { getUsuarios } from "../lib/services/users";
    import { getCourses } from "../lib/services/courses";
    import { getEnrollments } from "../lib/services/enrollments";

    const reportTabs = [
        {
            id: "cursos",
            label: "Gestión de Cursos",
            url: "https://app.powerbi.com/reportEmbed?reportId=8966942f-e3ca-4cc8-a31c-7070054c0250&autoAuth=true&ctid=740be6bd-fd36-470e-94d9-0f0c777fadb9",
        },
    ];
    let activeTab = reportTabs[0].id;
    $: activeReport = reportTabs.find((t) => t.id === activeTab);

    const statusMap: Record<string, string> = {
        "1": "Activo", "2": "Inactivo", "3": "Pendiente",
        "4": "Finalizado", "5": "Cancelado", "6": "Suspendido",
    };

    let loading = true;
    let generatingPDF = false;

    // Stats cards
    let totalActivos = 0;
    let totalEstudiantes = 0;
    let totalDocentes = 0;
    let totalCursos = 0;
    let totalCuposOfrecidos = 0;
    let totalInscripciones = 0;
    let topCursoNombre = "N/A";
    let topCursoInscripciones = 0;

    let allUsers: any[] = [];
    let allCourses: any[] = [];
    let allEnrollments: any[] = [];

    // ── Modo del generador ───────────────────────────────────────────────
    type Mode = "ocupacion" | "inscripciones";
    let mode: Mode = "ocupacion";

    // Filtros compartidos
    let filterCursoId = "";
    // Solo para modo inscripciones
    let filterEstadoInsc = "";

    function resetFilters() {
        filterCursoId = "";
        filterEstadoInsc = "";
    }

    // ── Datos computados ─────────────────────────────────────────────────

    // Modo 1: ocupación por curso
    $: reporteOcupacion = allCourses
        .filter((c) => !filterCursoId || String(c.course_id) === filterCursoId)
        .map((c) => {
            const teacher = allUsers.find((u) => u.user_id === c.teacher_user_id);
            const teacherName = teacher
                ? [teacher.first_name, teacher.last_name].filter(Boolean).join(" ")
                : "Sin asignar";
            const inscritos = allEnrollments.filter((e) => e.course_id === c.course_id).length;
            const disponibles = Math.max(0, c.max_capacity - inscritos);
            const pct = c.max_capacity > 0 ? Math.round((inscritos / c.max_capacity) * 100) : 0;
            return { ...c, teacherName, inscritos, disponibles, pct };
        });

    // Modo 2: detalle de inscripciones
    $: reporteInscripciones = allEnrollments
        .filter((e) => {
            const cursoOk = !filterCursoId || String(e.course_id) === filterCursoId;
            const estOk = !filterEstadoInsc || String(e.status_id) === filterEstadoInsc;
            return cursoOk && estOk;
        })
        .map((e) => {
            const student = allUsers.find((u) => u.user_id === e.student_user_id);
            const course = allCourses.find((c) => c.course_id === e.course_id);
            const teacher = course
                ? allUsers.find((u) => u.user_id === course.teacher_user_id)
                : null;
            return {
                studentName: student
                    ? [student.first_name, student.middle_name, student.last_name, student.second_last_name].filter(Boolean).join(" ")
                    : "—",
                studentDoc: student?.identity_document || "—",
                studentEmail: student?.email || "—",
                courseName: course?.course_name || "—",
                courseCode: course?.course_code || "—",
                courseSchedule: course?.schedule || "—",
                teacherName: teacher
                    ? [teacher.first_name, teacher.last_name].filter(Boolean).join(" ")
                    : "Sin asignar",
                statusLabel: statusMap[String(e.status_id)] || "—",
                status_id: e.status_id,
            };
        });

    $: activeCount = mode === "ocupacion" ? reporteOcupacion.length : reporteInscripciones.length;
    $: hasResults = activeCount > 0;

    onMount(async () => {
        try {
            const [users, courses, enrollments] = await Promise.all([
                getUsuarios(), getCourses(), getEnrollments(),
            ]);
            allUsers = users || [];
            allCourses = courses || [];
            allEnrollments = enrollments || [];

            totalActivos = allUsers.filter((u) => u.status_id === 1).length;
            totalEstudiantes = allUsers.filter((u) => u.role_id === 3).length;
            totalDocentes = allUsers.filter((u) => u.role_id === 2).length;
            totalCursos = allCourses.length;
            totalCuposOfrecidos = allCourses.reduce((sum, c) => sum + c.max_capacity, 0);
            totalInscripciones = allEnrollments.length;

            if (allCourses.length > 0 && allEnrollments.length > 0) {
                const countMap: Record<number, number> = {};
                allEnrollments.forEach((e) => {
                    countMap[e.course_id] = (countMap[e.course_id] || 0) + 1;
                });
                let maxCount = 0, maxId: number | null = null;
                for (const [cId, count] of Object.entries(countMap)) {
                    if (count > maxCount) { maxCount = count; maxId = parseInt(cId); }
                }
                if (maxId) {
                    const best = allCourses.find((c) => c.course_id === maxId);
                    if (best) { topCursoNombre = best.course_name; topCursoInscripciones = maxCount; }
                }
            }
        } catch (error) {
            console.error("Error generando reportes", error);
        } finally {
            loading = false;
        }
    });

    // ── PDF ──────────────────────────────────────────────────────────────
    function buildPDFHeader(doc: any, title: string, subtitle: string, filters: string[]) {
        const pageW = doc.internal.pageSize.getWidth();
        const now = new Date();
        const dateStr = now.toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" });
        const timeStr = now.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });

        doc.setFillColor(30, 58, 95);
        doc.rect(0, 0, pageW, 40, "F");

        doc.setTextColor(255, 255, 255);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(15);
        doc.text("SISTEMA ACADÉMICO CUL", 14, 13);

        doc.setFont("helvetica", "bold");
        doc.setFontSize(10);
        doc.text(title, 14, 22);

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.text(subtitle, 14, 29);
        doc.text(`Generado: ${dateStr}  •  ${timeStr}`, 14, 36);

        filters.forEach((f, i) => {
            doc.text(f, pageW - 14, 13 + i * 7, { align: "right" });
        });

        doc.setDrawColor(96, 165, 250);
        doc.setLineWidth(1);
        doc.line(14, 40, pageW - 14, 40);
    }

    function buildPDFFooter(doc: any) {
        const pageCount = (doc as any).internal.getNumberOfPages();
        for (let p = 1; p <= pageCount; p++) {
            doc.setPage(p);
            const pageW = doc.internal.pageSize.getWidth();
            const pageH = doc.internal.pageSize.getHeight();
            doc.setFillColor(30, 58, 95);
            doc.rect(0, pageH - 12, pageW, 12, "F");
            doc.setTextColor(255, 255, 255);
            doc.setFont("helvetica", "normal");
            doc.setFontSize(7.5);
            doc.text("Sistema Académico CUL  —  Documento generado automáticamente.", 14, pageH - 4);
            doc.text(`Página ${p} de ${pageCount}`, pageW - 14, pageH - 4, { align: "right" });
        }
    }

    function buildSummaryBar(doc: any, stats: { label: string; value: string; color: [number, number, number] }[], yStart: number) {
        const pageW = doc.internal.pageSize.getWidth();
        doc.setFillColor(239, 246, 255);
        doc.roundedRect(14, yStart, pageW - 28, 22, 2, 2, "F");
        const colW = (pageW - 28) / stats.length;
        stats.forEach((s, i) => {
            const x = 14 + i * colW + colW / 2;
            doc.setFont("helvetica", "bold");
            doc.setFontSize(13);
            doc.setTextColor(s.color[0], s.color[1], s.color[2]);
            doc.text(s.value, x, yStart + 11, { align: "center" });
            doc.setFont("helvetica", "normal");
            doc.setFontSize(7);
            doc.setTextColor(80, 80, 80);
            doc.text(s.label, x, yStart + 18, { align: "center" });
        });
    }

    function generatePDF() {
        generatingPDF = true;
        try {
            const doc = new jsPDF({ orientation: "landscape" });
            const now = new Date();

            if (mode === "ocupacion") {
                const cursoLabel = filterCursoId
                    ? (allCourses.find((c) => String(c.course_id) === filterCursoId)?.course_name ?? "Todos")
                    : "Todos";

                buildPDFHeader(doc,
                    "Reporte de Ocupación de Cursos Electivos",
                    "Capacidad, inscritos y disponibilidad por curso",
                    [`Curso: ${cursoLabel}`]
                );

                const totalInscritos = reporteOcupacion.reduce((s, c) => s + c.inscritos, 0);
                const totalDisp = reporteOcupacion.reduce((s, c) => s + c.disponibles, 0);
                const avgPct = reporteOcupacion.length > 0
                    ? Math.round(reporteOcupacion.reduce((s, c) => s + c.pct, 0) / reporteOcupacion.length)
                    : 0;

                buildSummaryBar(doc, [
                    { label: "Cursos", value: String(reporteOcupacion.length), color: [30, 58, 95] },
                    { label: "Total inscritos", value: String(totalInscritos), color: [29, 78, 216] },
                    { label: "Cupos disponibles", value: String(totalDisp), color: [21, 128, 61] },
                    { label: "Ocupación promedio", value: `${avgPct}%`, color: avgPct >= 80 ? [185, 28, 28] : [146, 64, 14] },
                ], 45);

                autoTable(doc, {
                    startY: 73,
                    head: [["Código", "Nombre del Curso", "Docente", "Horario", "Capacidad", "Inscritos", "Disponibles", "Ocupación"]],
                    body: reporteOcupacion.map((c) => [
                        c.course_code || "—",
                        c.course_name,
                        c.teacherName,
                        c.schedule || "—",
                        c.max_capacity,
                        c.inscritos,
                        c.disponibles,
                        `${c.pct}%`,
                    ]),
                    headStyles: { fillColor: [30, 58, 95], textColor: 255, fontStyle: "bold", fontSize: 8.5, cellPadding: 4 },
                    alternateRowStyles: { fillColor: [248, 250, 255] },
                    bodyStyles: { fontSize: 8, textColor: [40, 40, 40], cellPadding: 3.5 },
                    columnStyles: {
                        0: { halign: "center", cellWidth: 22 },
                        4: { halign: "center", cellWidth: 22 },
                        5: { halign: "center", cellWidth: 22, fontStyle: "bold" },
                        6: { halign: "center", cellWidth: 25 },
                        7: { halign: "center", cellWidth: 22, fontStyle: "bold" },
                    },
                    didParseCell: (data: any) => {
                        if (data.section === "body" && data.column.index === 7) {
                            const pct = parseInt(String(data.cell.raw));
                            if (pct >= 90) data.cell.styles.textColor = [185, 28, 28];
                            else if (pct >= 70) data.cell.styles.textColor = [146, 64, 14];
                            else data.cell.styles.textColor = [21, 128, 61];
                        }
                    },
                    margin: { left: 14, right: 14 },
                });

                buildPDFFooter(doc);
                doc.save(`ocupacion-cursos-${now.toISOString().slice(0, 10)}.pdf`);

            } else {
                const cursoLabel = filterCursoId
                    ? (allCourses.find((c) => String(c.course_id) === filterCursoId)?.course_name ?? "Todos")
                    : "Todos";
                const estLabel = filterEstadoInsc ? (statusMap[filterEstadoInsc] ?? "Todos") : "Todos";

                buildPDFHeader(doc,
                    "Reporte de Inscripciones a Cursos Electivos",
                    "Detalle de estudiantes inscritos por curso",
                    [`Curso: ${cursoLabel}`, `Estado: ${estLabel}`]
                );

                const activas = reporteInscripciones.filter((r) => r.status_id === 1).length;
                const pendientes = reporteInscripciones.filter((r) => r.status_id === 3).length;
                const otras = reporteInscripciones.length - activas - pendientes;

                buildSummaryBar(doc, [
                    { label: "Total inscripciones", value: String(reporteInscripciones.length), color: [30, 58, 95] },
                    { label: "Activas", value: String(activas), color: [21, 128, 61] },
                    { label: "Pendientes", value: String(pendientes), color: [146, 64, 14] },
                    { label: "Otras", value: String(otras), color: [100, 100, 100] },
                ], 45);

                autoTable(doc, {
                    startY: 73,
                    head: [["Documento", "Estudiante", "Email", "Curso Electivo", "Código", "Docente", "Horario", "Estado"]],
                    body: reporteInscripciones.map((r) => [
                        r.studentDoc,
                        r.studentName,
                        r.studentEmail,
                        r.courseName,
                        r.courseCode,
                        r.teacherName,
                        r.courseSchedule,
                        r.statusLabel,
                    ]),
                    headStyles: { fillColor: [30, 58, 95], textColor: 255, fontStyle: "bold", fontSize: 8, cellPadding: 4 },
                    alternateRowStyles: { fillColor: [248, 250, 255] },
                    bodyStyles: { fontSize: 7.5, textColor: [40, 40, 40], cellPadding: 3 },
                    columnStyles: {
                        0: { cellWidth: 24 },
                        1: { cellWidth: 42 },
                        2: { cellWidth: 46 },
                        4: { halign: "center", cellWidth: 18 },
                        7: { halign: "center", fontStyle: "bold", cellWidth: 22 },
                    },
                    didParseCell: (data: any) => {
                        if (data.section === "body" && data.column.index === 7) {
                            const val = String(data.cell.raw);
                            if (val === "Activo") data.cell.styles.textColor = [21, 128, 61];
                            else if (val === "Inactivo" || val === "Suspendido" || val === "Cancelado") data.cell.styles.textColor = [185, 28, 28];
                            else if (val === "Pendiente") data.cell.styles.textColor = [146, 64, 14];
                        }
                    },
                    margin: { left: 14, right: 14 },
                });

                buildPDFFooter(doc);
                doc.save(`inscripciones-${now.toISOString().slice(0, 10)}.pdf`);
            }
        } finally {
            generatingPDF = false;
        }
    }
</script>

<div class="flex-1">
    <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Reportes y Estadísticas</h2>
        <p class="text-gray-500 text-sm mt-1">Visión general del estado actual del sistema académico.</p>
    </div>

    {#if loading}
        <div class="flex items-center justify-center p-12">
            <p class="text-gray-500 font-medium">Calculando métricas...</p>
        </div>
    {:else}
        <!-- Tarjetas de métricas -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-gray-500 font-semibold text-sm">Total Usuarios Activos</h3>
                    <div class="p-2 bg-blue-50 rounded-lg text-blue-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                    </div>
                </div>
                <div>
                    <p class="text-3xl font-bold text-gray-800 mb-1">{totalActivos}</p>
                    <div class="flex text-sm text-gray-500 gap-4 mt-2">
                        <span><strong class="text-gray-700">{totalEstudiantes}</strong> Estudiantes</span>
                        <span><strong class="text-gray-700">{totalDocentes}</strong> Docentes</span>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-gray-500 font-semibold text-sm">Cursos Habilitados</h3>
                    <div class="p-2 bg-purple-50 rounded-lg text-purple-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                    </div>
                </div>
                <div>
                    <p class="text-3xl font-bold text-gray-800 mb-1">{totalCursos}</p>
                    <p class="text-sm text-gray-500 mt-2">Capacidad total: <strong class="text-gray-700">{totalCuposOfrecidos}</strong> cupos</p>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-gray-500 font-semibold text-sm">Total Inscripciones</h3>
                    <div class="p-2 bg-green-50 rounded-lg text-green-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </div>
                </div>
                <div>
                    <p class="text-3xl font-bold text-gray-800 mb-1">{totalInscripciones}</p>
                    <div class="mt-2 text-sm">
                        <span class="text-gray-500">Curso más popular: </span>
                        <span class="font-semibold text-gray-700">{topCursoNombre}</span>
                        <span class="text-xs bg-green-100 text-green-800 px-1.5 rounded">{topCursoInscripciones} matriculados</span>
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- ── GENERADOR DE REPORTES ──────────────────────────────────────── -->
    {#if !loading}
        <div class="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">

            <!-- Encabezado -->
            <div class="bg-gradient-to-r from-blue-900 to-blue-700 px-6 py-4 flex flex-col sm:flex-row sm:items-center gap-4">
                <div class="flex items-center gap-3 flex-1">
                    <div class="p-2 bg-white/10 rounded-lg shrink-0">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-white font-bold text-base">Generador de Reportes</h3>
                        <p class="text-blue-200 text-xs">Consulta en tiempo real · Exporta a PDF</p>
                    </div>
                </div>

                <!-- Selector de modo -->
                <div class="flex bg-white/10 rounded-lg p-1 gap-1">
                    <button on:click={() => { mode = "ocupacion"; resetFilters(); }}
                        class="px-3 py-1.5 rounded-md text-xs font-semibold transition {mode === 'ocupacion' ? 'bg-white text-blue-900' : 'text-white hover:bg-white/10'}">
                        Ocupación de Cursos
                    </button>
                    <button on:click={() => { mode = "inscripciones"; resetFilters(); }}
                        class="px-3 py-1.5 rounded-md text-xs font-semibold transition {mode === 'inscripciones' ? 'bg-white text-blue-900' : 'text-white hover:bg-white/10'}">
                        Detalle de Inscripciones
                    </button>
                </div>
            </div>

            <div class="p-6">
                <!-- Filtros -->
                <div class="flex flex-wrap gap-4 mb-6">
                    <div class="flex-1 min-w-[200px]">
                        <label for="sel-curso" class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                            Curso Electivo
                        </label>
                        <select id="sel-curso" bind:value={filterCursoId} class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                            <option value="">Todos los cursos</option>
                            {#each allCourses as c}
                                <option value={String(c.course_id)}>{c.course_name}</option>
                            {/each}
                        </select>
                    </div>

                    {#if mode === "inscripciones"}
                        <div class="flex-1 min-w-[180px]">
                            <label for="sel-estado" class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                                Estado de Inscripción
                            </label>
                            <select id="sel-estado" bind:value={filterEstadoInsc} class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                                <option value="">Todos los estados</option>
                                <option value="1">Activo</option>
                                <option value="2">Inactivo</option>
                                <option value="3">Pendiente</option>
                                <option value="4">Finalizado</option>
                                <option value="5">Cancelado</option>
                                <option value="6">Suspendido</option>
                            </select>
                        </div>
                    {/if}
                </div>

                <!-- Barra de resultados + botón PDF -->
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-5">
                    <div class="flex items-center gap-3 flex-wrap">
                        <span class="inline-flex items-center gap-1.5 bg-blue-50 text-blue-700 text-sm font-semibold px-3 py-1.5 rounded-full">
                            {#if mode === "ocupacion"}
                                {activeCount} curso{activeCount !== 1 ? "s" : ""}
                            {:else}
                                {activeCount} inscripción{activeCount !== 1 ? "es" : ""}
                            {/if}
                        </span>
                        {#if filterCursoId || filterEstadoInsc}
                            <button on:click={resetFilters} class="text-xs text-gray-400 hover:text-gray-600 underline transition">
                                Limpiar filtros
                            </button>
                        {/if}
                    </div>

                    <button on:click={generatePDF} disabled={generatingPDF || !hasResults}
                        class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-900 hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-sm transition">
                        {#if generatingPDF}
                            <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                            </svg>
                            Generando...
                        {:else}
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            Descargar PDF
                        {/if}
                    </button>
                </div>

                <!-- Tabla: Ocupación de Cursos -->
                {#if mode === "ocupacion"}
                    {#if reporteOcupacion.length > 0}
                        <div class="overflow-x-auto rounded-lg border border-gray-100 max-h-96 overflow-y-auto">
                            <table class="w-full text-sm">
                                <thead class="sticky top-0 z-10">
                                    <tr class="bg-blue-900 text-white text-xs uppercase tracking-wide">
                                        <th class="px-3 py-3 text-left">Código</th>
                                        <th class="px-3 py-3 text-left">Nombre del Curso</th>
                                        <th class="px-3 py-3 text-left">Docente</th>
                                        <th class="px-3 py-3 text-left">Horario</th>
                                        <th class="px-3 py-3 text-center">Capacidad</th>
                                        <th class="px-3 py-3 text-center">Inscritos</th>
                                        <th class="px-3 py-3 text-center">Disponibles</th>
                                        <th class="px-3 py-3 text-center">Ocupación</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each reporteOcupacion as c, i}
                                        <tr class="{i % 2 === 0 ? 'bg-white' : 'bg-blue-50/30'} border-b border-gray-50 hover:bg-blue-50/60 transition-colors">
                                            <td class="px-3 py-2.5 font-mono text-xs text-gray-500">{c.course_code || "—"}</td>
                                            <td class="px-3 py-2.5 font-medium text-gray-800">{c.course_name}</td>
                                            <td class="px-3 py-2.5 text-gray-600 text-xs">{c.teacherName}</td>
                                            <td class="px-3 py-2.5 text-gray-500 text-xs">{c.schedule || "—"}</td>
                                            <td class="px-3 py-2.5 text-center text-gray-700">{c.max_capacity}</td>
                                            <td class="px-3 py-2.5 text-center font-bold text-blue-700">{c.inscritos}</td>
                                            <td class="px-3 py-2.5 text-center {c.disponibles === 0 ? 'text-red-600 font-semibold' : 'text-green-700'}">{c.disponibles}</td>
                                            <td class="px-3 py-2.5 text-center">
                                                <div class="flex items-center justify-center gap-1.5">
                                                    <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                                        <div class="h-full rounded-full {c.pct >= 90 ? 'bg-red-500' : c.pct >= 70 ? 'bg-yellow-500' : 'bg-green-500'}"
                                                            style="width: {c.pct}%"></div>
                                                    </div>
                                                    <span class="text-xs font-bold {c.pct >= 90 ? 'text-red-600' : c.pct >= 70 ? 'text-yellow-600' : 'text-green-600'}">{c.pct}%</span>
                                                </div>
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    {:else}
                        <div class="text-center py-10 text-gray-400">
                            <p class="text-sm">No hay cursos con los filtros seleccionados</p>
                        </div>
                    {/if}

                <!-- Tabla: Detalle de Inscripciones -->
                {:else}
                    {#if reporteInscripciones.length > 0}
                        <div class="overflow-x-auto rounded-lg border border-gray-100 max-h-96 overflow-y-auto">
                            <table class="w-full text-sm">
                                <thead class="sticky top-0 z-10">
                                    <tr class="bg-blue-900 text-white text-xs uppercase tracking-wide">
                                        <th class="px-3 py-3 text-left">Documento</th>
                                        <th class="px-3 py-3 text-left">Estudiante</th>
                                        <th class="px-3 py-3 text-left">Email</th>
                                        <th class="px-3 py-3 text-left">Curso Electivo</th>
                                        <th class="px-3 py-3 text-center">Código</th>
                                        <th class="px-3 py-3 text-left">Docente</th>
                                        <th class="px-3 py-3 text-left">Horario</th>
                                        <th class="px-3 py-3 text-center">Estado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each reporteInscripciones as r, i}
                                        <tr class="{i % 2 === 0 ? 'bg-white' : 'bg-blue-50/30'} border-b border-gray-50 hover:bg-blue-50/60 transition-colors">
                                            <td class="px-3 py-2.5 font-mono text-xs text-gray-500">{r.studentDoc}</td>
                                            <td class="px-3 py-2.5 font-medium text-gray-800">{r.studentName}</td>
                                            <td class="px-3 py-2.5 text-gray-500 text-xs">{r.studentEmail}</td>
                                            <td class="px-3 py-2.5 text-gray-700 text-xs font-medium">{r.courseName}</td>
                                            <td class="px-3 py-2.5 text-center font-mono text-xs text-gray-500">{r.courseCode}</td>
                                            <td class="px-3 py-2.5 text-gray-600 text-xs">{r.teacherName}</td>
                                            <td class="px-3 py-2.5 text-gray-500 text-xs">{r.courseSchedule}</td>
                                            <td class="px-3 py-2.5 text-center">
                                                <span class="text-xs px-2 py-0.5 rounded-full font-semibold
                                                    {r.status_id === 1 ? 'bg-green-100 text-green-700' :
                                                     r.status_id === 3 ? 'bg-yellow-100 text-yellow-700' :
                                                     r.status_id === 5 || r.status_id === 6 ? 'bg-red-100 text-red-700' :
                                                     'bg-gray-100 text-gray-600'}">
                                                    {r.statusLabel}
                                                </span>
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    {:else}
                        <div class="text-center py-10 text-gray-400">
                            <p class="text-sm">No hay inscripciones con los filtros seleccionados</p>
                        </div>
                    {/if}
                {/if}
            </div>
        </div>
    {/if}

    <!-- Power BI -->
    <div class="mt-8 w-full overflow-hidden rounded-xl shadow-sm border border-gray-100 bg-white">
        {#if reportTabs.length > 1}
            <div class="flex border-b border-gray-100 px-4 pt-3 gap-1">
                {#each reportTabs as tab}
                    <button on:click={() => activeTab = tab.id}
                        class="px-4 py-2 text-sm font-medium rounded-t-lg transition border-b-2 {activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}">
                        {tab.label}
                    </button>
                {/each}
            </div>
        {/if}
        <iframe title={activeReport?.label ?? "Reporte Power BI"} width="100%" src={activeReport?.url}
            frameborder="0" allowFullScreen={true}
            style="height: clamp(400px, 60vw, 700px); display: block;" />
    </div>
</div>
