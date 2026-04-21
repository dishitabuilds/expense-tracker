<?php
/**
 * Spark Summary API
 * Reads data from Spark-generated summary tables
 * 
 * Endpoints:
 *   GET ?action=monthly          → Monthly summary data
 *   GET ?action=category&month=X&year=Y → Category breakdown
 *   GET ?action=trends&period=week|month|year → Trend data for charts
 *   GET ?action=insights         → Smart spending insights
 *   GET ?action=recommendations  → Smart recommendations
 *   GET ?action=last_run         → Last Spark run timestamp
 *   GET ?action=overview         → All data combined (for dashboard load)
 */

require_once '../config/database.php';
require_once '../config/session.php';

requireLogin();
header('Content-Type: application/json');

$userId = getCurrentUserId();
$action = $_GET['action'] ?? 'overview';

switch ($action) {
    case 'monthly':
        getMonthlyData($userId);
        break;
    case 'category':
        getCategoryData($userId);
        break;
    case 'trends':
        getTrendData($userId);
        break;
    case 'insights':
        getInsights($userId);
        break;
    case 'recommendations':
        getRecommendations($userId);
        break;
    case 'last_run':
        getLastRun($userId);
        break;
    case 'overview':
        getOverview($userId);
        break;
    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid action']);
}

/**
 * Monthly Summary — all months for the user
 */
function getMonthlyData($userId) {
    try {
        $conn = getDBConnection();
        
        $stmt = $conn->prepare("
            SELECT year, month, month_name, total_amount, 
                   transaction_count, avg_amount, max_amount, min_amount,
                   generated_at
            FROM monthly_summary
            WHERE user_id = ?
            ORDER BY year DESC, month DESC
            LIMIT 24
        ");
        $stmt->bind_param("i", $userId);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $data = [];
        $grandTotal = 0;
        $monthCount = 0;
        
        while ($row = $result->fetch_assoc()) {
            $row['total_amount'] = floatval($row['total_amount']);
            $row['avg_amount'] = floatval($row['avg_amount']);
            $row['max_amount'] = floatval($row['max_amount']);
            $row['min_amount'] = floatval($row['min_amount']);
            $row['transaction_count'] = intval($row['transaction_count']);
            $data[] = $row;
            $grandTotal += $row['total_amount'];
            $monthCount++;
        }
        
        echo json_encode([
            'success' => true,
            'data' => $data,
            'summary' => [
                'grand_total' => round($grandTotal, 2),
                'avg_monthly' => $monthCount > 0 ? round($grandTotal / $monthCount, 2) : 0,
                'months_covered' => $monthCount
            ]
        ]);
        
        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Category Breakdown — optionally filtered by month/year
 */
function getCategoryData($userId) {
    try {
        $conn = getDBConnection();
        
        $month = intval($_GET['month'] ?? date('n'));
        $year = intval($_GET['year'] ?? date('Y'));
        
        $stmt = $conn->prepare("
            SELECT category_name, category_color, total_amount, 
                   transaction_count, percentage, avg_amount,
                   generated_at
            FROM category_summary
            WHERE user_id = ? AND year = ? AND month = ?
            ORDER BY total_amount DESC
        ");
        $stmt->bind_param("iii", $userId, $year, $month);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $data = [];
        while ($row = $result->fetch_assoc()) {
            $row['total_amount'] = floatval($row['total_amount']);
            $row['percentage'] = floatval($row['percentage']);
            $row['avg_amount'] = floatval($row['avg_amount']);
            $row['transaction_count'] = intval($row['transaction_count']);
            $data[] = $row;
        }
        
        echo json_encode([
            'success' => true,
            'data' => $data,
            'filters' => ['month' => $month, 'year' => $year]
        ]);
        
        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Trend Data — weekly, monthly, or yearly
 */
function getTrendData($userId) {
    try {
        $conn = getDBConnection();
        
        $period = $_GET['period'] ?? 'monthly';
        $validPeriods = ['weekly', 'monthly', 'yearly'];
        
        if (!in_array($period, $validPeriods)) {
            $period = 'monthly';
        }
        
        $stmt = $conn->prepare("
            SELECT period_type, period_label, period_start, period_end,
                   total_amount, transaction_count, avg_daily,
                   generated_at
            FROM trend_summary
            WHERE user_id = ? AND period_type = ?
            ORDER BY period_start ASC
        ");
        $stmt->bind_param("is", $userId, $period);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $data = [];
        while ($row = $result->fetch_assoc()) {
            $row['total_amount'] = floatval($row['total_amount']);
            $row['avg_daily'] = floatval($row['avg_daily']);
            $row['transaction_count'] = intval($row['transaction_count']);
            $data[] = $row;
        }
        
        echo json_encode([
            'success' => true,
            'data' => $data,
            'period' => $period
        ]);
        
        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Smart Insights (2 per user)
 */
function getInsights($userId) {
    try {
        $conn = getDBConnection();
        
        $stmt = $conn->prepare("
            SELECT insight_type, category, message, severity, 
                   score, metadata, generated_at
            FROM spark_insights
            WHERE user_id = ?
            ORDER BY score DESC
            LIMIT 2
        ");
        $stmt->bind_param("i", $userId);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $data = [];
        while ($row = $result->fetch_assoc()) {
            $row['score'] = floatval($row['score']);
            if ($row['metadata']) {
                $row['metadata'] = json_decode($row['metadata'], true);
            }
            $data[] = $row;
        }
        
        echo json_encode(['success' => true, 'insights' => $data]);
        
        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Smart Recommendations (2 per user)
 */
function getRecommendations($userId) {
    try {
        $conn = getDBConnection();
        
        $stmt = $conn->prepare("
            SELECT rec_type, category, message, priority, 
                   potential_savings, current_spending, metadata, generated_at
            FROM spark_recommendations
            WHERE user_id = ?
            ORDER BY potential_savings DESC
            LIMIT 2
        ");
        $stmt->bind_param("i", $userId);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $data = [];
        while ($row = $result->fetch_assoc()) {
            $row['potential_savings'] = floatval($row['potential_savings']);
            $row['current_spending'] = floatval($row['current_spending']);
            if ($row['metadata']) {
                $row['metadata'] = json_decode($row['metadata'], true);
            }
            $data[] = $row;
        }
        
        echo json_encode(['success' => true, 'recommendations' => $data]);
        
        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Last Spark Run Timestamp
 */
function getLastRun($userId) {
    try {
        $conn = getDBConnection();
        
        // Check the most recent generated_at across summary tables
        $result = $conn->query("
            SELECT MAX(generated_at) as last_run FROM (
                SELECT MAX(generated_at) as generated_at FROM monthly_summary WHERE user_id = $userId
                UNION ALL
                SELECT MAX(generated_at) as generated_at FROM category_summary WHERE user_id = $userId
                UNION ALL
                SELECT MAX(generated_at) as generated_at FROM trend_summary WHERE user_id = $userId
            ) t
        ");
        
        $row = $result->fetch_assoc();
        
        echo json_encode([
            'success' => true,
            'last_run' => $row['last_run'] ?? null,
            'has_data' => !empty($row['last_run'])
        ]);
        
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Overview — combined data for initial dashboard load
 */
function getOverview($userId) {
    try {
        $conn = getDBConnection();
        
        // Monthly data (last 12 months)
        $monthlyStmt = $conn->prepare("
            SELECT year, month, month_name, total_amount, transaction_count, 
                   avg_amount, max_amount, min_amount
            FROM monthly_summary
            WHERE user_id = ?
            ORDER BY year DESC, month DESC
            LIMIT 12
        ");
        $monthlyStmt->bind_param("i", $userId);
        $monthlyStmt->execute();
        $monthlyResult = $monthlyStmt->get_result();
        $monthly = [];
        $grandTotal = 0;
        while ($row = $monthlyResult->fetch_assoc()) {
            $row['total_amount'] = floatval($row['total_amount']);
            $row['avg_amount'] = floatval($row['avg_amount']);
            $row['max_amount'] = floatval($row['max_amount']);
            $row['min_amount'] = floatval($row['min_amount']);
            $monthly[] = $row;
            $grandTotal += $row['total_amount'];
        }
        
        // Category data (current month)
        $curMonth = intval(date('n'));
        $curYear = intval(date('Y'));
        $catStmt = $conn->prepare("
            SELECT category_name, category_color, total_amount, percentage, transaction_count
            FROM category_summary
            WHERE user_id = ? AND year = ? AND month = ?
            ORDER BY total_amount DESC
        ");
        $catStmt->bind_param("iii", $userId, $curYear, $curMonth);
        $catStmt->execute();
        $catResult = $catStmt->get_result();
        $categories = [];
        while ($row = $catResult->fetch_assoc()) {
            $row['total_amount'] = floatval($row['total_amount']);
            $row['percentage'] = floatval($row['percentage']);
            $categories[] = $row;
        }
        
        // Insights
        $insStmt = $conn->prepare("
            SELECT insight_type, category, message, severity, score, metadata
            FROM spark_insights WHERE user_id = ? ORDER BY score DESC LIMIT 2
        ");
        $insStmt->bind_param("i", $userId);
        $insStmt->execute();
        $insResult = $insStmt->get_result();
        $insights = [];
        while ($row = $insResult->fetch_assoc()) {
            $row['score'] = floatval($row['score']);
            if ($row['metadata']) $row['metadata'] = json_decode($row['metadata'], true);
            $insights[] = $row;
        }
        
        // Recommendations
        $recStmt = $conn->prepare("
            SELECT rec_type, category, message, priority, potential_savings, current_spending, metadata
            FROM spark_recommendations WHERE user_id = ? ORDER BY potential_savings DESC LIMIT 2
        ");
        $recStmt->bind_param("i", $userId);
        $recStmt->execute();
        $recResult = $recStmt->get_result();
        $recommendations = [];
        while ($row = $recResult->fetch_assoc()) {
            $row['potential_savings'] = floatval($row['potential_savings']);
            $row['current_spending'] = floatval($row['current_spending']);
            if ($row['metadata']) $row['metadata'] = json_decode($row['metadata'], true);
            $recommendations[] = $row;
        }
        
        // Last run
        $lastRunResult = $conn->query("
            SELECT MAX(generated_at) as last_run FROM monthly_summary WHERE user_id = $userId
        ");
        $lastRun = $lastRunResult->fetch_assoc()['last_run'] ?? null;
        
        echo json_encode([
            'success' => true,
            'monthly' => $monthly,
            'categories' => $categories,
            'insights' => $insights,
            'recommendations' => $recommendations,
            'summary' => [
                'grand_total' => round($grandTotal, 2),
                'avg_monthly' => count($monthly) > 0 ? round($grandTotal / count($monthly), 2) : 0,
                'months_covered' => count($monthly),
                'total_categories' => count($categories)
            ],
            'last_run' => $lastRun,
            'has_data' => !empty($lastRun)
        ]);
        
        $conn->close();
    } catch (Exception $e) {
        handleError($e);
    }
}

/**
 * Error handler
 */
function handleError($e) {
    error_log("Spark Summary API Error: " . $e->getMessage());
    
    // Check if table doesn't exist (Spark hasn't run yet)
    if (strpos($e->getMessage(), "doesn't exist") !== false) {
        echo json_encode([
            'success' => false,
            'message' => 'Spark analytics have not been run yet. Please run the Spark job first.',
            'spark_not_run' => true
        ]);
    } else {
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'message' => 'Failed to fetch data: ' . $e->getMessage()
        ]);
    }
}
?>
