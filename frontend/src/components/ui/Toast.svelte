<script>
    import { fly } from "svelte/transition";
    import { cubicOut } from "svelte/easing";

    export let message = "";
    export let type = "success"; // success, error
    export let show = false;

    $: bgClass = type === 'success' ? 'bg-green-600' : 'bg-red-600';
</script>

{#if show}
<div
    class="fixed top-20 right-5 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium z-50 {bgClass}"
    in:fly={{ x: 80, duration: 280, easing: cubicOut }}
    out:fly={{ x: 80, duration: 200 }}
>
    {message}
</div>
{/if}
