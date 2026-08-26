<script lang="ts">
  import { onMount } from 'svelte';
  import { token, userEmail } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { 
    ShieldCheck, Check, Loader, Lock, Users, UserCog, AlertTriangle, Key, ShieldAlert 
  } from '@lucide/svelte';

  interface Permission {
    id: number;
    name: string;
    description?: string;
  }

  interface Role {
    id: number;
    name: string;
    description?: string;
    permissions: Permission[];
  }

  interface UserView {
    id: number;
    email: string;
    role: string;
    is_active: boolean;
    created_at: string;
    roles: Role[];
  }

  let roles = $state<Role[]>([]);
  let permissions = $state<Permission[]>([]);
  let users = $state<UserView[]>([]);
  
  let activeToken = "";
  let currentEmail = $state("");
  let errorMsg = $state("");
  let successMsg = $state("");
  let loading = $state(false);
  let actionLoading = $state<string | null>(null); // tracks role/permission update actions
  let activeTab = $state<'matrix' | 'users'>('matrix');

  async function loadData() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(v => activeToken = v || "")();
      userEmail.subscribe(v => currentEmail = v || "")();
      
      const [fetchedRoles, fetchedPermissions, fetchedUsers] = await Promise.all([
        apiRequest('GET', '/api/admin/roles', null, activeToken),
        apiRequest('GET', '/api/admin/permissions', null, activeToken),
        apiRequest('GET', '/api/admin/users', null, activeToken)
      ]);
      
      roles = fetchedRoles;
      permissions = fetchedPermissions;
      users = fetchedUsers;
    } catch (err: any) {
      errorMsg = err.message || "Failed to load roles, permissions, or user accounts.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  async function togglePermission(role: Role, perm: Permission, event: Event) {
    const isChecked = (event.target as HTMLInputElement).checked;
    errorMsg = "";
    successMsg = "";
    const key = `role-${role.id}-perm-${perm.id}`;
    actionLoading = key;

    let activePermIds = role.permissions.map(p => p.id);
    if (isChecked) {
      if (!activePermIds.includes(perm.id)) {
        activePermIds.push(perm.id);
      }
    } else {
      activePermIds = activePermIds.filter(id => id !== perm.id);
    }

    try {
      await apiRequest('PUT', `/api/admin/roles/${role.id}/permissions`, {
        permission_ids: activePermIds
      }, activeToken);
      
      successMsg = `Successfully updated permissions for role "${role.name}"`;
      await loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to update role permissions.";
      // Revert checked state
      (event.target as HTMLInputElement).checked = !isChecked;
    } finally {
      actionLoading = null;
    }
  }

  async function toggleUserRole(user: UserView, roleId: number, event: Event) {
    const isChecked = (event.target as HTMLInputElement).checked;
    errorMsg = "";
    successMsg = "";
    const key = `user-${user.id}-role-${roleId}`;
    actionLoading = key;

    let activeRoleIds = user.roles.map(r => r.id);
    if (isChecked) {
      if (!activeRoleIds.includes(roleId)) {
        activeRoleIds.push(roleId);
      }
    } else {
      activeRoleIds = activeRoleIds.filter(id => id !== roleId);
    }

    try {
      await apiRequest('PUT', `/api/admin/users/${user.id}/roles`, {
        role_ids: activeRoleIds
      }, activeToken);

      successMsg = `Successfully updated roles for user ${user.email}`;
      await loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to update user roles.";
      // Revert checked state
      (event.target as HTMLInputElement).checked = !isChecked;
    } finally {
      actionLoading = null;
    }
  }
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
      <ShieldCheck class="w-6 h-6 text-purple-400" />
      <span class="bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
        RBAC Configuration Console
      </span>
    </h1>
    <p class="text-xs text-slate-400 mt-1">
      Manage enterprise security credentials, configure custom roles and permission maps, and assign user capabilities.
    </p>
  </div>

  <!-- Messages -->
  {#if errorMsg}
    <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-4 rounded-xl text-xs">
      <ShieldAlert class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
      <span>{errorMsg}</span>
    </div>
  {/if}

  {#if successMsg}
    <div class="flex items-start space-x-2 bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 p-4 rounded-xl text-xs">
      <Check class="w-4 h-4 text-emerald-400 shrink-0" />
      <span>{successMsg}</span>
    </div>
  {/if}

  {#if loading}
    <div class="flex flex-col items-center justify-center py-20 space-y-4">
      <Loader class="w-8 h-8 text-purple-400 animate-spin" />
      <p class="text-slate-450 text-xs">Retrieving security credentials...</p>
    </div>
  {:else}
    <!-- Tabs -->
    <div class="flex space-x-1 bg-slate-900/60 p-1 rounded-xl w-fit border border-slate-800/80 backdrop-blur">
      <button 
        onclick={() => activeTab = 'matrix'}
        class="px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 {activeTab === 'matrix' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}"
      >
        <Key class="w-4 h-4" />
        <span>Permission Matrix</span>
      </button>
      <button 
        onclick={() => activeTab = 'users'}
        class="px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 {activeTab === 'users' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}"
      >
        <UserCog class="w-4 h-4" />
        <span>User Assignments</span>
      </button>
    </div>

    <div class="mt-4">
      
      <!-- Tab 1: Roles vs Permissions Checklist Matrix -->
      {#if activeTab === 'matrix'}
      <div class="space-y-6 animate-in fade-in duration-300">
        <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl p-6">
          <div class="flex items-center space-x-2 mb-4">
            <Key class="w-4.5 h-4.5 text-purple-400" />
            <h2 class="text-sm font-bold text-white uppercase tracking-wider">
              Role Permissions Mapping Matrix
            </h2>
          </div>
          
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="bg-slate-950/30 text-slate-450 font-semibold border-b border-slate-800">
                  <th class="p-3">System Permission</th>
                  {#each roles as r}
                    <th class="p-3 text-center min-w-[100px]">
                      <span class="block text-slate-200 font-bold">{r.name}</span>
                      <span class="block text-[8px] text-slate-500 font-normal mt-0.5 max-w-[120px] mx-auto truncate" title={r.description}>
                        {r.description}
                      </span>
                    </th>
                  {/each}
                </tr>
              </thead>
              <tbody>
                {#each permissions as p}
                  <tr class="border-b border-slate-850 hover:bg-slate-900/10 transition">
                    <td class="p-3">
                      <span class="block font-mono text-slate-200 font-semibold text-[11px]">{p.name}</span>
                      <span class="block text-[10px] text-slate-450 mt-0.5">{p.description}</span>
                    </td>
                    {#each roles as r}
                      <td class="p-3 text-center">
                        <div class="inline-flex items-center justify-center relative">
                          <input 
                            type="checkbox" 
                            checked={r.permissions.some(rp => rp.id === p.id)}
                            onchange={(e) => togglePermission(r, p, e)}
                            disabled={actionLoading !== null}
                            class="w-4.5 h-4.5 accent-purple-500 rounded border-slate-800 bg-slate-950 cursor-pointer disabled:opacity-40"
                          />
                        </div>
                      </td>
                    {/each}
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      {/if}

      <!-- Tab 2: User Role Assignment -->
      {#if activeTab === 'users'}
      <div class="space-y-6 animate-in fade-in duration-300">
        <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl p-6 shadow-2xl flex flex-col">
          <div class="flex items-center justify-between mb-4 border-b border-slate-800/60 pb-3">
            <div class="flex items-center space-x-2">
              <UserCog class="w-4.5 h-4.5 text-purple-400" />
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">
                User Role Assignments
              </h3>
            </div>
            <button onclick={loadData} class="text-[10px] text-purple-400 hover:underline">
              Refresh Accounts
            </button>
          </div>

          <div class="space-y-4 max-h-[600px] overflow-y-auto pr-1">
            {#each users as u}
              <div class="bg-slate-950/40 border border-slate-850 rounded-xl p-4 space-y-3 relative transition hover:border-slate-800">
                <div class="flex items-start justify-between">
                  <div class="min-w-0">
                    <p class="text-xs font-semibold text-slate-250 truncate">{u.email}</p>
                    <span class="text-[9px] text-slate-500 font-semibold uppercase tracking-wider block mt-0.5">
                      User ID: #{u.id}
                    </span>
                  </div>
                  
                  {#if u.email === currentEmail}
                    <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider bg-purple-950/20 text-purple-400 border border-purple-900/30">
                      You
                    </span>
                  {/if}
                </div>

                <!-- Active Roles badging -->
                <div class="flex flex-wrap gap-1">
                  {#if u.roles.length === 0}
                    <span class="text-[9px] text-slate-600 font-semibold">No Roles Assigned</span>
                  {:else}
                    {#each u.roles as role}
                      <span class="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase tracking-wider border 
                                   {role.name === 'Super Admin' 
                                     ? 'bg-purple-950/40 text-purple-400 border-purple-900/30' 
                                     : role.name === 'Maker Admin'
                                       ? 'bg-amber-950/40 text-amber-400 border-amber-900/30'
                                       : role.name === 'Checker Admin'
                                         ? 'bg-blue-950/40 text-blue-400 border-blue-900/30'
                                         : 'bg-slate-900 text-slate-400 border-slate-800'}">
                        {role.name}
                      </span>
                    {/each}
                  {/if}
                </div>

                <!-- Roles checklist selector -->
                <div class="border-t border-slate-850/60 pt-2.5 space-y-2">
                  <span class="block text-[9px] font-bold uppercase tracking-wider text-slate-500">Edit Roles:</span>
                  <div class="grid grid-cols-2 gap-2">
                    {#each roles as r}
                      <label class="flex items-center space-x-2 text-[10px] text-slate-350 select-none cursor-pointer hover:text-slate-200">
                        <input 
                          type="checkbox" 
                          checked={u.roles.some(ur => ur.id === r.id)}
                          onchange={(e) => toggleUserRole(u, r.id, e)}
                          disabled={u.email === currentEmail || actionLoading !== null}
                          class="w-3.5 h-3.5 accent-purple-500 rounded border-slate-800 bg-slate-950 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                        />
                        <span class="truncate" title={r.description}>{r.name}</span>
                      </label>
                    {/each}
                  </div>
                  {#if u.email === currentEmail}
                    <span class="block text-[8px] text-amber-400 mt-1 font-semibold">
                      Self role edits disabled to prevent lockout.
                    </span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>
      {/if}
      
    </div>
  {/if}
</div>
