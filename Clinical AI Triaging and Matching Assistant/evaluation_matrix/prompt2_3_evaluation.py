"""
Evaluation script for Prompt 2 (Parent Summary) and Prompt 3 (Clinical Summary).
Evaluates summary generation using faithfulness, completeness, and correctness.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SummaryEvaluation:
    """
    Evaluation results for summary generation (Prompts 2 and 3).
    
    Metrics:
    - Faithfulness: How accurately the summary reflects the source material
    - Completeness: How much of the important information is included
    - Correctness: Factual accuracy and clinical correctness
    """
    faithfulness_score: float  # 0-1
    completeness_score: float  # 0-1
    correctness_score: float  # 0-1
    overall_score: float  # 0-1
    missing_information: List[str]  # Important info missing from summary
    incorrect_information: List[str]  # Factually incorrect or unsafe claims
    hallucination_detected: bool  # Whether summary contains fabricated information


class SummaryEvaluator:
    """Evaluator for summary generation (Prompts 2 and 3)."""
    
    def evaluate_prompt2(self, parent_summary: str, 
                        conversation_history: List[Dict[str, Any]]) -> SummaryEvaluation:
        """
        Evaluate Prompt 2: Parent Summary generation.
        
        Args:
            parent_summary: Generated parent summary
            conversation_history: Original conversation history
            
        Returns:
            SummaryEvaluation with faithfulness, completeness, correctness
        """
        return self._evaluate_summary(
            summary=parent_summary,
            source_material=conversation_history,
            summary_type="parent"
        )
    
    def evaluate_prompt3(self, clinical_summary: str,
                        conversation_history: List[Dict[str, Any]],
                        parent_summary: str) -> SummaryEvaluation:
        """
        Evaluate Prompt 3: Clinical Summary generation.
        
        Args:
            clinical_summary: Generated clinical summary
            conversation_history: Original conversation history
            parent_summary: Parent-confirmed summary
            
        Returns:
            SummaryEvaluation with faithfulness, completeness, correctness
        """
        source_material = {
            "conversation_history": conversation_history,
            "parent_summary": parent_summary
        }
        
        return self._evaluate_summary(
            summary=clinical_summary,
            source_material=source_material,
            summary_type="clinical"
        )
    
    def _evaluate_summary(self, summary: str, source_material: Any,
                         summary_type: str) -> SummaryEvaluation:
        """
        Core evaluation logic for summary generation.
        
        Args:
            summary: Generated summary text
            source_material: Original material (conversation or dict with multiple sources)
            summary_type: "parent" or "clinical"
            
        Returns:
            SummaryEvaluation object
        """
        # Placeholder extraction logic
        source_info = self._extract_key_information(source_material)
        summary_info = self._extract_key_information_from_summary(summary, summary_type)
        
        # Calculate scores (placeholders)
        faithfulness_score = self._calculate_faithfulness(source_info, summary_info)
        completeness_score = self._calculate_completeness(source_info, summary_info)
        correctness_score, incorrect_info, hallucination = self._calculate_correctness(
            summary, source_info, summary_type
        )
        
        missing_info = self._find_missing_information(source_info, summary_info)
        
        # Overall score (weighted)
        overall_score = (
            faithfulness_score * 0.4 +
            completeness_score * 0.3 +
            correctness_score * 0.3
        )
        
        return SummaryEvaluation(
            faithfulness_score=faithfulness_score,
            completeness_score=completeness_score,
            correctness_score=correctness_score,
            overall_score=overall_score,
            missing_information=missing_info,
            incorrect_information=incorrect_info,
            hallucination_detected=hallucination
        )
    
    def _extract_key_information(self, source: Any) -> Dict[str, Any]:
        """Extract key information from source material (placeholder)."""
        if isinstance(source, list):
            return {
                "demographics": "extracted from conversation",
                "symptoms": "extracted from conversation",
                "medical_history": "extracted from conversation",
                "topics": "extracted from conversation"
            }
        elif isinstance(source, dict):
            return {
                "from_conversation": "extracted",
                "from_parent_summary": "extracted"
            }
        return {}
    
    def _extract_key_information_from_summary(self, summary: str, 
                                             summary_type: str) -> Dict[str, Any]:
        """Extract key information from generated summary (placeholder)."""
        return {
            "demographics": "extracted from summary",
            "symptoms": "extracted from summary",
            "key_points": "extracted from summary"
        }
    
    def _calculate_faithfulness(self, source_info: Dict, summary_info: Dict) -> float:
        """Calculate faithfulness (placeholder)."""
        return 0.85
    
    def _calculate_completeness(self, source_info: Dict, summary_info: Dict) -> float:
        """Calculate completeness (placeholder)."""
        return 0.80
    
    def _calculate_correctness(self, summary: str, source_info: Dict, 
                              summary_type: str) -> Tuple[float, List[str], bool]:
        """Calculate correctness (placeholder)."""
        incorrect_info = []
        hallucination = False
        
        summary_lower = summary.lower()
        if "diagnosis" in summary_lower and summary_type == "clinical":
            if "observation" not in summary_lower:
                incorrect_info.append("Contains diagnosis without observation")
        
        if incorrect_info or hallucination:
            correctness_score = max(0.0, 1.0 - len(incorrect_info) * 0.2)
        else:
            correctness_score = 0.95
        
        return correctness_score, incorrect_info, hallucination
    
    def _find_missing_information(self, source_info: Dict, summary_info: Dict) -> List[str]:
        """Find important information missing from summary (placeholder)."""
        return []


if __name__ == "__main__":
    # Example usage
    evaluator = SummaryEvaluator()
    
    sample_conversation = [
        {"role": "user", "content": "Patient is 5 years old"},
        {"role": "assistant", "content": "Thank you"}
    ]
    
    parent_summary = "Patient is 5 years old with fever"
    result = evaluator.evaluate_prompt2(parent_summary, sample_conversation)
    
    print(f"Faithfulness: {result.faithfulness_score:.2f}")
    print(f"Completeness: {result.completeness_score:.2f}")
    print(f"Correctness: {result.correctness_score:.2f}")
    print(f"Overall: {result.overall_score:.2f}")

