<script lang="ts">
  import Sidebar from '$lib/components/Sidebar.svelte';
  let { children } = $props();
</script>

<div class="flex-1 flex overflow-hidden w-full">
  <Sidebar role="user" />
  <div class="flex-1 flex flex-col overflow-hidden">
    {@render children()}
  </div>
</div>
