<?php
/**
 * Monthly Budget API
 * GET  - Fetch current monthly budget + spending stats
 * POST - Set/update monthly budget
 */

require_once '../config/database.php';
require_once '../config/session.php';

requireLogin();
header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];
$userId = getCurrentUserId();

switch ($method) {
    case 'GET':
        getBudgetStats($userId);
        break;
    case 'POST':
        setMonthlyBudget($userId);
        break;
    default:
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Method not allowed']);
}

function getBudgetStats($userId) {
    try {
        $conn = getDBConnection();

        // Get monthly budget from user_preferences
        $stmt = $conn->prepare("SELECT monthly_budget FROM user_preferences WHERE user_id = ?");
        $stmt->bind_param("i", $userId);
        $stmt->execute();
        $result = $stmt->get_result();
        $prefs = $result->fetch_assoc();
        $monthlyBudget = $prefs ? floatval($prefs['monthly_budget']) : 0;

        // Get current month's total spending
        $stmt = $conn->prepare("
            SELECT COALESCE(SUM(amount), 0) as total_spent, COUNT(*) as count
            FROM expenses
            WHERE user_id = ? 
              AND MONTH(expense_date) = MONTH(CURDATE()) 
              AND YEAR(expense_date) = YEAR(CURDATE())
        ");
        $stmt->bind_param("i", $userId);
        $stmt->execute();
        $spending = $stmt->get_result()->fetch_assoc();
        $totalSpent = floatval($spending['total_spent']);

        // Get average monthly spending (last 6 months)
        $stmt = $conn->prepare("
            SELECT COALESCE(AVG(monthly_total), 0) as avg_monthly
            FROM (
                SELECT SUM(amount) as monthly_total
                FROM expenses
                WHERE user_id = ?
                  AND expense_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                  AND NOT (MONTH(expense_date) = MONTH(CURDATE()) AND YEAR(expense_date) = YEAR(CURDATE()))
                GROUP BY YEAR(expense_date), MONTH(expense_date)
            ) monthly_totals
        ");
        $stmt->bind_param("i", $userId);
        $stmt->execute();
        $avgResult = $stmt->get_result()->fetch_assoc();
        $avgMonthly = floatval($avgResult['avg_monthly']);

        // Days progress in current month
        $today = intval(date('j'));
        $daysInMonth = intval(date('t'));
        $monthProgress = round(($today / $daysInMonth) * 100);

        // Projected spending
        $dailyRate = ($today > 0) ? ($totalSpent / $today) : 0;
        $projectedTotal = $dailyRate * $daysInMonth;

        $remaining = $monthlyBudget > 0 ? $monthlyBudget - $totalSpent : 0;
        $percentUsed = $monthlyBudget > 0 ? round(($totalSpent / $monthlyBudget) * 100, 1) : 0;

        echo json_encode([
            'success' => true,
            'budget' => [
                'monthly_budget' => $monthlyBudget,
                'total_spent' => round($totalSpent, 2),
                'remaining' => round($remaining, 2),
                'percent_used' => $percentUsed,
                'avg_monthly' => round($avgMonthly, 2),
                'projected_total' => round($projectedTotal, 2),
                'month_progress' => $monthProgress,
                'days_remaining' => $daysInMonth - $today,
                'will_exceed' => $monthlyBudget > 0 && $projectedTotal > $monthlyBudget
            ]
        ]);

        $conn->close();
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => $e->getMessage()]);
    }
}

function setMonthlyBudget($userId) {
    try {
        $data = json_decode(file_get_contents('php://input'), true);
        $budget = floatval($data['monthly_budget'] ?? 0);

        if ($budget < 0) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Budget must be positive']);
            return;
        }

        $conn = getDBConnection();

        // Upsert into user_preferences
        $stmt = $conn->prepare("
            INSERT INTO user_preferences (user_id, monthly_budget)
            VALUES (?, ?)
            ON DUPLICATE KEY UPDATE monthly_budget = VALUES(monthly_budget)
        ");
        $stmt->bind_param("id", $userId, $budget);
        $stmt->execute();

        echo json_encode([
            'success' => true,
            'message' => 'Monthly budget updated',
            'monthly_budget' => $budget
        ]);

        $conn->close();
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => $e->getMessage()]);
    }
}
