<script lang="ts">
  import { onMount } from 'svelte';
  import { token } from '$lib/store';
  import { apiRequest } from '$lib/api';
  import { Check, Settings, ShieldCheck, Sparkles, Plus, Loader, Layers, Edit, Trash2 } from '@lucide/svelte';

  interface Feature {
    id: number;
    name: string;
    code: string;
    description?: string;
  }

  interface Tier {
    id: number;
    name: string;
    price: number;
    description?: string;
    features: Feature[];
  }

  let tiers = $state<Tier[]>([]);
  let features = $state<Feature[]>([]);
  let activeToken = "";
  let errorMsg = $state("");
  let successMsg = $state("");
  let loading = $state(false);
  let activeTab = $state<'matrix' | 'tier' | 'feature'>('matrix');

  // Permission states
  let hasManageTiers = $state(false);
  let hasMakeRequest = $state(false);

  // Form states
  let newTierName = $state("");
  let newTierPrice = $state(0.0);
  let newTierDesc = $state("");
  
  let newFeatureName = $state("");
  let newFeatureCode = $state("");
  let newFeatureDesc = $state("");

  async function loadData() {
    loading = true;
    errorMsg = "";
    try {
      token.subscribe(v => activeToken = v || "")();
      const [fetchedTiers, fetchedFeatures, me] = await Promise.all([
        apiRequest('GET', '/api/tiers', null, activeToken),
        apiRequest('GET', '/api/admin/features', null, activeToken),
        apiRequest('GET', '/api/auth/me', null, activeToken)
      ]);
      tiers = fetchedTiers;
      features = fetchedFeatures;

      // Resolve roles & permissions
      const isSuper = me.roles.some((r: any) => r.name === 'Super Admin' || r.name === 'Admin');
      hasManageTiers = isSuper || me.roles.some((r: any) => r.permissions.some((p: any) => p.name === 'manage_tiers'));
      hasMakeRequest = isSuper || me.roles.some((r: any) => r.permissions.some((p: any) => p.name === 'make_request'));
    } catch (err: any) {
      errorMsg = err.message || "Failed to load subscription tiers or features.";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  async function handleCreateTier(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = "";
    successMsg = "";
    try {
      if (hasManageTiers) {
        await apiRequest('POST', '/api/admin/tiers', {
          name: newTierName,
          price: newTierPrice,
          description: newTierDesc
        }, activeToken);
        successMsg = `Tier "${newTierName}" created successfully directly!`;
      } else if (hasMakeRequest) {
        await apiRequest('POST', '/api/admin/requests', {
          request_type: "create_tier",
          payload: JSON.stringify({
            name: newTierName,
            price: newTierPrice,
            description: newTierDesc
          })
        }, activeToken);
        successMsg = `Maker-Checker request submitted to create tier "${newTierName}". Awaiting approval.`;
      } else {
        throw new Error("You do not have permission to create subscription plans.");
      }
      
      newTierName = "";
      newTierPrice = 0.0;
      newTierDesc = "";
      loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to create tier.";
    }
  }

  async function handleCreateFeature(e: SubmitEvent) {
    e.preventDefault();
    errorMsg = "";
    successMsg = "";
    try {
      if (hasManageTiers) {
        await apiRequest('POST', '/api/admin/features', {
          name: newFeatureName,
          code: newFeatureCode,
          description: newFeatureDesc
        }, activeToken);
        successMsg = `Feature "${newFeatureName}" registered successfully directly!`;
      } else if (hasMakeRequest) {
        await apiRequest('POST', '/api/admin/requests', {
          request_type: "create_feature",
          payload: JSON.stringify({
            name: newFeatureName,
            code: newFeatureCode,
            description: newFeatureDesc
          })
        }, activeToken);
        successMsg = `Maker-Checker request submitted to register feature "${newFeatureName}". Awaiting approval.`;
      } else {
        throw new Error("You do not have permission to register new features.");
      }
      
      newFeatureName = "";
      newFeatureCode = "";
      newFeatureDesc = "";
      loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to create feature.";
    }
  }

  async function toggleFeatureRelation(tier: Tier, feature: Feature, event: Event) {
    const isChecked = (event.target as HTMLInputElement).checked;
    errorMsg = "";
    successMsg = "";
    
    // Construct the new list of feature IDs
    let currentFeatureIds = tier.features.map(f => f.id);
    if (isChecked) {
      if (!currentFeatureIds.includes(feature.id)) {
        currentFeatureIds.push(feature.id);
      }
    } else {
      currentFeatureIds = currentFeatureIds.filter(id => id !== feature.id);
    }

    try {
      if (hasManageTiers) {
        await apiRequest('PUT', `/api/admin/tiers/${tier.id}/features`, {
          feature_ids: currentFeatureIds
        }, activeToken);
        successMsg = `Updated features checklist for ${tier.name} tier directly!`;
      } else if (hasMakeRequest) {
        // Revert checked state in matrix table visually (since it requires approval)
        (event.target as HTMLInputElement).checked = !isChecked;

        await apiRequest('POST', '/api/admin/requests', {
          request_type: "update_tier_features",
          payload: JSON.stringify({
            tier_id: tier.id,
            feature_ids: currentFeatureIds
          })
        }, activeToken);
        successMsg = `Maker-Checker request submitted to update features for tier "${tier.name}". Awaiting approval.`;
      } else {
        (event.target as HTMLInputElement).checked = !isChecked;
        throw new Error("You do not have permission to modify plan features.");
      }
      loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to update tier features.";
    }
  }

  // Edit/Delete tier states and handlers
  let editingTier = $state<Tier | null>(null);
  let editingTierName = $state("");
  let editingTierPrice = $state(0.0);
  let editingTierDesc = $state("");

  function startEdit(tier: Tier) {
    editingTier = tier;
    editingTierName = tier.name;
    editingTierPrice = tier.price;
    editingTierDesc = tier.description || "";
  }

  function cancelEdit() {
    editingTier = null;
    editingTierName = "";
    editingTierPrice = 0.0;
    editingTierDesc = "";
  }

  async function handleUpdateTier(e: SubmitEvent) {
    e.preventDefault();
    if (!editingTier) return;
    errorMsg = "";
    successMsg = "";
    try {
      if (hasManageTiers) {
        await apiRequest('PUT', `/api/admin/tiers/${editingTier.id}`, {
          name: editingTierName,
          price: editingTierPrice,
          description: editingTierDesc
        }, activeToken);
        successMsg = `Tier "${editingTierName}" updated successfully directly!`;
      } else if (hasMakeRequest) {
        await apiRequest('POST', '/api/admin/requests', {
          request_type: "update_tier",
          payload: JSON.stringify({
            tier_id: editingTier.id,
            name: editingTierName,
            price: editingTierPrice,
            description: editingTierDesc
          })
        }, activeToken);
        successMsg = `Maker-Checker request submitted to update tier "${editingTierName}". Awaiting approval.`;
      } else {
        throw new Error("You do not have permission to edit subscription plans.");
      }
      cancelEdit();
      loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to update tier.";
    }
  }

  async function handleDeleteTier(tier: Tier) {
    if (!confirm(`Are you sure you want to permanently delete subscription plan "${tier.name}"?`)) return;
    errorMsg = "";
    successMsg = "";
    try {
      if (hasManageTiers) {
        await apiRequest('DELETE', `/api/admin/tiers/${tier.id}`, null, activeToken);
        successMsg = `Tier "${tier.name}" deleted successfully directly!`;
      } else if (hasMakeRequest) {
        await apiRequest('POST', '/api/admin/requests', {
          request_type: "delete_tier",
          payload: JSON.stringify({
            tier_id: tier.id
          })
        }, activeToken);
        successMsg = `Maker-Checker request submitted to delete tier "${tier.name}". Awaiting approval.`;
      } else {
        throw new Error("You do not have permission to delete subscription plans.");
      }
      loadData();
    } catch (err: any) {
      errorMsg = err.message || "Failed to delete tier.";
    }
  }
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
      <Settings class="w-6 h-6 text-emerald-400" />
      <span>Tiers & Features Control Matrix</span>
    </h1>
    <p class="text-xs text-slate-400 mt-1">
      Create subscription plans, register access codes, and customize features matrix checklists.
    </p>
  </div>

  <!-- Messages -->
  {#if errorMsg}
    <div class="flex items-start space-x-2 bg-red-950/40 border border-red-800/50 text-red-300 p-4 rounded-xl text-xs">
      <span>{errorMsg}</span>
    </div>
  {/if}

  {#if successMsg}
    <div class="flex items-start space-x-2 bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 p-4 rounded-xl text-xs">
      <Check class="w-4 h-4 text-emerald-400 shrink-0" />
      <span>{successMsg}</span>
    </div>
  {/if}

  <!-- Tabs -->
  <div class="flex space-x-1 bg-slate-900/60 p-1 rounded-xl w-fit border border-slate-800/80 backdrop-blur">
    <button 
      onclick={() => activeTab = 'matrix'}
      class="px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 {activeTab === 'matrix' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}"
    >
      <Layers class="w-4 h-4" />
      <span>Features Matrix</span>
    </button>
    <button 
      onclick={() => activeTab = 'tier'}
      class="px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 {activeTab === 'tier' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}"
    >
      <Settings class="w-4 h-4" />
      <span>Manage Tiers</span>
    </button>
    <button 
      onclick={() => activeTab = 'feature'}
      class="px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 {activeTab === 'feature' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}"
    >
      <Plus class="w-4 h-4" />
      <span>Manage Features</span>
    </button>
  </div>

  <div class="mt-4">
    
    <!-- Tab 1: Matrix -->
    {#if activeTab === 'matrix'}
    <div class="space-y-6 animate-in fade-in duration-300">
      <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl p-6">
        <h2 class="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-1.5">
          <Layers class="w-4 h-4 text-emerald-400" />
          <span>Plans Features Checklists</span>
        </h2>
        
        {#if tiers.length === 0}
          <p class="text-slate-500 text-xs py-4">No tiers created. Use the right form to register tiers.</p>
        {:else}
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="bg-slate-950/30 text-slate-400 font-semibold border-b border-slate-800">
                  <th class="p-3">Plan Tier</th>
                  {#each features as f}
                    <th class="p-3 text-center" title={f.description}>
                      <span class="block font-bold">{f.name}</span>
                      <span class="block text-[8px] text-slate-500 mt-0.5 font-mono">{f.code}</span>
                    </th>
                  {/each}
                  <th class="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each tiers as t}
                  <tr class="border-b border-slate-850 hover:bg-slate-900/10 transition">
                    <td class="p-3 font-semibold text-slate-200">
                      <span class="block text-xs">{t.name}</span>
                      <span class="block text-[10px] text-emerald-400 font-mono mt-0.5">${t.price}/mo</span>
                    </td>
                    {#each features as f}
                      <td class="p-3 text-center">
                        <input 
                          type="checkbox" 
                          checked={t.features.some(tf => tf.id === f.id)}
                          onchange={(e) => toggleFeatureRelation(t, f, e)}
                          class="w-4 h-4 accent-emerald-500 rounded border-slate-800 bg-slate-950 cursor-pointer"
                        />
                      </td>
                    {/each}
                    <td class="p-3 text-right">
                      <div class="inline-flex items-center justify-end space-x-1.5 font-sans">
                        <button 
                          onclick={() => startEdit(t)}
                          class="p-1 bg-slate-950 hover:bg-slate-850 border border-slate-800 text-slate-300 rounded-lg transition"
                          title="Edit Plan"
                        >
                          <Edit class="w-3.5 h-3.5" />
                        </button>
                        <button 
                          onclick={() => handleDeleteTier(t)}
                          class="p-1 bg-red-950/20 hover:bg-red-950/80 border border-red-900/30 text-red-400 hover:text-white rounded-lg transition"
                          title="Delete Plan"
                        >
                          <Trash2 class="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
    {/if}

    <!-- Tab 2: Create/Edit Tier Form -->
    {#if activeTab === 'tier'}
    <div class="space-y-6 animate-in fade-in duration-300">
      <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl p-6 shadow-xl font-sans">
        {#if editingTier}
          <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-1.5">
            <Edit class="w-4 h-4 text-emerald-450" />
            <span>Edit Tier: {editingTier.name}</span>
          </h3>
          
          <form onsubmit={handleUpdateTier} class="space-y-4">
            <div>
              <label for="edit-tier-name" class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Tier Name</label>
              <input 
                id="edit-tier-name"
                type="text" 
                required
                bind:value={editingTierName}
                class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition"
              />
            </div>
            <div>
              <label for="edit-tier-price" class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Monthly Cost ($)</label>
              <input 
                id="edit-tier-price"
                type="number" 
                step="any"
                required
                bind:value={editingTierPrice}
                class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition font-mono"
              />
            </div>
            <div>
              <label for="edit-tier-desc" class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Description</label>
              <textarea 
                id="edit-tier-desc"
                rows="2"
                bind:value={editingTierDesc}
                class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition resize-none"
              ></textarea>
            </div>
            <div class="flex space-x-2">
              <button 
                type="submit"
                class="flex-1 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-slate-950 text-xs font-bold uppercase tracking-wider rounded-xl transition shadow shadow-emerald-500/10"
              >
                Save
              </button>
              <button 
                type="button"
                onclick={cancelEdit}
                class="px-4 py-2 bg-slate-950 hover:bg-slate-850 border border-slate-800 text-slate-300 text-xs font-bold uppercase tracking-wider rounded-xl transition"
              >
                Cancel
              </button>
            </div>
          </form>
        {:else}
          <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-1.5">
            <Plus class="w-4 h-4 text-emerald-400" />
            <span>Create Custom Tier</span>
          </h3>
          
          <form onsubmit={handleCreateTier} class="space-y-4">
            <div>
              <label for="tier-name" class="block text-[10px] font-bold uppercase tracking-wider text-slate-450 mb-1">Tier Name</label>
              <input 
                id="tier-name"
                type="text" 
                required
                placeholder="e.g. Standard Plus" 
                bind:value={newTierName}
                class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition"
              />
            </div>
            <div>
              <label for="tier-price" class="block text-[10px] font-bold uppercase tracking-wider text-slate-455 mb-1">Monthly Cost ($)</label>
              <input 
                id="tier-price"
                type="number" 
                step="any"
                required
                placeholder="19.99" 
                bind:value={newTierPrice}
                class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition font-mono"
              />
            </div>
            <div>
              <label for="tier-desc" class="block text-[10px] font-bold uppercase tracking-wider text-slate-455 mb-1">Description</label>
              <textarea 
                id="tier-desc"
                rows="2"
                placeholder="Tier features..." 
                bind:value={newTierDesc}
                class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition resize-none"
              ></textarea>
            </div>
            <button 
              type="submit"
              class="w-full py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-slate-950 text-xs font-bold uppercase tracking-wider rounded-xl transition shadow shadow-emerald-500/10"
            >
              Add Subscription Plan
            </button>
          </form>
        {/if}
      </div>
    </div>
    {/if}

    <!-- Tab 3: Create Feature Form -->
    {#if activeTab === 'feature'}
    <div class="space-y-6 animate-in fade-in duration-300">
      <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl p-6 shadow-xl">
        <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-1.5">
          <Plus class="w-4 h-4 text-emerald-400" />
          <span>Register New Feature</span>
        </h3>
        
        <form onsubmit={handleCreateFeature} class="space-y-4">
          <div>
            <label for="feat-name" class="block text-[10px] font-bold uppercase tracking-wider text-slate-455 mb-1">Feature Title</label>
            <input 
              id="feat-name"
              type="text" 
              required
              placeholder="e.g. Advanced AI Screener" 
              bind:value={newFeatureName}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition"
            />
          </div>
          <div>
            <label for="feat-code" class="block text-[10px] font-bold uppercase tracking-wider text-slate-455 mb-1">Unique Code</label>
            <input 
              id="feat-code"
              type="text" 
              required
              placeholder="e.g. ai_screener" 
              bind:value={newFeatureCode}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition font-mono"
            />
          </div>
          <div>
            <label for="feat-desc" class="block text-[10px] font-bold uppercase tracking-wider text-slate-455 mb-1">Description</label>
            <textarea 
              id="feat-desc"
              rows="2"
              placeholder="What this feature does..." 
              bind:value={newFeatureDesc}
              class="w-full bg-slate-950/50 border border-slate-800 focus:border-slate-700 rounded-xl py-2 px-3 text-white text-xs outline-none transition resize-none"
            ></textarea>
          </div>
          <button 
            type="submit"
            class="w-full py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-slate-950 text-xs font-bold uppercase tracking-wider rounded-xl transition shadow shadow-emerald-500/10"
          >
            Register Feature
          </button>
        </form>
      </div>
    </div>
    {/if}

  </div>
</div>
