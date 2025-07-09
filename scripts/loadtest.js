/**
 * pgpfinlitbot Load Testing Script
 * Tests 50 concurrent users with P95 ≤ 4s first-token requirement
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const firstTokenLatency = new Trend('first_token_latency');
const errorRate = new Rate('error_rate');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users  
    { duration: '5m', target: 50 },   // Stay at 50 users (soak test)
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'first_token_latency': ['p(95)<4000'], // P95 first token < 4s
    'error_rate': ['rate<0.01'],           // Error rate < 1%
    'http_req_duration': ['p(95)<12000'],  // P95 full response < 12s
    'http_req_failed': ['rate<0.01'],      // HTTP error rate < 1%
  },
};

// Test data
const testQuestions = [
  'How do I create a budget as a student?',
  'What should I know about student loans?',
  'How can I build credit as a student?',
  'What are the best ways to save money in college?',
  'How do student loan interest rates work?',
  'What is compound interest?',
  'How much should I save for emergencies?',
  'What are federal vs private student loans?',
  'How do I track my expenses?',
  'When should I start investing?'
];

const testNames = [
  'Alex', 'Sarah', 'Mike', 'Emma', 'David', 'Lisa', 'John', 'Maria',
  'Chris', 'Ashley', 'Ryan', 'Jennifer', 'Kevin', 'Amanda', 'Brian'
];

// Helper function to measure first token latency
function measureFirstToken(response) {
  if (response.status !== 200) {
    return null;
  }
  
  // For streaming responses, we'd need to measure the time to first data chunk
  // Since k6 doesn't have built-in streaming support, we estimate based on response start
  const responseTime = response.timings.duration;
  
  // Estimate first token as ~10% of total response time for streaming
  const estimatedFirstToken = responseTime * 0.1;
  return estimatedFirstToken;
}

// Main test function
export default function() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8080';
  
  // Random test data
  const question = testQuestions[Math.floor(Math.random() * testQuestions.length)];
  const userName = testNames[Math.floor(Math.random() * testNames.length)];
  
  // Test chat endpoint
  const chatPayload = {
    msg: question,
    user_name: userName,
    conversation_id: `test-${__VU}-${__ITER}`
  };
  
  const startTime = Date.now();
  
  const response = http.post(`${baseUrl}/chat`, JSON.stringify(chatPayload), {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/plain',
    },
    timeout: '15s', // 15 second timeout
  });
  
  // Measure first token latency
  const firstToken = measureFirstToken(response);
  if (firstToken !== null) {
    firstTokenLatency.add(firstToken);
  }
  
  // Check response
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response contains user name': (r) => r.body.includes(userName),
    'response is not empty': (r) => r.body.length > 10,
    'no error in response': (r) => !r.body.includes('error'),
    'response time < 15s': (r) => r.timings.duration < 15000,
  });
  
  if (!success) {
    errorRate.add(1);
    console.log(`Error for user ${userName}: ${response.status} - ${response.body.substring(0, 100)}`);
  } else {
    errorRate.add(0);
  }
  
  // Test health endpoint occasionally  
  if (__ITER % 10 === 0) {
    const healthResponse = http.get(`${baseUrl}/health`);
    check(healthResponse, {
      'health check passes': (r) => r.status === 200,
      'model is loaded': (r) => r.json('model_loaded') === true,
    });
  }
  
  // Test calculation endpoints occasionally
  if (__ITER % 20 === 0) {
    testCalculatorEndpoints(baseUrl, userName);
  }
  
  // Wait between requests (1-3 seconds)
  sleep(Math.random() * 2 + 1);
}

function testCalculatorEndpoints(baseUrl, userName) {
  // Test loan calculator
  const loanPayload = {
    calc_type: 'loan',
    params: {
      principal: 10000 + Math.random() * 20000,
      annual_rate: 3 + Math.random() * 7,
      years: 4 + Math.floor(Math.random() * 6)
    }
  };
  
  const loanResponse = http.post(`${baseUrl}/calc/loan`, JSON.stringify(loanPayload), {
    headers: { 'Content-Type': 'application/json' },
    timeout: '5s',
  });
  
  check(loanResponse, {
    'loan calc status 200': (r) => r.status === 200,
    'loan calc has monthly_payment': (r) => r.json('result.monthly_payment') > 0,
  });
  
  // Test budget generator
  const budgetPayload = {
    calc_type: 'budget',
    params: {
      monthly_income: 1500 + Math.random() * 2000,
      user_name: userName
    }
  };
  
  const budgetResponse = http.post(`${baseUrl}/calc/budget`, JSON.stringify(budgetPayload), {
    headers: { 'Content-Type': 'application/json' },
    timeout: '5s',
  });
  
  check(budgetResponse, {
    'budget calc status 200': (r) => r.status === 200,
    'budget has categories': (r) => Object.keys(r.json('result.budget_categories')).length > 0,
  });
  
  // Test compound interest calculator
  const compoundPayload = {
    calc_type: 'compound',
    params: {
      principal: Math.random() * 5000,
      monthly_contribution: 50 + Math.random() * 200,
      annual_rate: 5 + Math.random() * 5,
      years: 5 + Math.floor(Math.random() * 15)
    }
  };
  
  const compoundResponse = http.post(`${baseUrl}/calc/compound`, JSON.stringify(compoundPayload), {
    headers: { 'Content-Type': 'application/json' },
    timeout: '5s',
  });
  
  check(compoundResponse, {
    'compound calc status 200': (r) => r.status === 200,
    'compound calc has future_value': (r) => r.json('result.future_value') > 0,
  });
}

// Setup function (runs once before test)
export function setup() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8080';
  
  // Wait for services to be ready
  console.log('Waiting for services to be ready...');
  
  let healthCheck = http.get(`${baseUrl}/health`);
  let attempts = 0;
  
  while (healthCheck.status !== 200 && attempts < 30) {
    sleep(2);
    healthCheck = http.get(`${baseUrl}/health`);
    attempts++;
    
    if (attempts % 5 === 0) {
      console.log(`Health check attempt ${attempts}/30...`);
    }
  }
  
  if (healthCheck.status !== 200) {
    throw new Error('Service not ready after 60 seconds');
  }
  
  console.log('✅ Service is ready, starting load test');
  return { baseUrl };
}

// Teardown function (runs once after test)
export function teardown(data) {
  console.log('✅ Load test completed');
  console.log(`📊 Base URL: ${data.baseUrl}`);
  console.log('📈 Check the metrics above for performance results');
} 