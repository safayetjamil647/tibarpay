<script lang="ts">
  import { onMount } from 'svelte';
  import { token, userEmail } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { Check, X, ShieldAlert, Clock, RefreshCw, AlertCircle, UserCheck } from '@lucide/svelte';

  interface ApprovalRequest {
    id: number;
    request_type: string;
    payload: string;
    status: string;
    maker_id: number;
    checker_id?: number;
    created_at: string;
    actioned_at?: string;
    rejection_reason?: string;
    maker_email?: string;
    checker_email?: string;
  }

  let requests = $state<ApprovalRequest[]>([]);
  let currentUserId = $state<number | null>(null);
  let activeToken = "";
  let emailVal = "";
  let errorMsg = $state("");
  let successMsg = $state("");
  let loading = $state(false);
  let rejectionReasons = $state<Record<number, string>>({});
  
  // Tab control
  let activeTab = $state("pending"); // "pending" or "history"

  async function loadRequests() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(v => activeToken = v || "")();
      
      // Fetch user self profile to know our own User ID
      const me = await apiRequest('GET', '/api/auth/me', null, activeToken);
      currentUserId = me.id;

      requests = await apiRequest('GET', '/api/admin/requests', null, activeToken);
    } catch (err: any) {
      errorMsg = err.message || "Failed to load approval requests.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    userEmail.subscribe(v => emailVal = v || "")();
    loadRequests();
  });

  async function handleApprove(reqId: number) {
    errorMsg = "";
    successMsg = "";
    try {
      await apiRequest('POST', `/api/admin/requests/${reqId}/approve`, null, activeToken);
      successMsg = "Request approved successfully!";
      loadRequests();
    } catch (err: any) {
      errorMsg = err.message || "Failed to approve request.";
    }
  }

  async function handleReject(reqId: number) {
    errorMsg = "";
    successMsg = "";
    const reason = rejectionReasons[reqId] || "";
    if (!reason.trim()) {
      errorMsg = "Please provide a rejection reason.";
      return;
    }

    try {
      await apiRequest('POST', `/api/admin/requests/${reqId}/reject`, {
        rejection_reason: reason
      }, activeToken);
      successMsg = "Request rejected successfully!";
      rejectionReasons[reqId] = ""; // Reset
      loadRequests();
    } catch (err: any) {
      errorMsg = err.message || "Failed to reject request.";
    }
  }

  function parsePayload(payloadStr: string): string {
    try {
      const obj = JSON.parse(payloadStr);
      let details = [];
      for (const [key, val] of Object.entries(obj)) {
        details.push(`${key}: ${JSON.stringify(val)}`);
      }
      return details.join(", ");
    } catch (err) {
      return payloadStr;
    }
  }

  function getReadableType(type: string): string {
    switch(type) {
      case "change_user_tier": return "Upgrade User Subscription Tier";
      case "update_tier_features": return "Update Plan Feature Matrix";
      case "create_tier": return "Create New Subscription Plan";
      default: return type;
    }
  }

  // Filter requests
  let pendingRequests = $derived(requests.filter(r => r.status === "pending"));
  let historicRequests = $derived(requests.filter(r => r.status !== "pending"));
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-3 sm:space-y-0">
    <div>
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
        <UserCheck class="w-6 h-6 text-emerald-400" />
        <span>Maker-Checker Audit Center</span>
      </h1>
      <p class="text-xs text-slate-400 mt-1">
        Review admin change requests. Makers cannot approve or action their own requests.
      </p>
    </div>
    <button 
      onclick={loadRequests}
      disabled={loading}
      class="flex items-center space-x-2 px-3 py-1.5 bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-slate-350 text-xs font-semibold rounded-xl transition disabled:opacity-50"
    >
      <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
      <span>Sync Center</span>
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

  <!-- Tab Buttons -->
  <div class="flex border-b border-slate-800 space-x-4">
    <button 
      onclick={() => activeTab = "pending"}
      class="pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 outline-none
             {activeTab === 'pending' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}"
    >
      Pending Approvals ({pendingRequests.length})
    </button>
    <button 
      onclick={() => activeTab = "history"}
      class="pb-3 text-xs font-bold uppercase tracking-wider transition border-b-2 outline-none
             {activeTab === 'history' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'}"
    >
      Action History ({historicRequests.length})
    </button>
  </div>

  <!-- Content Section -->
  <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl overflow-hidden flex flex-col">
    {#if activeTab === 'pending'}
      <div class="p-5 border-b border-slate-800 bg-slate-950/20">
        <h2 class="text-xs font-bold text-white uppercase tracking-wider">Awaiting Verification</h2>
      </div>

      <div class="divide-y divide-slate-850">
        {#if pendingRequests.length === 0}
          <div class="p-8 text-center text-slate-500 text-xs">
            No pending requests found. All administrative changes are fully actioned.
          </div>
        {:else}
          {#each pendingRequests as req}
            <div class="p-5 flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0 hover:bg-slate-900/10 transition">
              <!-- Left Side details -->
              <div class="space-y-1.5 flex-1 min-w-0">
                <div class="flex items-center space-x-2.5">
                  <span class="text-xs font-bold text-white font-mono">#{req.id}</span>
                  <span class="text-xs font-bold uppercase text-emerald-400 tracking-wider">
                    {getReadableType(req.request_type)}
                  </span>
                  {#if req.maker_id === currentUserId}
                    <span class="px-2 py-0.5 rounded text-[8px] font-bold uppercase bg-red-950/45 text-red-400 border border-red-900/30">
                      Created by You
                    </span>
                  {/if}
                </div>
                <p class="text-xs text-slate-300 font-mono break-all pr-4">
                  {parsePayload(req.payload)}
                </p>
                <div class="flex items-center space-x-3 text-[10px] text-slate-500">
                  <span>Maker: {req.maker_email}</span>
                  <span>•</span>
                  <span class="flex items-center space-x-1">
                    <Clock class="w-3 h-3" />
                    <span>{new Date(req.created_at).toLocaleString()}</span>
                  </span>
                </div>
              </div>

              <!-- Right Side action tools -->
              <div class="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 w-full md:w-auto shrink-0">
                <!-- Rejection Reason input -->
                <input 
                  type="text" 
                  placeholder="Reason for rejection..." 
                  disabled={req.maker_id === currentUserId}
                  bind:value={rejectionReasons[req.id]}
                  class="bg-slate-950/60 border border-slate-850 focus:border-slate-750 text-white text-xs py-1.5 px-3 rounded-xl outline-none placeholder-slate-600 disabled:opacity-40"
                />

                <div class="flex space-x-2 justify-end">
                  <button 
                    onclick={() => handleReject(req.id)}
                    disabled={req.maker_id === currentUserId}
                    class="flex items-center justify-center p-1.5 bg-red-950/20 hover:bg-red-950/80 border border-red-900/30 text-red-400 hover:text-white rounded-xl transition disabled:opacity-30 disabled:cursor-not-allowed"
                    title="Reject Request"
                  >
                    <X class="w-4 h-4" />
                  </button>

                  <button 
                    onclick={() => handleApprove(req.id)}
                    disabled={req.maker_id === currentUserId}
                    class="flex items-center justify-center px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 text-xs font-bold uppercase tracking-wider rounded-xl transition disabled:opacity-30 disabled:cursor-not-allowed shadow shadow-emerald-500/5"
                    title="Approve Request"
                  >
                    Approve
                  </button>
                </div>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    {:else}
      <!-- History Tab -->
      <div class="p-5 border-b border-slate-800 bg-slate-950/20 flex justify-between items-center">
        <h2 class="text-xs font-bold text-white uppercase tracking-wider">Completed Audit Records</h2>
        <span class="text-xs font-mono text-slate-500">{historicRequests.length} logs</span>
      </div>

      <div class="overflow-x-auto">
        {#if historicRequests.length === 0}
          <div class="p-8 text-center text-slate-500 text-xs">
            No historical records found.
          </div>
        {:else}
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-950/30 text-slate-400 font-semibold border-b border-slate-800">
                <th class="p-4">ID</th>
                <th class="p-4">Action Request</th>
                <th class="p-4">Maker / Checker</th>
                <th class="p-4">Execution Status</th>
                <th class="p-4">Completed Date</th>
              </tr>
            </thead>
            <tbody>
              {#each historicRequests as r}
                <tr class="border-b border-slate-850 hover:bg-slate-900/10 transition">
                  <td class="p-4 font-mono text-slate-450">#{r.id}</td>
                  <td class="p-4 space-y-1">
                    <span class="font-bold text-slate-200 block">{getReadableType(r.request_type)}</span>
                    <span class="font-mono text-slate-500 block text-[10px] break-all">{parsePayload(r.payload)}</span>
                    {#if r.rejection_reason}
                      <span class="block text-[10px] text-red-400 font-semibold bg-red-950/20 border border-red-900/20 px-2 py-0.5 rounded mt-1">
                        Reason: {r.rejection_reason}
                      </span>
                    {/if}
                  </td>
                  <td class="p-4 space-y-0.5 text-slate-350">
                    <div class="block">Maker: <span class="font-semibold">{r.maker_email}</span></div>
                    <div class="block">Checker: <span class="font-semibold text-slate-400">{r.checker_email || '—'}</span></div>
                  </td>
                  <td class="p-4">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border
                                 {r.status === 'approved' 
                                   ? 'bg-emerald-950/40 text-emerald-450 border-emerald-900/40' 
                                   : 'bg-red-950/40 text-red-400 border-red-900/40'}">
                      {r.status}
                    </span>
                  </td>
                  <td class="p-4 text-slate-500 font-mono">
                    {r.actioned_at ? new Date(r.actioned_at).toLocaleString() : '—'}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
    {/if}
  </div>
</div>
