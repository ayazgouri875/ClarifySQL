"""
Benchmark Evaluation Runner for QueryMind.
Executes the benchmark dataset and calculates:
- Ambiguity Detection Accuracy
- SQL Generation & Validation Accuracy
- Database Execution Accuracy
- Security Adversarial Rejection Accuracy
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.intent.models import QueryRequest
from app.services.query_service import query_service
from app.sql.validator import sql_validator

DATASET_PATH = os.path.join(os.path.dirname(__file__), "benchmark_dataset.json")

def run_evaluation():
    with open(DATASET_PATH, "r") as f:
        cases = json.load(f)

    results_by_type = {}
    total_cases = len(cases)
    passed_cases = 0

    print("=" * 75)
    print(" 🚀 QueryMind Comprehensive Benchmark Evaluation")
    print("=" * 75)

    for case in cases:
        q_id = case["id"]
        q_type = case["type"]
        question = case["question"]
        is_ambiguous_expected = case["is_ambiguous"]

        if q_type not in results_by_type:
            results_by_type[q_type] = {"total": 0, "correct": 0}
        results_by_type[q_type]["total"] += 1

        # Test Case 1: Security Adversarial Queries
        if q_type == "security_adversarial":
            is_valid, _, err = sql_validator.validate_and_sanitize(question)
            if not is_valid:
                results_by_type[q_type]["correct"] += 1
                passed_cases += 1
                print(f"[{q_id}] PASS (Security Blocked): {question}")
            else:
                print(f"[{q_id}] FAIL (Security Missed): {question}")
            continue

        # Test Case 2: Ambiguous queries requiring clarification
        if is_ambiguous_expected:
            req1 = QueryRequest(question=question)
            res1 = query_service.process_query(req1)

            if res1.status == "clarification_required" and res1.clarification:
                # Clarification detected correctly, now test resolution
                clarification_choice = case.get("test_clarification", res1.clarification.options[0])
                req2 = QueryRequest(
                    session_id=res1.session_id,
                    question=question,
                    selected_clarification=clarification_choice
                )
                res2 = query_service.process_query(req2)
                if res2.status == "success" and res2.data and res2.data.row_count > 0:
                    results_by_type[q_type]["correct"] += 1
                    passed_cases += 1
                    print(f"[{q_id}] PASS (Ambiguity Resolved): '{question}' -> '{clarification_choice}' ({res2.data.row_count} rows)")
                else:
                    print(f"[{q_id}] FAIL (Resolution Failed): '{question}'")
            else:
                print(f"[{q_id}] FAIL (Ambiguity Undetected): '{question}'")
            continue

        # Test Case 3: Clear direct queries
        req = QueryRequest(question=question)
        res = query_service.process_query(req)
        if res.status == "success" and res.data and res.data.row_count >= 0:
            results_by_type[q_type]["correct"] += 1
            passed_cases += 1
            print(f"[{q_id}] PASS (Direct Execution): '{question}' ({res.data.row_count} rows in {res.data.execution_time_ms}ms)")
        else:
            print(f"[{q_id}] FAIL (Query Failed): '{question}' - Error: {res.error_message}")

    print("\n" + "=" * 75)
    print(" 📊 EVALUATION SUMMARY (Benchmark Report Table)")
    print("=" * 75)
    print(f"{'Query Type':<25} | {'Evaluated':<12} | {'Correct':<12} | {'Accuracy':<10}")
    print("-" * 75)

    for q_type, stats in results_by_type.items():
        acc = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0.0
        print(f"{q_type.title():<25} | {stats['total']:<12} | {stats['correct']:<12} | {acc:>7.1f}%")

    overall_acc = (passed_cases / total_cases) * 100 if total_cases > 0 else 0.0
    print("-" * 75)
    print(f"{'TOTAL OVERALL':<25} | {total_cases:<12} | {passed_cases:<12} | {overall_acc:>7.1f}%")
    print("=" * 75)

if __name__ == "__main__":
    run_evaluation()
