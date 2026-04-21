<?php
/**
 * Session Configuration
 * Manages sessions, authentication, guest mode, and CSRF protection
 */

// Secure session settings
if (session_status() === PHP_SESSION_NONE) {
    ini_set('session.cookie_httponly', 1);
    ini_set('session.cookie_samesite', 'Lax');
    ini_set('session.use_strict_mode', 1);
    session_start();
}

/**
 * Check if user is logged in
 */
function isLoggedIn() {
    return isset($_SESSION['user_id']) && !empty($_SESSION['user_id']);
}

/**
 * Check if user is in guest mode
 */
function isGuest() {
    return !isLoggedIn();
}

/**
 * Redirect to login if not authenticated
 */
function requireLogin() {
    if (!isLoggedIn()) {
        $_SESSION['error'] = 'Please log in to access this feature.';
        header('Location: /personal_expense/index.php');
        exit();
    }
}

/**
 * Allow guest access — does NOT redirect if not logged in.
 * Pages using this will handle guest vs. logged-in state themselves.
 */
function allowGuestAccess() {
    // No redirect — the page will check isLoggedIn() / isGuest() itself
    if (isGuest()) {
        // Set a guest session marker
        if (!isset($_SESSION['guest_mode'])) {
            $_SESSION['guest_mode'] = true;
        }
    }
}

/**
 * Require login for specific premium features (reports, export)
 * If guest, redirects with a helpful message
 */
function requireLoginForFeature($featureName = 'this feature') {
    if (!isLoggedIn()) {
        $_SESSION['error'] = "Please log in to access {$featureName}. Your guest data will be preserved.";
        header('Location: /personal_expense/index.php?redirect=' . urlencode($_SERVER['REQUEST_URI']));
        exit();
    }
}

/**
 * Redirect to dashboard if already logged in
 */
function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        header('Location: /personal_expense/dashboard.php');
        exit();
    }
}

/**
 * Get current user ID
 */
function getCurrentUserId() {
    return $_SESSION['user_id'] ?? null;
}

/**
 * Get current user data
 */
function getCurrentUser() {
    return [
        'id' => $_SESSION['user_id'] ?? null,
        'username' => $_SESSION['username'] ?? null,
        'email' => $_SESSION['email'] ?? null
    ];
}

/**
 * Get user initial for avatar
 */
function getUserInitial() {
    if (isLoggedIn()) {
        $username = $_SESSION['username'] ?? $_SESSION['email'] ?? 'U';
        return strtoupper(substr($username, 0, 1));
    }
    return 'G'; // Guest
}

/**
 * Get display name
 */
function getDisplayName() {
    if (isLoggedIn()) {
        return $_SESSION['username'] ?? $_SESSION['email'] ?? 'User';
    }
    return 'Guest';
}

// ============================================
// CSRF Protection
// ============================================

/**
 * Generate CSRF token
 */
function generateCSRFToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

/**
 * Get CSRF hidden input field HTML
 */
function csrfField() {
    $token = generateCSRFToken();
    return '<input type="hidden" name="csrf_token" value="' . htmlspecialchars($token) . '">';
}

/**
 * Validate CSRF token from POST request
 */
function validateCSRFToken() {
    $token = $_POST['csrf_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if (empty($token) || !hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        http_response_code(403);
        echo json_encode(['success' => false, 'message' => 'Invalid security token. Please refresh and try again.']);
        exit();
    }
}

// ============================================
// Remember Me
// ============================================

/**
 * Check for remember-me cookie and auto-login
 */
function checkRememberMe() {
    if (isLoggedIn()) return;
    
    $token = $_COOKIE['remember_token'] ?? null;
    if (!$token) return;
    
    try {
        require_once __DIR__ . '/database.php';
        $conn = getDBConnection();
        
        $stmt = $conn->prepare("SELECT id, username, email, remember_token, remember_expires_at FROM users WHERE remember_token IS NOT NULL AND remember_expires_at > NOW()");
        $stmt->execute();
        $result = $stmt->get_result();
        
        while ($user = $result->fetch_assoc()) {
            if (hash_equals($user['remember_token'], hash('sha256', $token))) {
                // Auto-login
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                $_SESSION['email'] = $user['email'];
                break;
            }
        }
        
        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        error_log('Remember-me check failed: ' . $e->getMessage());
    }
}

// Auto-check remember-me on every page load
checkRememberMe();
?>
