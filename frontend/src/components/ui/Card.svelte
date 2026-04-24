<script>
    export let title = "";
</script>

<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 {$$props.class || ''}">
    {#if title}
    <h3 class="text-xl font-bold {$$props.titleClass || 'text-gray-800'} mb-4">{title}</h3>
    {/if}
    <slot></slot>
</div>
