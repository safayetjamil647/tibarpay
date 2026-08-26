<script lang="ts">
  import './layout.css';
  import favicon from '$lib/assets/favicon.svg';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { token, userRole, userTier, logout } from '$lib/store';
  import { apiRequest } from '$lib/api';

  let { children } = $props();

  async function checkUserSession() {
    let activeToken = "";
    token.subscribe(val => activeToken = val || "")();
    
    if (activeToken) {
      try {
        const user = await apiRequest('GET', '/api/auth/me', null, activeToken);
        userTier.set(user.tier || null);
      } catch (err) {
        // Token has expired or is invalid, log out the user
        logout();
        goto('/login');
      }
    }
  }

  onMount(() => {
    checkUserSession();
  });

  // Client-side routing guards
  $effect(() => {
    const currentPath = $page.url.pathname;
    let activeToken: string | null = null;
    let activeRole: string | null = null;

    token.subscribe(v => activeToken = v)();
    userRole.subscribe(v => activeRole = v)();

    const isAdmin = activeRole ? activeRole.toLowerCase().includes('admin') : false;

    if (!activeToken) {
      if (currentPath.startsWith('/dashboard') || currentPath.startsWith('/admin') || currentPath === '/') {
        goto('/login');
      }
    } else {
      if (currentPath === '/login' || currentPath === '/register' || currentPath === '/') {
        if (isAdmin) {
          window.location.href = '/admin';
        } else {
          goto('/dashboard');
        }
      }

      if (currentPath.startsWith('/admin') && !isAdmin) {
        goto('/dashboard');
      }
    }
  });
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
  <title>Tibarpay - Advanced Trading Platform</title>
  <meta name="description" content="State-of-the-art interactive charts and trading platform clone." />
</svelte:head>

<div class="min-h-screen bg-[#070b13] text-slate-100 flex flex-col font-sans antialiased selection:bg-emerald-500 selection:text-slate-900">
  {@render children()}
</div>
