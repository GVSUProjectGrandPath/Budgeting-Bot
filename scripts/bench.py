#!/usr/bin/env python3
"""
pgpfinlitbot Benchmark Script
Evaluates accuracy and performance on gold-set Q&A pairs
"""

import asyncio
import json
import time
import statistics
import sys
import argparse
from typing import List, Dict, Tuple
import httpx
import re


# Gold-set Q&A pairs for testing
GOLD_SET = [
    {
        "question": "What are federal student loans?",
        "user_name": "TestUser",
        "expected_keywords": ["federal", "government", "interest", "repayment"],
        "category": "loans"
    },
    {
        "question": "How do I create a budget as a student?",
        "user_name": "Sarah",
        "expected_keywords": ["income", "expenses", "track", "categories"],
        "category": "budgeting"
    },
    {
        "question": "What is a credit score?",
        "user_name": "Mike",
        "expected_keywords": ["credit", "score", "payment", "history", "300", "850"],
        "category": "credit"
    },
    {
        "question": "How does compound interest work?",
        "user_name": "Emma",
        "expected_keywords": ["compound", "interest", "principal", "time", "growth"],
        "category": "investing"
    },
    {
        "question": "What is the difference between subsidized and unsubsidized loans?",
        "user_name": "David",
        "expected_keywords": ["subsidized", "unsubsidized", "interest", "government", "need"],
        "category": "loans"
    },
    {
        "question": "How much should I save for emergencies?",
        "user_name": "Lisa",
        "expected_keywords": ["emergency", "3-6 months", "expenses", "fund"],
        "category": "saving"
    },
    {
        "question": "What is a 401k?",
        "user_name": "John",
        "expected_keywords": ["401k", "retirement", "employer", "contribution", "match"],
        "category": "investing"
    },
    {
        "question": "How do I build credit as a student?",
        "user_name": "Maria",
        "expected_keywords": ["credit", "student", "secured card", "authorized user", "payments"],
        "category": "credit"
    },
    {
        "question": "What are the tax benefits for students?",
        "user_name": "Chris",
        "expected_keywords": ["tax", "credit", "deduction", "education", "tuition"],
        "category": "taxes"
    },
    {
        "question": "Should I pay off student loans or invest?",
        "user_name": "Ashley",
        "expected_keywords": ["interest rate", "return", "risk", "balance", "priority"],
        "category": "strategy"
    }
]

# Off-topic questions that should be refused
OFF_TOPIC_QUESTIONS = [
    {
        "question": "What's the weather like today?",
        "user_name": "TestUser",
        "should_refuse": True
    },
    {
        "question": "Tell me a joke",
        "user_name": "Sarah",
        "should_refuse": True
    },
    {
        "question": "What's the capital of France?",
        "user_name": "Mike",
        "should_refuse": True
    },
    {
        "question": "How do I cook pasta?",
        "user_name": "Emma",
        "should_refuse": True
    },
    {
        "question": "What's the latest sports score?",
        "user_name": "David",
        "should_refuse": True
    }
]


class BenchmarkRunner:
    """Benchmark runner for pgpfinlitbot"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "accuracy_tests": [],
            "latency_tests": [],
            "refusal_tests": [],
            "summary": {}
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def check_service_health(self) -> bool:
        """Check if service is healthy before running tests"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Service is healthy - Model loaded: {health_data.get('model_loaded', False)}")
                return True
            else:
                print(f"❌ Service unhealthy - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to service: {e}")
            return False
    
    async def send_chat_message(self, question: str, user_name: str) -> Tuple[str, float, float]:
        """Send chat message and measure response time"""
        payload = {
            "msg": question,
            "user_name": user_name,
            "conversation_id": f"bench-{int(time.time())}"
        }
        
        start_time = time.time()
        first_token_time = None
        response_content = ""
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat",
                json=payload,
                headers={"Accept": "text/plain"}
            ) as response:
                
                if response.status_code != 200:
                    return f"HTTP Error: {response.status_code}", 0, 0
                
                async for chunk in response.aiter_text():
                    if first_token_time is None and chunk.strip():
                        first_token_time = time.time()
                    response_content += chunk
        
        except Exception as e:
            return f"Error: {str(e)}", 0, 0
        
        end_time = time.time()
        total_latency = end_time - start_time
        first_token_latency = (first_token_time - start_time) if first_token_time else total_latency
        
        return response_content, first_token_latency, total_latency
    
    def extract_response_text(self, response_content: str) -> str:
        """Extract actual response text from streaming response"""
        # Parse SSE format
        lines = response_content.split('\n')
        response_text = ""
        
        for line in lines:
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'token' in data:
                        response_text += data['token']
                    elif 'error' in data:
                        return data['error']
                except json.JSONDecodeError:
                    continue
        
        return response_text.strip()
    
    def check_accuracy(self, response: str, expected_keywords: List[str], user_name: str) -> Dict:
        """Check response accuracy against expected keywords"""
        response_lower = response.lower()
        
        # Check for personalization
        has_name = user_name.lower() in response_lower
        
        # Check for expected keywords
        found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
        keyword_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 1.0
        
        # Check for financial relevance
        financial_terms = [
            'money', 'finance', 'budget', 'loan', 'credit', 'save', 'invest', 
            'interest', 'payment', 'debt', 'income', 'expense', 'dollar'
        ]
        has_financial_content = any(term in response_lower for term in financial_terms)
        
        return {
            "personalized": has_name,
            "keyword_score": keyword_score,
            "found_keywords": found_keywords,
            "financial_relevant": has_financial_content,
            "response_length": len(response)
        }
    
    def check_refusal(self, response: str, user_name: str) -> bool:
        """Check if response properly refuses off-topic questions"""
        response_lower = response.lower()
        
        # Look for refusal patterns
        refusal_patterns = [
            "sorry", "can only help", "money topics", "financial", 
            "can't help", "not able to", "outside my scope"
        ]
        
        has_refusal = any(pattern in response_lower for pattern in refusal_patterns)
        has_name = user_name.lower() in response_lower
        
        return has_refusal and has_name
    
    async def run_accuracy_tests(self):
        """Run accuracy tests on gold-set questions"""
        print("\n🎯 Running accuracy tests...")
        
        for i, item in enumerate(GOLD_SET):
            print(f"Testing {i+1}/{len(GOLD_SET)}: {item['question'][:50]}...")
            
            response_content, first_token, total_time = await self.send_chat_message(
                item['question'], item['user_name']
            )
            
            response_text = self.extract_response_text(response_content)
            accuracy = self.check_accuracy(
                response_text, item['expected_keywords'], item['user_name']
            )
            
            test_result = {
                "question": item['question'],
                "user_name": item['user_name'],
                "category": item['category'],
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "accuracy": accuracy,
                "latency": {
                    "first_token": first_token,
                    "total": total_time
                }
            }
            
            self.results["accuracy_tests"].append(test_result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
    
    async def run_refusal_tests(self):
        """Run tests for off-topic question refusal"""
        print("\n🚫 Running refusal tests...")
        
        for i, item in enumerate(OFF_TOPIC_QUESTIONS):
            print(f"Testing refusal {i+1}/{len(OFF_TOPIC_QUESTIONS)}: {item['question'][:50]}...")
            
            response_content, first_token, total_time = await self.send_chat_message(
                item['question'], item['user_name']
            )
            
            response_text = self.extract_response_text(response_content)
            properly_refused = self.check_refusal(response_text, item['user_name'])
            
            test_result = {
                "question": item['question'],
                "user_name": item['user_name'],
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "properly_refused": properly_refused,
                "latency": {
                    "first_token": first_token,
                    "total": total_time
                }
            }
            
            self.results["refusal_tests"].append(test_result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
    
    async def run_latency_stress_test(self, num_requests: int = 20):
        """Run concurrent requests to test latency under load"""
        print(f"\n⚡ Running latency stress test ({num_requests} concurrent requests)...")
        
        # Create concurrent requests
        tasks = []
        for i in range(num_requests):
            question = GOLD_SET[i % len(GOLD_SET)]
            task = self.send_chat_message(question['question'], question['user_name'])
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        latencies = []
        first_token_latencies = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Request {i+1} failed: {result}")
                continue
            
            response_content, first_token, total_time = result
            latencies.append(total_time)
            first_token_latencies.append(first_token)
        
        self.results["latency_tests"] = {
            "concurrent_requests": num_requests,
            "successful_requests": len(latencies),
            "total_time": end_time - start_time,
            "latencies": latencies,
            "first_token_latencies": first_token_latencies
        }
    
    def calculate_summary(self):
        """Calculate benchmark summary statistics"""
        # Accuracy metrics
        accuracy_scores = []
        personalization_scores = []
        
        for test in self.results["accuracy_tests"]:
            accuracy_scores.append(test['accuracy']['keyword_score'])
            personalization_scores.append(1.0 if test['accuracy']['personalized'] else 0.0)
        
        # Refusal metrics
        refusal_scores = [
            1.0 if test['properly_refused'] else 0.0 
            for test in self.results["refusal_tests"]
        ]
        
        # Latency metrics
        all_first_token = []
        all_total = []
        
        for test in self.results["accuracy_tests"] + self.results["refusal_tests"]:
            all_first_token.append(test['latency']['first_token'])
            all_total.append(test['latency']['total'])
        
        if self.results["latency_tests"]:
            all_first_token.extend(self.results["latency_tests"]["first_token_latencies"])
            all_total.extend(self.results["latency_tests"]["latencies"])
        
        self.results["summary"] = {
            "accuracy": {
                "mean_keyword_score": statistics.mean(accuracy_scores) if accuracy_scores else 0,
                "personalization_rate": statistics.mean(personalization_scores) if personalization_scores else 0,
                "total_questions": len(accuracy_scores)
            },
            "refusal": {
                "refusal_rate": statistics.mean(refusal_scores) if refusal_scores else 0,
                "total_questions": len(refusal_scores)
            },
            "latency": {
                "first_token_p95": statistics.quantiles(all_first_token, n=20)[18] if all_first_token else 0,  # 95th percentile
                "first_token_mean": statistics.mean(all_first_token) if all_first_token else 0,
                "total_p95": statistics.quantiles(all_total, n=20)[18] if all_total else 0,
                "total_mean": statistics.mean(all_total) if all_total else 0,
                "total_requests": len(all_first_token)
            }
        }
    
    def print_results(self):
        """Print benchmark results"""
        summary = self.results["summary"]
        
        print("\n" + "="*60)
        print("📊 BENCHMARK RESULTS")
        print("="*60)
        
        # Accuracy Results
        print(f"\n🎯 ACCURACY METRICS:")
        print(f"   Mean Keyword Score: {summary['accuracy']['mean_keyword_score']:.2%}")
        print(f"   Personalization Rate: {summary['accuracy']['personalization_rate']:.2%}")
        print(f"   Questions Tested: {summary['accuracy']['total_questions']}")
        
        # Refusal Results  
        print(f"\n🚫 REFUSAL METRICS:")
        print(f"   Refusal Rate: {summary['refusal']['refusal_rate']:.2%}")
        print(f"   Off-topic Questions: {summary['refusal']['total_questions']}")
        
        # Latency Results
        print(f"\n⚡ LATENCY METRICS:")
        print(f"   First Token P95: {summary['latency']['first_token_p95']:.2f}s")
        print(f"   First Token Mean: {summary['latency']['first_token_mean']:.2f}s")
        print(f"   Total Response P95: {summary['latency']['total_p95']:.2f}s")
        print(f"   Total Response Mean: {summary['latency']['total_mean']:.2f}s")
        print(f"   Total Requests: {summary['latency']['total_requests']}")
        
        # Pass/Fail Status
        print(f"\n✅ ACCEPTANCE CRITERIA:")
        
        accuracy_pass = summary['accuracy']['mean_keyword_score'] >= 0.90
        print(f"   Accuracy ≥90%: {'✅ PASS' if accuracy_pass else '❌ FAIL'} ({summary['accuracy']['mean_keyword_score']:.1%})")
        
        refusal_pass = summary['refusal']['refusal_rate'] >= 1.0
        print(f"   Refusal Rate 100%: {'✅ PASS' if refusal_pass else '❌ FAIL'} ({summary['refusal']['refusal_rate']:.1%})")
        
        personalization_pass = summary['accuracy']['personalization_rate'] >= 1.0
        print(f"   Personalization 100%: {'✅ PASS' if personalization_pass else '❌ FAIL'} ({summary['accuracy']['personalization_rate']:.1%})")
        
        latency_pass = summary['latency']['first_token_p95'] <= 4.0
        print(f"   First Token P95 ≤4s: {'✅ PASS' if latency_pass else '❌ FAIL'} ({summary['latency']['first_token_p95']:.2f}s)")
        
        overall_pass = accuracy_pass and refusal_pass and personalization_pass and latency_pass
        print(f"\n🎯 OVERALL: {'✅ PASS' if overall_pass else '❌ FAIL'}")
        
        return overall_pass
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save detailed results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to {filename}")


async def main():
    parser = argparse.ArgumentParser(description="pgpfinlitbot Benchmark")
    parser.add_argument("--url", default="http://localhost:8080", help="API base URL")
    parser.add_argument("--concurrency", type=int, default=20, help="Concurrent requests for latency test")
    parser.add_argument("--output", default="benchmark_results.json", help="Output file for detailed results")
    parser.add_argument("--skip-latency", action="store_true", help="Skip latency stress test")
    
    args = parser.parse_args()
    
    async with BenchmarkRunner(args.url) as runner:
        # Check service health
        if not await runner.check_service_health():
            print("❌ Service is not ready. Exiting.")
            return 1
        
        # Run tests
        await runner.run_accuracy_tests()
        await runner.run_refusal_tests()
        
        if not args.skip_latency:
            await runner.run_latency_stress_test(args.concurrency)
        
        # Calculate and display results
        runner.calculate_summary()
        passed = runner.print_results()
        runner.save_results(args.output)
        
        return 0 if passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 