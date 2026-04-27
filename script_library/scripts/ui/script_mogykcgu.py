import http.server
import socketserver
import socket
import threading
import webbrowser
import time
import json
import urllib.parse
import urllib.request
import csv
import io
from pathlib import Path
from datetime import datetime, timezone


HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球购买力对比 </title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700;900&display=swap');
        :root {
            --indigo: #4f46e5;
            --violet: #7c3aed;
            --green: #16a34a;
            --rose: #f43f5e;
            --slate: #0f172a;
        }
        body {
            font-family: 'Noto Sans SC', sans-serif;
            background:
                radial-gradient(circle at top left, rgba(99,102,241,.18), transparent 36rem),
                radial-gradient(circle at top right, rgba(14,165,233,.13), transparent 30rem),
                linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        }
        .glass {
            background: rgba(255,255,255,.78);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }
        .card-animate { transition: all .28s cubic-bezier(0.4, 0, 0.2, 1); }
        .card-animate:hover { transform: translateY(-4px); }
        input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
        .tab-active {
            background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
            color: white !important;
            box-shadow: 0 16px 34px rgba(79,70,229,.24);
        }
        .country-active {
            background: #0f172a !important;
            color: white !important;
        }
        .soft-scroll::-webkit-scrollbar { height: 5px; width: 5px; }
        .soft-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
        .rank-pill {
            background: linear-gradient(135deg, rgba(79,70,229,.1), rgba(124,58,237,.08));
        }
    </style>
</head>
<body class="text-slate-900 min-h-screen pb-28">
    <div class="max-w-7xl mx-auto px-4 pt-6 md:pt-8">
        <div class="sticky top-0 z-30 -mx-4 px-4 py-3 glass border-b border-white/60 mb-6">
            <div class="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-3">
                <div class="flex flex-wrap items-center gap-2">
                    <div class="flex items-center gap-2 bg-white/80 px-3 py-2 rounded-full shadow-sm border border-white">
                        <div id="statusDot" class="w-2 h-2 rounded-full bg-slate-300"></div>
                        <span id="statusText" class="text-[11px] font-black text-slate-500 tracking-tight">数据准备中...</span>
                    </div>
                    <div class="flex items-center gap-2 bg-white/80 px-3 py-2 rounded-full shadow-sm border border-white">
                        <div id="cacheDot" class="w-2 h-2 rounded-full bg-slate-300"></div>
                        <span id="cacheText" class="text-[11px] font-black text-slate-500 tracking-tight">缓存状态检查中...</span>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="syncAll(true)" class="px-3 py-2 bg-white rounded-xl border border-slate-200 text-slate-500 hover:text-indigo-600 hover:border-indigo-200 transition-colors flex items-center gap-2 text-xs font-black">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                        强制刷新
                    </button>
                    <button onclick="toggleEditMode()" class="p-2 bg-white rounded-xl border border-slate-200 text-slate-500 hover:text-indigo-600 hover:border-indigo-200 transition-colors" title="修改各国价格">
                        <i data-lucide="settings-2" class="w-5 h-5"></i>
                    </button>
                </div>
            </div>
        </div>

        <header class="text-center mb-8">
            <div class="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-full text-xs font-black mb-4 border border-indigo-100">
                <i data-lucide="globe-2" class="w-4 h-4"></i>
                多商品 · 多国家 · 中国基准 1x
            </div>
            <h1 class="text-4xl md:text-6xl font-black tracking-tight text-slate-900">
                全球<span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">购买力</span>对比器
            </h1>
            <p class="text-slate-500 mt-3 font-bold">输入任意人民币金额，比较它在不同国家能买到多少生活用品。</p>
        </header>

        <section class="grid grid-cols-1 xl:grid-cols-12 gap-6 mb-6">
            <div class="xl:col-span-7 bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-700 rounded-[2rem] p-7 md:p-8 shadow-2xl shadow-indigo-200 relative overflow-hidden text-white">
                <div class="relative z-10">
                    <label class="block text-indigo-100 text-xs font-black uppercase tracking-widest mb-4">投入金额 (CNY)</label>
                    <div class="flex items-center gap-4">
                        <span class="text-5xl md:text-6xl font-black">¥</span>
                        <input type="number" id="baseAmount" value="100" step="0.01"
                            class="bg-transparent text-5xl md:text-7xl font-black w-full outline-none border-b-4 border-indigo-300 focus:border-white transition-colors placeholder-indigo-200">
                    </div>
                    <div class="mt-7 flex flex-wrap gap-3">
                        <button onclick="setAmount(100)" class="px-4 py-2 rounded-2xl bg-white/15 text-white text-sm font-black hover:bg-white/25 transition-all">¥100</button>
                        <button onclick="setAmount(500)" class="px-4 py-2 rounded-2xl bg-white/15 text-white text-sm font-black hover:bg-white/25 transition-all">¥500</button>
                        <button onclick="setAmount(1000)" class="px-4 py-2 rounded-2xl bg-white/15 text-white text-sm font-black hover:bg-white/25 transition-all">¥1,000</button>
                        <button onclick="setAmount(10000)" class="px-4 py-2 rounded-2xl bg-white/15 text-white text-sm font-black hover:bg-white/25 transition-all">¥10,000</button>
                    </div>
                </div>
                <div class="absolute -right-20 -bottom-28 w-80 h-80 bg-white rounded-full opacity-10"></div>
                <div class="absolute right-8 top-8 text-white/10 text-8xl font-black">PPP</div>
            </div>

            <div class="xl:col-span-5 glass rounded-[2rem] p-6 border border-white shadow-xl">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-sm font-black text-slate-700 flex items-center gap-2">
                        <i data-lucide="trophy" class="w-4 h-4 text-indigo-600"></i>
                        当前商品购买力前三
                    </h3>
                    <span id="currentItemBadge" class="text-xs font-black text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full"></span>
                </div>
                <div id="topRanks" class="space-y-3"></div>
            </div>
        </section>

        <section class="glass rounded-[2rem] p-4 md:p-5 border border-white shadow-lg mb-6">
            <div class="flex items-center justify-between gap-3 mb-4">
                <div>
                    <p class="text-xs font-black text-slate-400 uppercase tracking-widest">选择对比物</p>
                    <p class="text-sm text-slate-500 font-bold">切换后卡片、排行和热力表会一起更新</p>
                </div>
                <button onclick="toggleOverview()" class="hidden md:flex items-center gap-2 text-xs font-black px-3 py-2 rounded-xl bg-slate-900 text-white">
                    <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
                    总览
                </button>
            </div>
            <div id="itemTabs" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3"></div>
        </section>

        <section id="overviewSection" class="glass rounded-[2rem] p-5 border border-white shadow-lg mb-6">
            <div class="flex flex-wrap justify-between items-center gap-3 mb-4">
                <div>
                    <h2 class="text-lg font-black text-slate-800">一眼看懂：各国综合购买力</h2>
                    <p class="text-xs text-slate-500 font-bold">按 6 类商品平均倍数排序，数值越高表示同样人民币换汇后越经花。</p>
                </div>
                <span id="overviewHint" class="text-[11px] font-black text-slate-400 bg-white px-3 py-2 rounded-full border border-slate-100"></span>
            </div>
            <div class="overflow-x-auto soft-scroll">
                <table class="min-w-[920px] w-full text-left border-separate border-spacing-y-2">
                    <thead>
                        <tr class="text-[11px] text-slate-400 font-black uppercase">
                            <th class="px-3 py-2">国家</th>
                            <th class="px-3 py-2">综合倍数</th>
                            <th class="px-3 py-2">大米</th>
                            <th class="px-3 py-2">西瓜</th>
                            <th class="px-3 py-2">汉堡</th>
                            <th class="px-3 py-2">鸡蛋</th>
                            <th class="px-3 py-2">牛奶</th>
                            <th class="px-3 py-2">餐巾纸</th>
                        </tr>
                    </thead>
                    <tbody id="overviewTable"></tbody>
                </table>
            </div>
        </section>

        <section class="glass rounded-[2rem] p-4 border border-white shadow-lg mb-6">
            <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <p class="text-xs font-black text-slate-400 uppercase tracking-widest">筛选国家</p>
                    <p class="text-sm text-slate-500 font-bold">可以只看你关心的国家，方便横向比较</p>
                </div>
                <div class="flex gap-2">
                    <button onclick="selectAllCountries()" class="text-xs font-black px-3 py-2 bg-white rounded-xl border border-slate-200 text-slate-600">全选</button>
                    <button onclick="resetCountries()" class="text-xs font-black px-3 py-2 bg-white rounded-xl border border-slate-200 text-slate-600">默认</button>
                </div>
            </div>
            <div id="countryFilter" class="flex gap-2 overflow-x-auto soft-scroll pt-4 pb-1"></div>
        </section>

        <section class="grid grid-cols-1 xl:grid-cols-12 gap-6 mb-6">
            <div class="xl:col-span-4 glass rounded-[2rem] p-6 border border-white shadow-lg">
                <h3 id="chinaTitle" class="text-slate-400 text-xs font-black uppercase tracking-widest mb-4">中国购买力 (基准 1x)</h3>
                <div id="chinaReference" class="space-y-2"></div>
            </div>
            <div class="xl:col-span-8 glass rounded-[2rem] p-6 border border-white shadow-lg">
                <h3 class="text-slate-700 text-sm font-black mb-4 flex items-center gap-2">
                    <i data-lucide="info" class="w-4 h-4 text-indigo-600"></i>
                    数据说明
                </h3>
                <div id="sourceNote" class="text-xs text-slate-500 leading-relaxed font-bold grid md:grid-cols-2 gap-3"></div>
            </div>
        </section>

        <div id="resultsGrid" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"></div>

        <div id="editModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-white rounded-[2rem] max-w-3xl w-full p-8 shadow-2xl">
                <h2 class="text-2xl font-black mb-2 flex items-center gap-2">
                    <i data-lucide="edit-3" class="text-indigo-600"></i>
                    调整当前商品价格
                </h2>
                <p class="text-xs text-slate-400 font-bold mb-6">单位会随当前对比物变化。修改后立即用于计算，不会改动源代码。</p>
                <div id="editInputs" class="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto pr-2 soft-scroll"></div>
                <div class="mt-8 flex gap-4">
                    <button onclick="toggleEditMode()" class="flex-1 py-4 bg-slate-100 rounded-2xl font-black text-slate-600">取消</button>
                    <button onclick="savePrices()" class="flex-1 py-4 bg-indigo-600 rounded-2xl font-black text-white shadow-lg shadow-indigo-100">保存修改</button>
                </div>
            </div>
        </div>
    </div>

    <audio id="bgmAudio" preload="none"></audio>
    <button id="bgmButton" onclick="toggleBGM()" 
        class="fixed bottom-5 right-5 z-40 px-4 py-3 rounded-full bg-slate-950 text-white shadow-2xl text-xs hover:bg-indigo-600 transition-all flex items-center gap-2 font-black">
        <span id="bgmIcon">▶</span>
        <span id="bgmText">播放购买力小曲</span>
    </button>

    <script>
        const ITEMS = {
            rice: { name: '大米', short: '大米', emoji: '🍚', priceUnit: '每 KG', qtyFactor: 2, qtyLabel: '斤' },
            watermelon: { name: '西瓜', short: '西瓜', emoji: '🍉', priceUnit: '每 KG', qtyFactor: 2, qtyLabel: '斤' },
            burger: { name: '麦当劳汉堡', short: '汉堡', emoji: '🍔', priceUnit: '每个', qtyFactor: 1, qtyLabel: '个' },
            eggs: { name: '鸡蛋', short: '鸡蛋', emoji: '🥚', priceUnit: '每 12 枚', qtyFactor: 12, qtyLabel: '枚' },
            milk: { name: '牛奶', short: '牛奶', emoji: '🥛', priceUnit: '每 L', qtyFactor: 1, qtyLabel: '升' },
            napkins: { name: '餐巾纸', short: '纸巾', emoji: '🧻', priceUnit: '每包', qtyFactor: 1, qtyLabel: '包' }
        };

        let currentItem = 'rice';
        let visibleCountries = ['USD','AUD','NZD','KRW','HKD','GBP','EUR_DE','ISK','EUR_FR','CAD'];

        let COUNTRY_DATA = {
            CNY: { name: '中国', flag: '🇨🇳', symbol: '¥', iso3: 'CHN', prices: { rice: 8.6, watermelon: 4.8, burger: 25.0, eggs: 12.0, milk: 11.0, napkins: 5.0 } },
            USD: { name: '美国', flag: '🇺🇸', symbol: '$', iso3: 'USA', prices: { rice: 4.80, watermelon: 1.70, burger: 5.69, eggs: 4.50, milk: 1.05, napkins: 2.50 } },
            AUD: { name: '澳大利亚', flag: '🇦🇺', symbol: 'A$', iso3: 'AUS', prices: { rice: 3.60, watermelon: 3.90, burger: 7.70, eggs: 5.80, milk: 1.75, napkins: 3.20 } },
            NZD: { name: '新西兰', flag: '🇳🇿', symbol: 'NZ$', iso3: 'NZL', prices: { rice: 5.10, watermelon: 4.50, burger: 8.10, eggs: 8.50, milk: 2.90, napkins: 3.80 } },
            KRW: { name: '韩国', flag: '🇰🇷', symbol: '₩', iso3: 'KOR', prices: { rice: 5400, watermelon: 4200, burger: 5500, eggs: 7200, milk: 2800, napkins: 2500 } },
            HKD: { name: '中国香港', flag: '🇭🇰', symbol: 'HK$', iso3: 'HKG', prices: { rice: 15.2, watermelon: 18.0, burger: 24.0, eggs: 32.0, milk: 24.0, napkins: 12.0 } },
            GBP: { name: '英国', flag: '🇬🇧', symbol: '£', iso3: 'GBR', prices: { rice: 1.55, watermelon: 1.60, burger: 4.49, eggs: 2.80, milk: 1.15, napkins: 1.80 } },
            EUR_DE: { name: '德国', flag: '🇩🇪', symbol: '€', iso3: 'DEU', currency: 'EUR', prices: { rice: 2.20, watermelon: 1.90, burger: 5.29, eggs: 3.20, milk: 1.10, napkins: 1.70 } },
            ISK: { name: '冰岛', flag: '🇮🇸', symbol: 'kr', iso3: 'ISL', prices: { rice: 520, watermelon: 390, burger: 990, eggs: 850, milk: 240, napkins: 450 } },
            EUR_FR: { name: '法国', flag: '🇫🇷', symbol: '€', iso3: 'FRA', currency: 'EUR', prices: { rice: 2.40, watermelon: 2.20, burger: 5.40, eggs: 3.60, milk: 1.25, napkins: 1.90 } },
            CAD: { name: '加拿大', flag: '🇨🇦', symbol: 'C$', iso3: 'CAN', prices: { rice: 4.20, watermelon: 2.20, burger: 7.05, eggs: 5.30, milk: 2.60, napkins: 2.80 } }
        };

        let exchangeRates = { CNY: 1, USD: 0.138, AUD: 0.21, NZD: 0.23, KRW: 188.5, HKD: 1.08, GBP: 0.11, EUR: 0.128, ISK: 19.2, CAD: 0.19 };
        let meta = { rates: {}, prices: {}, generatedAt: null };

        function getCurrencyCode(code) { return COUNTRY_DATA[code].currency || code; }
        function getRate(code) { return exchangeRates[getCurrencyCode(code)] || 1; }
        function amount() { return parseFloat(document.getElementById('baseAmount').value) || 0; }

        function initTabs() {
            const tabs = document.getElementById('itemTabs');
            tabs.innerHTML = '';
            Object.keys(ITEMS).forEach(key => {
                const item = ITEMS[key];
                const btn = document.createElement('button');
                btn.id = 'tab-' + key;
                btn.onclick = () => setItem(key);
                btn.className = "px-4 py-4 rounded-2xl bg-white text-slate-700 font-black text-sm hover:bg-indigo-50 hover:text-indigo-600 transition-all flex items-center justify-center gap-2 border border-slate-100";
                btn.innerHTML = `<span class="text-2xl">${item.emoji}</span><span>${item.name}</span>`;
                tabs.appendChild(btn);
            });
            updateTabStyle();
        }

        function initCountryFilter() {
            const box = document.getElementById('countryFilter');
            box.innerHTML = '';
            Object.keys(COUNTRY_DATA).forEach(code => {
                if (code === 'CNY') return;
                const c = COUNTRY_DATA[code];
                const btn = document.createElement('button');
                btn.id = 'country-' + code;
                btn.onclick = () => toggleCountry(code);
                btn.className = "shrink-0 px-3 py-2 rounded-2xl bg-white border border-slate-200 text-slate-700 text-xs font-black flex items-center gap-2 transition";
                btn.innerHTML = `<span>${c.flag}</span><span>${c.name}</span>`;
                box.appendChild(btn);
            });
            updateCountryStyle();
        }

        function updateTabStyle() {
            Object.keys(ITEMS).forEach(key => {
                const el = document.getElementById('tab-' + key);
                if (el) el.classList.toggle('tab-active', key === currentItem);
            });
        }

        function updateCountryStyle() {
            Object.keys(COUNTRY_DATA).forEach(code => {
                if (code === 'CNY') return;
                const el = document.getElementById('country-' + code);
                if (el) el.classList.toggle('country-active', visibleCountries.includes(code));
            });
        }

        function toggleCountry(code) {
            if (visibleCountries.includes(code)) {
                visibleCountries = visibleCountries.filter(x => x !== code);
            } else {
                visibleCountries.push(code);
            }
            if (visibleCountries.length === 0) visibleCountries = [code];
            updateCountryStyle();
            render();
        }
        function selectAllCountries() {
            visibleCountries = Object.keys(COUNTRY_DATA).filter(x => x !== 'CNY');
            updateCountryStyle();
            render();
        }
        function resetCountries() {
            visibleCountries = ['USD','AUD','NZD','KRW','HKD','GBP','EUR_DE','ISK','EUR_FR','CAD'];
            updateCountryStyle();
            render();
        }

        function setItem(key) {
            currentItem = key;
            updateTabStyle();
            render();
        }

        function setAmount(val) {
            document.getElementById('baseAmount').value = val;
            render();
        }

        function calculateQuantity(inputAmount, code, itemKey) {
            const item = ITEMS[itemKey];
            const country = COUNTRY_DATA[code];
            const rate = getRate(code);
            return (inputAmount * rate / country.prices[itemKey]) * item.qtyFactor;
        }

        function multiplier(code, itemKey) {
            const cn = calculateQuantity(100, 'CNY', itemKey);
            const foreign = calculateQuantity(100, code, itemKey);
            return cn ? foreign / cn : 0;
        }

        function avgMultiplier(code) {
            const keys = Object.keys(ITEMS);
            return keys.reduce((sum, k) => sum + multiplier(code, k), 0) / keys.length;
        }

        function sortedCurrentCountries() {
            return visibleCountries
                .map(code => ({ code, m: multiplier(code, currentItem), avg: avgMultiplier(code) }))
                .sort((a,b) => b.m - a.m);
        }

        function colorClass(m) {
            if (m >= 1.2) return 'text-green-600';
            if (m < 0.8) return 'text-rose-500';
            return 'text-indigo-600';
        }
        function barClass(m) {
            if (m >= 1.2) return 'bg-green-500';
            if (m < 0.8) return 'bg-rose-400';
            return 'bg-indigo-500';
        }
        function cellBg(m) {
            if (m >= 1.3) return 'bg-green-50 text-green-700';
            if (m >= 1.0) return 'bg-indigo-50 text-indigo-700';
            if (m < 0.7) return 'bg-rose-50 text-rose-600';
            return 'bg-slate-50 text-slate-600';
        }

        async function syncAll(force=false) {
            const status = document.getElementById('statusText');
            const dot = document.getElementById('statusDot');
            const cache = document.getElementById('cacheText');
            const cacheDot = document.getElementById('cacheDot');
            status.innerText = "同步稳定数据源中...";
            dot.className = "w-2 h-2 rounded-full bg-amber-400 animate-pulse";
            cache.innerText = "正在检查缓存...";
            cacheDot.className = "w-2 h-2 rounded-full bg-amber-400 animate-pulse";

            try {
                const res = await fetch('/api/all-data' + (force ? '?force=1' : ''));
                const data = await res.json();
                if (!data.ok) throw new Error(data.error || '同步失败');

                if (data.rates) exchangeRates = Object.assign(exchangeRates, data.rates);
                if (data.prices) {
                    Object.keys(data.prices).forEach(code => {
                        if (!COUNTRY_DATA[code]) return;
                        Object.keys(data.prices[code]).forEach(itemKey => {
                            const v = parseFloat(data.prices[code][itemKey]);
                            if (v > 0) COUNTRY_DATA[code].prices[itemKey] = v;
                        });
                    });
                }
                meta = data.meta || meta;

                status.innerText = "数据同步完成";
                dot.className = "w-2 h-2 rounded-full bg-green-500";
                const cacheText = meta.cacheUsed ? "已使用缓存兜底" : "已连接实时/公开数据源";
                cache.innerText = cacheText;
                cacheDot.className = meta.cacheUsed ? "w-2 h-2 rounded-full bg-amber-400" : "w-2 h-2 rounded-full bg-green-500";
            } catch (e) {
                status.innerText = "接口失败，使用内置数据";
                dot.className = "w-2 h-2 rounded-full bg-slate-400";
                cache.innerText = "本地默认值兜底";
                cacheDot.className = "w-2 h-2 rounded-full bg-slate-400";
            }
            render();
        }

        function renderTopRanks() {
            const box = document.getElementById('topRanks');
            const list = sortedCurrentCountries().slice(0, 3);
            document.getElementById('currentItemBadge').innerText = ITEMS[currentItem].emoji + ' ' + ITEMS[currentItem].name;
            box.innerHTML = list.map((x, idx) => {
                const c = COUNTRY_DATA[x.code];
                return `
                    <div class="rank-pill rounded-2xl p-4 border border-white flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center text-xs font-black text-indigo-600">#${idx+1}</div>
                            <div>
                                <p class="font-black text-slate-800">${c.flag} ${c.name}</p>
                                <p class="text-[11px] text-slate-400 font-bold">同样金额可买更多 ${ITEMS[currentItem].short}</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-2xl font-black ${colorClass(x.m)}">${x.m.toFixed(2)}x</p>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function renderOverview() {
            const body = document.getElementById('overviewTable');
            const rows = Object.keys(COUNTRY_DATA)
                .filter(code => code !== 'CNY')
                .map(code => ({ code, avg: avgMultiplier(code) }))
                .sort((a,b) => b.avg - a.avg);

            body.innerHTML = rows.map((r, idx) => {
                const c = COUNTRY_DATA[r.code];
                const cells = Object.keys(ITEMS).map(k => {
                    const m = multiplier(r.code, k);
                    return `<td class="px-3 py-3"><span class="px-2 py-1 rounded-lg text-xs font-black ${cellBg(m)}">${m.toFixed(2)}x</span></td>`;
                }).join('');
                return `
                    <tr class="bg-white shadow-sm">
                        <td class="px-3 py-3 rounded-l-2xl">
                            <div class="flex items-center gap-2 font-black text-sm">
                                <span class="text-slate-400 text-xs w-5">#${idx+1}</span>
                                <span>${c.flag}</span>
                                <span>${c.name}</span>
                            </div>
                        </td>
                        <td class="px-3 py-3"><span class="font-black text-indigo-600">${r.avg.toFixed(2)}x</span></td>
                        ${cells}
                    </tr>
                `;
            }).join('');

            const updated = meta.generatedAt ? ("更新：" + meta.generatedAt) : "使用当前本地数据计算";
            document.getElementById('overviewHint').innerText = updated;
        }

        function renderChina() {
            const inputAmount = amount();
            const item = ITEMS[currentItem];
            const chinaQty = calculateQuantity(inputAmount, 'CNY', currentItem);
            document.getElementById('chinaTitle').innerText = `中国${item.name}购买力`;
            document.getElementById('chinaReference').innerHTML = `
                <div class="flex items-end gap-2">
                    <div class="text-5xl font-black text-slate-900">${chinaQty.toFixed(2)}</div>
                    <div class="text-lg font-black text-slate-400 mb-1">${item.qtyLabel}</div>
                </div>
                <p class="text-xs text-slate-500 leading-relaxed font-bold">中国作为基准：<span class="text-indigo-600">1.00x</span></p>
                <div class="mt-4 bg-white rounded-2xl p-4 border border-slate-100">
                    <p class="text-[11px] text-slate-400 font-black uppercase">中国价格</p>
                    <p class="text-lg font-black text-slate-800">${COUNTRY_DATA.CNY.symbol}${COUNTRY_DATA.CNY.prices[currentItem]} / ${item.priceUnit}</p>
                </div>
            `;
        }

        function renderSourceNote() {
            const ratesMeta = meta.rates || {};
            const pricesMeta = meta.prices || {};
            const bigmac = pricesMeta.bigmacDate ? `Big Mac 数据同步到 ${pricesMeta.bigmacDate}` : "Big Mac 使用默认参考价或缓存";
            const note = [
                { title: "汇率", text: ratesMeta.source ? `${ratesMeta.source}；失败时自动使用缓存或内置汇率。` : "实时接口失败时使用缓存或内置汇率。" },
                { title: "汉堡", text: bigmac + "，适合做购买力参照。" },
                { title: "生活品", text: "西瓜、鸡蛋、牛奶、餐巾纸没有稳定覆盖全球的免费实时零售价 API，因此保留默认参考价，并可手动修改。" },
                { title: "稳定性", text: "Python 后端统一请求接口，带超时、缓存、备用源和默认值，减少手机浏览器跨域和网络失败。" }
            ];
            document.getElementById('sourceNote').innerHTML = note.map(x => `
                <div class="bg-white/75 rounded-2xl p-4 border border-slate-100">
                    <p class="text-slate-800 font-black mb-1">${x.title}</p>
                    <p>${x.text}</p>
                </div>
            `).join('');
        }

        function renderCards() {
            const inputAmount = amount();
            const grid = document.getElementById('resultsGrid');
            const item = ITEMS[currentItem];
            const chinaQty = calculateQuantity(inputAmount, 'CNY', currentItem);

            grid.innerHTML = sortedCurrentCountries().map(({code, m}) => {
                const country = COUNTRY_DATA[code];
                const rate = getRate(code);
                const localQty = calculateQuantity(inputAmount, code, currentItem);
                const ppp = ((COUNTRY_DATA.CNY.prices[currentItem] / country.prices[currentItem]) * (1 / rate));
                const marketCny = rate ? (1 / rate) : 0;
                const width = Math.max(5, Math.min(m * 50, 100));

                return `
                    <div class="card-animate bg-white/90 rounded-[2rem] p-6 border border-white shadow-lg">
                        <div class="flex justify-between items-start mb-5">
                            <div class="flex items-center gap-3">
                                <div class="w-12 h-12 rounded-2xl bg-slate-50 flex items-center justify-center text-3xl">${country.flag}</div>
                                <div>
                                    <h4 class="font-black text-slate-900">${country.name}</h4>
                                    <p class="text-[11px] font-bold text-slate-400">¥100 ≈ ${country.symbol}${(100*rate).toFixed(2)}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-3xl font-black ${colorClass(m)}">${localQty.toFixed(2)}</div>
                                <p class="text-[11px] font-black text-slate-300">${item.qtyLabel}</p>
                            </div>
                        </div>

                        <div class="bg-slate-50 rounded-2xl p-4 mb-4 border border-slate-100">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-[11px] font-black text-slate-400">购买力倍数</span>
                                <span class="text-sm font-black ${colorClass(m)}">中国的 ${m.toFixed(2)} 倍</span>
                            </div>
                            <div class="h-3 w-full bg-white rounded-full overflow-hidden border border-slate-100">
                                <div class="h-full rounded-full transition-all duration-1000 ${barClass(m)}" style="width:${width}%"></div>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-3 text-center">
                            <div class="bg-slate-50 rounded-2xl p-3">
                                <p class="text-[10px] text-slate-400 uppercase font-black">${item.name}价格</p>
                                <p class="text-xs font-black text-slate-700">${country.symbol}${country.prices[currentItem]} / ${item.priceUnit}</p>
                            </div>
                            <div class="bg-slate-50 rounded-2xl p-3">
                                <p class="text-[10px] text-slate-400 uppercase font-black">购买力汇率</p>
                                <p class="text-xs font-black text-slate-700">1 ${getCurrencyCode(code)} = ${ppp.toFixed(2)} ¥</p>
                            </div>
                            <div class="bg-slate-50 rounded-2xl p-3">
                                <p class="text-[10px] text-slate-400 uppercase font-black">市场汇率</p>
                                <p class="text-xs font-black text-slate-700">1 ${getCurrencyCode(code)} = ${marketCny.toFixed(2)} ¥</p>
                            </div>
                            <div class="bg-slate-50 rounded-2xl p-3">
                                <p class="text-[10px] text-slate-400 uppercase font-black">综合倍数</p>
                                <p class="text-xs font-black text-slate-700">${avgMultiplier(code).toFixed(2)}x</p>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function render() {
            renderTopRanks();
            renderOverview();
            renderChina();
            renderSourceNote();
            renderCards();
        }

        function toggleOverview() {
            const el = document.getElementById('overviewSection');
            el.classList.toggle('hidden');
        }

        function toggleEditMode() {
            const modal = document.getElementById('editModal');
            modal.classList.toggle('hidden');
            if (!modal.classList.contains('hidden')) {
                const container = document.getElementById('editInputs');
                const item = ITEMS[currentItem];
                container.innerHTML = '';
                Object.keys(COUNTRY_DATA).forEach(code => {
                    const country = COUNTRY_DATA[code];
                    container.innerHTML += `
                        <div>
                            <label class="text-xs font-black text-slate-400 mb-2 block">${country.flag} ${country.name} ${item.name}价格（${item.priceUnit}）</label>
                            <input type="number" step="0.01" data-code="${code}" value="${country.prices[currentItem]}" class="price-input w-full p-3 bg-slate-50 border border-slate-100 rounded-xl font-black outline-none focus:border-indigo-500">
                        </div>
                    `;
                });
            }
        }

        function savePrices() {
            document.querySelectorAll('.price-input').forEach(input => {
                const code = input.getAttribute('data-code');
                COUNTRY_DATA[code].prices[currentItem] = parseFloat(input.value) || COUNTRY_DATA[code].prices[currentItem];
            });
            toggleEditMode();
            render();
        }

        let bgmPlaying = false, bgmLoaded = false, bgmEventAttached = false;
        const BGM_LOOP_START = 0, BGM_LOOP_END = 30;

        function attachBGMEvents(audio) {
            if (bgmEventAttached) return;
            bgmEventAttached = true;
            audio.addEventListener("loadedmetadata", () => { try { audio.currentTime = BGM_LOOP_START; } catch (e) {} });
            audio.addEventListener("timeupdate", () => {
                if (bgmPlaying && audio.currentTime >= BGM_LOOP_END) {
                    audio.currentTime = BGM_LOOP_START;
                    audio.play().catch(() => {});
                }
            });
            audio.addEventListener("ended", () => {
                if (bgmPlaying) {
                    audio.currentTime = BGM_LOOP_START;
                    audio.play().catch(() => {});
                }
            });
        }

        async function loadAndalusiaBGM() {
            const audio = document.getElementById('bgmAudio');
            const text = document.getElementById('bgmText');
            if (bgmLoaded && audio.src) return true;
            text.innerText = "正在连接原版小曲...";
            try {
                const res = await fetch("/deezer-preview");
                const data = await res.json();
                if (!data.ok || !data.previewUrl) throw new Error(data.error || "no preview");
                audio.src = data.previewUrl;
                audio.load();
                bgmLoaded = true;
                return true;
            } catch (e) {
                text.innerText = "小曲连接失败";
                alert("没有拿到 Deezer 的 30 秒试听源。可能是当前网络无法访问 Deezer。");
                return false;
            }
        }

        async function toggleBGM() {
            const audio = document.getElementById('bgmAudio');
            const icon = document.getElementById('bgmIcon');
            const text = document.getElementById('bgmText');
            attachBGMEvents(audio);
            if (!bgmPlaying) {
                const ok = await loadAndalusiaBGM();
                if (!ok) return;
                audio.volume = 0.48;
                try { audio.currentTime = BGM_LOOP_START; } catch (e) {}
                audio.play().then(() => {
                    bgmPlaying = true;
                    icon.innerText = "⏸";
                    text.innerText = "暂停购买力小曲";
                }).catch(() => {
                    icon.innerText = "▶";
                    text.innerText = "播放购买力小曲";
                    alert("手机浏览器限制了播放，请再点一次播放按钮。");
                });
            } else {
                audio.pause();
                bgmPlaying = false;
                icon.innerText = "▶";
                text.innerText = "播放购买力小曲";
            }
        }

        document.getElementById('baseAmount').addEventListener('input', render);
        window.onload = () => {
            if (window.lucide) lucide.createIcons();
            initTabs();
            initCountryFilter();
            render();
            syncAll(false);
        };
    </script>
</body>
</html>"""

APP_DIR = Path(__file__).resolve().parent
CACHE_FILE = APP_DIR / "purchasing_power_cache.json"
CACHE_TTL_SECONDS = 6 * 60 * 60

DEFAULT_RATES = {
    "CNY": 1, "USD": 0.138, "AUD": 0.21, "NZD": 0.23, "KRW": 188.5,
    "HKD": 1.08, "GBP": 0.11, "EUR": 0.128, "ISK": 19.2, "CAD": 0.19
}

DEFAULT_PRICES = {
    "CNY": { "rice": 8.6, "watermelon": 4.8, "burger": 25.0, "eggs": 12.0, "milk": 11.0, "napkins": 5.0 },
    "USD": { "rice": 4.80, "watermelon": 1.70, "burger": 5.69, "eggs": 4.50, "milk": 1.05, "napkins": 2.50 },
    "AUD": { "rice": 3.60, "watermelon": 3.90, "burger": 7.70, "eggs": 5.80, "milk": 1.75, "napkins": 3.20 },
    "NZD": { "rice": 5.10, "watermelon": 4.50, "burger": 8.10, "eggs": 8.50, "milk": 2.90, "napkins": 3.80 },
    "KRW": { "rice": 5400, "watermelon": 4200, "burger": 5500, "eggs": 7200, "milk": 2800, "napkins": 2500 },
    "HKD": { "rice": 15.2, "watermelon": 18.0, "burger": 24.0, "eggs": 32.0, "milk": 24.0, "napkins": 12.0 },
    "GBP": { "rice": 1.55, "watermelon": 1.60, "burger": 4.49, "eggs": 2.80, "milk": 1.15, "napkins": 1.80 },
    "EUR_DE": { "rice": 2.20, "watermelon": 1.90, "burger": 5.29, "eggs": 3.20, "milk": 1.10, "napkins": 1.70 },
    "ISK": { "rice": 520, "watermelon": 390, "burger": 990, "eggs": 850, "milk": 240, "napkins": 450 },
    "EUR_FR": { "rice": 2.40, "watermelon": 2.20, "burger": 5.40, "eggs": 3.60, "milk": 1.25, "napkins": 1.90 },
    "CAD": { "rice": 4.20, "watermelon": 2.20, "burger": 7.05, "eggs": 5.30, "milk": 2.60, "napkins": 2.80 }
}

COUNTRY_ISO_TO_CODE = {
    "CHN": "CNY", "USA": "USD", "AUS": "AUD", "NZL": "NZD", "KOR": "KRW",
    "HKG": "HKD", "GBR": "GBP", "DEU": "EUR_DE", "ISL": "ISK",
    "FRA": "EUR_FR", "CAN": "CAD"
}


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def http_json(url, timeout=10):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def http_text(url, timeout=10):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/csv,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def load_cache():
    if not CACHE_FILE.exists():
        return None
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_cache(data):
    try:
        CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def cache_is_fresh(cache):
    if not cache or "savedAtEpoch" not in cache:
        return False
    return (time.time() - float(cache.get("savedAtEpoch", 0))) < CACHE_TTL_SECONDS


def fetch_rates_primary():
    data = http_json("https://open.er-api.com/v6/latest/CNY", timeout=10)
    if data.get("result") == "success":
        return {
            "rates": normalize_rates(data.get("rates", {})),
            "source": "open.er-api.com",
            "updated": data.get("time_last_update_utc")
        }
    raise RuntimeError("open.er-api 返回失败")


def fetch_rates_backup():
    data = http_json("https://api.frankfurter.app/latest?from=CNY", timeout=10)
    rates = data.get("rates", {})
    if rates:
        # frankfurter 不一定支持所有货币，能拿多少拿多少
        normalized = {"CNY": 1}
        for k in ["USD", "AUD", "NZD", "KRW", "HKD", "GBP", "EUR", "ISK", "CAD"]:
            if k in rates:
                normalized[k] = rates[k]
        if len(normalized) > 2:
            return {
                "rates": normalized,
                "source": "frankfurter.app",
                "updated": data.get("date")
            }
    raise RuntimeError("frankfurter 返回失败")


def normalize_rates(raw_rates):
    rates = {"CNY": 1}
    for key in ["USD", "AUD", "NZD", "KRW", "HKD", "GBP", "EUR", "ISK", "CAD"]:
        if key in raw_rates:
            try:
                rates[key] = float(raw_rates[key])
            except Exception:
                pass
    return rates


def fetch_rates_stable(cache=None):
    errors = []
    for fn in [fetch_rates_primary, fetch_rates_backup]:
        try:
            result = fn()
            merged = dict(DEFAULT_RATES)
            merged.update(result["rates"])
            return merged, {
                "source": result.get("source"),
                "updated": result.get("updated"),
                "cacheUsed": False,
                "errors": errors
            }
        except Exception as e:
            errors.append(str(e))

    if cache and cache.get("rates"):
        merged = dict(DEFAULT_RATES)
        merged.update(cache["rates"])
        return merged, {
            "source": "本地缓存",
            "updated": cache.get("generatedAt"),
            "cacheUsed": True,
            "errors": errors
        }

    return dict(DEFAULT_RATES), {
        "source": "内置默认汇率",
        "updated": None,
        "cacheUsed": True,
        "errors": errors
    }


def fetch_bigmac_prices():
    urls = [
        "https://raw.githubusercontent.com/TheEconomist/big-mac-data/master/source-data/big-mac-source-data.csv",
        "https://raw.githubusercontent.com/TheEconomist/big-mac-data/master/output-data/big-mac-raw-index.csv",
    ]

    last_error = None
    for url in urls:
        try:
            text = http_text(url, timeout=12)
            rows = list(csv.DictReader(io.StringIO(text)))
            usable = []
            for row in rows:
                iso = row.get("iso_a3") or row.get("iso")
                local_price = row.get("local_price")
                date = row.get("date")
                if iso in COUNTRY_ISO_TO_CODE and local_price:
                    try:
                        usable.append((date, iso, float(local_price)))
                    except Exception:
                        pass

            if not usable:
                continue

            latest_date = sorted(set(x[0] for x in usable if x[0]))[-1]
            prices = {}
            for date, iso, price in usable:
                if date == latest_date:
                    code = COUNTRY_ISO_TO_CODE[iso]
                    prices.setdefault(code, {})["burger"] = price
            return prices, latest_date, url
        except Exception as e:
            last_error = str(e)

    raise RuntimeError(last_error or "Big Mac 数据获取失败")


def deep_merge_prices(base, update):
    result = json.loads(json.dumps(base, ensure_ascii=False))
    for code, item_prices in (update or {}).items():
        if code not in result:
            result[code] = {}
        for item, value in item_prices.items():
            try:
                value = float(value)
                if value > 0:
                    result[code][item] = value
            except Exception:
                pass
    return result


def fetch_prices_stable(cache=None):
    prices = json.loads(json.dumps(DEFAULT_PRICES, ensure_ascii=False))
    meta = {
        "source": "默认参考价 + 可用公开数据",
        "bigmacDate": None,
        "bigmacSource": None,
        "cacheUsed": False,
        "errors": []
    }

    try:
        bigmac, date, source = fetch_bigmac_prices()
        prices = deep_merge_prices(prices, bigmac)
        meta["bigmacDate"] = date
        meta["bigmacSource"] = source
    except Exception as e:
        meta["errors"].append(str(e))
        if cache and cache.get("prices"):
            cached_prices = {}
            for code, item_prices in cache["prices"].items():
                if "burger" in item_prices:
                    cached_prices.setdefault(code, {})["burger"] = item_prices["burger"]
            prices = deep_merge_prices(prices, cached_prices)
            meta["cacheUsed"] = True
            meta["source"] = "默认参考价 + 缓存 Big Mac"

    return prices, meta


def build_all_data(force=False):
    cache = load_cache()
    if (not force) and cache_is_fresh(cache):
        cache["meta"]["cacheUsed"] = True
        return cache

    rates, rates_meta = fetch_rates_stable(cache)
    prices, prices_meta = fetch_prices_stable(cache)

    data = {
        "ok": True,
        "rates": rates,
        "prices": prices,
        "generatedAt": now_iso(),
        "savedAtEpoch": time.time(),
        "meta": {
            "generatedAt": now_iso(),
            "cacheUsed": bool(rates_meta.get("cacheUsed") or prices_meta.get("cacheUsed")),
            "rates": rates_meta,
            "prices": prices_meta
        }
    }
    save_cache(data)
    return data


def fetch_deezer_preview():
    query = 'artist:"Antoine Chambe" track:"Andalusia (Filatov & Karas Remix)"'
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.deezer.com/search?q={encoded_query}&limit=15"
    data = http_json(url, timeout=10)
    results = data.get("data", [])
    if not results:
        return {"ok": False, "error": "Deezer 没有返回搜索结果"}

    def score(item):
        title = (item.get("title") or "").lower()
        title_short = (item.get("title_short") or "").lower()
        artist = (item.get("artist") or {}).get("name", "").lower()
        text = title + " " + title_short
        s = 0
        if "andalusia" in text: s += 20
        if "filatov" in text: s += 20
        if "karas" in text: s += 20
        if "remix" in text: s += 10
        if "antoine" in artist: s += 10
        return s

    results.sort(key=score, reverse=True)
    for item in results:
        preview = item.get("preview")
        if preview:
            return {
                "ok": True,
                "previewUrl": preview,
                "title": item.get("title") or item.get("title_short") or "Andalusia",
                "artist": (item.get("artist") or {}).get("name", ""),
            }
    return {"ok": False, "error": "找到了歌曲，但没有可用 previewUrl"}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.send_bytes(HTML_CONTENT.encode("utf-8"), "text/html; charset=utf-8")

        if self.path.startswith("/api/all-data"):
            force = "force=1" in self.path
            try:
                result = build_all_data(force=force)
                result["ok"] = True
            except Exception as e:
                result = {
                    "ok": True,
                    "rates": DEFAULT_RATES,
                    "prices": DEFAULT_PRICES,
                    "meta": {
                        "generatedAt": now_iso(),
                        "cacheUsed": True,
                        "rates": {"source": "内置默认汇率", "errors": [str(e)]},
                        "prices": {"source": "内置默认价格", "errors": [str(e)]}
                    }
                }
            return self.send_json(result)

        if self.path.startswith("/deezer-preview"):
            try:
                result = fetch_deezer_preview()
            except Exception as e:
                result = {"ok": False, "error": str(e)}
            return self.send_json(result)

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("404 Not Found".encode("utf-8"))

    def send_json(self, result):
        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        return self.send_bytes(body, "application/json; charset=utf-8", no_store=True)

    def send_bytes(self, body, content_type, no_store=False):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        if no_store:
            self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def find_free_port(start_port=8765):
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("没有找到可用端口，请关闭其他占用端口的程序后重试。")


def start_server():
    port = find_free_port()
    url = f"http://127.0.0.1:{port}/"

    # 启动时先尝试预热缓存，失败也不影响页面打开
    try:
        build_all_data(force=False)
    except Exception:
        pass

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print("=" * 60)
        print("全球购买力对比器 Pro Max 已启动")
        print("手机浏览器打开：")
        print(url)
        print()
        print("升级内容：")
        print("1. 多源汇率 + 缓存 + 默认值兜底。")
        print("2. 汉堡优先同步 The Economist Big Mac 数据。")
        print("3. 更美观 UI：排行、总览表、国家筛选、卡片对比。")
        print("4. 右下角继续播放购买力小曲。")
        print("=" * 60)

        def open_browser():
            time.sleep(1)
            try:
                webbrowser.open(url)
            except Exception:
                pass

        threading.Thread(target=open_browser, daemon=True).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止运行。")


if __name__ == "__main__":
    start_server()
