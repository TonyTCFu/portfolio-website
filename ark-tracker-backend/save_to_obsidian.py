#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed.json")
# Detect run environment
IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

if IS_GITHUB_ACTIONS:
    # On GitHub Actions, write directly to the repository folder
    REPO_ROOT = os.path.dirname(BASE_DIR)
    RESEARCH_DIR = os.path.join(REPO_ROOT, "ark", "data")
    TRACKER_DIR = os.path.join(RESEARCH_DIR, "daily-notes")
else:
    OBSIDIAN_VAULT_PATH = "/Users/tonyfu/Library/Mobile Documents/iCloud~md~obsidian/Documents/AI-Knowledge-Wiki"
    RESEARCH_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "02-The-Wiki", "05-商业金融与量化交易", "03-市场分析与产品研究")
    TRACKER_DIR = os.path.join(RESEARCH_DIR, "ARK-Daily-Tracker")

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

def generate_markdown(data, active_date):
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    md = f"""---
date: {active_date}
tags:
  - investment/ark-tracker
  - investment/portfolio-daily
  - finance/quant
type: research-note
title: "ARK & 全球頂級基金持股觀測日報 ({active_date})"
---

# ARK & 全球頂級基金持股觀測日報 ({active_date})

> **數據基準時間**：{date_str}  
> **線上看板**：[futienchun.com/ark/](https://futienchun.com/ark/)

---

## 1. 今日調倉與板塊輪動深度解讀

"""
    # 1. Daily Analysis & Rotation Narrative
    for fund_id in ["ARKK", "ARKG", "IDNA", "VHT"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            md += f"### {fund_id} ({fund['name']})\n"
            md += f"- **資金規模變動**：`{aum_change}` (昨日收盤比)\n"
            md += f"- **淨資金流入估算**：`${analysis['net_cash_flow']:+,.2f} USD`\n"
            md += f"- **前十持股集中度**：`{analysis['concentration_today']}%` ({conc_diff} 日增減)\n"
            md += f"- **解讀分析**：{analysis['narrative']}\n\n"
            
    md += "---\n\n## 2. 板塊權重與個股偏離分析\n\n"
    
    # 2. Individual Weight shifts (Gainers vs Losers)
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            md += f"### {fund_id} 權重增減倉偏離度排行榜\n"
            md += "| 增倉 Top 3 (Ticker) | 權重變動 | 減倉 Top 3 (Ticker) | 權重變動 |\n"
            md += "| :--- | :--- | :--- | :--- |\n"
            
            gainers = analysis["weight_gainers"][:3]
            losers = analysis["weight_losers"][:3]
            
            for i in range(3):
                g_ticker = gainers[i]["ticker"] if i < len(gainers) else "-"
                g_diff = f"{gainers[i]['weight_diff']:+.2f}%" if i < len(gainers) else "-"
                l_ticker = losers[i]["ticker"] if i < len(losers) else "-"
                l_diff = f"{losers[i]['weight_diff']:+.2f}%" if i < len(losers) else "-"
                md += f"| {g_ticker} | {g_diff} | {l_ticker} | {l_diff} |\n"
            md += "\n"
            
            # Sector Shifts
            md += f"#### {fund_id} 今日板塊權重偏離與偏移值 (%)\n"
            md += "| 細分板塊 | 今日權重 | 昨日權重 | 權重偏移 |\n"
            md += "| :--- | :--- | :--- | :--- |\n"
            for s in analysis.get("sector_shifts", []):
                diff_str = f"{s['weight_diff']:+.2f}%"
                md += f"| {s['sector']} | {s['weight_today']:.2f}% | {s['weight_prev']:.2f}% | {diff_str} |\n"
            md += "\n"

    md += "---\n\n## 3. 主要交易明細 (Trades Digest)\n\n"
    md += "| 基金 | 股票代碼 | 公司名稱 | 調倉方向 | 股數變動 | 權重比 |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for fund_id in ["ARKK", "ARKG", "IDNA", "VHT"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        recent_trades = fund.get("recent_trades", [])
        for t in sorted(recent_trades, key=lambda x: abs(x.get("shares_diff_pct", 0) or 0), reverse=True)[:3]:
            direction = "🟩 買入" if t["shares_diff"] > 0 else "🟥 賣出"
            diff_pct = f"{t['shares_diff_pct']:.2f}%" if t.get('shares_diff_pct') is not None else "NEW"
            shares_diff = f"{t['shares_diff']:+d}" if isinstance(t['shares_diff'], int) else t['shares_diff']
            md += f"| {fund_id} | **{t['ticker']}** | {t['company']} | {direction} | {shares_diff} ({diff_pct}) | {t['weight']:.2f}% |\n"
            
    md += "\n---\n\n## 4. 全球機構 AI 醫療共識度對比\n\n"
    md += "| 排名 | 代碼 (Ticker) | 公司名稱 | 細分板塊 | 共識得分 | 權重分布 (ARK / NVDA / IDNA / VHT) |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    consensus_list = data.get("consensus_data", [])
    for idx, c in enumerate(sorted(consensus_list, key=lambda x: x.get("consensus_score", 0), reverse=True)[:8], 1):
        stars = "★" * c["consensus_score"] + "☆" * (4 - c["consensus_score"])
        # Format weights
        ark_w = f"{c['funds']['ARK']['weight']:.2f}%" if c['funds']['ARK']['owned'] else "-"
        nv_w = f"{c['funds']['NVIDIA']['weight']:.2f}%" if c['funds']['NVIDIA']['owned'] else "-"
        idna_w = f"{c['funds']['BlackRock']['weight']:.2f}%" if c['funds']['BlackRock']['owned'] else "-"
        vht_w = f"{c['funds']['Vanguard']['weight']:.2f}%" if c['funds']['Vanguard']['owned'] else "-"
        weights_str = f"{ark_w} / {nv_w} / {idna_w} / {vht_w}"
        md += f"| {idx} | **{c['ticker']}** | {c['company']} | {c['sector']} | {stars} ({c['consensus_score']}/4) | {weights_str} |\n"
        
    return md

def update_index_files(active_date):
    # 1. Update sub-directory index
    tracker_index_path = os.path.join(TRACKER_DIR, "index.md")
    new_note_link = f"- [[{active_date}]]"
    
    try:
        if not os.path.exists(tracker_index_path):
            index_content = f"""---
type: index
title: "ARK & Global Top Funds Daily Tracker Index"
description: "Index of ARK & Global Top Funds Daily Tracker notes"
---

# ARK & Global Top Funds Daily Tracker Index

## Daily Reports

{new_note_link}
"""
            with open(tracker_index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            print("Created new tracker index.md")
        else:
            with open(tracker_index_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Parse links and avoid duplicates
            existing_links = []
            header_lines = []
            for line in lines:
                if line.strip().startswith("- [[") and "]]" in line:
                    existing_links.append(line.strip())
                else:
                    header_lines.append(line)
                    
            if new_note_link not in existing_links:
                existing_links.insert(0, new_note_link)
                
            # Sort files chronologically descending
            existing_links = sorted(list(set(existing_links)), reverse=True)
                
            # Write back
            new_content = "".join(header_lines)
            if not new_content.endswith("\n\n"):
                new_content += "\n"
            new_content += "\n".join(existing_links) + "\n"
            with open(tracker_index_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Updated tracker index.md links.")
    except PermissionError as pe:
        print(f"Warning: Permission denied when updating tracker index.md. Indexing skipped. ({pe})")
    except Exception as e:
        print(f"Warning: Failed to update tracker index.md: {e}")
        
    # 2. Update parent directory index
    parent_index_path = os.path.join(RESEARCH_DIR, "index.md")
    parent_link = f"- [ARK-Daily-Tracker Index](ARK-Daily-Tracker/index.md)"
    try:
        if os.path.exists(parent_index_path):
            with open(parent_index_path, 'r', encoding='utf-8') as f:
                p_content = f.read()
            if parent_link not in p_content:
                # Append it to the Concepts section
                if "## Concepts" in p_content:
                    p_content = p_content.replace("## Concepts", f"## Concepts\n\n{parent_link}")
                    with open(parent_index_path, 'w', encoding='utf-8') as f:
                        f.write(p_content)
                    print("Linked tracker index inside research index.md.")
    except PermissionError as pe:
        print(f"Warning: Permission denied when reading parent index.md. Linking skipped. ({pe})")
    except Exception as e:
        print(f"Warning: Failed to update parent index.md: {e}")

def main():
    data = load_processed_data()
    if not data:
        return
        
    # Find active date
    active_date = "Daily"
    for fid in ["ARKK", "ARKG"]:
        if fid in data["funds_data"]:
            active_date = data["funds_data"][fid]["date"]
            break
            
    # Target file
    try:
        os.makedirs(TRACKER_DIR, exist_ok=True)
        target_note_path = os.path.join(TRACKER_DIR, f"{active_date}.md")
        
        # Generate MD and write
        md_content = generate_markdown(data, active_date)
        with open(target_note_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"Successfully saved daily note to Obsidian: {target_note_path}")
        
        # Update indices
        update_index_files(active_date)
    except PermissionError as pe:
        print(f"Error: Permission denied when writing daily note to Obsidian folder: {pe}")
        print("Please check your iCloud directory permissions or grant Full Disk Access to /bin/bash or your python binary.")
    except Exception as e:
        print(f"Error: Failed to save daily note to Obsidian: {e}")


if __name__ == "__main__":
    main()
