#!/usr/bin/env python3
"""
ARK & Top Global Funds Daily Summary Email Dispatcher
- Pure FormSubmit.co HTTP API transport (sender: submissions@formsubmit.co)
- Zero local Mail.app / AppleScript calls (completely avoids local SSL errors and popups)
- Single-field structured text payload (avoids FormSubmit field-name underscores like 1__xxx)
- Clean, high-legibility plain text typography matching Apple Mobile Mail rendering
- Export companion HTML to futienchun.com/ark/daily_digest.html
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed.json")
CONFIG_FILE = os.path.join(BASE_DIR, ".email_config.json")
DIGEST_HTML_LOCAL = os.path.join(BASE_DIR, "data", "daily_digest.html")
DIGEST_HTML_WEB = os.path.join(BASE_DIR, "..", "portfolio-website", "ark", "daily_digest.html")

KNOWN_SECTORS = {
    "TSLA": "智能电动与空间算力 (Robotaxi/FSD)",
    "TWST": "合成生物学与DNA测序高通量平台",
    "COIN": "合规加密金融与交易流动性基础设施",
    "CRCL": "稳定币与跨境链上支付结算底层",
    "META": "空间计算、开源大模型(Llama)与广告AI",
    "RKLB": "商业航天、低轨星座组网与运载发射",
    "RKLB UQ": "商业航天、低轨星座组网与运载发射",
    "NVDA": "全球AI算力基础设施核心芯片",
    "CBRS": "晶圆级超算AI集群芯片 (Cerebras)",
    "XYZ": "去中心化商业支付与移动金融生态 (Block)",
    "AVGO": "定制化AI网络ASIC与高速互联芯片",
    "NET": "全球边缘网络安全与分布式云防护",
    "AMD": "数据中心GPU与高性能异构计算",
    "TXG": "单细胞基因组学与空间生物学测序",
    "NTLA": "体内CRISPR基因编辑与罕见病疗法",
    "CRSP": "CRISPR基因编辑技术与基因疗法Casgevy",
    "GH": "肿瘤精准早筛与血液液体活检技术",
    "CDNA": "实体器官移植术后无创分子监控",
    "CMPS": "新型神经精神病学与合成致幻药研发",
    "TEM": "AI精准肿瘤医疗大数据引擎 (Tempus AI)",
    "PLTR": "企业级与国防AI大数据操作系统 (AIP)",
    "SHOP": "全球分布式独立站与跨境电商SaaS",
    "HOOD": "下一代全资产零售投资与加密网关",
    "BEAM": "单碱基精准基因编辑药物开发",
    "VCYT": "基因组诊断与恶性肿瘤鉴别检测",
    "HON": "航空航天精密航电设备与工业自动化"
}

def load_processed_data():
    if not os.path.exists(PROCESSED_FILE):
        print(f"Error: processed.json not found at {PROCESSED_FILE}")
        return None
    try:
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading processed.json: {e}")
        return None

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def generate_stock_narrative(item, is_buy=True):
    ticker = item.get("ticker", "")
    base_ticker = ticker.split(" ")[0]
    sector = KNOWN_SECTORS.get(ticker, KNOWN_SECTORS.get(base_ticker, "前沿颠覆性创新赛道"))
    company = item.get("company", ticker)
    shares_diff = item.get("shares_diff", 0)
    shares_diff_pct = item.get("shares_diff_pct", 0) or 0
    weight = item.get("weight", 0)
    streak = item.get("streak", 0)
    
    if is_buy:
        if streak >= 3:
            narrative = f"机构对 {company} 展现极高确定性，已连续 {streak} 个交易日持续净增仓。在 {sector} 景气度持续上行阶段，木头姐正逢低强化其行业定价权筹码。"
            advice = "高置信多头标的，行业基本面扎实；建议列入重点观察池，可待盘中回撤分批低吸跟投。"
            advice_tag = "逢低跟投 / 积极关注"
        elif shares_diff_pct > 15:
            narrative = f"单日增持比例高达 {shares_diff_pct:.1f}%，属于战术性突击建仓动作。主力资金借估值回调快速锁仓优质筹码，中短线进攻信号鲜明。"
            advice = "机构突击建仓，短期波动弹性加剧；建议轻仓试探，避免盲目追高，严格设好动态止损线。"
            advice_tag = "轻仓跟进 / 注意防守"
        else:
            narrative = f"主力小幅加码，当前持仓权重稳步抬升至 {weight:.2f}%。该标的在 {sector} 领域具备核心护城河，属于资产组合中的稳健核心持仓。"
            advice = "底仓稳健增持，中长线发展逻辑良好；建议长期投资者继续保持底仓并耐心持有。"
            advice_tag = "底仓持有 / 长期看好"
    else:
        abs_streak = abs(streak)
        if weight > 8.0:
            narrative = f"{company} 当前持仓权重仍高达 {weight:.2f}%。本次微幅减持主要受限于基金单一标的 10% 顶格风控红线，属于被动再平衡 (Passive Rebalance) 获利了结，中长期赛道逻辑未变。"
            advice = "规则性被动减持而非基本面恶化；中长期多头逻辑完好，无需过度恐慌杀跌。"
            advice_tag = "被动再平衡 / 无需恐慌"
        elif abs_streak >= 3 or shares_diff_pct < -8.0:
            narrative = f"主力对 {company} 展开持续性减持（连续减仓 {abs_streak} 天），持仓敞口显著收缩。在 {sector} 行业研发周期或资金成本压力下，机构选择战略性回收流动性。"
            advice = "主力持续离场信号明确，短期承压动能较强；建议逢反弹减持多头头寸，暂不建议盲目抄底。"
            advice_tag = "反弹离场 / 暂不抄底"
        else:
            narrative = f"单日小额获利减持，仓位占比微调至 {weight:.2f}%。在近期股价上行后释放部分浮盈，属于常规仓位管理操作。"
            advice = "技术性小幅锁定利润，整体趋势中性偏多；已有盈利持仓可适当分批止盈，保留核心底仓。"
            advice_tag = "适度止盈 / 观察支撑"
            
    return sector, narrative, advice, advice_tag

def extract_market_intelligence(data):
    funds = data.get("funds_data", {})
    all_buys = []
    all_sells = []
    
    for fid, fund in funds.items():
        if not fid.startswith("ARK"):
            continue
        trades = fund.get("recent_trades", [])
        for t in trades:
            item = dict(t)
            item["fund"] = fid
            shares = item.get("shares", 0)
            value = item.get("value", 0)
            item["price"] = (value / shares) if (shares and value) else 0.0
            
            s_diff = item.get("shares_diff", 0)
            if s_diff > 0:
                all_buys.append(item)
            elif s_diff < 0:
                all_sells.append(item)
                
    top_buys_raw = sorted(all_buys, key=lambda x: abs(x.get("value_diff", 0)), reverse=True)[:5]
    top_sells_raw = sorted(all_sells, key=lambda x: abs(x.get("value_diff", 0)), reverse=True)[:5]
    
    top_buys = []
    for b in top_buys_raw:
        sec, nar, adv, tag = generate_stock_narrative(b, is_buy=True)
        b["sector"] = sec
        b["narrative"] = nar
        b["advice"] = adv
        b["advice_tag"] = tag
        top_buys.append(b)
        
    top_sells = []
    for s in top_sells_raw:
        sec, nar, adv, tag = generate_stock_narrative(s, is_buy=False)
        s["sector"] = sec
        s["narrative"] = nar
        s["advice"] = adv
        s["advice_tag"] = tag
        top_sells.append(s)

    streak_buys = []
    streak_sells = []
    for fid, fund in funds.items():
        if not fid.startswith("ARK"):
            continue
        holdings_map = {h["ticker"]: h for h in fund.get("holdings", [])}
        streaks = fund.get("streaks", {})
        
        for item in streaks.get("buying", []):
            it = dict(item)
            it["fund"] = fid
            h = holdings_map.get(it["ticker"], {})
            it["shares"] = h.get("shares", 0)
            it["price"] = (h.get("value", 0) / h.get("shares", 1)) if h.get("shares") else 0.0
            it["weight_diff"] = h.get("weight_diff", 0)
            it["shares_diff"] = h.get("shares_diff", 0)
            it["shares_diff_pct"] = h.get("shares_diff_pct", 0)
            sec, nar, adv, tag = generate_stock_narrative(it, is_buy=True)
            it["sector"] = sec
            it["narrative"] = nar
            it["advice"] = adv
            it["advice_tag"] = tag
            streak_buys.append(it)
            
        for item in streaks.get("selling", []):
            it = dict(item)
            it["fund"] = fid
            h = holdings_map.get(it["ticker"], {})
            it["shares"] = h.get("shares", 0)
            it["price"] = (h.get("value", 0) / h.get("shares", 1)) if h.get("shares") else 0.0
            it["weight_diff"] = h.get("weight_diff", 0)
            it["shares_diff"] = h.get("shares_diff", 0)
            it["shares_diff_pct"] = h.get("shares_diff_pct", 0)
            sec, nar, adv, tag = generate_stock_narrative(it, is_buy=False)
            it["sector"] = sec
            it["narrative"] = nar
            it["advice"] = adv
            it["advice_tag"] = tag
            streak_sells.append(it)

    top_streak_buys = sorted(streak_buys, key=lambda x: (x.get("streak", 0), x.get("weight", 0)), reverse=True)[:5]
    top_streak_sells = sorted(streak_sells, key=lambda x: (abs(x.get("streak", 0)), x.get("weight", 0)), reverse=True)[:5]

    return {
        "top_buys": top_buys,
        "top_sells": top_sells,
        "streak_buys": top_streak_buys,
        "streak_sells": top_streak_sells
    }

def build_apple_style_html_report(data, intel):
    """
    Exportable companion HTML (for web view at futienchun.com/ark/daily_digest.html)
    """
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ver_stamp = datetime.now().strftime("%Y%m%d%H%M")
    top_buys = intel["top_buys"]
    top_sells = intel["top_sells"]
    streak_buys = intel["streak_buys"]
    streak_sells = intel["streak_sells"]

    html_out = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="version" content="{ver_stamp}">
<title>ARK & 全球顶尖基金持股观测日刊</title>
</head>
<body style="margin:0; padding:0; background-color:#FFFFFF; font-family:-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'PingFang SC', 'Hiragino Sans GB', 'Helvetica Neue', Arial, sans-serif; -webkit-font-smoothing:antialiased; color:#111827; line-height:1.68;">

<div style="max-width:620px; margin:0 auto; padding:24px 18px 48px 18px;">

  <!-- Header -->
  <div style="border-bottom:2px solid #111827; padding-bottom:14px; margin-bottom:26px;">
    <div style="font-size:11px; font-weight:700; color:#4B5563; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
      ARK & TOP GLOBAL FUNDS DAILY DIGEST
    </div>
    <h1 style="font-size:22px; font-weight:800; color:#111827; margin:0 0 6px 0; line-height:1.3; letter-spacing:-0.4px;">
      ARK & 全球顶尖基金持股观测日刊
    </h1>
    <div style="font-size:13px; color:#6B7280;">
      数据基准时间：{date_str} · 美股收盘持仓监控
    </div>
  </div>
'''

    # Section 1: Buys
    html_out += '''
  <div style="margin-bottom:34px;">
    <h2 style="font-size:18px; font-weight:800; color:#111827; margin:0 0 18px 0; line-height:1.35; letter-spacing:-0.2px;">
      1. 核心买入榜 | 机构重拳建仓与增持 Top 5 深度透视
    </h2>
'''
    for idx, b in enumerate(top_buys, 1):
        streak_str = f"连买 {b.get('streak')} 天" if b.get('streak', 0) > 1 else "单日加仓"
        html_out += f'''
    <div style="margin-bottom:22px; padding-bottom:18px; border-bottom:1px solid #F1F5F9;">
      <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:6px; line-height:1.4;">
        #{idx} [{b['fund']}] {b['ticker']} · {b['company']}
        <span style="display:inline-block; background:#DCFCE7; color:#15803D; font-size:11px; font-weight:700; padding:2px 7px; border-radius:4px; margin-left:6px; vertical-align:middle;">买入 {b.get('shares_diff_pct', 0):+.2f}%</span>
      </div>
      <div style="font-size:13px; color:#4B5563; margin-bottom:8px; line-height:1.55;">
        • 变动股数：<strong style="color:#111827;">{b['shares_diff']:+,d} 股</strong> (总持股: <strong style="color:#111827;">{b.get('shares', 0):,} 股</strong>)<br>
        • 最新单价：<strong style="color:#111827;">${b['price']:.2f} USD</strong> | 增持市值：<strong style="color:#15803D;">+${abs(b.get('value_diff', 0))/1e6:.2f}M USD</strong><br>
        • 持仓权重：<strong style="color:#111827;">{b.get('weight', 0):.2f}%</strong> (日偏离 <strong style="color:#111827;">{b.get('weight_diff', 0):+.2f}%</strong>) | 状态：<strong style="color:#2563EB;">{streak_str}</strong>
      </div>
      <div style="font-size:14.5px; color:#374151; line-height:1.68; margin-bottom:10px;">
        {b['narrative']}
      </div>
      <div style="background:#F0FDF4; border-left:3px solid #16A34A; border-radius:2px; padding:9px 12px; font-size:13px; color:#14532D; margin-bottom:8px; line-height:1.55;">
        <strong>💡 建议参考 [{b['advice_tag']}]</strong>：{b['advice']}
      </div>
      <div>
        <span style="display:inline-block; background:#F3F4F6; color:#6B7280; font-size:11px; padding:3px 9px; border-radius:9999px;">来源 ARK官方持仓 · 赛道: {b['sector']}</span>
      </div>
    </div>
'''
    html_out += "  </div>\n"

    # Section 2: Sells
    html_out += '''
  <div style="margin-bottom:34px;">
    <h2 style="font-size:18px; font-weight:800; color:#111827; margin:0 0 18px 0; line-height:1.35; letter-spacing:-0.2px;">
      2. 核心卖出榜 | 资金减持与获利防御 Top 5 深度透视
    </h2>
'''
    for idx, s in enumerate(top_sells, 1):
        abs_streak = abs(s.get('streak', 0))
        streak_str = f"连卖 {abs_streak} 天" if abs_streak > 1 else "单日减持"
        html_out += f'''
    <div style="margin-bottom:22px; padding-bottom:18px; border-bottom:1px solid #F1F5F9;">
      <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:6px; line-height:1.4;">
        #{idx} [{s['fund']}] {s['ticker']} · {s['company']}
        <span style="display:inline-block; background:#FEE2E2; color:#B91C1C; font-size:11px; font-weight:700; padding:2px 7px; border-radius:4px; margin-left:6px; vertical-align:middle;">减持 {s.get('shares_diff_pct', 0):.2f}%</span>
      </div>
      <div style="font-size:13px; color:#4B5563; margin-bottom:8px; line-height:1.55;">
        • 变动股数：<strong style="color:#111827;">{s['shares_diff']:+,d} 股</strong> (总持股: <strong style="color:#111827;">{s.get('shares', 0):,} 股</strong>)<br>
        • 最新单价：<strong style="color:#111827;">${s['price']:.2f} USD</strong> | 减持市值：<strong style="color:#B91C1C;">-${abs(s.get('value_diff', 0))/1e6:.2f}M USD</strong><br>
        • 持仓权重：<strong style="color:#111827;">{s.get('weight', 0):.2f}%</strong> (日偏离 <strong style="color:#111827;">{s.get('weight_diff', 0):+.2f}%</strong>) | 状态：<strong style="color:#EA580C;">{streak_str}</strong>
      </div>
      <div style="font-size:14.5px; color:#374151; line-height:1.68; margin-bottom:10px;">
        {s['narrative']}
      </div>
      <div style="background:#FEF2F2; border-left:3px solid #DC2626; border-radius:2px; padding:9px 12px; font-size:13px; color:#7F1D1D; margin-bottom:8px; line-height:1.55;">
        <strong>⚠️ 建议参考 [{s['advice_tag']}]</strong>：{s['advice']}
      </div>
      <div>
        <span style="display:inline-block; background:#F3F4F6; color:#6B7280; font-size:11px; padding:3px 9px; border-radius:9999px;">来源 ARK官方持仓 · 赛道: {s['sector']}</span>
      </div>
    </div>
'''
    html_out += "  </div>\n"

    # Section 3: Buying Streaks
    if streak_buys:
        html_out += '''
  <div style="margin-bottom:34px;">
    <h2 style="font-size:18px; font-weight:800; color:#111827; margin:0 0 18px 0; line-height:1.35; letter-spacing:-0.2px;">
      3. 持续加仓追踪 | 机构高置信连买异动监控
    </h2>
'''
        for idx, sb in enumerate(streak_buys, 1):
            html_out += f'''
    <div style="margin-bottom:22px; padding-bottom:18px; border-bottom:1px solid #F1F5F9;">
      <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:6px; line-height:1.4;">
        #{idx} [{sb['fund']}] {sb['ticker']} · {sb['company']}
        <span style="display:inline-block; background:#EFF6FF; color:#1D4ED8; font-size:11px; font-weight:700; padding:2px 7px; border-radius:4px; margin-left:6px; vertical-align:middle;">连买 {sb['streak']} 天</span>
      </div>
      <div style="font-size:13px; color:#4B5563; margin-bottom:8px; line-height:1.55;">
        • 持仓总量：<strong style="color:#111827;">{sb.get('shares', 0):,} 股</strong> | 最新单价：<strong style="color:#111827;">${sb.get('price', 0):.2f} USD</strong><br>
        • 持仓权重：<strong style="color:#111827;">{sb.get('weight', 0):.2f}%</strong> | 赛道：<strong style="color:#4B5563;">{sb['sector']}</strong>
      </div>
      <div style="font-size:14.5px; color:#374151; line-height:1.68; margin-bottom:10px;">
        {sb['narrative']}
      </div>
      <div style="background:#EFF6FF; border-left:3px solid #2563EB; border-radius:2px; padding:9px 12px; font-size:13px; color:#1E3A8A; margin-bottom:8px; line-height:1.55;">
        <strong>💡 建议参考 [{sb['advice_tag']}]</strong>：{sb['advice']}
      </div>
      <div>
        <span style="display:inline-block; background:#F3F4F6; color:#6B7280; font-size:11px; padding:3px 9px; border-radius:9999px;">连续加仓 {sb['streak']} 个交易日 · 机构持续建仓</span>
      </div>
    </div>
'''
        html_out += "  </div>\n"

    # Section 4: Selling Streaks
    if streak_sells:
        html_out += '''
  <div style="margin-bottom:34px;">
    <h2 style="font-size:18px; font-weight:800; color:#111827; margin:0 0 18px 0; line-height:1.35; letter-spacing:-0.2px;">
      4. 持续减仓预警 | 资金撤离与防御收缩监控
    </h2>
'''
        for idx, ss in enumerate(streak_sells, 1):
            abs_days = abs(ss['streak'])
            html_out += f'''
    <div style="margin-bottom:22px; padding-bottom:18px; border-bottom:1px solid #F1F5F9;">
      <div style="font-size:16px; font-weight:700; color:#111827; margin-bottom:6px; line-height:1.4;">
        #{idx} [{ss['fund']}] {ss['ticker']} · {ss['company']}
        <span style="display:inline-block; background:#FFF7ED; color:#C2410C; font-size:11px; font-weight:700; padding:2px 7px; border-radius:4px; margin-left:6px; vertical-align:middle;">连卖 {abs_days} 天</span>
      </div>
      <div style="font-size:13px; color:#4B5563; margin-bottom:8px; line-height:1.55;">
        • 剩余持股：<strong style="color:#111827;">{ss.get('shares', 0):,} 股</strong> | 最新单价：<strong style="color:#111827;">${ss.get('price', 0):.2f} USD</strong><br>
        • 持仓权重：<strong style="color:#111827;">{ss.get('weight', 0):.2f}%</strong> | 赛道：<strong style="color:#4B5563;">{ss['sector']}</strong>
      </div>
      <div style="font-size:14.5px; color:#374151; line-height:1.68; margin-bottom:10px;">
        {ss['narrative']}
      </div>
      <div style="background:#FFF7ED; border-left:3px solid #EA580C; border-radius:2px; padding:9px 12px; font-size:13px; color:#7C2D12; margin-bottom:8px; line-height:1.55;">
        <strong>⚠️ 建议参考 [{ss['advice_tag']}]</strong>：{ss['advice']}
      </div>
      <div>
        <span style="display:inline-block; background:#F3F4F6; color:#6B7280; font-size:11px; padding:3px 9px; border-radius:9999px;">连续减持 {abs_days} 个交易日 · 警惕抛压风险</span>
      </div>
    </div>
'''
        html_out += "  </div>\n"

    # Section 5: Sector Shifts
    html_out += '''
  <div style="margin-bottom:34px;">
    <h2 style="font-size:18px; font-weight:800; color:#111827; margin:0 0 18px 0; line-height:1.35; letter-spacing:-0.2px;">
      5. 资金流向与板块轮动深度解读
    </h2>
'''
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            html_out += f'''
    <div style="margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid #F1F5F9;">
      <div style="font-size:15px; font-weight:700; color:#111827; margin-bottom:4px;">
        ■ {fund_id} ({fund['name']})
      </div>
      <div style="font-size:13px; color:#4B5563; margin-bottom:6px;">
        规模变动: <strong style="color:#111827;">{aum_change}</strong> | 净现金流: <strong style="color:#111827;">${analysis['net_cash_flow']:+,.2f} USD</strong> | 前十大集中度: <strong style="color:#111827;">{analysis['concentration_today']}%</strong> ({conc_diff})
      </div>
      <div style="font-size:14px; color:#374151; line-height:1.65;">
        {analysis['narrative']}
      </div>
    </div>
'''
    html_out += '''
  </div>

  <!-- Footer -->
  <div style="border-top:1px solid #E5E7EB; margin-top:36px; padding-top:16px; font-size:12px; color:#9CA3AF; text-align:center; line-height:1.6;">
    ARK & 全球顶尖基金持股观测看板 · 自动化智能投研简报<br>
    线上看板: <a href="https://futienchun.com/ark/" style="color:#2563EB; text-decoration:none;">https://futienchun.com/ark/</a>
  </div>

</div>
</body>
</html>
'''
    return html_out

def build_plain_text_report(data, intel):
    """
    Renders pure, clean, beautifully structured plain text.
    Uses consistent lines, clear spacing, zero underscores, and distinct section breaks.
    """
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ver_stamp = datetime.now().strftime("%Y%m%d%H%M")
    top_buys = intel["top_buys"]
    top_sells = intel["top_sells"]
    streak_buys = intel["streak_buys"]
    streak_sells = intel["streak_sells"]

    report = "=====================================================\n"
    report += "ARK & 全球顶尖基金持股观测日刊\n"
    report += f"数据基准时间：{date_str} (美股收盘监控)\n"
    report += f"📱 高清图文阅读器: https://futienchun.com/ark/daily_digest.html?v={ver_stamp}\n"
    report += "=====================================================\n\n"

    # 1. Top 5 Buys
    report += "【1. 核心买入榜 | 机构增持 Top 5 深度透视】\n"
    report += "─────────────────────────────────────────────────────\n"
    for idx, b in enumerate(top_buys, 1):
        streak_str = f"连买 {b.get('streak')} 天" if b.get('streak', 0) > 1 else "单日加仓"
        report += f"#{idx} [{b['fund']}] {b['ticker']} · {b['company']}  [买入 {b.get('shares_diff_pct', 0):+.2f}%]\n"
        report += f"  • 变动股数: {b['shares_diff']:+,d} 股  (总持股: {b.get('shares', 0):,} 股)\n"
        report += f"  • 最新单价: ${b['price']:.2f} USD  |  增持市值: +${abs(b.get('value_diff', 0))/1e6:.2f}M USD\n"
        report += f"  • 持仓权重: {b.get('weight', 0):.2f}% (日偏离 {b.get('weight_diff', 0):+.2f}%)  |  状态: {streak_str}\n\n"
        report += f"  【深度分析说明】\n  {b['narrative']}\n\n"
        report += f"  【💡 建议参考 · {b['advice_tag']}】\n  {b['advice']}\n\n"
        report += f"  来源: ARK官方持仓 · 赛道: {b['sector']}\n"
        report += "─────────────────────────────────────────────────────\n"
    report += "\n"

    # 2. Top 5 Sells
    report += "【2. 核心卖出榜 | 资金减持 Top 5 深度透视】\n"
    report += "─────────────────────────────────────────────────────\n"
    for idx, s in enumerate(top_sells, 1):
        abs_streak = abs(s.get('streak', 0))
        streak_str = f"连卖 {abs_streak} 天" if abs_streak > 1 else "单日减持"
        report += f"#{idx} [{s['fund']}] {s['ticker']} · {s['company']}  [减持 {s.get('shares_diff_pct', 0):.2f}%]\n"
        report += f"  • 变动股数: {s['shares_diff']:+,d} 股  (总持股: {s.get('shares', 0):,} 股)\n"
        report += f"  • 最新单价: ${s['price']:.2f} USD  |  减持市值: -${abs(s.get('value_diff', 0))/1e6:.2f}M USD\n"
        report += f"  • 持仓权重: {s.get('weight', 0):.2f}% (日偏离 {s.get('weight_diff', 0):+.2f}%)  |  状态: {streak_str}\n\n"
        report += f"  【深度分析说明】\n  {s['narrative']}\n\n"
        report += f"  【⚠️ 建议参考 · {s['advice_tag']}】\n  {s['advice']}\n\n"
        report += f"  来源: ARK官方持仓 · 赛道: {s['sector']}\n"
        report += "─────────────────────────────────────────────────────\n"
    report += "\n"

    # 3. Buying Streaks
    if streak_buys:
        report += "【3. 持续加仓追踪 | 机构高置信连买异动监控】\n"
        report += "─────────────────────────────────────────────────────\n"
        for idx, sb in enumerate(streak_buys, 1):
            report += f"#{idx} [{sb['fund']}] {sb['ticker']} · {sb['company']}  [连续买进 {sb['streak']} 天]\n"
            report += f"  • 当前持股: {sb.get('shares', 0):,} 股  |  最新单价: ${sb.get('price', 0):.2f} USD\n"
            report += f"  • 持仓权重: {sb.get('weight', 0):.2f}%  |  赛道: {sb['sector']}\n\n"
            report += f"  【异动说明】\n  {sb['narrative']}\n\n"
            report += f"  【💡 建议参考 · {sb['advice_tag']}】\n  {sb['advice']}\n\n"
            report += f"  连续加仓 {sb['streak']} 个交易日 · 机构持续建仓\n"
            report += "─────────────────────────────────────────────────────\n"
        report += "\n"

    # 4. Selling Streaks
    if streak_sells:
        report += "【4. 持续减仓预警 | 资金撤离与防御收缩监控】\n"
        report += "─────────────────────────────────────────────────────\n"
        for idx, ss in enumerate(streak_sells, 1):
            abs_days = abs(ss['streak'])
            report += f"#{idx} [{ss['fund']}] {ss['ticker']} · {ss['company']}  [连续卖出 {abs_days} 天]\n"
            report += f"  • 剩余持股: {ss.get('shares', 0):,} 股  |  最新单价: ${ss.get('price', 0):.2f} USD\n"
            report += f"  • 持仓权重: {ss.get('weight', 0):.2f}%  |  赛道: {ss['sector']}\n\n"
            report += f"  【预警说明】\n  {ss['narrative']}\n\n"
            report += f"  【⚠️ 建议参考 · {ss['advice_tag']}】\n  {ss['advice']}\n\n"
            report += f"  连续减持 {abs_days} 个交易日 · 警惕抛压风险\n"
            report += "─────────────────────────────────────────────────────\n"
        report += "\n"

    # 5. Sector Shifts & Daily Rotation
    report += "【5. 资金流向与板块轮动深度解读】\n"
    report += "─────────────────────────────────────────────────────\n"
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            report += f"■ {fund_id} ({fund['name']})\n"
            report += f"  • 规模变动: {aum_change}  |  净现金流: ${analysis['net_cash_flow']:+,.2f} USD\n"
            report += f"  • 前十持仓集中度: {analysis['concentration_today']}% ({conc_diff})\n"
            report += f"  • 宏观解读: {analysis['narrative']}\n\n"

    report += "=====================================================\n"
    report += "线上看板: https://futienchun.com/ark/\n"
    report += "=====================================================\n"
    return report

def export_web_digest(html_content):
    try:
        os.makedirs(os.path.dirname(DIGEST_HTML_LOCAL), exist_ok=True)
        with open(DIGEST_HTML_LOCAL, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Exported local web digest to {DIGEST_HTML_LOCAL}")
    except Exception as e:
        print(f"Warning: Failed to export local digest: {e}")

    try:
        web_dir = os.path.dirname(DIGEST_HTML_WEB)
        if os.path.exists(web_dir):
            with open(DIGEST_HTML_WEB, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Exported website digest to {DIGEST_HTML_WEB}")
    except Exception as e:
        print(f"Warning: Failed to export website digest: {e}")

def send_via_formsubmit(subject, message_text, receiver_email):
    """
    Delivers summary report via FormSubmit.co HTTP POST API.
    Single message body parameter completely avoids FormSubmit generating underscores like 1__xxx.
    """
    url = f"https://formsubmit.co/ajax/{receiver_email}"
    data = {
        "_subject": subject,
        "每日持仓投资简报": message_text,
        "_template": "box"
    }
    payload = urllib.parse.urlencode(data).encode('utf-8')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Origin': 'https://futienchun.com',
        'Referer': 'https://futienchun.com/ark/'
    }
    req = urllib.request.Request(url, data=payload, headers=headers)
    
    max_retries = 3
    retry_delay = 10
    for attempt in range(max_retries + 1):
        try:
            print(f"Sending email report to {receiver_email} via FormSubmit HTTP API (Attempt {attempt + 1})...")
            with urllib.request.urlopen(req, timeout=20) as response:
                res = json.loads(response.read().decode('utf-8'))
                if res.get("success") == "true":
                    print("Email report sent successfully via FormSubmit (submissions@formsubmit.co)!")
                    return True
                else:
                    print(f"FormSubmit API Notice: {res.get('message')}")
                    return False
        except Exception as e:
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"All FormSubmit attempts failed: {e}")
    return False

def build_weekly_text_report(data):
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report = "=====================================================\n"
    report += "ARK & 全球顶尖基金持股观测【每周综合投资报告】\n"
    report += f"报告时间：{date_str} (周日报告)\n"
    report += "线上看板：https://futienchun.com/ark/\n"
    report += "=====================================================\n\n"
    
    arkk = data.get("funds_data", {}).get("ARKK", {})
    digest = arkk.get("weekly_digest", {})
    if digest:
        report += f"■ ARKK 旗舰基金操作摘要：{digest.get('narrative', '持股平稳')}\n\n"
        top10_forecast = digest.get("top10_8w_forecast", [])
        if top10_forecast:
            report += "【前十大持仓 8 周异动与前瞻预测】\n"
            for item in top10_forecast:
                report += f"#{item['rank']} {item['ticker']} ({item['company']}): 权重 {item['weight']:.2f}%, 动作: {item['action']}, 预测: 【{item['forecast']}】\n"
                report += f"   逻辑: {item['logic']}\n"
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Send ARK Summary Email Report")
    parser.add_argument("--weekly", action="store_true", help="Send weekly report")
    parser.add_argument("--to", type=str, default=None, help="Override recipient email")
    parser.add_argument("--export-only", action="store_true", help="Export HTML/text locally without sending email")
    args = parser.parse_args()

    data = load_processed_data()
    if not data:
        print("Skipping email: No processed data found.")
        return

    active_date = data.get("last_updated", datetime.now().strftime("%Y-%m-%d"))
    for fid in ["ARKK", "ARKG"]:
        if fid in data.get("funds_data", {}):
            active_date = data["funds_data"][fid].get("date", active_date)
            break

    is_sunday = datetime.now().weekday() == 6
    is_weekly = args.weekly or is_sunday

    config = load_config()
    receiver_email = config.get("receiver_email", "tony.tc.fu@icloud.com")
    if args.to:
        receiver_email = args.to

    # Extract intelligence & generate reports
    intel = extract_market_intelligence(data)
    html_content = build_apple_style_html_report(data, intel)
    text_content = build_plain_text_report(data, intel)

    if is_weekly:
        subject = f"ARK & 全球顶尖基金持股观测【每周综合投资报告】({active_date})"
        text_content = build_weekly_text_report(data)
    else:
        subject = f"ARK & 全球顶尖基金持股观测日刊 ({active_date})"

    # Export to static web
    export_web_digest(html_content)

    if args.export_only:
        print("Export-only mode finished successfully.")
        return

    # Strictly use FormSubmit HTTP API (submissions@formsubmit.co)
    sent = send_via_formsubmit(subject, text_content, receiver_email)

    if sent:
        print("Summary email dispatched successfully via FormSubmit.")
    else:
        print("Notice: Summary email sending completed with notice.")

if __name__ == "__main__":
    main()
