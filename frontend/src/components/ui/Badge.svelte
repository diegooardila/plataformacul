<script>
    export let color = "gray";
    export let text = "";
    
    const colorMap = {
        green: "bg-green-100 text-green-700",
        red: "bg-red-100 text-red-700",
        yellow: "bg-yellow-100 text-yellow-800",
        blue: "bg-blue-100 text-blue-700",
        gray: "bg-gray-100 text-gray-700",
        purple: "bg-purple-100 text-purple-700",
        orange: "bg-orange-100 text-orange-700",
        indigo: "bg-indigo-100 text-indigo-700"
    };
    
    $: currentClass = colorMap[color] || colorMap.gray;
</script>

<span class="inline-block {currentClass} text-xs font-semibold px-2.5 py-1 rounded-full {$$props.class || ''}">
    {#if text}{text}{:else}<slot></slot>{/if}
</span>
