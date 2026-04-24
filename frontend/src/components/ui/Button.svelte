<script>
    export let variant = 'primary'; // primary, secondary, danger
    export let type = 'button';
    export let disabled = false;
    export let fullWidth = false;

    let baseClass = "font-medium py-2 px-4 rounded-lg transition shadow-sm cursor-pointer border-0 flex justify-center items-center gap-2";
    
    $: variantClass = {
        primary: "bg-blue-600 hover:bg-blue-700 text-white",
        secondary: "bg-gray-200 hover:bg-gray-300 text-gray-800",
        danger: "bg-red-600 hover:bg-red-700 text-white",
        indigo: "bg-indigo-600 hover:bg-indigo-700 text-white"
    }[variant] || "bg-blue-600 font-white";

    $: widthClass = fullWidth ? "w-full" : "";
    $: disabledClass = disabled ? "opacity-50 cursor-not-allowed pointer-events-none" : "";
</script>

<button type={type === 'submit' ? 'submit' : 'button'} {disabled} class="{baseClass} {variantClass} {widthClass} {disabledClass} {$$props.class || ''}" on:click>
    <slot></slot>
</button>
