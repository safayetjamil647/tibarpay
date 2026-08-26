<script lang="ts">
  import { Settings, Save, Server, Sliders, Shield, Database } from '@lucide/svelte';
  
  let sandboxMode = $state(true);
  let rateLimit = $state(100);
  let dbPool = $state(20);
  let maintenanceMode = $state(false);
  let logLevel = $state("INFO");
  let saveSuccess = $state(false);

  function handleSave(e: SubmitEvent) {
    e.preventDefault();
    saveSuccess = true;
    setTimeout(() => {
      saveSuccess = false;
    }, 3000);
  }
</script>

<div class="p-6 space-y-6 max-w-4xl w-full mx-auto overflow-y-auto">
  <div>
    <h1 class="text-2xl font-bold text-white tracking-tight">System Settings</h1>
    <p class="text-xs text-slate-400 mt-1">Configure global API variables, database bounds, and system rules.</p>
  </div>

  {#if saveSuccess}
    <div class="bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 p-4 rounded-xl text-sm animate-pulse">
      Settings saved and applied successfully.
    </div>
  {/if}

  <form onsubmit={handleSave} class="space-y-6">
    
    <!-- Panel 1: API Configuration -->
    <div class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 space-y-4">
      <div class="flex items-center space-x-2.5 mb-2">
        <Server class="w-5 h-5 text-emerald-400" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Server Configuration</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="rate-limit" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">API Rate Limit (req/min)</label>
          <input 
            id="rate-limit"
            type="number"
            bind:value={rateLimit}
            class="w-full bg-slate-950/50 border border-slate-850 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2 px-4 text-white text-sm outline-none transition"
          />
        </div>

        <div>
          <label for="log-level" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Logging Verbosity</label>
          <select 
            id="log-level"
            bind:value={logLevel}
            class="w-full bg-slate-950/50 border border-slate-850 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2 px-4 text-white text-sm outline-none transition">
            <option>DEBUG</option>
            <option>INFO</option>
            <option>WARNING</option>
            <option>ERROR</option>
          </select>
        </div>
      </div>

      <div class="flex items-center justify-between p-3 bg-slate-950/40 border border-slate-850 rounded-xl">
        <div>
          <p class="text-xs font-bold text-slate-200">Sandbox Pricing Engine</p>
          <p class="text-[10px] text-slate-500">Enable simulated data streams instead of real market feeds.</p>
        </div>
        <button 
          type="button" 
          onclick={() => sandboxMode = !sandboxMode}
          class="relative w-11 h-6 rounded-full transition-colors {sandboxMode ? 'bg-emerald-500' : 'bg-slate-800'}">
          <span class="absolute top-1 left-1 bg-slate-900 w-4 h-4 rounded-full transition-transform {sandboxMode ? 'translate-x-5' : 'translate-x-0'}"></span>
        </button>
      </div>
    </div>

    <!-- Panel 2: Database Settings -->
    <div class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 space-y-4">
      <div class="flex items-center space-x-2.5 mb-2">
        <Database class="w-5 h-5 text-emerald-400" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Database Settings</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="db-pool" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Max Session Pool Size</label>
          <input 
            id="db-pool"
            type="number"
            bind:value={dbPool}
            class="w-full bg-slate-950/50 border border-slate-850 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2 px-4 text-white text-sm outline-none transition"
          />
        </div>

        <div>
          <label for="active-driver" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Active DB Dialect</label>
          <input 
            id="active-driver"
            type="text"
            readonly
            value="sqlite/sqlalchemy2.0"
            class="w-full bg-slate-950/20 border border-slate-850 rounded-xl py-2 px-4 text-slate-500 text-sm outline-none cursor-not-allowed font-mono"
          />
        </div>
      </div>
    </div>

    <!-- Panel 3: Security & Maintenance -->
    <div class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 space-y-4">
      <div class="flex items-center space-x-2.5 mb-2">
        <Shield class="w-5 h-5 text-emerald-400" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Security & Maintenance</h2>
      </div>

      <div class="flex items-center justify-between p-3 bg-slate-950/40 border border-slate-850 rounded-xl">
        <div>
          <p class="text-xs font-bold text-slate-200">Maintenance Mode</p>
          <p class="text-[10px] text-slate-500">Block user API requests and display a structural downtime splash.</p>
        </div>
        <button 
          type="button" 
          onclick={() => maintenanceMode = !maintenanceMode}
          class="relative w-11 h-6 rounded-full transition-colors {maintenanceMode ? 'bg-red-500' : 'bg-slate-800'}">
          <span class="absolute top-1 left-1 bg-slate-900 w-4 h-4 rounded-full transition-transform {maintenanceMode ? 'translate-x-5' : 'translate-x-0'}"></span>
        </button>
      </div>
    </div>

    <div class="flex justify-end">
      <button 
        type="submit"
        class="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-slate-950 font-bold text-xs uppercase tracking-wider rounded-xl transition shadow-lg shadow-emerald-900/10">
        <Save class="w-4 h-4" />
        <span>Save Configuration</span>
      </button>
    </div>

  </form>
</div>
