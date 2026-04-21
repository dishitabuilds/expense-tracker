<?php
/**
 * ============================================================================
 * AI Category Prediction API Bridge
 * ============================================================================
 * Bridges the PHP frontend to the Python Flask prediction API.
 * Receives expense description + amount, forwards to Flask, returns prediction.
 * 
 * Flask API must be running: python ml/predict_api.py (localhost:5000)
 * ============================================================================
 */

header('Content-Type: application/json');

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit;
}

// Get JSON input
$input = json_decode(file_get_contents('php://input'), true);

if (!$input || empty($input['description'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Description is required']);
    exit;
}

$description = trim($input['description']);
$amount = isset($input['amount']) ? floatval($input['amount']) : 0;

// Flask API URL
$flask_url = 'http://localhost:5000/predict';

// Prepare request to Flask API
$payload = json_encode([
    'description' => $description,
    'amount' => $amount
]);

// Use cURL to call Flask API
$ch = curl_init($flask_url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'Accept: application/json'
    ],
    CURLOPT_TIMEOUT => 5,          // 5 second timeout
    CURLOPT_CONNECTTIMEOUT => 2    // 2 second connection timeout
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

// Handle errors
if ($error) {
    http_response_code(503);
    echo json_encode([
        'error' => 'AI prediction service unavailable',
        'detail' => 'Make sure Flask API is running: python ml/predict_api.py',
        'curl_error' => $error
    ]);
    exit;
}

if ($http_code !== 200) {
    http_response_code($http_code);
    echo json_encode([
        'error' => 'Prediction service returned an error',
        'http_code' => $http_code,
        'response' => json_decode($response, true)
    ]);
    exit;
}

// Forward the Flask response
echo $response;
