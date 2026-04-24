<script>
    export let message = "";
    export let type = "success"; // success, error
    export let show = false;
    
    $: bgClass = type === 'success' ? 'bg-green-600' : 'bg-red-600';
</script>

{#if show}
<div class="fixed top-20 right-5 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-50 transition-all {bgClass}">
    {message}
</div>
{/if}
