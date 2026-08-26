<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { token, logout, userEmail } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { 
    Users, ShieldAlert, Cpu, HardDrive, Trash2, 
    RefreshCw, LogOut, Check, UserCog, TrendingUp, AlertCircle
  } from '@lucide/svelte';

  interface Role {
    id: number;
    name: string;
  }

  interface UserView {
    id: number;
    email: string;
    role: string;
    tier?: string;
    is_active: boolean;
    created_at: string;
    roles?: Role[];
  }

  interface Stats {
    total_users: number;
    admin_users: number;
    regular_users: number;
    system_status: string;
    memory_usage: string;
  }

  let users = $state<UserView[]>([]);
  let stats = $state<Stats | null>(null);
  let errorMsg = $state("");
  let successMsg = $state("");
  let activeToken = "";
  let emailVal = $state("");
  let loading = $state(false);

  async function loadAdminData() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(val => activeToken = val || "")();
      
      const [fetchedUsers, fetchedStats] = await Promise.all([
        apiRequest('GET', '/api/admin/users', null, activeToken),
        apiRequest('GET', '/api/admin/stats', null, activeToken)
      ]);

      users = fetchedUsers;
      stats = fetchedStats;
    } catch (err: any) {
      errorMsg = err.message || "Failed to load admin controls. Verify backend server is running.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    userEmail.subscribe(val => emailVal = val || "")();
    loadAdminData();
  });

  async function changeRole(user: UserView, newRole: string) {
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('PUT', `/api/admin/users/${user.id}/role`, { role: newRole }, activeToken);
      successMsg = `Role for ${user.email} updated to ${newRole}`;
      loadAdminData();
    } catch (err: any) {
      errorMsg = err.message || "Could not change role";
    }
  }

  async function changeTier(user: UserView, newTier: string) {
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('POST', '/api/admin/requests', {
        request_type: "change_user_tier",
        payload: JSON.stringify({ user_id: user.id, tier: newTier })
      }, activeToken);
      successMsg = `Request submitted: Change ${user.email} tier to ${newTier.toUpperCase()}. Awaiting verification.`;
      loadAdminData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to submit change request.";
    }
  }

  async function handleDelete(user: UserView) {
    if (!confirm(`Are you sure you want to permanently delete user ${user.email}?`)) return;
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('DELETE', `/api/admin/users/${user.id}`, null, activeToken);
      successMsg = `User ${user.email} deleted successfully.`;
      loadAdminData();
    } catch (err: any) {
      errorMsg = err.message || "Could not delete user";
    }
  }

  function handleLogout() {
    logout();
    window.location.href = '/login';
  }
</script>

<!-- Header Nav -->
<header class="h-16 border-b border-slate-800 bg-[#090d16]/80 backdrop-blur px-6 flex items-center justify-between shrink-0">
  <div class="flex items-center space-x-3">
    <div class="p-2 bg-gradient-to-tr from-emerald-600 to-teal-400 rounded-lg shadow-md shadow-emerald-500/10">
      <TrendingUp class="w-5 h-5 text-slate-900" />
    </div>
    <span class="font-bold tracking-wider text-white">TIBARPAY</span>
    <span class="text-xs px-2 py-0.5 bg-red-950 text-red-400 border border-red-800 rounded-full font-medium">Admin Terminal</span>
  </div>

  <div class="flex items-center space-x-4">
    <div class="hidden sm:flex flex-col items-end">
      <span class="text-xs text-slate-400">Admin Session</span>
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

<div class="flex-1 flex flex-col p-6 space-y-6 overflow-y-auto max-w-7xl w-full mx-auto">
  <!-- Page Header -->
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0">
    <div>
      <h1 class="text-2xl font-bold text-white tracking-tight">Administrative Control</h1>
      <p class="text-xs text-slate-400 mt-1">Manage global system metrics, roles, and databases.</p>
    </div>
    <button 
      onclick={loadAdminData}
      disabled={loading}
      class="flex items-center space-x-2 px-3 py-1.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-medium rounded-lg transition disabled:opacity-50">
      <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
      <span>Refresh Data</span>
    </button>
  </div>

  <!-- Messages -->
  {#if errorMsg}
    <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-4 rounded-xl text-sm">
      <AlertCircle class="w-5 h-5 shrink-0 text-red-400" />
      <span>{errorMsg}</span>
    </div>
  {/if}

  {#if successMsg}
    <div class="flex items-start space-x-2 bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 p-4 rounded-xl text-sm">
      <Check class="w-5 h-5 shrink-0 text-emerald-400" />
      <span>{successMsg}</span>
    </div>
  {/if}

  <!-- Stats Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Stat 1 -->
    <div class="bg-slate-900/40 border border-slate-800/60 p-5 rounded-2xl flex items-center space-x-4 shadow-xl">
      <div class="p-3 bg-blue-500/10 rounded-xl text-blue-400">
        <Users class="w-6 h-6" />
      </div>
      <div>
        <span class="text-xs text-slate-500 block uppercase tracking-wider font-semibold">Total Accounts</span>
        <span class="text-2xl font-bold text-white font-mono">{stats?.total_users ?? '--'}</span>
      </div>
    </div>

    <!-- Stat 2 -->
    <div class="bg-slate-900/40 border border-slate-800/60 p-5 rounded-2xl flex items-center space-x-4 shadow-xl">
      <div class="p-3 bg-red-500/10 rounded-xl text-red-400">
        <ShieldAlert class="w-6 h-6" />
      </div>
      <div>
        <span class="text-xs text-slate-500 block uppercase tracking-wider font-semibold">Admin Access</span>
        <span class="text-2xl font-bold text-white font-mono">{stats?.admin_users ?? '--'}</span>
      </div>
    </div>

    <!-- Stat 3 -->
    <div class="bg-slate-900/40 border border-slate-800/60 p-5 rounded-2xl flex items-center space-x-4 shadow-xl">
      <div class="p-3 bg-emerald-500/10 rounded-xl text-emerald-400">
        <Cpu class="w-6 h-6" />
      </div>
      <div>
        <span class="text-xs text-slate-500 block uppercase tracking-wider font-semibold">Server State</span>
        <span class="text-2xl font-bold text-emerald-400">{stats?.system_status ?? 'Connecting...'}</span>
      </div>
    </div>

    <!-- Stat 4 -->
    <div class="bg-slate-900/40 border border-slate-800/60 p-5 rounded-2xl flex items-center space-x-4 shadow-xl">
      <div class="p-3 bg-orange-500/10 rounded-xl text-orange-400">
        <HardDrive class="w-6 h-6" />
      </div>
      <div>
        <span class="text-xs text-slate-500 block uppercase tracking-wider font-semibold">RAM Usage</span>
        <span class="text-sm font-semibold text-slate-300 block mt-1">{stats?.memory_usage ?? '--'}</span>
      </div>
    </div>
  </div>

  <!-- Users Table Card -->
  <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl overflow-hidden flex flex-col">
    <div class="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-950/20">
      <div class="flex items-center space-x-2">
        <UserCog class="w-4.5 h-4.5 text-slate-400" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">User Directory & Permissions</h2>
      </div>
      <span class="text-xs text-slate-400 font-mono">{users.length} profiles loaded</span>
    </div>

    <div class="overflow-x-auto">
      {#if users.length === 0}
        <div class="p-8 text-center text-slate-500 text-sm">
          No users registered in directory.
        </div>
      {:else}
        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="bg-slate-950/30 text-slate-400 font-semibold border-b border-slate-800 text-xs">
              <th class="p-4">User ID</th>
              <th class="p-4">Email</th>
              <th class="p-4">Created Date</th>
              <th class="p-4">Active Role</th>
              <th class="p-4">Subscription Tier</th>
              <th class="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each users as user}
              <tr class="border-b border-slate-850 hover:bg-slate-900/10 transition">
                <td class="p-4 font-mono text-slate-400 text-xs">#{user.id}</td>
                <td class="p-4 font-medium text-slate-200">{user.email}</td>
                <td class="p-4 text-slate-400 text-xs">
                  {new Date(user.created_at).toLocaleDateString()} {new Date(user.created_at).toLocaleTimeString()}
                </td>
                <td class="p-4">
                  <div class="flex flex-wrap gap-1">
                    {#if user.roles && user.roles.length > 0}
                      {#each user.roles as role}
                        <span class="px-1.5 py-0.5 rounded text-[10px] font-bold border 
                                     {role.name === 'Super Admin' 
                                       ? 'bg-purple-950/40 text-purple-400 border-purple-900/30' 
                                       : role.name === 'Maker Admin'
                                         ? 'bg-amber-950/40 text-amber-400 border-amber-900/30'
                                         : role.name === 'Checker Admin'
                                           ? 'bg-blue-950/40 text-blue-400 border-blue-900/30'
                                           : 'bg-emerald-950/40 text-emerald-400 border-emerald-900/40'}">
                          {role.name}
                        </span>
                      {/each}
                    {:else}
                      <span class="px-2 py-0.5 rounded text-xs font-bold border 
                                   {user.role === 'admin' 
                                     ? 'bg-red-950/40 text-red-400 border-red-900/40' 
                                     : 'bg-emerald-950/40 text-emerald-400 border-emerald-900/40'}">
                        {user.role}
                      </span>
                    {/if}
                  </div>
                </td>
                <td class="p-4">
                  {#if user.role === 'admin'}
                    <span class="text-xs text-slate-500 font-semibold">—</span>
                  {:else}
                    <span class="px-2 py-0.5 rounded text-xs font-bold border
                                 {user.tier === 'premium' 
                                   ? 'bg-purple-950/40 text-purple-400 border-purple-900/40' 
                                   : user.tier === 'standard'
                                     ? 'bg-blue-950/40 text-blue-400 border-blue-900/40'
                                     : 'bg-slate-900 text-slate-400 border-slate-800'}">
                      {user.tier}
                    </span>
                  {/if}
                </td>
                <td class="p-4 text-right">
                  <div class="inline-flex items-center space-x-2">
                    {#if user.role !== 'admin'}
                      <select 
                        value={user.tier}
                        onchange={(e) => changeTier(user, (e.target as HTMLSelectElement).value)}
                        class="bg-slate-950 text-slate-300 text-xs rounded-lg border border-slate-800 focus:border-slate-700 px-2 py-1 outline-none transition cursor-pointer"
                      >
                        <option value="starter">Starter</option>
                        <option value="standard">Standard</option>
                        <option value="premium">Premium</option>
                      </select>
                    {/if}
                    <!-- Delete account -->
                    <button 
                      onclick={() => handleDelete(user)}
                      disabled={user.email === emailVal}
                      class="p-1 bg-red-950/20 hover:bg-red-950/80 border border-red-900/30 text-red-400 hover:text-white rounded-lg transition disabled:opacity-40 disabled:cursor-not-allowed"
                      title="Delete User">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  </div>
</div>
