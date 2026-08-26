<script lang="ts">
  import { HelpCircle, BookOpen, MessageSquare, Play } from '@lucide/svelte';
</script>

<div class="p-6 space-y-6 max-w-4xl w-full mx-auto overflow-y-auto">
  <div>
    <h1 class="text-2xl font-bold text-white tracking-tight">Help & Documentation</h1>
    <p class="text-xs text-slate-400 mt-1">Learn how to configure widgets, load assets, and execute market trades.</p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Section 1 -->
    <div class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 space-y-3">
      <div class="flex items-center space-x-2.5 text-emerald-400 mb-2">
        <BookOpen class="w-5 h-5" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Trading Guide</h2>
      </div>
      <p class="text-xs text-slate-400 leading-relaxed">
        Tibarpay simulates standard trading terminals. Select an asset from the watchlist, select BUY or SELL mode, specify the size, and execute the order. Open trades are logged instantly in your terminal's history container.
      </p>
    </div>

    <!-- Section 2 -->
    <div class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 space-y-3">
      <div class="flex items-center space-x-2.5 text-emerald-400 mb-2">
        <HelpCircle class="w-5 h-5" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Chart Controls</h2>
      </div>
      <p class="text-xs text-slate-400 leading-relaxed">
        The interactive chart uses TradingView's Lightweight Charts engine. Click and drag the price scale to stretch vertically, drag the timeline to pan horizontally, or scroll to zoom in and out. Double-click the timeline to fit data bounds automatically.
      </p>
    </div>
  </div>

  <!-- FAQ Panel -->
  <div class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 space-y-4">
    <div class="flex items-center space-x-2.5 text-emerald-400 mb-2">
      <MessageSquare class="w-5 h-5" />
      <h2 class="text-sm font-bold text-white uppercase tracking-wider">Frequently Asked Questions</h2>
    </div>

    <div class="space-y-4 divide-y divide-slate-850">
      <div class="pt-0">
        <p class="text-xs font-bold text-slate-200">How do I change roles to Admin?</p>
        <p class="text-xs text-slate-400 mt-1">
          Admins are managed directly in the database. Use the seeded credentials `admin@tibarpay.com` with password `admin123`. Logged-in Admins can promote other regular users to Admin using the role toggles in the Admin user directory.
        </p>
      </div>

      <div class="pt-4">
        <p class="text-xs font-bold text-slate-200">Where are migrations configured?</p>
        <p class="text-xs text-slate-400 mt-1">
          Migrations are handled by Alembic inside the `backend/` directory. All models are dialect-agnostic, supporting a PostgreSQL target by simply changing the `DATABASE_URL` inside the backend's `.env` configuration file.
        </p>
      </div>
    </div>
  </div>
</div>
