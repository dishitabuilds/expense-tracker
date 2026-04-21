<?php
/**
 * Authentication API
 * Handles signup, login (password + OTP), logout, and remember-me
 */

require_once '../config/database.php';
require_once '../config/session.php';
require_once '../config/mail.php';

header('Content-Type: application/json');

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'signup':
        handleSignup();
        break;
    case 'login':
        handleLogin();
        break;
    case 'send_otp':
        handleSendOTP();
        break;
    case 'verify_otp':
        handleVerifyOTP();
        break;
    case 'resend_otp':
        handleResendOTP();
        break;
    case 'logout':
        handleLogout();
        break;
    case 'guest':
        handleGuestMode();
        break;
    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid action']);
}

/**
 * Handle user signup
 */
function handleSignup() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Method not allowed']);
        return;
    }

    $username = trim($_POST['username'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $confirmPassword = $_POST['confirm_password'] ?? '';

    // Validation
    if (empty($username) || empty($email) || empty($password)) {
        $_SESSION['error'] = 'All fields are required';
        header('Location: /personal_expense/signup.php');
        exit();
    }

    if (strlen($username) < 3 || strlen($username) > 50) {
        $_SESSION['error'] = 'Username must be between 3 and 50 characters';
        header('Location: /personal_expense/signup.php');
        exit();
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $_SESSION['error'] = 'Invalid email format';
        header('Location: /personal_expense/signup.php');
        exit();
    }

    if (strlen($password) < 6) {
        $_SESSION['error'] = 'Password must be at least 6 characters';
        header('Location: /personal_expense/signup.php');
        exit();
    }

    if ($password !== $confirmPassword) {
        $_SESSION['error'] = 'Passwords do not match';
        header('Location: /personal_expense/signup.php');
        exit();
    }

    try {
        $conn = getDBConnection();

        // Check if username or email already exists
        $stmt = $conn->prepare("SELECT id FROM users WHERE username = ? OR email = ?");
        $stmt->bind_param("ss", $username, $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $_SESSION['error'] = 'Username or email already exists';
            header('Location: /personal_expense/signup.php');
            exit();
        }

        // Hash password
        $hashedPassword = password_hash($password, PASSWORD_DEFAULT);

        // Insert user
        $stmt = $conn->prepare("INSERT INTO users (username, email, password) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $username, $email, $hashedPassword);
        
        if ($stmt->execute()) {
            $userId = $conn->insert_id;

            // Create default categories for the new user
            createDefaultCategories($conn, $userId);

            $_SESSION['success'] = 'Account created successfully! Please login.';
            header('Location: /personal_expense/index.php');
        } else {
            $_SESSION['error'] = 'Failed to create account';
            header('Location: /personal_expense/signup.php');
        }

        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        error_log($e->getMessage());
        $_SESSION['error'] = 'An error occurred. Please try again.';
        header('Location: /personal_expense/signup.php');
    }
    exit();
}

/**
 * Handle user login (password-based)
 */
function handleLogin() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Method not allowed']);
        return;
    }

    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $remember = isset($_POST['remember']);

    if (empty($email) || empty($password)) {
        $_SESSION['error'] = 'Email and password are required';
        header('Location: /personal_expense/index.php');
        exit();
    }

    try {
        $conn = getDBConnection();

        // Check rate limiting
        $stmt = $conn->prepare("SELECT id, username, email, password, login_attempts, login_locked_until FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 0) {
            $_SESSION['error'] = 'Invalid email or password';
            header('Location: /personal_expense/index.php');
            exit();
        }

        $user = $result->fetch_assoc();

        // Check if account is locked
        if ($user['login_locked_until'] && strtotime($user['login_locked_until']) > time()) {
            $remaining = ceil((strtotime($user['login_locked_until']) - time()) / 60);
            $_SESSION['error'] = "Account temporarily locked. Try again in {$remaining} minute(s).";
            header('Location: /personal_expense/index.php');
            exit();
        }

        if (!password_verify($password, $user['password'])) {
            // Increment login attempts
            $attempts = ($user['login_attempts'] ?? 0) + 1;
            $lockUntil = null;
            
            if ($attempts >= 5) {
                // Lock for 15 minutes
                $lockUntil = date('Y-m-d H:i:s', strtotime('+15 minutes'));
                $attempts = 0;
            }
            
            $stmt2 = $conn->prepare("UPDATE users SET login_attempts = ?, login_locked_until = ? WHERE id = ?");
            $stmt2->bind_param("isi", $attempts, $lockUntil, $user['id']);
            $stmt2->execute();
            $stmt2->close();
            
            $_SESSION['error'] = 'Invalid email or password';
            header('Location: /personal_expense/index.php');
            exit();
        }

        // Reset login attempts on success
        $stmt3 = $conn->prepare("UPDATE users SET login_attempts = 0, login_locked_until = NULL WHERE id = ?");
        $stmt3->bind_param("i", $user['id']);
        $stmt3->execute();
        $stmt3->close();

        // Set session variables
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['email'] = $user['email'];
        unset($_SESSION['guest_mode']);

        // Handle remember me
        if ($remember) {
            setRememberToken($conn, $user['id']);
        }

        header('Location: /personal_expense/dashboard.php');

        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        error_log($e->getMessage());
        $_SESSION['error'] = 'An error occurred. Please try again.';
        header('Location: /personal_expense/index.php');
    }
    exit();
}

/**
 * Handle sending OTP
 */
function handleSendOTP() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Method not allowed']);
        return;
    }

    $input = json_decode(file_get_contents('php://input'), true);
    $email = trim($input['email'] ?? $_POST['email'] ?? '');

    if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo json_encode(['success' => false, 'message' => 'Please enter a valid email address']);
        return;
    }

    try {
        $conn = getDBConnection();

        // Check if user exists
        $stmt = $conn->prepare("SELECT id, otp_attempts, otp_last_sent_at FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 0) {
            echo json_encode(['success' => false, 'message' => 'No account found with this email']);
            return;
        }

        $user = $result->fetch_assoc();
        $stmt->close();

        // Rate limiting: max 3 OTPs per 10 minutes
        if ($user['otp_last_sent_at']) {
            $lastSent = strtotime($user['otp_last_sent_at']);
            $windowStart = strtotime('-' . OTP_RESEND_WINDOW_MINUTES . ' minutes');
            
            if ($lastSent > $windowStart && $user['otp_attempts'] >= OTP_MAX_RESEND) {
                $waitMinutes = ceil(($lastSent + (OTP_RESEND_WINDOW_MINUTES * 60) - time()) / 60);
                echo json_encode(['success' => false, 'message' => "Too many attempts. Please wait {$waitMinutes} minute(s)."]);
                return;
            }
        }

        // Generate OTP
        $otp = generateOTP();
        $hashedOTP = password_hash($otp, PASSWORD_DEFAULT);
        $expiresAt = date('Y-m-d H:i:s', strtotime('+' . OTP_EXPIRY_MINUTES . ' minutes'));
        $attempts = ($user['otp_last_sent_at'] && strtotime($user['otp_last_sent_at']) > strtotime('-' . OTP_RESEND_WINDOW_MINUTES . ' minutes'))
            ? $user['otp_attempts'] + 1 
            : 1;

        // Store hashed OTP in database
        $stmt = $conn->prepare("UPDATE users SET otp_code = ?, otp_expires_at = ?, otp_attempts = ?, otp_last_sent_at = NOW() WHERE id = ?");
        $stmt->bind_param("ssii", $hashedOTP, $expiresAt, $attempts, $user['id']);
        $stmt->execute();
        $stmt->close();

        // Send OTP email
        $mailResult = sendOTPEmail($email, $otp);

        $response = [
            'success' => $mailResult['success'],
            'message' => $mailResult['message'],
            'expires_in' => OTP_EXPIRY_MINUTES
        ];

        // In dev mode, include OTP for on-screen display
        if (isset($mailResult['otp_display']) && $mailResult['otp_display']) {
            $response['otp_display'] = $mailResult['otp_display'];
        }

        echo json_encode($response);
        $conn->close();

    } catch (Exception $e) {
        error_log($e->getMessage());
        echo json_encode(['success' => false, 'message' => 'An error occurred. Please try again.']);
    }
}

/**
 * Handle verifying OTP
 */
function handleVerifyOTP() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Method not allowed']);
        return;
    }

    $input = json_decode(file_get_contents('php://input'), true);
    $email = trim($input['email'] ?? $_POST['email'] ?? '');
    $otp = trim($input['otp'] ?? $_POST['otp'] ?? '');
    $remember = $input['remember'] ?? $_POST['remember'] ?? false;

    if (empty($email) || empty($otp)) {
        echo json_encode(['success' => false, 'message' => 'Email and OTP are required']);
        return;
    }

    try {
        $conn = getDBConnection();

        $stmt = $conn->prepare("SELECT id, username, email, otp_code, otp_expires_at FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 0) {
            echo json_encode(['success' => false, 'message' => 'Invalid email']);
            return;
        }

        $user = $result->fetch_assoc();
        $stmt->close();

        // Check if OTP has expired
        if (!$user['otp_code'] || !$user['otp_expires_at'] || strtotime($user['otp_expires_at']) < time()) {
            echo json_encode(['success' => false, 'message' => 'OTP has expired. Please request a new one.']);
            return;
        }

        // Verify OTP
        if (!password_verify($otp, $user['otp_code'])) {
            echo json_encode(['success' => false, 'message' => 'Invalid OTP. Please check and try again.']);
            return;
        }

        // Clear OTP from database
        $stmt = $conn->prepare("UPDATE users SET otp_code = NULL, otp_expires_at = NULL, otp_attempts = 0, login_attempts = 0, login_locked_until = NULL WHERE id = ?");
        $stmt->bind_param("i", $user['id']);
        $stmt->execute();
        $stmt->close();

        // Set session
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['email'] = $user['email'];
        unset($_SESSION['guest_mode']);

        // Handle remember me
        if ($remember) {
            setRememberToken($conn, $user['id']);
        }

        echo json_encode([
            'success' => true,
            'message' => 'Login successful!',
            'redirect' => '/personal_expense/dashboard.php'
        ]);

        $conn->close();

    } catch (Exception $e) {
        error_log($e->getMessage());
        echo json_encode(['success' => false, 'message' => 'An error occurred. Please try again.']);
    }
}

/**
 * Handle resend OTP (same as send but explicit resend)
 */
function handleResendOTP() {
    handleSendOTP(); // Same logic with rate limiting built in
}

/**
 * Handle guest mode activation
 */
function handleGuestMode() {
    $_SESSION['guest_mode'] = true;
    unset($_SESSION['user_id'], $_SESSION['username'], $_SESSION['email']);
    
    header('Location: /personal_expense/dashboard.php');
    exit();
}

/**
 * Handle user logout
 */
function handleLogout() {
    // Clear remember-me cookie and token
    if (isLoggedIn()) {
        try {
            require_once '../config/database.php';
            $conn = getDBConnection();
            $stmt = $conn->prepare("UPDATE users SET remember_token = NULL, remember_expires_at = NULL WHERE id = ?");
            $userId = $_SESSION['user_id'];
            $stmt->bind_param("i", $userId);
            $stmt->execute();
            $stmt->close();
            $conn->close();
        } catch (Exception $e) {
            error_log($e->getMessage());
        }
    }

    // Clear remember cookie
    if (isset($_COOKIE['remember_token'])) {
        setcookie('remember_token', '', time() - 3600, '/personal_expense/', '', false, true);
    }

    session_destroy();
    header('Location: /personal_expense/index.php');
    exit();
}

/**
 * Set remember-me token
 */
function setRememberToken($conn, $userId) {
    $rawToken = bin2hex(random_bytes(32));
    $hashedToken = hash('sha256', $rawToken);
    $expiresAt = date('Y-m-d H:i:s', strtotime('+30 days'));
    
    $stmt = $conn->prepare("UPDATE users SET remember_token = ?, remember_expires_at = ? WHERE id = ?");
    $stmt->bind_param("ssi", $hashedToken, $expiresAt, $userId);
    $stmt->execute();
    $stmt->close();
    
    setcookie('remember_token', $rawToken, [
        'expires' => strtotime('+30 days'),
        'path' => '/personal_expense/',
        'httponly' => true,
        'samesite' => 'Lax'
    ]);
}

/**
 * Create default categories for new user
 */
function createDefaultCategories($conn, $userId) {
    $defaultCategories = [
        ['Food & Dining', '#ef4444', 'utensils'],
        ['Transportation', '#3b82f6', 'car'],
        ['Shopping', '#8b5cf6', 'shopping-bag'],
        ['Entertainment', '#ec4899', 'film'],
        ['Bills & Utilities', '#f59e0b', 'file-text'],
        ['Healthcare', '#10b981', 'heart'],
        ['Education', '#06b6d4', 'book'],
        ['Other', '#6b7280', 'tag']
    ];

    $stmt = $conn->prepare("INSERT INTO categories (user_id, name, color, icon) VALUES (?, ?, ?, ?)");

    foreach ($defaultCategories as $category) {
        $stmt->bind_param("isss", $userId, $category[0], $category[1], $category[2]);
        $stmt->execute();
    }

    $stmt->close();
}
?>
