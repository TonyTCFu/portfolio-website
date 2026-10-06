#!/usr/bin/env python3
"""
ARK & Top Global Funds Daily Summary Email Dispatcher
Modern card-style newsletter layout matching high-fidelity mobile digest design:
- Categories & clear headlines
- Responsive SVG infographic charts (Top 5 Buys, Top 5 Sells, Consecutive Streaks)
- Detailed stock analytics (Shares change, Price, Weight, Streak days)
- Professional investment context analysis & actionable advice
- Dual-channel delivery: Direct HTML via SMTP (if configured) or enhanced FormSubmit.co HTTP API
- Automatic export to web companion (futienchun.com/ark/daily_digest.html)
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
import html
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# File paths
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

def format_number(val):
    if val is None:
        return "-"
    if isinstance(val, (int, float)):
        return f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
    return str(val)

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
            advice = "机构突击建仓，短期波动弹性加剧；建议轻仓试探，避免追高，严格设好 8% 动态止损线。"
            advice_tag = "轻仓跟进 / 注意防守"
        else:
            narrative = f"主力小幅加码，当前持仓权重稳步抬升至 {weight:.2f}%。该标的在 {sector} 领域具备核心护城河，属于资产组合中的稳健核心持仓。"
            advice = "底仓稳健增持，中长线发展逻辑良好；建议长期投资者继续保持底仓并耐心持有。"
            advice_tag = "底仓持有 / 长期看好"
    else:
        abs_streak = abs(streak)
        if weight > 8.0:
            narrative = f"{company} 当前持仓权重仍高达 {weight:.2f}%。本次微幅减持主要受限于基金单一标的 10% 顶格风控红线，属于被动再平衡（Passive Rebalance）获利了结，中长期赛道逻辑未变。"
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
    
    # 1. Extract Trades across active ARK ETFs
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
                
    # Sort buys & sells by absolute dollar trading value
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

    # 2. Extract Consecutive Streaks
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

def generate_svg_bar_chart(title, items, is_positive=True):
    if not items:
        return ""
    chart_h = 165
    chart_w = 560
    bar_w = 64
    gap = (chart_w - (bar_w * len(items))) / (len(items) + 1)
    
    max_val = max([abs(it.get("shares_diff_pct", 0) or it.get("value_diff", 0) or 1) for it in items] or [1])
    if max_val == 0:
        max_val = 1
        
    bar_color = "#10B981" if is_positive else "#EF4444"
    text_color = "#047857" if is_positive else "#B91C1C"
    
    svg = f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:12px;margin:12px 0 16px 0;">
<div style="font-size:12px;font-weight:700;color:#334155;margin-bottom:8px;text-align:left;">📊 {html.escape(title)}</div>
<svg width="100%" height="{chart_h}" viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
<line x1="10" y1="125" x2="{chart_w - 10}" y2="125" stroke="#CBD5E1" stroke-width="1.5" />
'''
    for i, it in enumerate(items):
        x = gap + i * (bar_w + gap)
        val = abs(it.get("shares_diff_pct", 0) or 1)
        bar_h = max(8, int((val / max_val) * 80))
        y = 125 - bar_h
        val_str = f"{it.get('shares_diff_pct', 0):+.1f}%" if it.get("shares_diff_pct") is not None else "NEW"
        lbl = it.get("ticker", "").split(" ")[0]
        fund_lbl = it.get("fund", "ARK")
        
        svg += f'''
<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="4" fill="{bar_color}" />
<text x="{x + bar_w/2:.1f}" y="{y - 6:.1f}" font-size="11" font-weight="700" fill="{text_color}" text-anchor="middle">{html.escape(val_str)}</text>
<text x="{x + bar_w/2:.1f}" y="142" font-size="12" font-weight="700" fill="#0F172A" text-anchor="middle">{html.escape(lbl)}</text>
<text x="{x + bar_w/2:.1f}" y="156" font-size="10" font-weight="500" fill="#64748B" text-anchor="middle">[{fund_lbl}]</text>
'''
    svg += "</svg></div>"
    return svg

def generate_svg_streak_chart(title, items, is_positive=True):
    if not items:
        return ""
    chart_h = 165
    chart_w = 560
    bar_w = 64
    gap = (chart_w - (bar_w * len(items))) / (len(items) + 1)
    
    max_days = max([abs(it.get("streak", 0)) for it in items] or [1])
    if max_days == 0:
        max_days = 1
        
    bar_color = "#3B82F6" if is_positive else "#F97316"
    text_color = "#1D4ED8" if is_positive else "#C2410C"
    
    svg = f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:12px;margin:12px 0 16px 0;">
<div style="font-size:12px;font-weight:700;color:#334155;margin-bottom:8px;text-align:left;">⚡ {html.escape(title)}</div>
<svg width="100%" height="{chart_h}" viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
<line x1="10" y1="125" x2="{chart_w - 10}" y2="125" stroke="#CBD5E1" stroke-width="1.5" />
'''
    for i, it in enumerate(items):
        x = gap + i * (bar_w + gap)
        days = abs(it.get("streak", 0))
        bar_h = max(8, int((days / max_days) * 80))
        y = 125 - bar_h
        lbl = it.get("ticker", "").split(" ")[0]
        day_str = f"连买{days}天" if is_positive else f"连卖{days}天"
        w_str = f"{it.get('weight', 0):.2f}%"
        
        svg += f'''
<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="4" fill="{bar_color}" />
<text x="{x + bar_w/2:.1f}" y="{y - 6:.1f}" font-size="11" font-weight="700" fill="{text_color}" text-anchor="middle">{day_str}</text>
<text x="{x + bar_w/2:.1f}" y="142" font-size="12" font-weight="700" fill="#0F172A" text-anchor="middle">{html.escape(lbl)}</text>
<text x="{x + bar_w/2:.1f}" y="156" font-size="10" font-weight="500" fill="#64748B" text-anchor="middle">仓位 {w_str}</text>
'''
    svg += "</svg></div>"
    return svg

def build_html_email_report(data, intel):
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    top_buys = intel["top_buys"]
    top_sells = intel["top_sells"]
    streak_buys = intel["streak_buys"]
    streak_sells = intel["streak_sells"]
    
    # SVG charts
    chart_buys = generate_svg_bar_chart("今日主要买入前五名 调仓增幅对比 (Shares Diff %)", top_buys, is_positive=True)
    chart_sells = generate_svg_bar_chart("今日主要卖出前五名 调仓减幅对比 (Shares Diff %)", top_sells, is_positive=False)
    chart_streak_buys = generate_svg_streak_chart("机构连续加仓天数异动排行榜", streak_buys, is_positive=True)
    chart_streak_sells = generate_svg_streak_chart("机构连续减持天数异动预警榜", streak_sells, is_positive=False)
    
    ver_stamp = datetime.now().strftime("%Y%m%d%H%M")
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="version" content="{ver_stamp}">
<title>ARK & 全球顶尖基金持股观测日刊</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    background-color: #F1F5F9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1E293B;
    -webkit-text-size-adjust: 100%;
    line-height: 1.6;
  }}
  .container {{
    max-width: 620px;
    margin: 0 auto;
    padding: 20px 14px 40px 14px;
  }}
  .header-card {{
    background: #0F172A;
    border-radius: 14px;
    padding: 22px 20px;
    color: #FFFFFF;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
  }}
  .header-tag {{
    display: inline-block;
    background: rgba(56, 189, 248, 0.2);
    color: #38BDF8;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
  }}
  .header-title {{
    font-size: 20px;
    font-weight: 800;
    margin: 0 0 8px 0;
    line-height: 1.35;
  }}
  .header-meta {{
    font-size: 12px;
    color: #94A3B8;
  }}
  .online-btn {{
    display: inline-block;
    margin-top: 12px;
    background: #3B82F6;
    color: #FFFFFF !important;
    text-decoration: none;
    font-size: 12px;
    font-weight: 700;
    padding: 7px 14px;
    border-radius: 8px;
  }}
  .section-card {{
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 18px;
    margin-bottom: 18px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  }}
  .section-headline {{
    font-size: 16px;
    font-weight: 800;
    color: #0F172A;
    margin: 0 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #F1F5F9;
    display: flex;
    align-items: center;
  }}
  .item-block {{
    background: #F8FAFC;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 14px;
    border: 1px solid #EEF2F6;
  }}
  .item-title-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }}
  .item-ticker {{
    font-size: 15px;
    font-weight: 800;
    color: #0F172A;
  }}
  .item-badge-buy {{
    background: #DCFCE7;
    color: #15803D;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
  }}
  .item-badge-sell {{
    background: #FEE2E2;
    color: #B91C1C;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
  }}
  .data-grid {{
    background: #FFFFFF;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 8px 0;
    border: 1px solid #E2E8F0;
    font-size: 12px;
  }}
  .data-row {{
    margin-bottom: 4px;
  }}
  .data-row:last-child {{
    margin-bottom: 0;
  }}
  .narrative-text {{
    font-size: 13px;
    color: #334155;
    margin: 8px 0 6px 0;
    line-height: 1.55;
  }}
  .pill-footer {{
    background: #F1F5F9;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
    color: #475569;
    margin-top: 8px;
  }}
  .advice-tag {{
    font-weight: 700;
    color: #1D4ED8;
  }}
  .footer-text {{
    text-align: center;
    font-size: 12px;
    color: #94A3B8;
    margin-top: 24px;
  }}
</style>
</head>
<body>
<div class="container">

  <!-- Header Card -->
  <div class="header-card">
    <div class="header-tag">ARK DAILY INTELLIGENCE</div>
    <div class="header-title">ARK & 全球顶尖基金持股观测日刊</div>
    <div class="header-meta">数据基准时间：{date_str}</div>
    <a href="https://futienchun.com/ark/daily_digest.html?v={ver_stamp}" class="online-btn">📱 手机全屏图文阅读器</a>
  </div>
'''

    # Section 1: Top 5 Buys
    html_content += f'''
  <div class="section-card">
    <div class="section-headline">1. 核心买入榜 | 机构增持 Top 5 深度透视</div>
    {chart_buys}
'''
    for idx, b in enumerate(top_buys, 1):
        streak_str = f"连买 {b.get('streak')} 天" if b.get('streak', 0) > 1 else "单日加仓"
        html_content += f'''
    <div class="item-block">
      <div class="item-title-row">
        <span class="item-ticker">#{idx} [{b['fund']}] {html.escape(b['ticker'])} · {html.escape(b['company'])}</span>
        <span class="item-badge-buy">买入 {b.get('shares_diff_pct', 0):+.2f}%</span>
      </div>
      <div class="data-grid">
        <div class="data-row">📊 <strong>变动股数</strong>：<strong>{b['shares_diff']:+,d} 股</strong> (总持股: <strong>{b.get('shares', 0):,} 股</strong>)</div>
        <div class="data-row">💲 <strong>最新价格</strong>：<strong>${b['price']:.2f} USD</strong> | 变动市值: <strong>${abs(b.get('value_diff', 0))/1e6:.2f}M USD</strong></div>
        <div class="data-row">⚖️ <strong>持仓权重</strong>：<strong>{b.get('weight', 0):.2f}%</strong> (日变动 <strong>{b.get('weight_diff', 0):+.2f}%</strong>) | 状态: <strong>{streak_str}</strong></div>
      </div>
      <div class="narrative-text">
        <strong>深度分析说明</strong>：{html.escape(b['narrative'])}
      </div>
      <div class="pill-footer">
        来源 ARK官方持仓 · 赛道: {html.escape(b['sector'])} · <span class="advice-tag">💡 建议参考 [{html.escape(b['advice_tag'])}]</span>：{html.escape(b['advice'])}
      </div>
    </div>
'''
    html_content += "  </div>\n"

    # Section 2: Top 5 Sells
    html_content += f'''
  <div class="section-card">
    <div class="section-headline">2. 核心卖出榜 | 资金减持 Top 5 深度透视</div>
    {chart_sells}
'''
    for idx, s in enumerate(top_sells, 1):
        abs_streak = abs(s.get('streak', 0))
        streak_str = f"连卖 {abs_streak} 天" if abs_streak > 1 else "单日减持"
        html_content += f'''
    <div class="item-block">
      <div class="item-title-row">
        <span class="item-ticker">#{idx} [{s['fund']}] {html.escape(s['ticker'])} · {html.escape(s['company'])}</span>
        <span class="item-badge-sell">减持 {s.get('shares_diff_pct', 0):.2f}%</span>
      </div>
      <div class="data-grid">
        <div class="data-row">📊 <strong>变动股数</strong>：<strong>{s['shares_diff']:+,d} 股</strong> (总持股: <strong>{s.get('shares', 0):,} 股</strong>)</div>
        <div class="data-row">💲 <strong>最新价格</strong>：<strong>${s['price']:.2f} USD</strong> | 减持市值: <strong>${abs(s.get('value_diff', 0))/1e6:.2f}M USD</strong></div>
        <div class="data-row">⚖️ <strong>持仓权重</strong>：<strong>{s.get('weight', 0):.2f}%</strong> (日变动 <strong>{s.get('weight_diff', 0):+.2f}%</strong>) | 状态: <strong>{streak_str}</strong></div>
      </div>
      <div class="narrative-text">
        <strong>深度分析说明</strong>：{html.escape(s['narrative'])}
      </div>
      <div class="pill-footer">
        来源 ARK官方持仓 · 赛道: {html.escape(s['sector'])} · <span class="advice-tag" style="color:#DC2626;">⚠️ 建议参考 [{html.escape(s['advice_tag'])}]</span>：{html.escape(s['advice'])}
      </div>
    </div>
'''
    html_content += "  </div>\n"

    # Section 3: Buying Streaks
    if streak_buys:
        html_content += f'''
  <div class="section-card">
    <div class="section-headline">3. 持续加仓追踪 | 机构高置信连买异动追踪</div>
    {chart_streak_buys}
'''
        for idx, sb in enumerate(streak_buys, 1):
            html_content += f'''
    <div class="item-block">
      <div class="item-title-row">
        <span class="item-ticker">#{idx} [{sb['fund']}] {html.escape(sb['ticker'])} · {html.escape(sb['company'])}</span>
        <span class="item-badge-buy">连续买进 <strong>{sb['streak']} 天</strong></span>
      </div>
      <div class="data-grid">
        <div class="data-row">📊 <strong>持仓总量</strong>：<strong>{sb.get('shares', 0):,} 股</strong> | 最新价格: <strong>${sb.get('price', 0):.2f} USD</strong></div>
        <div class="data-row">⚖️ <strong>当前权重</strong>：<strong>{sb.get('weight', 0):.2f}%</strong> | 赛道: <strong>{html.escape(sb['sector'])}</strong></div>
      </div>
      <div class="narrative-text">
        <strong>异动透视</strong>：{html.escape(sb['narrative'])}
      </div>
      <div class="pill-footer">
        连续加仓 {sb['streak']} 天 · <span class="advice-tag">💡 建议参考 [{html.escape(sb['advice_tag'])}]</span>：{html.escape(sb['advice'])}
      </div>
    </div>
'''
        html_content += "  </div>\n"

    # Section 4: Selling Streaks
    if streak_sells:
        html_content += f'''
  <div class="section-card">
    <div class="section-headline">4. 持续减仓预警 | 资金撤离与防御收缩</div>
    {chart_streak_sells}
'''
        for idx, ss in enumerate(streak_sells, 1):
            abs_days = abs(ss['streak'])
            html_content += f'''
    <div class="item-block">
      <div class="item-title-row">
        <span class="item-ticker">#{idx} [{ss['fund']}] {html.escape(ss['ticker'])} · {html.escape(ss['company'])}</span>
        <span class="item-badge-sell">连续卖出 <strong>{abs_days} 天</strong></span>
      </div>
      <div class="data-grid">
        <div class="data-row">📊 <strong>剩余持仓</strong>：<strong>{ss.get('shares', 0):,} 股</strong> | 最新价格: <strong>${ss.get('price', 0):.2f} USD</strong></div>
        <div class="data-row">⚖️ <strong>当前权重</strong>：<strong>{ss.get('weight', 0):.2f}%</strong> | 赛道: <strong>{html.escape(ss['sector'])}</strong></div>
      </div>
      <div class="narrative-text">
        <strong>减持预警</strong>：{html.escape(ss['narrative'])}
      </div>
      <div class="pill-footer">
        连续减持 {abs_days} 天 · <span class="advice-tag" style="color:#DC2626;">⚠️ 建议参考 [{html.escape(ss['advice_tag'])}]</span>：{html.escape(ss['advice'])}
      </div>
    </div>
'''
        html_content += "  </div>\n"

    # Section 5: Daily Rotation & Sector Shifts
    html_content += '''
  <div class="section-card">
    <div class="section-headline">5. 资金流向与板块轮动深度解读</div>
'''
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            html_content += f'''
    <div class="item-block" style="background:#FFFFFF;">
      <div style="font-size:14px;font-weight:700;color:#0F172A;margin-bottom:6px;">■ {fund_id} ({html.escape(fund['name'])})</div>
      <div style="font-size:12px;color:#475569;margin-bottom:6px;">
        资金规模变动: <strong>{aum_change}</strong> | 净现金流估算: <strong>${analysis['net_cash_flow']:+,.2f} USD</strong><br>
        前十大持仓集中度: <strong>{analysis['concentration_today']}%</strong> ({conc_diff})
      </div>
      <div style="font-size:13px;color:#1E293B;line-height:1.5;">{html.escape(analysis['narrative'])}</div>
    </div>
'''
    html_content += '''
  </div>

  <div class="footer-text">
    ARK & 全球顶尖基金持股观测看板 · 自动化智能简报<br>
    线上看板: <a href="https://futienchun.com/ark/" style="color:#3B82F6;">https://futienchun.com/ark/</a>
  </div>

</div>
</body>
</html>
'''
    return html_content

def build_plain_text_report(data, intel):
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ver_stamp = datetime.now().strftime("%Y%m%d%H%M")
    top_buys = intel["top_buys"]
    top_sells = intel["top_sells"]
    streak_buys = intel["streak_buys"]
    streak_sells = intel["streak_sells"]

    report = f"=============================================\n"
    report += f"ARK & 全球顶尖基金持股观测日刊\n"
    report += f"数据基准时间：{date_str}\n"
    report += f"手机端图文精美简报：https://futienchun.com/ark/daily_digest.html?v={ver_stamp}\n"
    report += f"=============================================\n\n"

    # 1. Top 5 Buys
    report += "【1. 核心买入榜 | 机构增持 Top 5 深度透视】\n"
    report += "---------------------------------------------\n"
    for idx, b in enumerate(top_buys, 1):
        streak_str = f"连买 {b.get('streak')} 天" if b.get('streak', 0) > 1 else "单日加仓"
        report += f"#{idx} [{b['fund']}] {b['ticker']} ({b['company']})\n"
        report += f"  - 变动股数: {b['shares_diff']:+,d} 股 ({b.get('shares_diff_pct', 0):+.2f}%) | 总持股: {b.get('shares', 0):,} 股\n"
        report += f"  - 最新单价: ${b['price']:.2f} USD | 估算变动市值: ${abs(b.get('value_diff', 0))/1e6:.2f}M USD\n"
        report += f"  - 持仓权重: {b.get('weight', 0):.2f}% ({b.get('weight_diff', 0):+.2f}%) | 状态: {streak_str}\n"
        report += f"  - 深度分析说明: {b['narrative']}\n"
        report += f"  - 💡 建议参考 [{b['advice_tag']}]: {b['advice']}\n\n"

    # 2. Top 5 Sells
    report += "【2. 核心卖出榜 | 资金减持 Top 5 深度透视】\n"
    report += "---------------------------------------------\n"
    for idx, s in enumerate(top_sells, 1):
        abs_streak = abs(s.get('streak', 0))
        streak_str = f"连卖 {abs_streak} 天" if abs_streak > 1 else "单日减持"
        report += f"#{idx} [{s['fund']}] {s['ticker']} ({s['company']})\n"
        report += f"  - 变动股数: {s['shares_diff']:+,d} 股 ({s.get('shares_diff_pct', 0):.2f}%) | 总持股: {s.get('shares', 0):,} 股\n"
        report += f"  - 最新单价: ${s['price']:.2f} USD | 估算减持市值: ${abs(s.get('value_diff', 0))/1e6:.2f}M USD\n"
        report += f"  - 持仓权重: {s.get('weight', 0):.2f}% ({s.get('weight_diff', 0):+.2f}%) | 状态: {streak_str}\n"
        report += f"  - 深度分析说明: {s['narrative']}\n"
        report += f"  - ⚠️ 建议参考 [{s['advice_tag']}]: {s['advice']}\n\n"

    # 3. Buying Streaks
    if streak_buys:
        report += "【3. 持续加仓追踪 | 机构高置信连买异动追踪】\n"
        report += "---------------------------------------------\n"
        for idx, sb in enumerate(streak_buys, 1):
            report += f"#{idx} [{sb['fund']}] {sb['ticker']} ({sb['company']}) | 连续买进 {sb['streak']} 天\n"
            report += f"  - 当前持股: {sb.get('shares', 0):,} 股 | 最新价格: ${sb.get('price', 0):.2f} USD\n"
            report += f"  - 持仓权重: {sb.get('weight', 0):.2f}% | 赛道: {sb['sector']}\n"
            report += f"  - 异动说明: {sb['narrative']}\n"
            report += f"  - 💡 建议参考 [{sb['advice_tag']}]: {sb['advice']}\n\n"

    # 4. Selling Streaks
    if streak_sells:
        report += "【4. 持续减仓预警 | 资金撤离与防御收缩】\n"
        report += "---------------------------------------------\n"
        for idx, ss in enumerate(streak_sells, 1):
            abs_days = abs(ss['streak'])
            report += f"#{idx} [{ss['fund']}] {ss['ticker']} ({ss['company']}) | 连续卖出 {abs_days} 天\n"
            report += f"  - 剩余持股: {ss.get('shares', 0):,} 股 | 最新价格: ${ss.get('price', 0):.2f} USD\n"
            report += f"  - 持仓权重: {ss.get('weight', 0):.2f}% | 赛道: {ss['sector']}\n"
            report += f"  - 预警说明: {ss['narrative']}\n"
            report += f"  - ⚠️ 建议参考 [{ss['advice_tag']}]: {ss['advice']}\n\n"

    # 5. Sector Shifts & Daily Rotation
    report += "【5. 资金流向与板块轮动深度解读】\n"
    report += "---------------------------------------------\n"
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            report += f"■ {fund_id} ({fund['name']}):\n"
            report += f"  - 资金规模变动: {aum_change} | 净流入出: ${analysis['net_cash_flow']:+,.2f} USD\n"
            report += f"  - 前十持股集中度: {analysis['concentration_today']}% ({conc_diff})\n"
            report += f"  - 板块解读: {analysis['narrative']}\n\n"

    report += f"欲查看精美图文卡片与矢量图表，请点击：\n"
    report += f"https://futienchun.com/ark/daily_digest.html?v={ver_stamp}\n"
    report += f"=============================================\n"
    return report

def build_sections_dict(data, intel):
    ver_stamp = datetime.now().strftime("%Y%m%d%H%M")
    top_buys = intel["top_buys"]
    top_sells = intel["top_sells"]
    streak_buys = intel["streak_buys"]
    streak_sells = intel["streak_sells"]

    sections = {}
    sections["📱 手机全屏图文阅读器 (带矢量图表)"] = f"https://futienchun.com/ark/daily_digest.html?v={ver_stamp}"

    # 1. Buys
    buys_text = ""
    for idx, b in enumerate(top_buys, 1):
        streak_str = f"连买 {b.get('streak')} 天" if b.get('streak', 0) > 1 else "单日加仓"
        buys_text += f"#{idx} [{b['fund']}] {b['ticker']} ({b['company']})\n"
        buys_text += f"• 变动股数: {b['shares_diff']:+,d} 股 ({b.get('shares_diff_pct', 0):+.2f}%) | 总持股: {b.get('shares', 0):,} 股\n"
        buys_text += f"• 最新单价: ${b['price']:.2f} USD | 变动市值: ${abs(b.get('value_diff', 0))/1e6:.2f}M USD\n"
        buys_text += f"• 持仓权重: {b.get('weight', 0):.2f}% ({b.get('weight_diff', 0):+.2f}%) | 状态: {streak_str}\n"
        buys_text += f"• 深度分析: {b['narrative']}\n"
        buys_text += f"• 💡 建议参考 [{b['advice_tag']}]: {b['advice']}\n\n"
    sections["1. 核心买入榜 Top 5 深度透视"] = buys_text.strip()

    # 2. Sells
    sells_text = ""
    for idx, s in enumerate(top_sells, 1):
        abs_streak = abs(s.get('streak', 0))
        streak_str = f"连卖 {abs_streak} 天" if abs_streak > 1 else "单日减持"
        sells_text += f"#{idx} [{s['fund']}] {s['ticker']} ({s['company']})\n"
        sells_text += f"• 变动股数: {s['shares_diff']:+,d} 股 ({s.get('shares_diff_pct', 0):.2f}%) | 总持股: {s.get('shares', 0):,} 股\n"
        sells_text += f"• 最新单价: ${s['price']:.2f} USD | 减持市值: ${abs(s.get('value_diff', 0))/1e6:.2f}M USD\n"
        sells_text += f"• 持仓权重: {s.get('weight', 0):.2f}% ({s.get('weight_diff', 0):+.2f}%) | 状态: {streak_str}\n"
        sells_text += f"• 深度分析: {s['narrative']}\n"
        sells_text += f"• ⚠️ 建议参考 [{s['advice_tag']}]: {s['advice']}\n\n"
    sections["2. 核心卖出榜 Top 5 深度透视"] = sells_text.strip()

    # 3. Streaks
    if streak_buys:
        sb_text = ""
        for idx, sb in enumerate(streak_buys, 1):
            sb_text += f"#{idx} [{sb['fund']}] {sb['ticker']} ({sb['company']}) | 连续买进 {sb['streak']} 天\n"
            sb_text += f"• 当前持股: {sb.get('shares', 0):,} 股 | 最新价格: ${sb.get('price', 0):.2f} USD\n"
            sb_text += f"• 持仓权重: {sb.get('weight', 0):.2f}% | 赛道: {sb['sector']}\n"
            sb_text += f"• 异动说明: {sb['narrative']}\n"
            sb_text += f"• 💡 建议参考 [{sb['advice_tag']}]: {sb['advice']}\n\n"
        sections["3. 持续加仓追踪 (连买多日)"] = sb_text.strip()

    if streak_sells:
        ss_text = ""
        for idx, ss in enumerate(streak_sells, 1):
            abs_days = abs(ss['streak'])
            ss_text += f"#{idx} [{ss['fund']}] {ss['ticker']} ({ss['company']}) | 连续卖出 {abs_days} 天\n"
            ss_text += f"• 剩余持股: {ss.get('shares', 0):,} 股 | 最新价格: ${ss.get('price', 0):.2f} USD\n"
            ss_text += f"• 持仓权重: {ss.get('weight', 0):.2f}% | 赛道: {ss['sector']}\n"
            ss_text += f"• 预警说明: {ss['narrative']}\n"
            ss_text += f"• ⚠️ 建议参考 [{ss['advice_tag']}]: {ss['advice']}\n\n"
        sections["4. 持续减仓预警 (连卖多日)"] = ss_text.strip()

    # 5. Sector Shifts
    macro_text = ""
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            macro_text += f"■ {fund_id} ({fund['name']}):\n"
            macro_text += f"• 资金规模变动: {aum_change} | 净现金流: ${analysis['net_cash_flow']:+,.2f} USD\n"
            macro_text += f"• 前十持仓集中度: {analysis['concentration_today']}% ({conc_diff})\n"
            macro_text += f"• 宏观解读: {analysis['narrative']}\n\n"
    sections["5. 资金流向与板块轮动解读"] = macro_text.strip()

    return sections

def export_web_digest(html_content):
    """
    Exports the generated HTML digest locally and into the website repo.
    """
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

def send_via_smtp(subject, html_content, text_content, receiver_email, config):
    smtp_host = config.get("smtp_host")
    smtp_port = config.get("smtp_port", 587)
    smtp_user = config.get("smtp_user")
    smtp_pass = config.get("smtp_password")

    if not (smtp_host and smtp_user and smtp_pass):
        return False

    try:
        print(f"Sending HTML email via SMTP ({smtp_host}:{smtp_port}) to {receiver_email}...")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = receiver_email

        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, receiver_email, msg.as_string())
        server.quit()
        print("HTML email sent successfully via SMTP!")
        return True
    except Exception as e:
        print(f"SMTP sending failed: {e}")
        return False

def send_via_formsubmit(subject, payload_data, receiver_email):
    url = f"https://formsubmit.co/ajax/{receiver_email}"
    data = {
        "_subject": subject,
        "_template": "box"
    }
    if isinstance(payload_data, dict):
        data.update(payload_data)
    else:
        data["简报内容"] = payload_data

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
                    print("Email report sent successfully via FormSubmit!")
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
    # Backward compatible weekly report logic
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report = f"=============================================\n"
    report += f"ARK & 全球顶尖基金持股观测【每周综合投资报告】\n"
    report += f"报告时间：{date_str} (周日报告)\n"
    report += f"线上看板：https://futienchun.com/ark/\n"
    report += f"=============================================\n\n"
    
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
    html_content = build_html_email_report(data, intel)
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

    # Attempt SMTP first if configured, otherwise fallback to FormSubmit
    sent = False
    if config.get("smtp_enabled", False):
        sent = send_via_smtp(subject, html_content, text_content, receiver_email, config)

    if not sent:
        sections = build_sections_dict(data, intel)
        sent = send_via_formsubmit(subject, sections, receiver_email)

    if sent:
        print("Summary email dispatched successfully.")
    else:
        print("Notice: Summary email sending completed with notice or fallback.")

if __name__ == "__main__":
    main()
