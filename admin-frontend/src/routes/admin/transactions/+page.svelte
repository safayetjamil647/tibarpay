<script lang="ts">
  import { onMount } from 'svelte';
  import { token } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { Activity, Clock, RefreshCw, AlertCircle } from '@lucide/svelte';

  let activeToken = "";
  let loading = $state(false);
  let errorMsg = $state("");
  let transactions = $state<any[]>([]);

  async function loadTransactions() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(v => activeToken = v || "")();
      
      // Fetch from both services
      const [addMoneyTxs, transferTxs] = await Promise.all([
        apiRequest('GET', '/api/add-money/transactions', null, activeToken).catch(() => []),
        apiRequest('GET', '/api/transfer-money/transactions', null, activeToken).catch(() => [])
      ]);
      
      let combined = [...(addMoneyTxs || []), ...(transferTxs || [])];
      
      // Sort by descending created_at
      combined.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      
      transactions = combined;
    } catch (err: any) {
      errorMsg = err.message || "Failed to load master ledger.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadTransactions();
  });
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0">
    <div>
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
        <Activity class="w-6 h-6 text-emerald-400" />
        <span>Master Ledger</span>
      </h1>
      <p class="text-xs text-slate-400 mt-1">
        Read-only global view of all financial transactions across the platform.
      </p>
    </div>
    <button 
      onclick={loadTransactions}
      disabled={loading}
      class="flex items-center space-x-2 px-3 py-1.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-350 text-xs font-semibold rounded-xl transition disabled:opacity-50"
    >
      <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
      <span>Sync Ledger</span>
    </button>
  </div>

  {#if errorMsg}
    <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-4 rounded-xl text-xs max-w-2xl">
      <AlertCircle class="w-4 h-4 text-red-400 shrink-0" />
      <span>{errorMsg}</span>
    </div>
  {/if}

  <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl overflow-hidden flex flex-col">
    <div class="p-5 border-b border-slate-800 bg-slate-950/20 flex justify-between items-center">
      <h2 class="text-xs font-bold text-white uppercase tracking-wider">All Network Transactions</h2>
      <span class="text-xs font-mono text-slate-500">{transactions.length} records</span>
    </div>

    <div class="overflow-x-auto">
      {#if transactions.length === 0}
        <div class="p-8 text-center text-slate-500 text-xs">
          No financial records found in the ledger.
        </div>
      {:else}
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-950/30 text-slate-400 font-semibold border-b border-slate-800">
              <th class="p-4">Tx ID</th>
              <th class="p-4">User ID</th>
              <th class="p-4">Type</th>
              <th class="p-4">Amount</th>
              <th class="p-4">Details</th>
              <th class="p-4">Date</th>
            </tr>
          </thead>
          <tbody>
            {#each transactions as tx}
              <tr class="border-b border-slate-850 hover:bg-slate-900/10 transition">
                <td class="p-4 font-mono text-slate-450">#{tx.id}</td>
                <td class="p-4 font-mono text-slate-300">UID: {tx.user_id}</td>
                <td class="p-4">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border
                               {tx.type === 'ADD_MONEY' ? 'bg-emerald-950/40 text-emerald-450 border-emerald-900/40' : 
                                tx.type === 'TRANSFER_IN' ? 'bg-blue-950/40 text-blue-400 border-blue-900/40' : 
                                'bg-purple-950/40 text-purple-400 border-purple-900/40'}">
                    {tx.type}
                  </span>
                </td>
                <td class="p-4 font-mono font-bold {tx.type === 'TRANSFER_OUT' ? 'text-red-400' : 'text-emerald-400'}">
                  {tx.type === 'TRANSFER_OUT' ? '-' : '+'}${tx.amount.toLocaleString()}
                </td>
                <td class="p-4 text-slate-500 font-mono text-[10px]">
                  {tx.details || '--'}
                </td>
                <td class="p-4 text-slate-500 font-mono flex items-center space-x-1.5">
                  <Clock class="w-3 h-3" />
                  <span>{new Date(tx.created_at).toLocaleString()}</span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  </div>
</div>
