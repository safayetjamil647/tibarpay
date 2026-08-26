<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { apiRequest } from '$lib/api';
  import { Mail, Lock, UserPlus, TrendingUp, AlertTriangle, CheckCircle2 } from '@lucide/svelte';

  let email = $state("");
  let password = $state("");
  let confirmPassword = $state("");
  let selectedTier = $state("starter");
  let errorMsg = $state("");
  let successMsg = $state("");
  let loading = $state(false);

  let tiers = $state<{id: number, name: string, price: number}[]>([]);

  onMount(async () => {
    try {
      tiers = await apiRequest('GET', '/api/tiers');
      if (tiers.length > 0) {
        selectedTier = tiers[0].name.toLowerCase();
      }
    } catch (err) {
      tiers = [
        {id: 1, name: "Starter", price: 0.0},
        {id: 2, name: "Standard", price: 19.0},
        {id: 3, name: "Premium", price: 49.0}
      ];
    }
  });

  async function handleRegister(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = "";
    successMsg = "";
    
    if (password !== confirmPassword) {
      errorMsg = "Passwords do not match.";
      return;
    }

    if (password.length < 6) {
      errorMsg = "Password must be at least 6 characters long.";
      return;
    }

    loading = true;
    try {
      await apiRequest('POST', '/api/auth/register', { email, password, tier: selectedTier });
      successMsg = "Account created successfully! Redirecting to login...";
      setTimeout(() => {
        goto('/login');
      }, 1500);
    } catch (err: any) {
      errorMsg = err.message || "Email is already registered or invalid.";
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex-1 flex flex-col items-center justify-center relative px-4 overflow-hidden bg-[#070b13]">
  <!-- Gradient background effects -->
  <div class="absolute w-[500px] h-[500px] rounded-full bg-emerald-500/10 blur-[120px] top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
  <div class="absolute w-[400px] h-[400px] rounded-full bg-blue-500/10 blur-[100px] bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

  <div class="w-full max-w-md z-10">
    <!-- Brand Header -->
    <div class="flex items-center justify-center space-x-3 mb-8">
      <div class="p-2.5 bg-gradient-to-tr from-emerald-600 to-teal-400 rounded-xl shadow-lg shadow-emerald-500/20">
        <TrendingUp class="w-7 h-7 text-slate-900" />
      </div>
      <span class="text-2xl font-bold tracking-wider bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
        TIBARPAY
      </span>
    </div>

    <!-- Registration Box -->
    <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl">
      <h2 class="text-xl font-bold text-white mb-1">Create Account</h2>
      <p class="text-sm text-slate-400 mb-6">Register a regular trading account.</p>

      {#if errorMsg}
        <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-3 rounded-lg text-sm mb-5">
          <AlertTriangle class="w-5 h-5 shrink-0 text-red-400" />
          <span>{errorMsg}</span>
        </div>
      {/if}

      {#if successMsg}
        <div class="flex items-start space-x-2 bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 p-3 rounded-lg text-sm mb-5">
          <CheckCircle2 class="w-5 h-5 shrink-0 text-emerald-400" />
          <span>{successMsg}</span>
        </div>
      {/if}

      <form onsubmit={handleRegister} class="space-y-5">
        <div>
          <label for="email" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Email Address</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
              <Mail class="w-4 h-4" />
            </div>
            <input 
              id="email" 
              type="email" 
              required 
              placeholder="name@domain.com" 
              bind:value={email}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm outline-none transition placeholder-slate-600"
            />
          </div>
        </div>

        <div>
          <label for="password" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Password</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
              <Lock class="w-4 h-4" />
            </div>
            <input 
              id="password" 
              type="password" 
              required 
              placeholder="Min 6 characters" 
              bind:value={password}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm outline-none transition placeholder-slate-600"
            />
          </div>
        </div>

        <div>
          <label for="confirm-password" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Confirm Password</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
              <Lock class="w-4 h-4" />
            </div>
            <input 
              id="confirm-password" 
              type="password" 
              required 
              placeholder="Confirm password" 
              bind:value={confirmPassword}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm outline-none transition placeholder-slate-600"
            />
          </div>
        </div>

        <!-- Subscription Tier -->
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Select Subscription Tier</label>
          <div class="grid grid-cols-3 gap-2">
            {#each tiers as t}
              <button 
                type="button" 
                onclick={() => selectedTier = t.name.toLowerCase()}
                class="flex flex-col items-center justify-center p-2.5 rounded-xl border text-center transition outline-none
                       {selectedTier === t.name.toLowerCase() 
                         ? 'bg-emerald-950/20 border-emerald-800 text-emerald-450 shadow shadow-emerald-500/10' 
                         : 'bg-slate-950/40 border-slate-850 text-slate-400 hover:text-slate-200'}">
                <span class="text-xs font-bold">{t.name}</span>
                <span class="text-[9px] text-slate-500 mt-1">${t.price}/mo</span>
              </button>
            {/each}
          </div>
        </div>

        <button 
          type="submit" 
          disabled={loading || !!successMsg}
          class="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 disabled:from-slate-700 disabled:to-slate-700 text-slate-950 text-sm font-semibold rounded-xl transition duration-200 transform active:scale-[0.98] shadow-lg shadow-emerald-500/10 disabled:scale-100 disabled:cursor-not-allowed">
          {#if loading}
            <span class="inline-block animate-pulse">Creating Account...</span>
          {:else}
            Sign Up
          {/if}
        </button>
      </form>

      <div class="mt-6 text-center">
        <span class="text-xs text-slate-500">Already have an account? </span>
        <a href="/login" class="text-xs text-emerald-400 hover:text-emerald-300 font-medium transition">
          Sign In
        </a>
      </div>
    </div>
  </div>
</div>
