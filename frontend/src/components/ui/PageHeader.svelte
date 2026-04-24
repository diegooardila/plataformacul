<script>
    export let title;
    export let subtitle = "";
</script>

<div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 {$$props.class || ''}">
    <div>
        <h2 class="text-2xl sm:text-3xl font-bold text-gray-800">{title}</h2>
        {#if subtitle}
        <p class="text-gray-500 text-sm mt-1">{subtitle}</p>
        {/if}
    </div>
    {#if $$slots.action}
    <div>
        <slot name="action"></slot>
    </div>
    {/if}
</div>
