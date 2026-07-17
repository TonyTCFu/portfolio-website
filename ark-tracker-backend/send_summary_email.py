#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
import time

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed.json")
CONFIG_FILE = os.path.join(BASE_DIR, ".email_config.json")

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
        return None
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading email configuration: {e}")
        return None

def build_plain_text_report(data):
    # Format current date
    date_str = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    report = f"=============================================\n"
    report += f"ARK & 全球頂級基金持股觀測日報\n"
    report += f"基準時間：{date_str}\n"
    report += f"=============================================\n\n"
    
    # 1. Daily Analysis & Rotation Narrative (Overall view)
    report += "【今日調倉與板塊輪動深度解讀】\n"
    report += "---------------------------------------------\n"
    for fund_id in ["ARKK", "ARKG", "IDNA", "VHT"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            aum_change = f"{analysis['aum_change_pct']:+.2f}%"
            conc_diff = f"{analysis['concentration_diff']:+.2f}%"
            report += f"■ {fund_id} ({fund['name']}):\n"
            report += f"  - 資金規模變動：{aum_change} | 估算淨流出入：${analysis['net_cash_flow']:+,.2f} USD\n"
            report += f"  - 前十持股集中度：{analysis['concentration_today']}% ({conc_diff})\n"
            report += f"  - 板塊偏離解讀：{analysis['narrative']}\n\n"
            
    # 2. Individual Weight shifts (Gainers vs Losers)
    report += "【個股權重增減倉偏移排行榜（前五名）】\n"
    report += "---------------------------------------------\n"
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            report += f"■ {fund_id} 權重偏離度：\n"
            gainers = [f"{g['ticker']} ({g['weight_diff']:+.2f}%)" for g in analysis["weight_gainers"][:5]]
            losers = [f"{l['ticker']} ({l['weight_diff']:+.2f}%)" for l in analysis["weight_losers"][:5]]
            report += f"  - 主要增倉：{', '.join(gainers)}\n"
            report += f"  - 主要減倉：{', '.join(losers)}\n"
    report += "\n"
    
    # 3. Sector Shifts (Detailed table formatting in plain text)
    report += "【今日板塊權重偏離與偏移值明細】\n"
    report += "---------------------------------------------\n"
    for fund_id in ["ARKK", "ARKG", "IDNA"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        analysis = fund.get("daily_analysis")
        if analysis:
            report += f"■ {fund_id} 板塊分佈偏移：\n"
            for s in analysis.get("sector_shifts", []):
                diff_str = f"{s['weight_diff']:+.2f}%"
                report += f"  - {s['sector']}: 目前權重 {s['weight_today']:.2f}% | 昨日 {s['weight_prev']:.2f}% | 偏移 {diff_str}\n"
            report += "\n"
    
    # 4. Key/Significant Trades of the Day
    report += "【主要交易明細 (Trades Digest)】\n"
    report += "---------------------------------------------\n"
    trade_count = 0
    for fund_id in ["ARKK", "ARKG", "IDNA", "VHT"]:
        if fund_id not in data["funds_data"]:
            continue
        fund = data["funds_data"][fund_id]
        recent_trades = fund.get("recent_trades", [])
        for t in sorted(recent_trades, key=lambda x: abs(x.get("shares_diff_pct", 0) or 0), reverse=True)[:3]:
            trade_count += 1
            direction = "買入" if t["shares_diff"] > 0 else "賣出"
            diff_pct = f"{t['shares_diff_pct']:.2f}%" if t.get('shares_diff_pct') is not None else "NEW"
            shares_diff = f"{t['shares_diff']:+d}" if isinstance(t['shares_diff'], int) else t['shares_diff']
            report += f"- {fund_id}: {t['ticker']} ({t['company']}) | {direction} {shares_diff} 股 ({diff_pct}) | 權重 {t['weight']:.2f}%\n"
    if trade_count == 0:
        report += "今日無顯著交易變動\n"
    report += "\n"
    
    # 5. Consensus Leaders
    report += "【全球機構 AI 醫療共識名單對比】\n"
    report += "---------------------------------------------\n"
    consensus_list = data.get("consensus_data", [])
    for idx, c in enumerate(sorted(consensus_list, key=lambda x: x.get("consensus_score", 0), reverse=True)[:8], 1):
        stars = "★" * c["consensus_score"] + "☆" * (4 - c["consensus_score"])
        # Format weights
        ark_w = f"{c['funds']['ARK']['weight']:.2f}%" if c['funds']['ARK']['owned'] else "-"
        nv_w = f"{c['funds']['NVIDIA']['weight']:.2f}%" if c['funds']['NVIDIA']['owned'] else "-"
        idna_w = f"{c['funds']['BlackRock']['weight']:.2f}%" if c['funds']['BlackRock']['owned'] else "-"
        vht_w = f"{c['funds']['Vanguard']['weight']:.2f}%" if c['funds']['Vanguard']['owned'] else "-"
        weights_str = f"ARK: {ark_w} / NVDA: {nv_w} / BlackRock: {idna_w} / Vanguard: {vht_w}"
        report += f"{idx}. {c['ticker']} ({c['company']}) | 共識: {stars} ({c['consensus_score']}/4)\n"
        report += f"   板塊: {c['sector']} | 權重: {weights_str}\n"
    report += "\n"
    
    # Link to live Dashboard
    report += "欲查看歷史資產趨勢圖及更多細節，請瀏覽線上觀測看板：\n"
    report += "線上觀測看板: https://futienchun.com/ark/\n"
    report += "=============================================\n"
    return report

def send_via_formsubmit(subject, message_text, receiver_email):
    url = f"https://formsubmit.co/ajax/{receiver_email}"
    
    data = {
        "_subject": subject,
        "日報內容": message_text,
        "_template": "box"
    }
    
    payload = urllib.parse.urlencode(data).encode('utf-8')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Origin': 'https://futienchun.com',
        'Referer': 'https://futienchun.com/ark/'
    }
    req = urllib.request.Request(url, data=payload, headers=headers)
    
    max_retries = 3
    retry_delay = 12
    for attempt in range(max_retries + 1):
        try:
            print(f"Sending daily report to {receiver_email} via FormSubmit.co HTTP API (Attempt {attempt + 1})...")
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                if res.get("success") == "true":
                    print("Email report sent successfully via FormSubmit!")
                    return True
                else:
                    print(f"FormSubmit API Notice: {res.get('message')}")
                    if "Activation" in res.get("message", ""):
                        print("--> IMPORTANT: Please check your inbox and click 'Activate Form' to start receiving daily reports!")
                        return True
                    return False
        except (urllib.error.URLError, ConnectionResetError) as e:
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Error: All {max_retries + 1} email attempts failed: {e}")
    return False

def main():
    data = load_processed_data()
    if not data:
        print("Skipping email sending: No processed data found.")
        return
        
    # Find active date
    active_date = "Daily"
    for fid in ["ARKK", "ARKG"]:
        if fid in data["funds_data"]:
            active_date = data["funds_data"][fid]["date"]
            break
            
    subject = f"ARK & 全球頂級基金持股觀測日報 ({active_date})"
    message_text = build_plain_text_report(data)
    
    # Send via FormSubmit to avoid local SMTP/Mail.app issues
    receiver_email = "tony.tc.fu@icloud.com"
    config = load_config()
    if config:
        receiver_email = config.get("receiver_email", receiver_email)
        
    success = send_via_formsubmit(subject, message_text, receiver_email)
    if success:
        print("Daily tracker email report task executed.")
    else:
        print("Email report delivery failed.")

if __name__ == "__main__":
    main()
