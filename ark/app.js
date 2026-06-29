// Application State
let appData = null;
let activeEtf = 'ARKK';
let activeTab = 'overview';
let searchQuery = '';
let sortField = 'rank';
let sortDirection = 'asc';

// Chart.js instances
const activeCharts = {
    aumChart: null,
    pieChart: null,
    detailSharesChart: null,
    detailWeightChart: null
};

// Utilities for formatting
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatCurrencyWithDecimals(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

function formatPercent(value) {
    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
}

// Fetch JSON data with cache busting
async function loadData() {
    try {
        const response = await fetch('data/processed.json?t=' + new Date().getTime());
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        appData = await response.json();
        document.getElementById('last-updated-time').textContent = appData.last_updated;
        initSelectors();
        switchEtf(appData.available_funds.includes('ARKK') ? 'ARKK' : appData.available_funds[0]);
    } catch (error) {
        console.error('Could not load processed data:', error);
        document.getElementById('last-updated-time').textContent = '載入錯誤';
        alert('無法加載數據，請確認 update_data.py 是否已經成功運行並生成 JSON 文件。');
    }
}

// Short company names helper mapping
function getShortName(ticker) {
    const names = {
        "TEM": "Tempus AI",
        "RXRX": "Recursion",
        "CRSP": "CRISPR",
        "SDGR": "Schrodinger",
        "NNOX": "Nano-X",
        "PLTR": "Palantir",
        "TSLA": "Tesla",
        "AMD": "AMD",
        "SHOP": "Shopify",
        "HOOD": "Robinhood",
        "COIN": "Coinbase",
        "NVDA": "NVIDIA",
        "LLY": "Eli Lilly",
        "VRTX": "Vertex",
        "REGN": "Regeneron",
        "NTLA": "Intellia",
        "BEAM": "Beam",
        "EXAI": "Exscientia",
        "ARM": "Arm",
        "SOUN": "SoundHound"
    };
    return names[ticker] || ticker;
}

// Initialize ETF selectors in Sidebar & Mobile Dropdown
function initSelectors() {
    const arkList = document.getElementById('etf-selector-list');
    const otherList = document.getElementById('other-selector-list');
    const mobileSelect = document.getElementById('mobile-fund-select');
    
    arkList.innerHTML = '';
    otherList.innerHTML = '';
    if (mobileSelect) mobileSelect.innerHTML = '';
    
    const arkFunds = ["ARKK", "ARKG", "ARKW", "ARKF", "ARKQ", "ARKX"];
    const otherFunds = ["NVIDIA", "IDNA", "VHT"];
    
    const displayNames = {
        "ARKK": "ARKK (Flagship 旗艦創新)",
        "ARKG": "ARKG (Genomics 基因醫學)",
        "ARKW": "ARKW (Web 下一代網路)",
        "ARKF": "ARKF (Fintech 金融科技)",
        "ARKQ": "ARKQ (Autonomous 自主與機器人)",
        "ARKX": "ARKX (space eXploration 太空探索)",
        "NVIDIA": "NVIDIA",
        "IDNA": "IDNA (BlackRock)",
        "VHT": "VHT (Vanguard)"
    };
    
    // Groups for mobile selector dropdown
    const arkGroup = document.createElement('optgroup');
    arkGroup.label = 'ARK 主動型 ETF';
    const otherGroup = document.createElement('optgroup');
    otherGroup.label = '其他頂級機構';
    
    appData.available_funds.forEach(fundId => {
        const fund = appData.funds_data[fundId];
        const item = document.createElement('li');
        item.className = `etf-item ${fundId === activeEtf ? 'active' : ''}`;
        item.dataset.etf = fundId;
        
        const dispName = displayNames[fundId] || fundId;
        
        item.innerHTML = `
            <span>${dispName}</span>
            <span class="etf-badge">${fund.holdings_count}</span>
        `;
        item.addEventListener('click', () => {
            // If in consensus tab, switch back to overview when clicking a specific fund
            if (activeTab === 'consensus-comparison') {
                changeTab('overview');
            }
            switchEtf(fundId);
        });
        
        if (arkFunds.includes(fundId)) {
            arkList.appendChild(item);
        } else if (otherFunds.includes(fundId)) {
            otherList.appendChild(item);
        }
        
        // Populate mobile dropdown options
        if (mobileSelect) {
            const option = document.createElement('option');
            option.value = fundId;
            option.textContent = dispName;
            
            if (arkFunds.includes(fundId)) {
                arkGroup.appendChild(option);
            } else if (otherFunds.includes(fundId)) {
                otherGroup.appendChild(option);
            }
        }
    });
    
    if (mobileSelect) {
        mobileSelect.appendChild(arkGroup);
        mobileSelect.appendChild(otherGroup);
        mobileSelect.value = activeEtf;
    }
}

// Switch Active ETF
function switchEtf(fundId) {
    activeEtf = fundId;
    
    // Sync mobile select
    const mobileSelect = document.getElementById('mobile-fund-select');
    if (mobileSelect) {
        mobileSelect.value = fundId;
    }
    
    // Update sidebar UI state
    document.querySelectorAll('.etf-item').forEach(item => {
        if (item.dataset.etf === fundId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    const fund = appData.funds_data[fundId];
    document.getElementById('active-etf-title').textContent = `${fundId} - ${fund.name}`;
    document.getElementById('active-etf-subtitle').textContent = `持股數據基準日：${fund.date}`;
    
    // Reset search
    document.getElementById('search-input').value = '';
    searchQuery = '';
    
    // Update stats and active panel
    updateStatsRow(fund);
    updateView();
}

// Update Stats Cards
function updateStatsRow(fund) {
    document.getElementById('stat-aum').textContent = formatCurrency(fund.aum);
    document.getElementById('stat-holdings-count').textContent = `${fund.holdings_count} 隻股票`;
    
    const buys = fund.trades_count.buys;
    const sells = fund.trades_count.sells;
    document.getElementById('stat-trades-count').textContent = `買 ${buys} / 賣 ${sells}`;
}

// Update Active Panel View
function updateView() {
    if (activeTab === 'consensus-comparison') {
        // Hide stats row and header search bar for consensus
        document.querySelector('.stats-grid').style.display = 'none';
        document.querySelector('.header-actions').style.display = 'none';
        document.getElementById('active-etf-title').textContent = '全球頂級機構 AI 醫療共識榜';
        document.getElementById('active-etf-subtitle').textContent = '對比分析 ARK Invest / NVIDIA Ventures / BlackRock IDNA / Vanguard VHT';
        
        // Remove active state from sidebar fund selectors
        document.querySelectorAll('.etf-item').forEach(item => item.classList.remove('active'));
        
        renderConsensusTab();
        return;
    }
    
    // Restore layout for normal tabs
    document.querySelector('.stats-grid').style.display = 'grid';
    document.querySelector('.header-actions').style.display = 'block';
    
    // Restore highlighted sidebar active fund
    document.querySelectorAll('.etf-item').forEach(item => {
        if (item.dataset.etf === activeEtf) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    const fund = appData.funds_data[activeEtf];
    document.getElementById('active-etf-title').textContent = `${activeEtf} - ${fund.name}`;
    document.getElementById('active-etf-subtitle').textContent = `持股數據基準日：${fund.date}`;
    
    if (activeTab === 'overview') {
        renderOverviewTab(fund);
    } else if (activeTab === 'daily-monitor') {
        renderDailyMonitorTab(fund);
    } else if (activeTab === 'streaks') {
        renderStreaksTab(fund);
    } else if (activeTab === 'weekly-summary') {
        renderWeeklySummaryTab(fund);
    }
}

// ----------------------------------------------------
// TAB RENDERING FUNCTIONS
// ----------------------------------------------------

// 1. OVERVIEW TAB
function renderOverviewTab(fund) {
    // AUM Line Chart
    renderAumChart(fund.historical_aum);
    
    // Weights Pie/Donut Chart
    renderWeightPieChart(fund.holdings);
    
    // Holdings List
    renderHoldingsTable(fund.holdings);
}

function renderAumChart(history) {
    const ctx = document.getElementById('aum-history-chart').getContext('2d');
    
    if (activeCharts.aumChart) {
        activeCharts.aumChart.destroy();
    }
    
    const labels = history.map(h => h.date.substring(5)); // MM-DD
    const values = history.map(h => h.aum / 1e6); // In Millions
    
    activeCharts.aumChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '資產總值 (百萬美元)',
                data: values,
                borderColor: '#8b5cf6',
                borderWidth: 2,
                pointBackgroundColor: '#8b5cf6',
                pointRadius: 3,
                pointHoverRadius: 6,
                backgroundColor: (context) => {
                    const chart = context.chart;
                    const {ctx, chartArea} = chart;
                    if (!chartArea) return null;
                    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.25)');
                    gradient.addColorStop(1, 'rgba(139, 92, 246, 0.00)');
                    return gradient;
                },
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `資產總值: $${context.parsed.y.toFixed(2)}M`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: { color: '#6b7280', font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#6b7280', font: { size: 10 } }
                }
            }
        }
    });
}

function renderWeightPieChart(holdings) {
    const ctx = document.getElementById('weight-pie-chart').getContext('2d');
    
    if (activeCharts.pieChart) {
        activeCharts.pieChart.destroy();
    }
    
    // Get Top 5 holdings, group others
    const sorted = [...holdings].sort((a,b) => b.weight - a.weight);
    const topHoldings = sorted.slice(0, 5);
    const othersWeight = sorted.slice(5).reduce((sum, h) => sum + h.weight, 0);
    
    const labels = topHoldings.map(h => h.ticker);
    const weights = topHoldings.map(h => h.weight);
    
    if (othersWeight > 0) {
        labels.push('其他持股');
        weights.push(othersWeight);
    }
    
    activeCharts.pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: weights,
                backgroundColor: [
                    '#8b5cf6', // Violet
                    '#a78bfa',
                    '#3b82f6', // Blue
                    '#60a5fa',
                    '#10b981', // Emerald
                    '#1e293b'  // Dark slate for others
                ],
                borderWidth: 1,
                borderColor: '#0d0f17'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 11, family: 'Outfit' },
                        boxWidth: 12
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `佔比: ${context.parsed.toFixed(2)}%`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

function renderHoldingsTable(holdings) {
    const tbody = document.getElementById('holdings-table-body');
    tbody.innerHTML = '';
    
    // Filter holdings based on search
    let filtered = holdings;
    if (searchQuery) {
        const q = searchQuery.toLowerCase();
        filtered = holdings.filter(h => 
            h.ticker.toLowerCase().includes(q) || 
            h.company.toLowerCase().includes(q)
        );
    }
    
    // Sort holdings
    filtered.sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];
        
        // Handle rank_shift special case
        if (sortField === 'rank_shift') {
            if (valA === 'NEW') valA = 999;
            if (valB === 'NEW') valB = 999;
        }
        
        if (typeof valA === 'string') {
            return sortDirection === 'asc' 
                ? valA.localeCompare(valB) 
                : valB.localeCompare(valA);
        } else {
            return sortDirection === 'asc' 
                ? valA - valB 
                : valB - valA;
        }
    });
    
    document.getElementById('holdings-list-count').textContent = filtered.length;
    
    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center" style="color: var(--text-dark); padding: 30px 0;">無符合搜尋條件的持股</td></tr>`;
        return;
    }
    
    filtered.forEach(h => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${h.rank}</td>
            <td class="ticker-cell">${h.ticker} <span class="ticker-name-sub">(${getShortName(h.ticker)})</span></td>
            <td class="company-name-cell">${h.company}</td>
            <td class="text-right">${formatNumber(h.shares)}</td>
            <td class="text-right">${formatCurrency(h.value)}</td>
            <td class="text-right weight-cell">${h.weight.toFixed(2)}%</td>
            <td class="text-center">${renderStreakBadge(h.streak)}</td>
        `;
        row.addEventListener('click', () => openDetailPanel(h));
        tbody.appendChild(row);
    });
}

function renderStreakBadge(streak) {
    if (streak > 0) {
        return `<span class="streak-badge fire"><i class="fa-solid fa-fire"></i> 連買 ${streak} 天</span>`;
    } else if (streak < 0) {
        return `<span class="streak-badge freeze"><i class="fa-solid fa-snowflake"></i> 連賣 ${Math.abs(streak)} 天</span>`;
    } else {
        return `<span style="color: var(--text-dark); font-size:12px;">無</span>`;
    }
}

// 2. DAILY MONITOR TAB
function renderDailyMonitorTab(fund) {
    // Trades list
    const tradesBody = document.getElementById('daily-trades-body');
    tradesBody.innerHTML = '';
    
    const activeTrades = fund.recent_trades;
    
    if (activeTrades.length === 0) {
        tradesBody.innerHTML = `<tr><td colspan="6" class="text-center" style="color: var(--text-dark); padding: 30px 0;">今日無任何持股數量變動。</td></tr>`;
    } else {
        activeTrades.forEach(t => {
            const row = document.createElement('tr');
            const pctText = t.shares_diff_pct !== null ? formatPercent(t.shares_diff_pct) : 'NEW';
            const badgeClass = t.shares_diff > 0 ? 'buy' : 'sell';
            const diffText = (t.shares_diff > 0 ? '+' : '') + formatNumber(t.shares_diff);
            
            row.innerHTML = `
                <td class="ticker-cell">${t.ticker} <span class="ticker-name-sub">(${getShortName(t.ticker)})</span></td>
                <td class="company-name-cell">${t.company}</td>
                <td class="text-right font-semibold ${t.shares_diff > 0 ? 'text-green' : 'text-red'}">${diffText}</td>
                <td class="text-right"><span class="badge ${badgeClass}">${pctText}</span></td>
                <td class="text-right weight-cell">${t.weight.toFixed(2)}%</td>
                <td class="text-center">${renderStreakBadge(t.streak)}</td>
            `;
            row.addEventListener('click', () => openDetailPanel(t));
            tradesBody.appendChild(row);
        });
    }
    
    // Top 10 Shifts List
    const shiftsBody = document.getElementById('top10-shifts-body');
    shiftsBody.innerHTML = '';
    
    const top10 = fund.holdings.slice(0, 10);
    top10.forEach((h, idx) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center font-bold">${h.rank}</td>
            <td class="ticker-cell">${h.ticker} <span class="ticker-name-sub">(${getShortName(h.ticker)})</span></td>
            <td class="weight-cell">${h.weight.toFixed(2)}%</td>
            <td class="text-center">${renderRankShiftBadge(h.rank_shift)}</td>
            <td class="text-right ${h.shares_diff > 0 ? 'text-green' : (h.shares_diff < 0 ? 'text-red' : 'text-muted')}">
                ${h.shares_diff !== 0 ? (h.shares_diff > 0 ? '+' : '') + formatNumber(h.shares_diff) : '--'}
            </td>
        `;
        row.addEventListener('click', () => openDetailPanel(h));
        shiftsBody.appendChild(row);
    });
}

function renderRankShiftBadge(shift) {
    if (shift === 'NEW') {
        return `<span class="badge rank-new">新進</span>`;
    } else if (shift > 0) {
        return `<span class="badge rank-up"><i class="fa-solid fa-caret-up"></i> ${shift}</span>`;
    } else if (shift < 0) {
        return `<span class="badge rank-down"><i class="fa-solid fa-caret-down"></i> ${Math.abs(shift)}</span>`;
    } else {
        return `<span style="color: var(--text-dark);">--</span>`;
    }
}

// 3. STREAKS TAB
function renderStreaksTab(fund) {
    const buysList = document.getElementById('accumulation-streaks-list');
    const sellsList = document.getElementById('distribution-streaks-list');
    
    buysList.innerHTML = '';
    sellsList.innerHTML = '';
    
    const buys = fund.streaks.buying;
    const sells = fund.streaks.selling;
    
    if (buys.length === 0) {
        buysList.innerHTML = `<div class="text-center" style="color: var(--text-dark); padding: 30px 0;">無連續買入交易</div>`;
    } else {
        buys.forEach(item => {
            const div = document.createElement('div');
            div.className = 'streak-item';
            div.innerHTML = `
                <div class="streak-info-left">
                    <span class="streak-ticker">${item.ticker} <span class="ticker-name-sub" style="font-weight:normal; font-size:11px;">(${getShortName(item.ticker)})</span></span>
                    <span class="streak-company">${item.company}</span>
                </div>
                <div class="streak-val-right">
                    <span>${item.streak} 天</span>
                </div>
            `;
            // Find holding object to open detail panel on click
            const h = fund.holdings.find(x => x.ticker === item.ticker);
            div.addEventListener('click', () => openDetailPanel(h));
            buysList.appendChild(div);
        });
    }
    
    if (sells.length === 0) {
        sellsList.innerHTML = `<div class="text-center" style="color: var(--text-dark); padding: 30px 0;">無連續賣出交易</div>`;
    } else {
        sells.forEach(item => {
            const div = document.createElement('div');
            div.className = 'streak-item';
            div.innerHTML = `
                <div class="streak-info-left">
                    <span class="streak-ticker">${item.ticker} <span class="ticker-name-sub" style="font-weight:normal; font-size:11px;">(${getShortName(item.ticker)})</span></span>
                    <span class="streak-company">${item.company}</span>
                </div>
                <div class="streak-val-right">
                    <span>${Math.abs(item.streak)} 天</span>
                </div>
            `;
            const h = fund.holdings.find(x => x.ticker === item.ticker);
            div.addEventListener('click', () => openDetailPanel(h));
            sellsList.appendChild(div);
        });
    }
}

// 4. WEEKLY SUMMARY TAB
function renderWeeklySummaryTab(fund) {
    const digest = fund.weekly_digest;
    
    document.getElementById('weekly-digest-period').textContent = `基準期：${digest.base_date} 至 ${digest.today_date}`;
    document.getElementById('weekly-narrative-text').innerHTML = `<p>${digest.narrative}</p>`;
    
    // New additions
    const newAddList = document.getElementById('weekly-new-additions');
    newAddList.innerHTML = '';
    if (digest.new_additions.length === 0) {
        newAddList.innerHTML = `<li class="text-muted">無新進持股</li>`;
    } else {
        digest.new_additions.forEach(a => {
            newAddList.innerHTML += `<li><span class="digest-list-item-ticker">${a.ticker}</span><span class="digest-list-item-val text-green">${a.weight.toFixed(2)}%</span></li>`;
        });
    }
    
    // Exits
    const exitsList = document.getElementById('weekly-exits');
    exitsList.innerHTML = '';
    if (digest.exits.length === 0) {
        exitsList.innerHTML = `<li class="text-muted">無清倉持股</li>`;
    } else {
        digest.exits.forEach(e => {
            exitsList.innerHTML += `<li><span class="digest-list-item-ticker">${e.ticker}</span><span class="digest-list-item-val text-red">已清倉</span></li>`;
        });
    }
    
    // Accumulations (Weekly)
    const accList = document.getElementById('weekly-top-accumulations');
    accList.innerHTML = '';
    if (digest.accumulations.length === 0) {
        accList.innerHTML = `<li class="text-muted">無顯著加倉</li>`;
    } else {
        digest.accumulations.slice(0, 5).forEach(a => {
            accList.innerHTML += `<li><span class="digest-list-item-ticker">${a.ticker}</span><span class="digest-list-item-val text-green">+${a.pct_change}%</span></li>`;
        });
    }
    
    // Distributions (Weekly)
    const distList = document.getElementById('weekly-top-distributions');
    distList.innerHTML = '';
    if (digest.distributions.length === 0) {
        distList.innerHTML = `<li class="text-muted">無顯著減持</li>`;
    } else {
        digest.distributions.slice(0, 5).forEach(d => {
            distList.innerHTML += `<li><span class="digest-list-item-ticker">${d.ticker}</span><span class="digest-list-item-val text-red">${d.pct_change}%</span></li>`;
        });
    }
}

// ----------------------------------------------------
// SLIDE-OUT DETAIL DRAWER RENDERING
// ----------------------------------------------------

function openDetailPanel(holding) {
    document.getElementById('detail-ticker').textContent = `${holding.ticker} (${getShortName(holding.ticker)})`;
    document.getElementById('detail-company').textContent = holding.company;
    document.getElementById('detail-shares').textContent = formatNumber(holding.shares);
    document.getElementById('detail-value').textContent = formatCurrency(holding.value);
    document.getElementById('detail-weight').textContent = `${holding.weight.toFixed(2)}%`;
    document.getElementById('detail-rank').textContent = `#${holding.rank}`;
    
    // Destroy previous detail charts
    if (activeCharts.detailSharesChart) activeCharts.detailSharesChart.destroy();
    if (activeCharts.detailWeightChart) activeCharts.detailWeightChart.destroy();
    
    // Create Detail Charts
    const trendDates = holding.trend.map(t => t.date.substring(5)); // MM-DD
    const trendShares = holding.trend.map(t => t.shares);
    const trendWeights = holding.trend.map(t => t.weight);
    
    // Shares Chart
    const ctxShares = document.getElementById('detail-shares-chart').getContext('2d');
    activeCharts.detailSharesChart = new Chart(ctxShares, {
        type: 'line',
        data: {
            labels: trendDates,
            datasets: [{
                label: '持有股數',
                data: trendShares,
                borderColor: '#3b82f6',
                borderWidth: 2,
                backgroundColor: 'rgba(59, 130, 246, 0.05)',
                fill: true,
                pointRadius: 2,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.02)' }, ticks: { color: '#6b7280', font: { size: 9 } } },
                x: { grid: { display: false }, ticks: { color: '#6b7280', font: { size: 9 } } }
            }
        }
    });
    
    // Weight Chart
    const ctxWeight = document.getElementById('detail-weight-chart').getContext('2d');
    activeCharts.detailWeightChart = new Chart(ctxWeight, {
        type: 'line',
        data: {
            labels: trendDates,
            datasets: [{
                label: '權重 (%)',
                data: trendWeights,
                borderColor: '#10b981',
                borderWidth: 2,
                backgroundColor: 'rgba(16, 185, 129, 0.05)',
                fill: true,
                pointRadius: 2,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.02)' }, ticks: { color: '#6b7280', font: { size: 9 } } },
                x: { grid: { display: false }, ticks: { color: '#6b7280', font: { size: 9 } } }
            }
        }
    });
    
    // Open drawer
    document.getElementById('detail-panel').classList.add('open');
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('open');
}

// Global Tab Switching Synchronizer (Desktop & Mobile)
function changeTab(targetTab) {
    activeTab = targetTab;
    
    // Update desktop tabs active state
    document.querySelectorAll('.nav-tab').forEach(t => {
        if (t.dataset.tab === targetTab) t.classList.add('active');
        else t.classList.remove('active');
    });
    
    // Update mobile tabs active state
    document.querySelectorAll('.mobile-nav-tab').forEach(t => {
        if (t.dataset.tab === targetTab) t.classList.add('active');
        else t.classList.remove('active');
    });
    
    // Toggle active panes
    document.querySelectorAll('.tab-pane').forEach(p => {
        if (p.id === `${targetTab}-pane`) {
            p.classList.add('active');
        } else {
            p.classList.remove('active');
        }
    });
    
    updateView();
}

// ----------------------------------------------------
// EVENT LISTENERS & SETUP
// ----------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    
    // Tab switching (Desktop list triggers)
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            changeTab(tab.dataset.tab);
        });
    });
    
    // Tab switching (Mobile horizontal swiper triggers)
    document.querySelectorAll('.mobile-nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            changeTab(tab.dataset.tab);
        });
    });
    
    // Mobile ETF Dropdown Switcher
    const mobSelectEl = document.getElementById('mobile-fund-select');
    if (mobSelectEl) {
        mobSelectEl.addEventListener('change', (e) => {
            if (activeTab === 'consensus-comparison') {
                changeTab('overview');
            }
            switchEtf(e.target.value);
        });
    }
    
    // Search functionality
    document.getElementById('search-input').addEventListener('input', (e) => {
        searchQuery = e.target.value;
        if (activeTab === 'overview') {
            const fund = appData.funds_data[activeEtf];
            renderHoldingsTable(fund.holdings);
        }
    });
    
    // Table Sorting
    document.querySelectorAll('#holdings-table th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.dataset.sort;
            
            // Determine sorting direction
            if (sortField === field) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                sortField = field;
                sortDirection = 'desc'; // Default to desc for values
                if (field === 'rank' || field === 'ticker' || field === 'company') {
                    sortDirection = 'asc'; // Default to asc for strings/rank
                }
            }
            
            // Reset header icons
            document.querySelectorAll('#holdings-table th i').forEach(icon => {
                icon.className = 'fa-solid fa-sort';
            });
            
            // Update icon for sorted field
            const icon = th.querySelector('i');
            icon.className = `fa-solid fa-sort-${sortDirection === 'asc' ? 'up' : 'down'}`;
            
            const fund = appData.funds_data[activeEtf];
            renderHoldingsTable(fund.holdings);
        });
    });
    
    // Close Drawer panel click triggers
    document.getElementById('close-panel-btn').addEventListener('click', closeDetailPanel);
    
    // Close drawer when pressing Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDetailPanel();
        }
    });
});

// 5. CONSENSUS COMPARISON TAB
function renderConsensusTab() {
    const tbody = document.getElementById('consensus-table-body');
    tbody.innerHTML = '';
    
    const consensus = appData.consensus_data;
    
    // Sort consensus by score descending, then total value descending
    const sorted = [...consensus].sort((a, b) => {
        if (b.consensus_score !== a.consensus_score) {
            return b.consensus_score - a.consensus_score;
        }
        return b.total_value - a.total_value;
    });
    
    sorted.forEach(c => {
        const row = document.createElement('tr');
        
        const arkInfo = c.funds.ARK;
        const nvInfo = c.funds.NVIDIA;
        const brInfo = c.funds.BlackRock;
        const vgInfo = c.funds.Vanguard;
        
        const arkText = arkInfo.owned ? `${arkInfo.weight.toFixed(1)}%` : '--';
        const nvText = nvInfo.owned ? `${nvInfo.weight.toFixed(1)}%` : '--';
        const brText = brInfo.owned ? `${brInfo.weight.toFixed(1)}%` : '--';
        const vgText = vgInfo.owned ? `${vgInfo.weight.toFixed(1)}%` : '--';
        
        let stars = '';
        for (let i = 0; i < 4; i++) {
            if (i < c.consensus_score) {
                stars += '<i class="fa-solid fa-star" style="color: #fbbf24; margin: 0 1px; font-size: 11px;"></i>';
            } else {
                stars += '<i class="fa-regular fa-star" style="color: var(--text-dark); margin: 0 1px; font-size: 11px;"></i>';
            }
        }
        
        row.innerHTML = `
            <td class="ticker-cell">${c.ticker} <span class="ticker-name-sub">(${getShortName(c.ticker)})</span></td>
            <td>
                <div style="font-weight:600; color:#fff;">${c.company}</div>
                <div style="font-size:11px; color:var(--text-dark); margin-top:2px; line-height:1.4;">${c.description}</div>
            </td>
            <td style="font-weight:500;">${c.sector}</td>
            <td class="text-center" style="white-space: nowrap;">
                <div style="font-weight:700; color:#fff; font-size:13px; margin-bottom:4px;">${c.consensus_score} / 4</div>
                <div>${stars}</div>
            </td>
            <td class="text-center ${arkInfo.owned ? 'text-green font-semibold' : 'text-muted'}">${arkText}</td>
            <td class="text-center ${nvInfo.owned ? 'text-green font-semibold' : 'text-muted'}">${nvText}</td>
            <td class="text-center ${brInfo.owned ? 'text-green font-semibold' : 'text-muted'}">${brText}</td>
            <td class="text-center ${vgInfo.owned ? 'text-green font-semibold' : 'text-muted'}">${vgText}</td>
            <td class="text-center">
                <span class="badge ${c.collective_action.includes('加碼') || c.collective_action.includes('買入') ? 'buy' : (c.collective_action.includes('減持') || c.collective_action.includes('調節') ? 'sell' : 'rank-new')}">
                    ${c.collective_action}
                </span>
            </td>
        `;
        
        row.addEventListener('click', () => {
            let holdingObj = null;
            // Seek this stock's details in ARKG first (main medical ETF), then other funds
            const order_to_seek = ["ARKG", "ARKK", "IDNA", "VHT", "NVIDIA"];
            for (let fId of order_to_seek) {
                const fData = appData.funds_data[fId];
                if (fData) {
                    const found = fData.holdings.find(x => x.ticker === c.ticker);
                    if (found) {
                        holdingObj = found;
                        break;
                    }
                }
            }
            if (holdingObj) {
                openDetailPanel(holdingObj);
            }
        });
        
        tbody.appendChild(row);
    });
}
