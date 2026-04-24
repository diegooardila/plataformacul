<script lang="ts">
    export let data: any[] = [];
    export let columns: { key: string; label: string; sortable?: boolean; center?: boolean }[] = [];
    export let pageSize: number = 10;
    export let searchPlaceholder: string = "Buscar...";
    export let searchFn: ((row: any, query: string) => boolean) | null = null;
    export let loading: boolean = false;
    export let loadingText: string = "Cargando...";
    export let emptyText: string = "No se encontraron registros";
    export let tableClass: string = "w-full";

    let search = "";
    let page = 1;
    let sortCol = "";
    let sortDir = 1;
    let rowsPerPage = pageSize;

    function defaultSearch(row: any, query: string): boolean {
        const q = query.toLowerCase();
        return columns.some(col =>
            String(row[col.key] ?? "").toLowerCase().includes(q)
        );
    }

    $: filtered = search
        ? data.filter(row => (searchFn ? searchFn(row, search) : defaultSearch(row, search)))
        : data;

    $: sorted = sortCol
        ? [...filtered].sort((a, b) => {
              const av = a[sortCol];
              const bv = b[sortCol];
              if (av == null) return sortDir;
              if (bv == null) return -sortDir;
              if (typeof av === "number" && typeof bv === "number") return sortDir * (av - bv);
              return sortDir * String(av).localeCompare(String(bv), "es", { numeric: true, sensitivity: "base" });
          })
        : filtered;

    $: totalPages = Math.max(1, Math.ceil(sorted.length / rowsPerPage));
    $: safePage = Math.min(page, totalPages);
    $: rows = sorted.slice((safePage - 1) * rowsPerPage, safePage * rowsPerPage);
    $: startIdx = sorted.length === 0 ? 0 : (safePage - 1) * rowsPerPage + 1;
    $: endIdx = Math.min(safePage * rowsPerPage, sorted.length);

    function setSort(key: string) {
        if (sortCol === key) {
            sortDir = -sortDir;
        } else {
            sortCol = key;
            sortDir = 1;
        }
        page = 1;
    }

    function prevPage() { if (page > 1) page--; }
    function nextPage() { if (page < totalPages) page++; }
</script>

<div>
    <!-- Barra de controles -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
        <div class="flex items-center gap-2 text-sm text-gray-500">
            <span>Mostrar</span>
            <select
                bind:value={rowsPerPage}
                on:change={() => (page = 1)}
                class="border border-gray-300 rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
            >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
            </select>
            <span>registros</span>
            {#if !loading}
                <span class="ml-2 text-gray-400">
                    — {sorted.length === 0 ? "Sin resultados" : `${startIdx}–${endIdx} de ${sorted.length}`}
                </span>
            {/if}
        </div>
        <input
            bind:value={search}
            on:input={() => (page = 1)}
            placeholder={searchPlaceholder}
            class="w-full sm:w-64 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
    </div>

    <!-- Tabla -->
    <div class="overflow-x-auto">
        <table class="{tableClass} text-sm">
            <thead class="bg-gray-50 border-b">
                <tr>
                    {#each columns as col}
                        <th
                            class="px-4 py-3 font-semibold whitespace-nowrap text-gray-600 {col.center ? 'text-center' : 'text-left'} {col.sortable !== false ? 'cursor-pointer select-none hover:bg-gray-100 transition-colors' : ''}"
                            on:click={() => col.sortable !== false && setSort(col.key)}
                        >
                            <span class="inline-flex items-center gap-1">
                                {col.label}
                                {#if col.sortable !== false}
                                    {#if sortCol === col.key}
                                        <span class="text-blue-500 text-xs">{sortDir === 1 ? "↑" : "↓"}</span>
                                    {:else}
                                        <span class="text-gray-300 text-xs">↕</span>
                                    {/if}
                                {/if}
                            </span>
                        </th>
                    {/each}
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {#if loading}
                    <tr>
                        <td colspan={columns.length} class="text-center py-10 text-gray-400">{loadingText}</td>
                    </tr>
                {:else if rows.length === 0}
                    <tr>
                        <td colspan={columns.length} class="text-center py-10 text-gray-400">
                            {search ? `Sin resultados para "${search}"` : emptyText}
                        </td>
                    </tr>
                {:else}
                    {#each rows as row, i}
                        <slot {row} {i} />
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>

    <!-- Paginación -->
    {#if totalPages > 1}
        <div class="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
            <span class="text-sm text-gray-500">Página {safePage} de {totalPages}</span>
            <div class="flex gap-2">
                <button
                    on:click={prevPage}
                    disabled={safePage === 1}
                    class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 font-medium transition {safePage === 1 ? 'opacity-40 cursor-not-allowed text-gray-400' : 'hover:bg-gray-50 cursor-pointer text-gray-700'}"
                >
                    ← Anterior
                </button>
                <button
                    on:click={nextPage}
                    disabled={safePage === totalPages}
                    class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 font-medium transition {safePage === totalPages ? 'opacity-40 cursor-not-allowed text-gray-400' : 'hover:bg-gray-50 cursor-pointer text-gray-700'}"
                >
                    Siguiente →
                </button>
            </div>
        </div>
    {/if}
</div>
