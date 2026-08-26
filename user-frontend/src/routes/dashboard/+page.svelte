<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { logout, userEmail, token } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import Chart from '$lib/components/Chart.svelte';
  import { 
    TrendingUp, LogOut, RefreshCw, Layers, Wallet, ArrowRightLeft, Plus
  } from '@lucide/svelte';

  let activeSymbol = $state("BTCUSD");
  let symbols = ["BTCUSD", "ETHUSD", "AAPL", "TSLA", "MSFT"];
  let emailVal = $state("");
  let activeToken = "";
  let userTierVal = $state("starter");
  let accountNumber = $state("");
  let amlLimits = $state<{action: string, limit_amount: number, source: string}[]>([]);
  
  // Finance State
  let activeTab = $state("trading"); // "trading", "add_money", "transfer"
  let balance = $state(0.0);
  let financeTransactions = $state<any[]>([]);

  // Forms
  let addMoneyAmount = $state<number>(0);
  let transferAmount = $state<number>(0);
  let transferRecipient = $state<str>("");
  let actionMessage = $state("");
  let actionError = $state("");

  // Asset prices (derived or mocked)
  let prices = $state<Record<string, number>>({
    "BTCUSD": 63520.40,
    "ETHUSD": 3452.80,
    "AAPL": 178.65,
    "TSLA": 210.15,
    "MSFT": 415.30
  });

  onMount(() => {
    userEmail.subscribe(val => emailVal = val || "")();
    token.subscribe(val => activeToken = val || "")();

    fetchUserData();

    const interval = setInterval(() => {
      for (let s in prices) {
        const change = (Math.random() - 0.5) * (prices[s] * 0.001);
        prices[s] = parseFloat((prices[s] + change).toFixed(2));
      }
    }, 3000);

    return () => clearInterval(interval);
  });

  async function fetchUserData() {
    try {
      const user = await apiRequest('GET', '/api/auth/me', null, activeToken);
      userTierVal = user.tier || "starter";
      accountNumber = user.account_number || "N/A";
      
      const limits = await apiRequest('GET', `/api/aml/user-limits?tier=${userTierVal}`, null, activeToken).catch(()=>[]);
      amlLimits = limits || [];

      // Fetch balance
      const balRes = await apiRequest('GET', '/api/add-money/balance', null, activeToken).catch(()=>({balance: 0}));
      balance = balRes.balance || 0;

      // Fetch transactions
      const [addMoneyTxs, transferTxs] = await Promise.all([
        apiRequest('GET', '/api/add-money/transactions', null, activeToken).catch(() => []),
        apiRequest('GET', '/api/transfer-money/transactions', null, activeToken).catch(() => [])
      ]);
      let combined = [...(addMoneyTxs || []), ...(transferTxs || [])];
      combined.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      financeTransactions = combined;
      
    } catch (e) {
      console.error("Failed to load user data", e);
    }
  }

  function handleLogout() {
    logout();
    goto('/login');
  }

  function selectSymbol(sym: string) {
    activeSymbol = sym;
  }

  async function handleAddMoney(e: Event) {
    e.preventDefault();
    actionError = ""; actionMessage = "";
    try {
      await apiRequest('POST', '/api/add-money/execute', { amount: addMoneyAmount }, activeToken);
      actionMessage = `Successfully added $${addMoneyAmount}`;
      addMoneyAmount = 0;
      fetchUserData();
    } catch (err: any) {
      actionError = err.message || "Add money failed";
    }
  }

  async function handleTransfer(e: Event) {
    e.preventDefault();
    actionError = ""; actionMessage = "";
    try {
      await apiRequest('POST', '/api/transfer-money/execute', { 
        recipient_account_number: transferRecipient,
        amount: transferAmount 
      }, activeToken);
      actionMessage = `Successfully transferred $${transferAmount}`;
      transferAmount = 0;
      transferRecipient = "";
      fetchUserData();
    } catch (err: any) {
      actionError = err.message || "Transfer failed";
    }
  }
</script>

<header class="h-16 border-b border-slate-800 bg-[#090d16]/80 backdrop-blur px-6 flex items-center justify-between shrink-0">
  <div class="flex items-center space-x-3">
    <div class="p-2 bg-gradient-to-tr from-emerald-600 to-teal-400 rounded-lg shadow-md shadow-emerald-500/10">
      <TrendingUp class="w-5 h-5 text-slate-900" />
    </div>
    <span class="font-bold tracking-wider text-white">TIBARPAY</span>
  </div>

  <div class="flex items-center space-x-4">
    <div class="hidden sm:flex flex-col items-end">
      <span class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Acct: {accountNumber}</span>
      <span class="text-xs font-semibold text-slate-200">{emailVal}</span>
    </div>
    <button 
      onclick={handleLogout}
      class="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-red-800 hover:text-red-400 transition"
      title="Logout">
      <LogOut class="w-4 h-4" />
    </button>
  </div>
</header>

<div class="flex-1 flex flex-col lg:flex-row overflow-hidden">
  <!-- Left Side: Watchlist & Balance -->
  <aside class="w-full lg:w-64 border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#080c14] flex flex-col shrink-0">
    <div class="p-5 border-b border-slate-800 bg-slate-900/50 flex flex-col items-center justify-center space-y-2">
      <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Available Balance</span>
      <span class="text-2xl font-mono font-bold text-white">${balance.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
    </div>

    <div class="p-4 border-b border-slate-800 flex items-center justify-between">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Market Watchlist</span>
      <RefreshCw class="w-3.5 h-3.5 text-slate-500 animate-spin" style="animation-duration: 8s" />
    </div>
    
    <div class="flex-1 overflow-y-auto p-2 space-y-1">
      {#each symbols as sym}
        <button 
          onclick={() => selectSymbol(sym)}
          class="w-full text-left p-3 rounded-xl border transition flex items-center justify-between
                 {activeSymbol === sym 
                   ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-md shadow-emerald-900/5' 
                   : 'bg-transparent border-transparent hover:bg-slate-900/50 text-slate-300 hover:text-white'}">
          <div class="flex flex-col">
            <span class="font-bold text-sm">{sym}</span>
            <span class="text-[10px] text-slate-500">Spot</span>
          </div>
          <div class="flex flex-col items-end">
            <span class="font-mono text-sm font-semibold">${prices[sym]}</span>
          </div>
        </button>
      {/each}
    </div>
  </aside>

  <!-- Middle Pane: Charting & Transactions -->
  <main class="flex-1 flex flex-col bg-[#090d16] border-b lg:border-b-0 lg:border-r border-slate-800 relative">
    <div class="h-12 border-b border-slate-850 px-4 flex items-center justify-between shrink-0 bg-[#090d16]/50">
      <span class="font-bold text-slate-100">{activeSymbol}</span>
    </div>

    <div class="flex-1 min-h-[350px]">
      <Chart symbol={activeSymbol} />
    </div>

    <div class="h-48 border-t border-slate-800 bg-[#080c14] flex flex-col shrink-0">
      <div class="h-8 border-b border-slate-850 px-4 flex items-center justify-between bg-[#080c14]/40">
        <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Financial History</span>
        <span class="text-[10px] text-slate-500">{financeTransactions.length} records</span>
      </div>
      <div class="flex-1 overflow-auto">
        {#if financeTransactions.length === 0}
          <div class="h-full flex flex-col items-center justify-center text-slate-600 text-xs">
            <Layers class="w-6 h-6 mb-1 text-slate-700" />
            No financial history found.
          </div>
        {:else}
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-900/50 text-slate-400 border-b border-slate-850">
                <th class="p-2.5">Type</th>
                <th class="p-2.5 text-right">Amount</th>
                <th class="p-2.5">Date</th>
              </tr>
            </thead>
            <tbody>
              {#each financeTransactions as tx}
                <tr class="border-b border-slate-900 hover:bg-slate-900/25">
                  <td class="p-2.5 font-bold text-slate-200">
                    <span class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase border
                               {tx.type === 'ADD_MONEY' ? 'bg-emerald-950/40 text-emerald-450 border-emerald-900/40' : 
                                tx.type === 'TRANSFER_IN' ? 'bg-blue-950/40 text-blue-400 border-blue-900/40' : 
                                'bg-purple-950/40 text-purple-400 border-purple-900/40'}">
                      {tx.type}
                    </span>
                  </td>
                  <td class="p-2.5 text-right font-mono font-bold {tx.type === 'TRANSFER_OUT' ? 'text-red-400' : 'text-emerald-400'}">
                    {tx.type === 'TRANSFER_OUT' ? '-' : '+'}${tx.amount.toLocaleString()}
                  </td>
                  <td class="p-2.5 text-slate-500 font-mono">{new Date(tx.created_at).toLocaleString()}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
    </div>
  </main>

  <!-- Right Pane: Actions & Limits -->
  <aside class="w-full lg:w-72 bg-[#080c14] flex flex-col shrink-0">
    <div class="flex border-b border-slate-800 bg-slate-900/20">
      <button 
        onclick={() => {activeTab = 'trading'; actionError = ''; actionMessage = '';}}
        class="flex-1 py-3 text-[10px] font-bold uppercase tracking-wider transition-all border-b-2 {activeTab === 'trading' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-300'}">
        Trade
      </button>
      <button 
        onclick={() => {activeTab = 'add_money'; actionError = ''; actionMessage = '';}}
        class="flex-1 py-3 text-[10px] font-bold uppercase tracking-wider transition-all border-b-2 {activeTab === 'add_money' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-300'}">
        Add
      </button>
      <button 
        onclick={() => {activeTab = 'transfer'; actionError = ''; actionMessage = '';}}
        class="flex-1 py-3 text-[10px] font-bold uppercase tracking-wider transition-all border-b-2 {activeTab === 'transfer' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-500 hover:text-slate-300'}">
        Transfer
      </button>
    </div>

    <div class="p-4 flex-1 flex flex-col overflow-y-auto">
      {#if actionError}
        <div class="mb-4 p-3 bg-red-950 border border-red-800 rounded-xl text-center text-xs font-medium text-red-400">
          {actionError}
        </div>
      {/if}
      {#if actionMessage}
        <div class="mb-4 p-3 bg-emerald-950 border border-emerald-800 rounded-xl text-center text-xs font-medium text-emerald-400">
          {actionMessage}
        </div>
      {/if}

      {#if activeTab === 'trading'}
        <div class="text-center text-slate-500 text-xs py-8">Trading UI disabled for this demo.</div>
      {:else if activeTab === 'add_money'}
        <form onsubmit={handleAddMoney} class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
              <Plus class="w-3 h-3 text-emerald-400" /> <span>Amount to Add</span>
            </label>
            <input type="number" min="1" step="any" required bind:value={addMoneyAmount} class="w-full bg-slate-950/50 border border-slate-850 focus:border-emerald-500/50 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition font-mono" placeholder="0.00" />
          </div>
          <button type="submit" class="w-full py-3 rounded-xl font-bold text-xs uppercase tracking-wider transition-all bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/5">
            Add Funds
          </button>
        </form>
      {:else if activeTab === 'transfer'}
        <form onsubmit={handleTransfer} class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
              <ArrowRightLeft class="w-3 h-3 text-emerald-400" /> <span>Recipient Account Number</span>
            </label>
            <input type="text" required bind:value={transferRecipient} class="w-full bg-slate-950/50 border border-slate-850 focus:border-emerald-500/50 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition font-mono" placeholder="1234567890" />
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Amount</label>
            <input type="number" min="1" step="any" required bind:value={transferAmount} class="w-full bg-slate-950/50 border border-slate-850 focus:border-emerald-500/50 rounded-xl py-2.5 px-4 text-white text-sm outline-none transition font-mono" placeholder="0.00" />
          </div>
          <button type="submit" class="w-full py-3 rounded-xl font-bold text-xs uppercase tracking-wider transition-all bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/5">
            Transfer Funds
          </button>
        </form>
      {/if}

      <!-- AML Limits Widget -->
      <div class="mt-8 border-t border-slate-800 pt-4">
        <h3 class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
          <span>AML Limits</span>
          <span class="px-1.5 py-0.5 rounded text-[8px] bg-emerald-950/40 text-emerald-400 border border-emerald-900/40">{userTierVal}</span>
        </h3>
        <div class="space-y-2">
          {#each amlLimits as limit}
            <div class="flex justify-between items-center text-xs bg-slate-950/50 p-2 rounded-lg border border-slate-850">
              <div class="flex flex-col">
                <span class="text-slate-300 font-bold capitalize">{limit.action.replace('_', ' ')}</span>
                <span class="text-[9px] text-slate-500 uppercase">Src: {limit.source}</span>
              </div>
              <span class="font-mono text-emerald-400 font-bold">${limit.limit_amount.toLocaleString()}</span>
            </div>
          {/each}
          {#if amlLimits.length === 0}
            <div class="text-xs text-slate-500 text-center py-2">Loading limits...</div>
          {/if}
        </div>
      </div>

    </div>
  </aside>
</div>
