<?php
/**
 * Smart Spending Suggestions API (Refactored)
 * Priority-aware insights based on category importance + budget + spending
 */

require_once '../config/database.php';
require_once '../config/session.php';

requireLogin();
header('Content-Type: application/json');

$userId = getCurrentUserId();

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    generateSmartSuggestions($userId);
} else {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
}

function generateSmartSuggestions($userId) {
    try {
        $conn = getDBConnection();

        // 1. Get category spending with priority + budget info
        $categoryData = getCategorySpending($conn, $userId);

        // 2. Get monthly budget
        $monthlyBudget = getMonthlyBudget($conn, $userId);

        // 3. Get total current month spending
        $totalSpent = array_sum(array_column($categoryData, 'current_spending'));

        // 4. Generate priority-aware insights (pick best 2)
        $insights = generatePriorityInsights($categoryData, $monthlyBudget, $totalSpent);

        // 5. Generate smart recommendations (pick best 2)
        $recommendations = generateSmartRecommendations($categoryData);

        echo json_encode([
            'success' => true,
            'generated_at' => date('Y-m-d H:i:s'),
            'insights' => array_slice($insights, 0, 2),
            'recommendations' => array_slice($recommendations, 0, 2),
            'spending_alerts' => [],
            'category_analysis' => $categoryData
        ]);

        $conn->close();
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => $e->getMessage()]);
    }
}

/**
 * Get each category's current month spending, budget, priority, and trend
 */
function getCategorySpending($conn, $userId) {
    // Current month spending per category
    $stmt = $conn->prepare("
        SELECT 
            c.id, c.name, c.color, c.budget, c.priority,
            COALESCE(SUM(e.amount), 0) as current_spending,
            COUNT(e.id) as transaction_count
        FROM categories c
        LEFT JOIN expenses e ON c.id = e.category_id 
            AND e.user_id = ?
            AND MONTH(e.expense_date) = MONTH(CURDATE())
            AND YEAR(e.expense_date) = YEAR(CURDATE())
        WHERE c.user_id = ?
        GROUP BY c.id, c.name, c.color, c.budget, c.priority
        ORDER BY current_spending DESC
    ");
    $stmt->bind_param("ii", $userId, $userId);
    $stmt->execute();
    $result = $stmt->get_result();

    $categories = [];
    while ($row = $result->fetch_assoc()) {
        $spending = floatval($row['current_spending']);
        $budget = floatval($row['budget']);
        $priority = $row['priority'] ?: 'moderate';

        // Calculate % of budget used
        $budgetPercent = ($budget > 0) ? round(($spending / $budget) * 100, 1) : 0;

        // Get last 3 months trend for this category
        $trend = getCategoryTrend($conn, $userId, $row['id']);

        $categories[] = [
            'id' => intval($row['id']),
            'name' => $row['name'],
            'color' => $row['color'],
            'budget' => $budget,
            'priority' => $priority,
            'current_spending' => round($spending, 2),
            'transaction_count' => intval($row['transaction_count']),
            'budget_percent' => $budgetPercent,
            'has_budget' => $budget > 0,
            'trend' => $trend
        ];
    }

    return $categories;
}

/**
 * Simple trend calculation: compare this month vs avg of last 3 months
 */
function getCategoryTrend($conn, $userId, $categoryId) {
    $stmt = $conn->prepare("
        SELECT COALESCE(AVG(monthly_total), 0) as avg_monthly
        FROM (
            SELECT SUM(amount) as monthly_total
            FROM expenses
            WHERE user_id = ? AND category_id = ?
              AND expense_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
              AND NOT (MONTH(expense_date) = MONTH(CURDATE()) AND YEAR(expense_date) = YEAR(CURDATE()))
            GROUP BY YEAR(expense_date), MONTH(expense_date)
        ) t
    ");
    $stmt->bind_param("ii", $userId, $categoryId);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();
    return round(floatval($row['avg_monthly']), 2);
}

/**
 * Get global monthly budget
 */
function getMonthlyBudget($conn, $userId) {
    $stmt = $conn->prepare("SELECT monthly_budget FROM user_preferences WHERE user_id = ?");
    $stmt->bind_param("i", $userId);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();
    return $row ? floatval($row['monthly_budget']) : 0;
}

/**
 * Generate priority-aware insights (max 2: 1 behavioral + 1 predictive)
 */
function generatePriorityInsights($categoryData, $monthlyBudget, $totalSpent) {
    $behavioral = [];
    $predictive = [];

    foreach ($categoryData as $cat) {
        if ($cat['current_spending'] <= 0) continue;

        $priority = $cat['priority'];
        $pct = $cat['budget_percent'];
        $name = $cat['name'];
        $spending = $cat['current_spending'];
        $budget = $cat['budget'];
        $avgPrev = $cat['trend'];

        // --- BEHAVIORAL INSIGHTS (based on priority + budget) ---

        if ($priority === 'discretionary') {
            // Always flag high discretionary spending
            if ($budget > 0 && $pct > 100) {
                $behavioral[] = [
                    'type' => 'spending_pattern',
                    'category' => $name,
                    'message' => "High spending on $name (discretionary) — ₹" . number_format($spending, 0) .
                        " spent, which is {$pct}% of your ₹" . number_format($budget, 0) .
                        " budget. Reducing this can significantly improve savings.",
                    'severity' => 'warning',
                    'score' => $pct + 100  // boost discretionary
                ];
            } elseif ($spending > 0 && (!$budget || $budget == 0)) {
                $behavioral[] = [
                    'type' => 'spending_pattern',
                    'category' => $name,
                    'message' => "You've spent ₹" . number_format($spending, 0) .
                        " on $name (discretionary) this month with no budget set. Consider setting a limit.",
                    'severity' => 'info',
                    'score' => 60
                ];
            }
        } elseif ($priority === 'moderate') {
            if ($budget > 0 && $pct > 100) {
                $behavioral[] = [
                    'type' => 'spending_pattern',
                    'category' => $name,
                    'message' => "Spending on $name is exceeding your budget — ₹" . number_format($spending, 0) .
                        " of ₹" . number_format($budget, 0) .
                        " ({$pct}%). Consider adjusting purchases.",
                    'severity' => 'warning',
                    'score' => $pct + 50
                ];
            }
        } elseif ($priority === 'essential') {
            // Only flag if > 120% of budget
            if ($budget > 0 && $pct > 120) {
                $behavioral[] = [
                    'type' => 'spending_pattern',
                    'category' => $name,
                    'message' => "Your essential spending on $name is ₹" . number_format($spending, 0) .
                        " ({$pct}% of budget). Consider optimizing usage where possible.",
                    'severity' => 'info',
                    'score' => $pct
                ];
            }
        }

        // --- PREDICTIVE INSIGHTS (trend-based) ---
        if ($avgPrev > 0) {
            $changePercent = round((($spending - $avgPrev) / $avgPrev) * 100, 1);
            if ($changePercent > 30) {
                $predictive[] = [
                    'type' => 'trend_prediction',
                    'category' => $name,
                    'message' => "Spending on $name has increased " . abs($changePercent) .
                        "% compared to your 3-month average (₹" . number_format($avgPrev, 0) .
                        " → ₹" . number_format($spending, 0) . "). This trend may continue next month.",
                    'severity' => $changePercent > 50 ? 'warning' : 'info',
                    'confidence' => $changePercent > 50 ? 'high' : 'medium',
                    'score' => abs($changePercent)
                ];
            } elseif ($changePercent < -20) {
                $predictive[] = [
                    'type' => 'trend_prediction',
                    'category' => $name,
                    'message' => "Great job! Spending on $name is down " . abs($changePercent) .
                        "% vs your average. Keep it up!",
                    'severity' => 'success',
                    'confidence' => 'high',
                    'score' => abs($changePercent) * 0.5  // lower priority for positive
                ];
            }
        }
    }

    // Global budget insight
    if ($monthlyBudget > 0 && $totalSpent > 0) {
        $globalPct = round(($totalSpent / $monthlyBudget) * 100, 1);
        $today = intval(date('j'));
        $daysInMonth = intval(date('t'));
        $dailyRate = $totalSpent / max($today, 1);
        $projected = $dailyRate * $daysInMonth;

        if ($projected > $monthlyBudget) {
            $predictive[] = [
                'type' => 'trend_prediction',
                'category' => 'Overall Budget',
                'message' => "You've used {$globalPct}% of your monthly budget (₹" . number_format($totalSpent, 0) .
                    " of ₹" . number_format($monthlyBudget, 0) .
                    "). At this rate, you're likely to exceed your budget by ₹" .
                    number_format($projected - $monthlyBudget, 0) . ".",
                'severity' => 'warning',
                'confidence' => 'high',
                'score' => 200  // highest priority
            ];
        } elseif ($globalPct > 60) {
            $predictive[] = [
                'type' => 'trend_prediction',
                'category' => 'Overall Budget',
                'message' => "You've used {$globalPct}% of your ₹" . number_format($monthlyBudget, 0) .
                    " monthly budget with " . ($daysInMonth - $today) . " days remaining.",
                'severity' => 'info',
                'confidence' => 'medium',
                'score' => $globalPct
            ];
        }
    }

    // Sort by score descending, pick top 1 of each type
    usort($behavioral, fn($a, $b) => $b['score'] - $a['score']);
    usort($predictive, fn($a, $b) => $b['score'] - $a['score']);

    $result = [];
    if (!empty($behavioral)) $result[] = $behavioral[0];
    if (!empty($predictive)) $result[] = $predictive[0];

    // Fallback if we have no insights
    if (empty($result) && $totalSpent > 0) {
        $result[] = [
            'type' => 'spending_pattern',
            'category' => 'All Categories',
            'message' => "You've spent ₹" . number_format($totalSpent, 0) . " this month across " .
                count(array_filter($categoryData, fn($c) => $c['current_spending'] > 0)) . " categories.",
            'severity' => 'info',
            'score' => 0
        ];
    }

    return $result;
}

/**
 * Generate smart recommendations (max 2)
 * Priority: Discretionary overspend → Moderate overspend → Essential overspend
 */
function generateSmartRecommendations($categoryData) {
    $recommendations = [];

    // Score each category for recommendation priority
    foreach ($categoryData as $cat) {
        if ($cat['current_spending'] <= 0) continue;

        $priority = $cat['priority'];
        $pct = $cat['budget_percent'];
        $spending = $cat['current_spending'];
        $budget = $cat['budget'];
        $name = $cat['name'];

        // Priority multiplier: discretionary=3, moderate=2, essential=1
        $priorityMultiplier = ['discretionary' => 3, 'moderate' => 2, 'essential' => 1];
        $mult = $priorityMultiplier[$priority] ?? 2;

        if ($budget > 0 && $pct > 100) {
            $overspend = $spending - $budget;
            $suggestedSaving = round($overspend * 0.8, 2); // suggest saving 80% of overspend
            $score = $pct * $mult;

            if ($priority === 'essential') {
                $actionMsg = "Optimize your $name spending — try to find more efficient alternatives.";
                $recType = 'set_budget';
            } elseif ($priority === 'moderate') {
                $actionMsg = "Consider adjusting your $name purchases to stay within budget.";
                $recType = 'reduce_spending';
            } else {
                $actionMsg = "Reduce discretionary spending on $name to boost your savings.";
                $recType = 'reduce_spending';
            }

            $recommendations[] = [
                'type' => $recType,
                'priority' => ($score > 300) ? 'high' : (($score > 150) ? 'medium' : 'low'),
                'category' => $name,
                'message' => $actionMsg,
                'overspend_percent' => round($pct - 100, 1),
                'potential_savings' => $suggestedSaving,
                'current_spending' => $spending,
                'budget' => $budget,
                'category_priority' => $priority,
                'actionable' => true,
                'score' => $score
            ];
        } elseif (!$cat['has_budget'] && $spending > 500) {
            // No budget set but meaningful spending
            $suggestedBudget = round($spending * 1.1, 2);
            $score = 50 * $mult;

            $recommendations[] = [
                'type' => 'set_budget',
                'priority' => 'medium',
                'category' => $name,
                'message' => "Set a budget of ₹" . number_format($suggestedBudget, 0) .
                    " for $name based on current spending.",
                'suggested_budget' => $suggestedBudget,
                'current_spending' => $spending,
                'category_priority' => $priority,
                'actionable' => true,
                'score' => $score
            ];
        }
    }

    // Sort by score (highest first = most actionable)
    usort($recommendations, fn($a, $b) => $b['score'] - $a['score']);

    return array_slice($recommendations, 0, 2);
}
