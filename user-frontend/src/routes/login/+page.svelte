<script lang="ts">
  import { goto } from '$app/navigation';
  import { apiRequest } from '$lib/api';
  import { token, userRole, userEmail, userTier } from '$lib/store';
  import { Mail, Lock, TrendingUp, AlertTriangle } from '@lucide/svelte';

  let email = $state("");
  let password = $state("");
  let errorMsg = $state("");
  let loading = $state(false);

  async function handleLogin(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = "";
    loading = true;
    try {
      const res = await apiRequest('POST', '/api/auth/login', { email, password });
      token.set(res.access_token);
      userRole.set(res.role);
      userEmail.set(email);
      userTier.set(res.tier || null);
      
      const isAdmin = res.role ? res.role.toLowerCase().includes('admin') : false;
      if (isAdmin) {
        window.location.href = '/admin';
      } else {
        goto('/dashboard');
      }
    } catch (err: any) {
      errorMsg = err.message || "Invalid credentials. Please try again.";
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

    <!-- Login Box -->
    <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl">
      <h2 class="text-xl font-bold text-white mb-1">Sign In</h2>
      <p class="text-sm text-slate-400 mb-6">Enter details to access your trading workspace.</p>

      {#if errorMsg}
        <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-3 rounded-lg text-sm mb-5">
          <AlertTriangle class="w-5 h-5 shrink-0 text-red-400" />
          <span>{errorMsg}</span>
        </div>
      {/if}

      <form onsubmit={handleLogin} class="space-y-5">
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
              placeholder="••••••••" 
              bind:value={password}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm outline-none transition placeholder-slate-600"
            />
          </div>
        </div>

        <button 
          type="submit" 
          disabled={loading}
          class="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 disabled:from-slate-700 disabled:to-slate-700 text-slate-950 text-sm font-semibold rounded-xl transition duration-200 transform active:scale-[0.98] shadow-lg shadow-emerald-500/10 disabled:scale-100 disabled:cursor-not-allowed">
          {#if loading}
            <span class="inline-block animate-pulse">Authenticating...</span>
          {:else}
            Sign In
          {/if}
        </button>
      </form>

      <div class="mt-6 text-center">
        <span class="text-xs text-slate-500">Don't have an account? </span>
        <a href="/register" class="text-xs text-emerald-400 hover:text-emerald-300 font-medium transition">
          Create User Account
        </a>
      </div>
    </div>
  </div>
</div>
