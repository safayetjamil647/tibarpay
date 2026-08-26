<script lang="ts">
  import { TrendingUp, RefreshCw, BarChart2 } from '@lucide/svelte';

  const assets = [
    { symbol: "BTCUSD", name: "Bitcoin / US Dollar", price: 63520.40, change: "+1.15%", up: true, vol: "$14.2B", high: 64100, low: 62900 },
    { symbol: "ETHUSD", name: "Ethereum / US Dollar", price: 3452.80, change: "+0.85%", up: true, vol: "$6.8B", high: 3505, low: 3410 },
    { symbol: "AAPL", name: "Apple Inc.", price: 178.65, change: "-0.42%", up: false, vol: "$8.4B", high: 180.2, low: 177.8 },
    { symbol: "TSLA", name: "Tesla Inc.", price: 210.15, change: "-1.85%", up: false, vol: "$12.1B", high: 215.0, low: 208.5 },
    { symbol: "MSFT", name: "Microsoft Corp.", price: 415.30, change: "+0.15%", up: true, vol: "$5.1B", high: 417.8, low: 413.2 }
  ];
</script>

<div class="p-6 space-y-6 max-w-7xl w-full mx-auto overflow-y-auto">
  <div>
    <h1 class="text-2xl font-bold text-white tracking-tight">Market Screener</h1>
    <p class="text-xs text-slate-400 mt-1">Real-time status overview of trackable crypto and stock assets.</p>
  </div>

  <div class="bg-slate-900/40 border border-slate-800/80 backdrop-blur rounded-2xl shadow-2xl overflow-hidden flex flex-col">
    <div class="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-950/20">
      <div class="flex items-center space-x-2">
        <BarChart2 class="w-4.5 h-4.5 text-slate-400" />
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Spot Asset Screener</h2>
      </div>
      <span class="text-xs text-slate-500 font-mono">5 active tickers</span>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm border-collapse">
        <thead>
          <tr class="bg-slate-950/30 text-slate-400 font-semibold border-b border-slate-800 text-xs">
            <th class="p-4">Symbol</th>
            <th class="p-4">Name</th>
            <th class="p-4 text-right">Last Price</th>
            <th class="p-4 text-right">24h Change</th>
            <th class="p-4 text-right">24h Volume</th>
            <th class="p-4 text-right">24h Range</th>
            <th class="p-4 text-right">Terminal</th>
          </tr>
        </thead>
        <tbody>
          {#each assets as asset}
            <tr class="border-b border-slate-850 hover:bg-slate-900/10 transition">
              <td class="p-4 font-bold text-slate-200">{asset.symbol}</td>
              <td class="p-4 text-slate-400 text-xs">{asset.name}</td>
              <td class="p-4 text-right font-mono text-slate-200">${asset.price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
              <td class="p-4 text-right font-mono font-bold {asset.up ? 'text-emerald-400' : 'text-red-400'}">
                {asset.change}
              </td>
              <td class="p-4 text-right font-mono text-slate-300">{asset.vol}</td>
              <td class="p-4 text-right font-mono text-slate-450 text-xs">
                ${asset.low.toLocaleString()} - ${asset.high.toLocaleString()}
              </td>
              <td class="p-4 text-right">
                <a 
                  href="/dashboard"
                  class="inline-block px-3 py-1 bg-emerald-600/10 hover:bg-emerald-600 text-emerald-400 hover:text-slate-950 text-xs font-semibold rounded-lg transition border border-emerald-500/20">
                  Open Chart
                </a>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
