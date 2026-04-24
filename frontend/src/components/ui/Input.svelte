<script>
    export let id;
    export let label = "";
    export let type = 'text';
    export let value;
    export let required = false;
    export let placeholder = "";
</script>

<div>
    {#if label}
    <label class="block text-sm font-medium text-gray-700 mb-1" for="{id}">
        {label} {#if required}<span class="text-red-500">*</span>{/if}
    </label>
    {/if}
    {#if type === 'password'}
        <input type="password" {id} {required} {placeholder} bind:value class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none {$$props.class || ''}" />
    {:else if type === 'email'}
        <input type="email" {id} {required} {placeholder} bind:value class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none {$$props.class || ''}" />
    {:else}
        <input type="text" {id} {required} {placeholder} bind:value class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none {$$props.class || ''}" />
    {/if}
</div>
