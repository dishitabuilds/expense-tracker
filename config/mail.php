<?php
/**
 * Mail Configuration
 * Handles OTP email sending
 * 
 * MODE: 'dev' = display OTP on screen (no email sent)
 *       'smtp' = send via Gmail SMTP (requires PHPMailer + App Password)
 */

define('MAIL_MODE', 'dev'); // Change to 'smtp' for production

// SMTP Settings (only used when MAIL_MODE = 'smtp')
define('SMTP_HOST', 'smtp.gmail.com');
define('SMTP_PORT', 587);
define('SMTP_USERNAME', 'your-email@gmail.com');
define('SMTP_PASSWORD', 'your-app-password');
define('SMTP_FROM_NAME', 'ExpenseTracker');
define('SMTP_FROM_EMAIL', 'noreply@expensetracker.com');

// OTP Settings
define('OTP_LENGTH', 6);
define('OTP_EXPIRY_MINUTES', 5);
define('OTP_MAX_RESEND', 3);
define('OTP_RESEND_WINDOW_MINUTES', 10);

/**
 * Generate a random numeric OTP
 */
function generateOTP() {
    $otp = '';
    for ($i = 0; $i < OTP_LENGTH; $i++) {
        $otp .= random_int(0, 9);
    }
    return $otp;
}

/**
 * Send OTP to email
 * Returns: ['success' => bool, 'message' => string, 'otp_display' => string|null]
 */
function sendOTPEmail($email, $otp) {
    if (MAIL_MODE === 'dev') {
        // Dev mode: return OTP for on-screen display
        return [
            'success' => true,
            'message' => 'OTP generated (dev mode)',
            'otp_display' => $otp
        ];
    }
    
    // SMTP mode: use PHP mail() or PHPMailer
    $subject = "Your ExpenseTracker Login OTP";
    $htmlBody = getOTPEmailTemplate($otp);
    
    $headers = "MIME-Version: 1.0\r\n";
    $headers .= "Content-type: text/html; charset=UTF-8\r\n";
    $headers .= "From: " . SMTP_FROM_NAME . " <" . SMTP_FROM_EMAIL . ">\r\n";
    
    $sent = @mail($email, $subject, $htmlBody, $headers);
    
    return [
        'success' => $sent,
        'message' => $sent ? 'OTP sent to your email' : 'Failed to send OTP email',
        'otp_display' => null
    ];
}

/**
 * Get email template for OTP
 */
function getOTPEmailTemplate($otp) {
    return "
    <div style='font-family: -apple-system, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;'>
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #6366f1; font-size: 24px; margin: 0;'>💰 ExpenseTracker</h1>
        </div>
        <div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 30px; text-align: center;'>
            <h2 style='color: #1e293b; font-size: 20px; margin: 0 0 10px;'>Your Login OTP</h2>
            <p style='color: #64748b; font-size: 14px; margin: 0 0 25px;'>Use this code to log in to your account</p>
            <div style='background: #ffffff; border: 2px solid #6366f1; border-radius: 8px; padding: 15px; margin: 0 auto; max-width: 200px;'>
                <span style='font-size: 32px; font-weight: 700; letter-spacing: 8px; color: #6366f1;'>{$otp}</span>
            </div>
            <p style='color: #94a3b8; font-size: 13px; margin: 20px 0 0;'>This code expires in " . OTP_EXPIRY_MINUTES . " minutes</p>
        </div>
        <p style='color: #94a3b8; font-size: 12px; text-align: center; margin-top: 20px;'>
            If you didn't request this code, please ignore this email.
        </p>
    </div>";
}
?>
