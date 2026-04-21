<?php
require_once 'config/session.php';
redirectIfLoggedIn();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - ExpenseTracker</title>
    <meta name="description" content="Sign in to your ExpenseTracker account to manage your expenses, track spending, and generate reports.">
    <link rel="stylesheet" href="assets/css/auth.css">
</head>
<body class="auth-page">
    <div class="auth-container">
        <!-- LEFT: Branding Panel -->
        <div class="auth-brand-panel">
            <div class="brand-content">
                <div class="brand-logo">💰</div>
                <h1 class="brand-title">ExpenseTracker</h1>
                <p class="brand-tagline">Take control of your finances with smart tracking, AI-powered insights, and beautiful reports.</p>
                <ul class="brand-features">
                    <li><span class="feature-icon">📊</span> Real-time spending analytics & charts</li>
                    <li><span class="feature-icon">🤖</span> AI-powered spending insights</li>
                    <li><span class="feature-icon">📈</span> Detailed reports & CSV export</li>
                    <li><span class="feature-icon">🔒</span> Secure OTP-based authentication</li>
                </ul>
            </div>
        </div>

        <!-- RIGHT: Login Card -->
        <div class="auth-form-panel">
            <div class="auth-card">
                <div class="auth-card-header">
                    <span class="card-logo">💰</span>
                    <h1 class="card-brand">ExpenseTracker</h1>
                </div>

                <h2 class="card-title">Welcome back</h2>
                <p class="card-subtitle">Sign in to your account to continue</p>

                <!-- Alerts -->
                <?php if (isset($_SESSION['error'])): ?>
                    <div class="auth-alert auth-alert-error">
                        <?php echo htmlspecialchars($_SESSION['error']); unset($_SESSION['error']); ?>
                    </div>
                <?php endif; ?>
                <?php if (isset($_SESSION['success'])): ?>
                    <div class="auth-alert auth-alert-success">
                        <?php echo htmlspecialchars($_SESSION['success']); unset($_SESSION['success']); ?>
                    </div>
                <?php endif; ?>

                <!-- Tab Switcher -->
                <div class="auth-tabs" role="tablist">
                    <button type="button" class="auth-tab active" data-target="passwordPanel" role="tab" aria-selected="true">
                        🔑 Password
                    </button>
                    <button type="button" class="auth-tab" data-target="otpPanel" role="tab" aria-selected="false">
                        📧 Email OTP
                    </button>
                </div>

                <!-- ═══════════════════════════════════ -->
                <!-- PASSWORD LOGIN PANEL                -->
                <!-- ═══════════════════════════════════ -->
                <div class="auth-panel active" id="passwordPanel">
                    <form action="api/auth.php?action=login" method="POST" class="auth-form" id="loginForm" novalidate>
                        <div class="field">
                            <label for="loginEmail" class="field-label">Email Address</label>
                            <input type="email" id="loginEmail" name="email" class="field-input" placeholder="you@example.com" required autocomplete="email">
                        </div>

                        <div class="field">
                            <label for="loginPassword" class="field-label">Password</label>
                            <div class="field-password">
                                <input type="password" id="loginPassword" name="password" class="field-input" placeholder="Enter your password" required autocomplete="current-password">
                                <button type="button" class="field-toggle" data-toggle="loginPassword" aria-label="Show password">
                                    <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                                    <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                                </button>
                            </div>
                        </div>

                        <div class="field-row">
                            <label class="field-check">
                                <input type="checkbox" name="remember">
                                <span>Remember me</span>
                            </label>
                        </div>

                        <button type="submit" class="btn-primary" id="btnSignIn">Sign In</button>
                    </form>
                </div>

                <!-- ═══════════════════════════════════ -->
                <!-- OTP LOGIN PANEL                     -->
                <!-- ═══════════════════════════════════ -->
                <div class="auth-panel" id="otpPanel">
                    <!-- Step 1: Enter email -->
                    <div id="otpStep1">
                        <div class="field">
                            <label for="otpEmail" class="field-label">Email Address</label>
                            <input type="email" id="otpEmail" class="field-input" placeholder="you@example.com" required autocomplete="email">
                            <span class="field-hint">We'll send a 6-digit verification code</span>
                        </div>
                        <button type="button" class="btn-primary" id="btnSendOTP">Send OTP</button>
                    </div>

                    <!-- Step 2: Verify OTP -->
                    <div id="otpStep2" style="display:none;">
                        <div class="otp-sent-info">
                            <p>Enter the code sent to</p>
                            <strong id="otpEmailDisplay"></strong>
                        </div>

                        <!-- Dev mode display -->
                        <div id="otpDevBox" class="otp-dev-box" style="display:none;">
                            <span class="otp-dev-label">🛠 Dev Mode — Your OTP</span>
                            <span class="otp-dev-code" id="devOTPCode"></span>
                        </div>

                        <!-- Status message -->
                        <div id="otpStatusMsg"></div>

                        <!-- 6-digit OTP input -->
                        <div class="otp-digits">
                            <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" data-index="0" autocomplete="one-time-code">
                            <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" data-index="1">
                            <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" data-index="2">
                            <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" data-index="3">
                            <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" data-index="4">
                            <input type="text" class="otp-digit" maxlength="1" inputmode="numeric" data-index="5">
                        </div>

                        <div class="field-row" style="justify-content:center;">
                            <label class="field-check">
                                <input type="checkbox" id="otpRemember">
                                <span>Remember me</span>
                            </label>
                        </div>

                        <button type="button" class="btn-primary" id="btnVerifyOTP" disabled>Verify & Sign In</button>

                        <div class="otp-meta">
                            <span id="otpTimerWrap">Expires in <span class="otp-timer" id="otpTimer">5:00</span></span>
                            <div class="otp-actions">
                                <button type="button" class="link-btn" id="btnResendOTP" disabled>Resend Code</button>
                                <span class="otp-sep">·</span>
                                <button type="button" class="link-btn" id="btnChangeEmail">Change Email</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Divider -->
                <div class="auth-divider"><span>or</span></div>

                <!-- Guest Mode -->
                <a href="api/auth.php?action=guest" class="btn-ghost">👤 Continue as Guest</a>

                <!-- Footer -->
                <p class="auth-footer">Don't have an account? <a href="signup.php" class="auth-link">Create one</a></p>
            </div>
        </div>
    </div>

    <script>
    (function() {
        'use strict';

        // ── Tab Switching ─────────────────────────────
        const tabs = document.querySelectorAll('.auth-tab');
        const panels = document.querySelectorAll('.auth-panel');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.dataset.target;
                // Tabs
                tabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');
                // Panels
                panels.forEach(p => { p.classList.remove('active'); });
                document.getElementById(targetId).classList.add('active');
            });
        });

        // ── Password Toggle ──────────────────────────
        document.querySelectorAll('.field-toggle').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = document.getElementById(btn.dataset.toggle);
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                btn.querySelector('.eye-open').style.display = isPassword ? 'none' : 'block';
                btn.querySelector('.eye-closed').style.display = isPassword ? 'block' : 'none';
            });
        });

        // ── Form Submit Loading ──────────────────────
        const loginForm = document.getElementById('loginForm');
        loginForm.addEventListener('submit', () => {
            document.getElementById('btnSignIn').classList.add('loading');
            document.getElementById('btnSignIn').disabled = true;
        });

        // ── OTP Flow ─────────────────────────────────
        let otpEmail = '';
        let otpTimerInt = null;
        const otpDigits = document.querySelectorAll('.otp-digit');

        // Send OTP
        document.getElementById('btnSendOTP').addEventListener('click', async () => {
            const input = document.getElementById('otpEmail');
            otpEmail = input.value.trim();
            if (!otpEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(otpEmail)) {
                showStatus('Please enter a valid email', 'error'); return;
            }
            const btn = document.getElementById('btnSendOTP');
            btn.classList.add('loading'); btn.disabled = true;

            try {
                const res = await fetch('api/auth.php?action=send_otp', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({ email: otpEmail })
                });
                const data = await res.json();
                if (data.success) {
                    document.getElementById('otpStep1').style.display = 'none';
                    document.getElementById('otpStep2').style.display = 'block';
                    document.getElementById('otpEmailDisplay').textContent = otpEmail;
                    if (data.otp_display) {
                        document.getElementById('otpDevBox').style.display = 'flex';
                        document.getElementById('devOTPCode').textContent = data.otp_display;
                    }
                    startTimer(data.expires_in || 5);
                    otpDigits[0].focus();
                } else {
                    showStatus(data.message || 'Failed to send OTP', 'error');
                }
            } catch(e) { showStatus('Network error. Try again.', 'error'); }
            finally { btn.classList.remove('loading'); btn.disabled = false; }
        });

        // OTP Digit Input
        otpDigits.forEach((d, i) => {
            d.addEventListener('input', e => {
                d.value = d.value.replace(/\D/g, '').charAt(0) || '';
                if (d.value && i < 5) otpDigits[i+1].focus();
                d.classList.toggle('filled', !!d.value);
                checkOTP();
            });
            d.addEventListener('keydown', e => {
                if (e.key === 'Backspace' && !d.value && i > 0) {
                    otpDigits[i-1].focus();
                    otpDigits[i-1].value = '';
                    otpDigits[i-1].classList.remove('filled');
                    checkOTP();
                }
            });
            d.addEventListener('paste', e => {
                e.preventDefault();
                const txt = (e.clipboardData.getData('text')||'').replace(/\D/g,'').slice(0,6);
                txt.split('').forEach((c,j) => { if (otpDigits[j]) { otpDigits[j].value = c; otpDigits[j].classList.add('filled'); }});
                if (txt.length>0) otpDigits[Math.min(txt.length,5)].focus();
                checkOTP();
            });
        });

        function checkOTP() {
            const full = Array.from(otpDigits).every(d => d.value);
            document.getElementById('btnVerifyOTP').disabled = !full;
        }

        // Verify OTP
        document.getElementById('btnVerifyOTP').addEventListener('click', async () => {
            const otp = Array.from(otpDigits).map(d=>d.value).join('');
            if (otp.length !== 6) return;
            const btn = document.getElementById('btnVerifyOTP');
            btn.classList.add('loading'); btn.disabled = true;

            try {
                const res = await fetch('api/auth.php?action=verify_otp', {
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({ email: otpEmail, otp, remember: document.getElementById('otpRemember').checked })
                });
                const data = await res.json();
                if (data.success) {
                    showStatus('Login successful! Redirecting...', 'success');
                    clearInterval(otpTimerInt);
                    setTimeout(() => { window.location.href = data.redirect || '/personal_expense/dashboard.php'; }, 600);
                } else {
                    showStatus(data.message || 'Invalid OTP', 'error');
                    btn.classList.remove('loading'); btn.disabled = false;
                    otpDigits.forEach(d => { d.value=''; d.classList.remove('filled'); });
                    otpDigits[0].focus();
                }
            } catch(e) { showStatus('Network error', 'error'); btn.classList.remove('loading'); btn.disabled = false; }
        });

        // Resend
        document.getElementById('btnResendOTP').addEventListener('click', async () => {
            const btn = document.getElementById('btnResendOTP');
            btn.disabled = true;
            try {
                const res = await fetch('api/auth.php?action=resend_otp', {
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({ email: otpEmail })
                });
                const data = await res.json();
                if (data.success) {
                    showStatus('New code sent!', 'success');
                    startTimer(data.expires_in || 5);
                    otpDigits.forEach(d=>{d.value='';d.classList.remove('filled');});
                    document.getElementById('btnVerifyOTP').disabled = true;
                    otpDigits[0].focus();
                    if (data.otp_display) {
                        document.getElementById('devOTPCode').textContent = data.otp_display;
                        document.getElementById('otpDevBox').style.display = 'flex';
                    }
                } else { showStatus(data.message||'Failed', 'error'); }
            } catch(e) { showStatus('Network error','error'); }
        });

        // Change Email
        document.getElementById('btnChangeEmail').addEventListener('click', () => {
            clearInterval(otpTimerInt);
            document.getElementById('otpStep2').style.display = 'none';
            document.getElementById('otpStep1').style.display = 'block';
            document.getElementById('otpDevBox').style.display = 'none';
            document.getElementById('otpStatusMsg').innerHTML = '';
            otpDigits.forEach(d=>{d.value='';d.classList.remove('filled');});
        });

        // Timer
        function startTimer(mins) {
            clearInterval(otpTimerInt);
            let sec = mins * 60;
            document.getElementById('btnResendOTP').disabled = true;
            const el = document.getElementById('otpTimer');
            const wrap = document.getElementById('otpTimerWrap');
            otpTimerInt = setInterval(() => {
                sec--;
                el.textContent = Math.floor(sec/60) + ':' + (sec%60).toString().padStart(2,'0');
                if (sec <= 0) {
                    clearInterval(otpTimerInt);
                    wrap.innerHTML = '<span style="color:#ef4444;font-weight:600;">Code expired</span>';
                    document.getElementById('btnResendOTP').disabled = false;
                }
            }, 1000);
        }

        function showStatus(msg, type) {
            const el = document.getElementById('otpStatusMsg');
            el.innerHTML = '<div class="otp-status ' + type + '">' + msg + '</div>';
            setTimeout(() => { if (el.querySelector('.otp-status')) el.innerHTML=''; }, 5000);
        }
    })();
    </script>
</body>
</html>
