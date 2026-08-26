<script lang="ts">
  import { onMount } from 'svelte';
  import { userTier, token } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { ShieldCheck, Gem, CreditCard, Sparkles, Check, ArrowRight, Loader } from '@lucide/svelte';

  let currentTier = $state("starter");
  let activeToken = "";
  let successMsg = $state("");
  let errorMsg = $state("");
  let loadingPlan = $state<string | null>(null);
  let tiers = $state<{id: number, name: string, price: number, description: string, features: {id: number, name: string}[]}[]>([]);

  onMount(async () => {
    userTier.subscribe(v => currentTier = v || "starter")();
    token.subscribe(v => activeToken = v || "")();
    
    try {
      tiers = await apiRequest('GET', '/api/tiers');
    } catch (err) {
      tiers = [
        {
          id: 1, 
          name: "Starter", 
          price: 0.0, 
          description: "Standard basic free tier. Perfect for testing indicators and general market tracking.", 
          features: [{id: 1, name: "5 Asset Watchlist Spot Market"}, {id: 2, name: "Interactive TradingView Charts"}]
        },
        {
          id: 2, 
          name: "Standard", 
          price: 19.0, 
          description: "Advanced analytics tools and unlimited alerts. Tailored for active day traders.", 
          features: [{id: 1, name: "All Spot Market indicators"}, {id: 2, name: "Priority WebSocket updates"}]
        },
        {
          id: 3, 
          name: "Premium", 
          price: 49.0, 
          description: "Elite trading tools, historical data access, custom scripts, and dedicated support.", 
          features: [{id: 1, name: "Dedicated WebSocket stream"}, {id: 2, name: "Unlimited custom scripts"}]
        }
      ];
    }
  });

  async function handleUpgrade(targetTier: string) {
    if (targetTier === currentTier) return;
    
    loadingPlan = targetTier;
    errorMsg = "";
    successMsg = "";

    try {
      const res = await apiRequest('PUT', '/api/users/me/tier', { tier: targetTier }, activeToken);
      userTier.set(res.tier);
      currentTier = res.tier;
      successMsg = `Subscription upgrade to ${targetTier.toUpperCase()} completed successfully!`;
      
      setTimeout(() => {
        successMsg = "";
      }, 5000);
    } catch (err: any) {
      errorMsg = err.message || "Failed to update subscription. Please try again.";
    } finally {
      loadingPlan = null;
    }
  }
</script>

<div class="p-6 space-y-8 max-w-5xl w-full mx-auto overflow-y-auto animate-fade-in">
  <!-- Page Header -->
  <div class="text-center sm:text-left">
    <h1 class="text-2xl font-bold text-white tracking-tight flex items-center justify-center sm:justify-start space-x-2">
      <CreditCard class="w-6 h-6 text-emerald-400" />
      <span>Account Subscriptions</span>
    </h1>
    <p class="text-xs text-slate-400 mt-1">
      Select a plan tier below. Later, access to KYC systems and AML guidelines will be tailored to your registered tier.
    </p>
  </div>

  <!-- Messages -->
  {#if successMsg}
    <div class="flex items-start space-x-2 bg-emerald-950/40 border border-emerald-800/50 text-emerald-350 p-4 rounded-xl text-xs max-w-2xl">
      <ShieldCheck class="w-5 h-5 shrink-0 text-emerald-400" />
      <span class="font-medium">{successMsg}</span>
    </div>
  {/if}

  {#if errorMsg}
    <div class="flex items-start space-x-2 bg-red-950/45 border border-red-850/50 text-red-300 p-4 rounded-xl text-xs max-w-2xl">
      <span class="font-medium">{errorMsg}</span>
    </div>
  {/if}

  <!-- Plans Grid -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
    {#each tiers as t}
      <!-- Dynamic Tier Card -->
      <div class="relative flex flex-col justify-between p-6 rounded-2xl bg-[#090d16]/50 border transition-all duration-300 hover:translate-y-[-4px]
                  {currentTier === t.name.toLowerCase() 
                    ? 'border-emerald-500 shadow-lg shadow-emerald-950/15' 
                    : 'border-slate-800/80 hover:border-slate-700'}"
      >
        {#if currentTier === t.name.toLowerCase()}
          <span class="absolute top-3 right-3 text-[9px] px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-900/40 font-bold uppercase tracking-wider">Active</span>
        {/if}
        <div>
          <div class="text-xs font-bold text-slate-300 uppercase tracking-widest">{t.name}</div>
          <div class="mt-4 flex items-baseline text-white">
            <span class="text-3xl font-extrabold tracking-tight">${t.price}</span>
            <span class="ml-1 text-slate-450 text-xs">/month</span>
          </div>
          <p class="mt-3 text-xs text-slate-400 leading-relaxed">
            {t.description || 'Access standard features and tools.'}
          </p>

          <ul class="mt-6 space-y-3">
            {#each t.features as feat}
              <li class="flex items-center space-x-2 text-xs text-slate-300">
                <Check class="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>{feat.name}</span>
              </li>
            {/each}
          </ul>
        </div>

        <div class="mt-8">
          <button 
            onclick={() => handleUpgrade(t.name.toLowerCase())}
            disabled={currentTier === t.name.toLowerCase() || loadingPlan !== null}
            class="w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-200 border flex items-center justify-center space-x-1.5
                   {currentTier === t.name.toLowerCase() 
                     ? 'bg-slate-900/40 text-slate-500 border-slate-800/80 cursor-default' 
                     : 'bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-slate-950 border-transparent shadow-lg shadow-emerald-500/10'}"
          >
            {#if loadingPlan === t.name.toLowerCase()}
              <Loader class="w-3.5 h-3.5 animate-spin" />
              <span>Upgrading...</span>
            {:else}
              <span>{currentTier === t.name.toLowerCase() ? 'Selected' : `Upgrade to ${t.name}`}</span>
            {/if}
          </button>
        </div>
      </div>
    {/each}
  </div>
</div>
