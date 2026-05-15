<script>
    export let id;
    export let label = "";
    export let value;
    export let required = false;
    export let disabled = false;
    export let options = []; // Array of {value, label}
</script>

<div>
    {#if label}
    <label class="block text-sm font-medium text-gray-700 mb-1 {disabled ? 'opacity-40' : ''}" for="{id}">
        {label} {#if required}<span class="text-red-500">*</span>{/if}
    </label>
    {/if}
    <select
        {id}
        {required}
        {disabled}
        bind:value
        on:change
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white {disabled ? 'opacity-40 cursor-not-allowed bg-gray-50' : ''} {$$props.class || ''}"
    >
        {#each options as opt}
            <option value={opt.value}>{opt.label}</option>
        {/each}
        <slot></slot>
    </select>
</div>
