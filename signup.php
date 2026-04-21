<?php
require_once 'config/session.php';
redirectIfLoggedIn();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account - ExpenseTracker</title>
    <meta name="description" content="Create your free ExpenseTracker account and start managing your finances today.">
    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="stylesheet" href="assets/css/theme.css">
    <link rel="stylesheet" href="assets/css/auth.css">
</head>
<body>
    <div class="auth-container">
        <!-- Left Panel — Branding -->
        <div class="auth-brand-panel">
            <div class="brand-content">
                <div class="brand-logo">💰</div>
                <h1>ExpenseTracker</h1>
                <p>Join thousands of users who have taken control of their finances with smart expense tracking.</p>
                <ul class="brand-features">
                    <li>
                        <span class="feature-icon">⚡</span>
                        Get started in under 30 seconds
                    </li>
                    <li>
                        <span class="feature-icon">📱</span>
                        Works on all devices
                    </li>
                    <li>
                        <span class="feature-icon">🔐</span>
                        Your data is secure & encrypted
                    </li>
                    <li>
                        <span class="feature-icon">💡</span>
                        Free forever — no credit card needed
                    </li>
                </ul>
            </div>
        </div>

        <!-- Right Panel — Form -->
        <div class="auth-form-panel">
            <div class="auth-card">
                <!-- Brand -->
                <div class="auth-brand">
                    <span class="brand-emoji">💰</span>
                    <h1>ExpenseTracker</h1>
                </div>

                <!-- Header -->
                <div class="auth-header">
                    <h2 class="auth-title">Create your account</h2>
                    <p class="auth-subtitle">Start tracking your expenses today</p>
                </div>

                <!-- Alerts -->
                <?php if (isset($_SESSION['error'])): ?>
                    <div class="alert alert-error">
                        ⚠️ <?php echo htmlspecialchars($_SESSION['error']); unset($_SESSION['error']); ?>
                    </div>
                <?php endif; ?>

                <!-- Signup Form -->
                <form action="api/auth.php?action=signup" method="POST" class="auth-form" id="signupForm">
                    <div class="form-group">
                        <label for="username" class="form-label">Username</label>
                        <input 
                            type="text" 
                            id="username" 
                            name="username" 
                            class="form-input" 
                            placeholder="Choose a username"
                            required
                            minlength="3"
                            maxlength="50"
                            autocomplete="username"
                        >
                    </div>

                    <div class="form-group">
                        <label for="email" class="form-label">Email Address</label>
                        <input 
                            type="email" 
                            id="email" 
                            name="email" 
                            class="form-input" 
                            placeholder="you@example.com"
                            required
                            autocomplete="email"
                        >
                        <div class="form-help" id="emailHelp"></div>
                    </div>

                    <div class="form-group">
                        <label for="password" class="form-label">Password</label>
                        <div class="password-wrapper">
                            <input 
                                type="password" 
                                id="password" 
                                name="password" 
                                class="form-input" 
                                placeholder="Create a strong password"
                                required
                                minlength="6"
                                autocomplete="new-password"
                            >
                            <button type="button" class="password-toggle" id="togglePassword" aria-label="Toggle password visibility">
                                👁️
                            </button>
                        </div>
                        <!-- Password Strength Meter -->
                        <div class="password-strength" id="passwordStrength" style="display: none;">
                            <div class="strength-bar">
                                <div class="strength-fill" id="strengthFill"></div>
                            </div>
                            <span class="strength-text" id="strengthText"></span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <div class="password-wrapper">
                            <input 
                                type="password" 
                                id="confirm_password" 
                                name="confirm_password" 
                                class="form-input" 
                                placeholder="Re-enter your password"
                                required
                                autocomplete="new-password"
                            >
                            <button type="button" class="password-toggle" id="toggleConfirmPassword" aria-label="Toggle password visibility">
                                👁️
                            </button>
                        </div>
                        <div class="form-help" id="confirmHelp"></div>
                    </div>

                    <button type="submit" class="btn-signup" id="btnSignUp">
                        Create Account
                    </button>

                    <!-- Divider -->
                    <div class="auth-divider">or</div>

                    <!-- Guest Mode -->
                    <a href="api/auth.php?action=guest" class="btn-guest" style="display: block; text-align: center; text-decoration: none;">
                        👤 Continue as Guest
                    </a>

                    <div class="auth-footer" style="margin-top: 1.25rem;">
                        Already have an account? <a href="index.php" class="auth-link">Sign In</a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        // Password toggle
        function setupToggle(toggleId, inputId) {
            const btn = document.getElementById(toggleId);
            const input = document.getElementById(inputId);
            if (btn && input) {
                btn.addEventListener('click', () => {
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';
                    btn.textContent = isPassword ? '🙈' : '👁️';
                });
            }
        }
        setupToggle('togglePassword', 'password');
        setupToggle('toggleConfirmPassword', 'confirm_password');

        // Password strength meter
        const passwordInput = document.getElementById('password');
        const strengthMeter = document.getElementById('passwordStrength');
        const strengthFill = document.getElementById('strengthFill');
        const strengthText = document.getElementById('strengthText');

        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            if (!val) {
                strengthMeter.style.display = 'none';
                return;
            }
            strengthMeter.style.display = 'block';

            let score = 0;
            if (val.length >= 6) score++;
            if (val.length >= 10) score++;
            if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
            if (/\d/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            const levels = ['weak', 'weak', 'fair', 'good', 'strong', 'strong'];
            const labels = ['Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Strong'];
            const level = levels[score];

            strengthFill.className = 'strength-fill ' + level;
            strengthText.className = 'strength-text ' + level;
            strengthText.textContent = labels[score];
        });

        // Email validation
        const emailInput = document.getElementById('email');
        const emailHelp = document.getElementById('emailHelp');

        emailInput.addEventListener('blur', () => {
            const val = emailInput.value.trim();
            if (val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
                emailHelp.textContent = 'Please enter a valid email address';
                emailHelp.style.color = '#ef4444';
            } else {
                emailHelp.textContent = '';
            }
        });

        // Confirm password matching
        const confirmInput = document.getElementById('confirm_password');
        const confirmHelp = document.getElementById('confirmHelp');

        confirmInput.addEventListener('input', () => {
            if (confirmInput.value && confirmInput.value !== passwordInput.value) {
                confirmHelp.textContent = 'Passwords do not match';
                confirmHelp.style.color = '#ef4444';
            } else if (confirmInput.value) {
                confirmHelp.textContent = '✓ Passwords match';
                confirmHelp.style.color = '#22c55e';
            } else {
                confirmHelp.textContent = '';
            }
        });

        // Form submission
        const signupForm = document.getElementById('signupForm');
        signupForm.addEventListener('submit', function(e) {
            const password = passwordInput.value;
            const confirmPassword = confirmInput.value;

            if (password !== confirmPassword) {
                e.preventDefault();
                confirmHelp.textContent = 'Passwords do not match';
                confirmHelp.style.color = '#ef4444';
                return;
            }

            const btn = document.getElementById('btnSignUp');
            btn.classList.add('btn-loading');
            btn.disabled = true;
        });
    });
    </script>
</body>
</html>
