<script>
    export let title;
    export let isOpen = false;
    export let maxWidth = "max-w-2xl";
</script>

{#if isOpen}
<div class="fixed inset-0 z-40 flex items-center justify-center p-4">
    <button class="absolute inset-0 bg-black/50 border-0 outline-none" on:click={() => isOpen = false} aria-label="Cerrar modal"></button>
    <div class="relative bg-white rounded-xl shadow-2xl w-full {maxWidth} max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center px-6 py-4 border-b">
            <h3 class="text-lg font-bold text-gray-800">{title}</h3>
            <button on:click={() => isOpen = false} class="text-gray-400 hover:text-gray-600 cursor-pointer p-1 rounded-full hover:bg-gray-100 transition">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
        </div>
        <slot></slot>
    </div>
</div>
{/if}
