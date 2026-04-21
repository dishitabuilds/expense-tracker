<?php
/**
 * ONE-TIME Account Migration Script
 * Run this ONCE via: http://localhost/personal_expense/migrate_account.php
 * Then DELETE this file for security.
 * 
 * Migrates: dishita@exp.com → dishitabachudasama@gmail.com
 * Updates password to: Dishitaba0!555# (bcrypt hashed)
 * ALL EXPENSE DATA REMAINS INTACT
 */

require_once 'config/database.php';

header('Content-Type: text/html; charset=utf-8');

echo "<h2>Account Migration Tool</h2>";

try {
    $conn = getDBConnection();
    
    // Step 1: Check if old account exists
    $stmt = $conn->prepare("SELECT id, username, email FROM users WHERE email = ? OR email = ?");
    $oldEmail = 'dishita@exp.com';
    $newEmail = 'dishitabachudasama@gmail.com';
    $stmt->bind_param("ss", $oldEmail, $newEmail);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $existingUser = null;
    $alreadyMigrated = false;
    
    while ($row = $result->fetch_assoc()) {
        if ($row['email'] === $newEmail) {
            $alreadyMigrated = true;
            $existingUser = $row;
        } elseif ($row['email'] === $oldEmail) {
            $existingUser = $row;
        }
    }
    $stmt->close();
    
    if ($alreadyMigrated) {
        echo "<p style='color: #22c55e; font-weight: bold;'>✅ Account already migrated!</p>";
        echo "<p>Email: {$existingUser['email']}</p>";
        echo "<p>Username: {$existingUser['username']}</p>";
        
        // Still update password to ensure it's correct
        $newPassword = password_hash('Dishitaba0!555#', PASSWORD_DEFAULT);
        $stmt = $conn->prepare("UPDATE users SET password = ?, updated_at = NOW() WHERE email = ?");
        $stmt->bind_param("ss", $newPassword, $newEmail);
        $stmt->execute();
        $stmt->close();
        echo "<p style='color: #3b82f6;'>🔑 Password updated to new value.</p>";
        
    } elseif ($existingUser) {
        // Check if new email is already taken by another user
        $stmt = $conn->prepare("SELECT id FROM users WHERE email = ? AND id != ?");
        $stmt->bind_param("si", $newEmail, $existingUser['id']);
        $stmt->execute();
        $checkResult = $stmt->get_result();
        
        if ($checkResult->num_rows > 0) {
            echo "<p style='color: #ef4444; font-weight: bold;'>❌ Error: Email {$newEmail} is already in use by another account!</p>";
            $stmt->close();
            $conn->close();
            exit;
        }
        $stmt->close();
        
        // Perform migration
        $newPassword = password_hash('Dishitaba0!555#', PASSWORD_DEFAULT);
        $stmt = $conn->prepare("UPDATE users SET email = ?, password = ?, updated_at = NOW() WHERE id = ?");
        $stmt->bind_param("ssi", $newEmail, $newPassword, $existingUser['id']);
        
        if ($stmt->execute()) {
            echo "<p style='color: #22c55e; font-weight: bold;'>✅ Migration successful!</p>";
            echo "<p><strong>Old email:</strong> {$oldEmail}</p>";
            echo "<p><strong>New email:</strong> {$newEmail}</p>";
            echo "<p><strong>Username:</strong> {$existingUser['username']}</p>";
            echo "<p><strong>New password:</strong> Dishitaba0!555#</p>";
            
            // Verify expense data is intact
            $stmt2 = $conn->prepare("SELECT COUNT(*) as count FROM expenses WHERE user_id = ?");
            $stmt2->bind_param("i", $existingUser['id']);
            $stmt2->execute();
            $expResult = $stmt2->get_result()->fetch_assoc();
            echo "<p style='color: #22c55e;'>📊 Expenses intact: {$expResult['count']} records</p>";
            $stmt2->close();
            
            $stmt3 = $conn->prepare("SELECT COUNT(*) as count FROM categories WHERE user_id = ?");
            $stmt3->bind_param("i", $existingUser['id']);
            $stmt3->execute();
            $catResult = $stmt3->get_result()->fetch_assoc();
            echo "<p style='color: #22c55e;'>📁 Categories intact: {$catResult['count']} records</p>";
            $stmt3->close();
        } else {
            echo "<p style='color: #ef4444; font-weight: bold;'>❌ Migration failed: " . $stmt->error . "</p>";
        }
        $stmt->close();
        
    } else {
        echo "<p style='color: #f59e0b; font-weight: bold;'>⚠️ No account found with email: {$oldEmail}</p>";
        echo "<p>If you already migrated, the account may be at: {$newEmail}</p>";
    }
    
    // Step 2: Run schema migration (add OTP columns)
    echo "<hr><h3>Schema Migration</h3>";
    
    $alterQueries = [
        "ALTER TABLE users ADD COLUMN otp_code VARCHAR(255) DEFAULT NULL" => "otp_code",
        "ALTER TABLE users ADD COLUMN otp_expires_at DATETIME DEFAULT NULL" => "otp_expires_at",
        "ALTER TABLE users ADD COLUMN otp_attempts INT DEFAULT 0" => "otp_attempts",
        "ALTER TABLE users ADD COLUMN otp_last_sent_at DATETIME DEFAULT NULL" => "otp_last_sent_at",
        "ALTER TABLE users ADD COLUMN remember_token VARCHAR(255) DEFAULT NULL" => "remember_token",
        "ALTER TABLE users ADD COLUMN remember_expires_at DATETIME DEFAULT NULL" => "remember_expires_at",
        "ALTER TABLE users ADD COLUMN login_attempts INT DEFAULT 0" => "login_attempts",
        "ALTER TABLE users ADD COLUMN login_locked_until DATETIME DEFAULT NULL" => "login_locked_until",
    ];
    
    foreach ($alterQueries as $query => $column) {
        // Check if column already exists
        $checkCol = $conn->query("SHOW COLUMNS FROM users LIKE '{$column}'");
        if ($checkCol->num_rows > 0) {
            echo "<p>⏭️ Column <code>{$column}</code> already exists - skipped</p>";
        } else {
            if ($conn->query($query)) {
                echo "<p style='color: #22c55e;'>✅ Added column: <code>{$column}</code></p>";
            } else {
                echo "<p style='color: #ef4444;'>❌ Failed to add <code>{$column}</code>: " . $conn->error . "</p>";
            }
        }
    }
    
    $conn->close();
    
    echo "<hr>";
    echo "<p style='color: #ef4444; font-weight: bold;'>⚠️ DELETE THIS FILE after migration!</p>";
    echo "<p>For security, remove: <code>personal_expense/migrate_account.php</code></p>";
    
} catch (Exception $e) {
    echo "<p style='color: #ef4444; font-weight: bold;'>❌ Error: " . htmlspecialchars($e->getMessage()) . "</p>";
}
?>
