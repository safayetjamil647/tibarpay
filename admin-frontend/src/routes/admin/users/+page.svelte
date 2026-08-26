<script lang="ts">
  import { onMount } from 'svelte';
  import { token, userEmail } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { Users, UserCog, Trash2, Check, AlertCircle } from '@lucide/svelte';

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

  let users = $state<UserView[]>([]);
  let errorMsg = $state("");
  let successMsg = $state("");
  let activeToken = "";
  let emailVal = $state("");
  let loading = $state(false);

  async function loadUsers() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(v => activeToken = v || "")();
      users = await apiRequest('GET', '/api/admin/users', null, activeToken);
    } catch (err: any) {
      errorMsg = err.message || "Failed to load directory";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    userEmail.subscribe(v => emailVal = v || "")();
    loadUsers();
  });

  async function changeRole(user: UserView, newRole: string) {
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('PUT', `/api/admin/users/${user.id}/role`, { role: newRole }, activeToken);
      successMsg = `Updated ${user.email} role to ${newRole}`;
      loadUsers();
    } catch (err: any) {
      errorMsg = err.message || "Failed to update role";
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
      loadUsers();
    } catch (err: any) {
      errorMsg = err.message || "Failed to submit change request.";
    }
  }

  async function handleDelete(user: UserView) {
    if (!confirm(`Delete user ${user.email}?`)) return;
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('DELETE', `/api/admin/users/${user.id}`, null, activeToken);
      successMsg = `Deleted ${user.email} successfully`;
      loadUsers();
    } catch (err: any) {
      errorMsg = err.message || "Failed to delete user";
    }
  }
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <div>
    <h1 class="text-2xl font-bold text-white tracking-tight">Directory Management</h1>
    <p class="text-xs text-slate-400 mt-1">Audit active registration accounts and change permission roles.</p>
  </div>

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

  <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl overflow-hidden flex flex-col">
    <div class="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-950/20">
      <div class="flex items-center space-x-2">
        <Users class="w-4.5 h-4.5 text-slate-450" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Registered Accounts</h2>
      </div>
      <button onclick={loadUsers} class="text-xs text-emerald-400 hover:underline">
        Refresh Table
      </button>
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
                <td class="p-4 text-slate-455 text-xs">
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
                                   ? 'bg-purple-950/40 text-purple-405 border-purple-900/40' 
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
                    <button 
                      onclick={() => handleDelete(user)}
                      disabled={user.email === emailVal}
                      class="p-1 bg-red-950/20 hover:bg-red-950/80 border border-red-900/30 text-red-400 hover:text-white rounded-lg transition disabled:opacity-40 disabled:cursor-not-allowed">
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
