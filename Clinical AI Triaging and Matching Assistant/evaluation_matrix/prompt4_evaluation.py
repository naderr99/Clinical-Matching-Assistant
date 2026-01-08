"""
Evaluation script for Prompt 4: Specialist Matching
Compares matches against goldset (70 patient summaries) to calculate accuracy.
Required accuracy: >80%
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class MatchingEvaluation:
    """
    Evaluation results for Prompt 4 specialist matching.
    """
    accuracy: float  # 0-1, must be >0.8
    correct_matches: int  # Number of correct matches
    total_cases: int  # Total number of cases evaluated
    incorrect_matches: List[Dict[str, Any]]  # List of incorrect matches with details
    matches_above_threshold: bool  # Whether accuracy > 0.8


class Prompt4Evaluator:
    """
    Evaluator for Prompt 4 specialist matching.
    Compares predicted matches against goldset.
    """
    
    def __init__(self, goldset_path: str):
        """
        Initialize evaluator with goldset.
        
        Args:
            goldset_path: Path to JSON file containing goldset matches
                         Format: List of dicts with:
                         - patient_id: Identifier
                         - clinical_summary: Summary text
                         - correct_specialist: Expected specialist match
                         - correct_specialist_id: ID of correct specialist
        """
        self.goldset_path = goldset_path
        self.goldset = self._load_goldset()
    
    def _load_goldset(self) -> List[Dict[str, Any]]:
        """Load goldset from file."""
        if os.path.exists(self.goldset_path):
            with open(self.goldset_path, 'r') as f:
                return json.load(f)
        else:
            # Return placeholder structure for 70 patient summaries
            return [
                {
                    "patient_id": f"patient_{i}",
                    "clinical_summary": f"Summary for patient {i}",
                    "correct_specialist": f"Specialist_{i % 5}",
                    "correct_specialist_id": f"spec_{i % 5}"
                }
                for i in range(70)
            ]
    
    def evaluate(self, predictions: List[Dict[str, Any]]) -> MatchingEvaluation:
        """
        Evaluate specialist matching predictions against goldset.
        
        Args:
            predictions: List of prediction dicts with:
                - patient_id: Identifier (must match goldset)
                - predicted_specialist: Matched specialist name
                - predicted_specialist_id: Matched specialist ID
                - rationale: Reasoning for match
                
        Returns:
            MatchingEvaluation with accuracy and detailed results
        """
        if len(predictions) != len(self.goldset):
            raise ValueError(
                f"Predictions count ({len(predictions)}) doesn't match "
                f"goldset count ({len(self.goldset)})"
            )
        
        # Create lookup dictionary for goldset
        goldset_dict = {
            item["patient_id"]: item 
            for item in self.goldset
        }
        
        correct_matches = 0
        incorrect_matches = []
        
        for pred in predictions:
            patient_id = pred["patient_id"]
            if patient_id not in goldset_dict:
                incorrect_matches.append({
                    "patient_id": patient_id,
                    "reason": "Patient ID not found in goldset"
                })
                continue
            
            goldset_entry = goldset_dict[patient_id]
            predicted_id = pred.get("predicted_specialist_id")
            correct_id = goldset_entry.get("correct_specialist_id")
            
            # Check if match is correct
            if predicted_id == correct_id:
                correct_matches += 1
            else:
                incorrect_matches.append({
                    "patient_id": patient_id,
                    "predicted": predicted_id,
                    "correct": correct_id,
                    "rationale": pred.get("rationale", "")
                })
        
        total_cases = len(predictions)
        accuracy = correct_matches / total_cases if total_cases > 0 else 0.0
        
        return MatchingEvaluation(
            accuracy=accuracy,
            correct_matches=correct_matches,
            total_cases=total_cases,
            incorrect_matches=incorrect_matches,
            matches_above_threshold=accuracy > 0.8
        )
    
    def evaluate_from_outputs(self, outputs_dir: str) -> MatchingEvaluation:
        """
        Evaluate matching from saved output files.
        
        Args:
            outputs_dir: Directory containing output JSON files with matching results
            
        Returns:
            MatchingEvaluation
        """
        predictions = []
        
        # Load all output files
        if os.path.exists(outputs_dir):
            for filename in os.listdir(outputs_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(outputs_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        
                        # Extract matching information
                        if "selected_specialist" in data and "clinical_summary" in data:
                            predictions.append({
                                "patient_id": data.get("patient_id", filename.replace('.json', '')),
                                "predicted_specialist": data["selected_specialist"].get("name", ""),
                                "predicted_specialist_id": data["selected_specialist"].get("id", ""),
                                "rationale": data.get("matching_rationale", "")
                            })
        
        return self.evaluate(predictions)
    
    def generate_report(self, evaluation: MatchingEvaluation) -> str:
        """
        Generate a human-readable evaluation report.
        
        Args:
            evaluation: MatchingEvaluation results
            
        Returns:
            Formatted report string
        """
        report = f"""
Specialist Matching Evaluation Report
=====================================
Total Cases Evaluated: {evaluation.total_cases}
Correct Matches: {evaluation.correct_matches}
Accuracy: {evaluation.accuracy:.2%}
Required Threshold: >80%
Meets Threshold: {'✓ YES' if evaluation.matches_above_threshold else '✗ NO'}

"""
        
        if evaluation.incorrect_matches:
            report += f"Incorrect Matches ({len(evaluation.incorrect_matches)}):\n"
            report += "-" * 50 + "\n"
            for match in evaluation.incorrect_matches[:10]:  # Show first 10
                report += f"Patient: {match['patient_id']}\n"
                report += f"  Predicted: {match.get('predicted', 'N/A')}\n"
                report += f"  Correct: {match.get('correct', 'N/A')}\n"
                if match.get('rationale'):
                    report += f"  Rationale: {match['rationale'][:100]}...\n"
                report += "\n"
            
            if len(evaluation.incorrect_matches) > 10:
                report += f"... and {len(evaluation.incorrect_matches) - 10} more\n"
        
        return report


if __name__ == "__main__":
    # Example usage
    evaluator = Prompt4Evaluator("evaluation_matrix/goldset.json")
    
    # Sample predictions (placeholder)
    sample_predictions = [
        {
            "patient_id": f"patient_{i}",
            "predicted_specialist": f"Specialist_{i % 5}",
            "predicted_specialist_id": f"spec_{i % 5}",
            "rationale": "Matched based on specialty alignment"
        }
        for i in range(70)
    ]
    
    result = evaluator.evaluate(sample_predictions)
    print(evaluator.generate_report(result))

