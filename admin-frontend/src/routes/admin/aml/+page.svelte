<script lang="ts">
  import { onMount } from 'svelte';
  import { token } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { ShieldAlert, Check, AlertCircle, RefreshCw, Layers, Globe } from '@lucide/svelte';

  let activeToken = "";
  let loading = $state(false);
  let errorMsg = $state("");
  let successMsg = $state("");

  let globalRules = $state<any[]>([]);
  let tierRules = $state<any[]>([]);
  let availableTiers = $state<any[]>([]);

  // Forms
  let globalForm = $state({ action: "add_money", limit_amount: 0 });
  let tierForm = $state({ tier_name: "", action: "add_money", limit_amount: 0 });

  async function loadData() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(v => activeToken = v || "")();
      
      const [amlData, tiersData] = await Promise.all([
        apiRequest('GET', '/api/aml/policies', null, activeToken),
        apiRequest('GET', '/api/tiers', null, activeToken)
      ]);
      
      globalRules = amlData.global_rules || [];
      tierRules = amlData.tier_rules || [];
      availableTiers = tiersData || [];
      if (availableTiers.length > 0) {
        tierForm.tier_name = availableTiers[0].name.toLowerCase();
      }
    } catch (err: any) {
      errorMsg = err.message || "Failed to load AML policies.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  async function submitGlobalRule(e: Event) {
    e.preventDefault();
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('POST', '/api/admin/requests', {
        request_type: 'update_global_aml',
        payload: JSON.stringify({
          action: globalForm.action,
          limit_amount: parseFloat(globalForm.limit_amount.toString())
        })
      }, activeToken);
      successMsg = "Global AML update request submitted to Maker-Checker Audit Center.";
      globalForm.limit_amount = 0;
    } catch (err: any) {
      errorMsg = err.message || "Failed to submit request.";
    }
  }

  async function submitTierRule(e: Event) {
    e.preventDefault();
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('POST', '/api/admin/requests', {
        request_type: 'update_tier_aml',
        payload: JSON.stringify({
          tier_name: tierForm.tier_name,
          action: tierForm.action,
          limit_amount: parseFloat(tierForm.limit_amount.toString())
        })
      }, activeToken);
      successMsg = "Tier AML update request submitted to Maker-Checker Audit Center.";
      tierForm.limit_amount = 0;
    } catch (err: any) {
      errorMsg = err.message || "Failed to submit request.";
    }
  }

  let activeTab = $state('global'); // 'global' or 'tier'
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0">
    <div>
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
        <ShieldAlert class="w-6 h-6 text-emerald-400" />
        <span>AML & Compliance Settings</span>
      </h1>
      <p class="text-xs text-slate-400 mt-1">
        Configure Global and Tier-specific Anti-Money Laundering limits. Changes require checker approval.
      </p>
    </div>
    <button 
      onclick={loadData}
      disabled={loading}
      class="flex items-center space-x-2 px-3 py-1.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-350 text-xs font-semibold rounded-xl transition disabled:opacity-50"
    >
      <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
      <span>Sync Policies</span>
    </button>
  </div>

  <!-- Messages -->
  {#if errorMsg}
    <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-4 rounded-xl text-xs max-w-2xl">
      <AlertCircle class="w-4 h-4 text-red-400 shrink-0" />
      <span>{errorMsg}</span>
    </div>
  {/if}

  {#if successMsg}
    <div class="flex items-start space-x-2 bg-emerald-950/40 border border-emerald-800/50 text-emerald-350 p-4 rounded-xl text-xs max-w-2xl">
      <Check class="w-4 h-4 text-emerald-400 shrink-0" />
      <span>{successMsg}</span>
    </div>
  {/if}

  <div class="flex border-b border-slate-800 bg-slate-900/40 rounded-t-2xl mt-6 overflow-hidden">
    <button 
      onclick={() => activeTab = 'global'}
      class="flex-1 py-4 text-xs font-bold uppercase tracking-wider transition-all border-b-2 {activeTab === 'global' ? 'border-emerald-500 text-emerald-400 bg-slate-900/80' : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900/60'}">
      <div class="flex items-center justify-center space-x-2">
        <Globe class="w-4 h-4" />
        <span>Global Limits</span>
      </div>
    </button>
    <button 
      onclick={() => activeTab = 'tier'}
      class="flex-1 py-4 text-xs font-bold uppercase tracking-wider transition-all border-b-2 {activeTab === 'tier' ? 'border-emerald-500 text-emerald-400 bg-slate-900/80' : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900/60'}">
      <div class="flex items-center justify-center space-x-2">
        <Layers class="w-4 h-4" />
        <span>Tier Overrides</span>
      </div>
    </button>
  </div>

  <div class="bg-slate-900/40 border border-t-0 border-slate-800/80 backdrop-blur rounded-b-2xl p-6 shadow-xl font-sans">
    
    <!-- Global Policies -->
    {#if activeTab === 'global'}
      <div class="space-y-6">
        <div class="mb-6 bg-slate-950/50 rounded-xl p-4 border border-slate-800">
          {#if globalRules.length === 0}
            <p class="text-xs text-slate-500">No global rules configured.</p>
          {:else}
            <div class="space-y-2">
              {#each globalRules as rule}
                <div class="flex justify-between items-center bg-slate-900 px-3 py-2 rounded-lg border border-slate-850">
                  <span class="text-xs font-mono font-bold text-slate-300">{rule.action}</span>
                  <span class="text-xs font-bold text-emerald-400">${rule.limit_amount.toLocaleString()}</span>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <form onsubmit={submitGlobalRule} class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Transaction Type</label>
            <select bind:value={globalForm.action} class="w-full bg-slate-950/60 border border-slate-800 text-white text-xs py-2 px-3 rounded-xl outline-none focus:border-emerald-500/50 transition">
              <option value="add_money">Add Money</option>
              <option value="transfer_money">Transfer Money</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">New Limit ($)</label>
            <input type="number" step="0.01" bind:value={globalForm.limit_amount} required class="w-full bg-slate-950/60 border border-slate-800 text-white text-xs py-2 px-3 rounded-xl outline-none focus:border-emerald-500/50 transition" />
          </div>
          <button type="submit" class="w-full py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold uppercase tracking-wider rounded-xl transition shadow shadow-emerald-500/10">
            Request Global Change
          </button>
        </form>
      </div>
    {/if}

    <!-- Tier Policies -->
    {#if activeTab === 'tier'}
      <div class="space-y-6">
        <div class="mb-6 bg-slate-950/50 rounded-xl p-4 border border-slate-800">
          {#if tierRules.length === 0}
            <p class="text-xs text-slate-500">No tier-specific overrides configured.</p>
          {:else}
            <div class="space-y-2">
              {#each tierRules as rule}
                <div class="flex justify-between items-center bg-slate-900 px-3 py-2 rounded-lg border border-slate-850">
                  <div class="flex items-center space-x-2">
                    <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase bg-purple-950/40 text-purple-400 border border-purple-900/30">{rule.tier_name}</span>
                    <span class="text-xs font-mono font-bold text-slate-300">{rule.action}</span>
                  </div>
                  <span class="text-xs font-bold text-emerald-400">${rule.limit_amount.toLocaleString()}</span>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <form onsubmit={submitTierRule} class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Subscription Tier</label>
              <select bind:value={tierForm.tier_name} class="w-full bg-slate-950/60 border border-slate-800 text-white text-xs py-2 px-3 rounded-xl outline-none focus:border-emerald-500/50 transition">
                {#each availableTiers as t}
                  <option value={t.name.toLowerCase()}>{t.name}</option>
                {/each}
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Transaction Type</label>
              <select bind:value={tierForm.action} class="w-full bg-slate-950/60 border border-slate-800 text-white text-xs py-2 px-3 rounded-xl outline-none focus:border-emerald-500/50 transition">
                <option value="add_money">Add Money</option>
                <option value="transfer_money">Transfer Money</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">New Limit ($)</label>
            <input type="number" step="0.01" bind:value={tierForm.limit_amount} required class="w-full bg-slate-950/60 border border-slate-800 text-white text-xs py-2 px-3 rounded-xl outline-none focus:border-emerald-500/50 transition" />
          </div>
          <button type="submit" class="w-full py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold uppercase tracking-wider rounded-xl transition shadow shadow-emerald-500/10">
            Request Tier Change
          </button>
        </form>
      </div>
    {/if}
  </div>

</div>
