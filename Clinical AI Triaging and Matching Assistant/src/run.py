"""
Main execution script for the multi-prompt conversational system.
This system chains four prompts to collect information, generate summaries,
create clinical documentation, and match patients with appropriate specialists.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class PromptSystem:
    """
    Orchestrates a 4-prompt system for collecting patient information,
    generating summaries, and matching with specialists.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the prompt system with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - api_key: OpenAI API key
                - model_name: Model to use for prompts
                - temperature: Temperature parameter for generation
                - max_tokens: Maximum tokens per response
                - required_topics: List of 8 required topics to collect
        """
        self.config = config
        self.conversation_history: List[Dict] = []
        self.parent_summary: Optional[str] = None
        self.clinical_summary: Optional[str] = None
        self.selected_specialist: Optional[Dict] = None
        self.human_in_loop_triggered = False
        self.emergency_detected = False
        
    def check_emergency_keywords(self, text: str) -> bool:
        """
        Check for emergency keywords that require immediate human intervention.
        
        Args:
            text: Input text to check
            
        Returns:
            True if emergency detected, False otherwise
        """
        emergency_keywords = [
            "suicide", "suicidal", "kill myself", "end my life",
            "abuse", "abusing", "neglect", "violence",
            "immediate danger", "urgent", "emergency",
            "hurt", "harm", "dangerous"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)
    
    def prompt_1_conversation_collection(self, user_input: str) -> Dict[str, Any]:
        """
        Prompt 1: Initial conversation with parent to collect information.
        Uses OpenAI Realtime API for voice or text interaction.
        
        Collects information on 8 required topics:
        1. Patient demographics
        2. Chief complaint / presenting symptoms
        3. Medical history
        4. Current medications
        5. Allergies
        6. Family medical history
        7. Social history / environmental factors
        8. Developmental history (for pediatric cases)
        
        Args:
            user_input: Text or transcribed voice input from parent
            
        Returns:
            Response dictionary with message and status
        """
        # Check for emergencies first
        if self.check_emergency_keywords(user_input):
            self.emergency_detected = True
            self.human_in_loop_triggered = True
            return {
                "message": "Emergency detected. Connecting you with a human specialist immediately.",
                "status": "emergency",
                "human_in_loop": True
            }
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if all 8 topics are covered
        topics_covered = self._check_topics_coverage()
        
        if len(topics_covered) == 8:
            # All topics covered, prepare for prompt 2
            response = {
                "message": "Thank you for providing this information. Let me prepare a summary for your review.",
                "status": "ready_for_summary",
                "topics_covered": topics_covered,
                "trigger_prompt_2": True
            }
        else:
            # Continue collecting information
            missing_topics = [i+1 for i in range(8) if i+1 not in topics_covered]
            response = {
                "message": f"I still need information about: {missing_topics}. Please continue.",
                "status": "collecting",
                "topics_covered": topics_covered,
                "trigger_prompt_2": False
            }
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response["message"],
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _check_topics_coverage(self) -> List[int]:
        """
        Analyze conversation history to determine which of the 8 required topics are covered.
        
        Returns:
            List of topic numbers (1-8) that have been covered
        """
        # Placeholder logic - would use NLP/classification in actual implementation
        covered_topics = []
        combined_text = " ".join([msg["content"] for msg in self.conversation_history])
        
        # Simplified topic detection (actual implementation would be more sophisticated)
        topic_keywords = {
            1: ["age", "birth", "gender", "demographic"],
            2: ["symptom", "complaint", "problem", "issue", "pain"],
            3: ["medical history", "diagnosed", "condition", "previous"],
            4: ["medication", "prescription", "taking", "drug"],
            5: ["allergy", "allergic", "reaction"],
            6: ["family history", "parent", "sibling", "inherited"],
            7: ["environment", "home", "school", "social"],
            8: ["development", "milestone", "growth", "pediatric"]
        }
        
        combined_lower = combined_text.lower()
        for topic_num, keywords in topic_keywords.items():
            if any(keyword in combined_lower for keyword in keywords):
                covered_topics.append(topic_num)
        
        return covered_topics
    
    def prompt_2_parent_summary_confirmation(self) -> Dict[str, Any]:
        """
        Prompt 2: Generates a summary of the conversation history and seeks
        confirmation from the parent.
        
        Evaluation metrics: faithfulness, completeness, correctness
        
        Returns:
            Summary text and confirmation request
        """
        # Placeholder for actual LLM call with temperature ~0.4
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history
        ])
        
        self.parent_summary = f"Summary of conversation:\n{conversation_text[:500]}..."
        
        return {
            "summary": self.parent_summary,
            "message": "Please review the summary above. Does this accurately reflect our conversation? (Yes/No)",
            "status": "awaiting_confirmation",
            "trigger_prompt_3": False
        }
    
    def confirm_parent_summary(self, confirmation: bool) -> Dict[str, Any]:
        """
        Handle parent's confirmation of the summary.
        
        Args:
            confirmation: True if parent confirms, False otherwise
            
        Returns:
            Status and next action
        """
        if confirmation:
            return {
                "message": "Thank you for confirming. Generating clinical summary...",
                "status": "confirmed",
                "trigger_prompt_3": True
            }
        else:
            return {
                "message": "Let me revise the summary. What would you like to correct?",
                "status": "revision_needed",
                "trigger_prompt_3": False
            }
    
    def prompt_3_clinical_summary_generation(self) -> Dict[str, Any]:
        """
        Prompt 3: Creates a clinical summary using both conversation history
        and parent summary. This summary guides specialists and is passed to prompt 4.
        
        Uses both:
        - Full conversation_history for context
        - parent_summary for confirmed information
        
        Evaluation metrics: faithfulness, completeness, correctness
        
        Temperature: Lower (0.3-0.5) for precise clinical documentation
        
        Returns:
            Clinical summary text
        """
        # Placeholder for actual LLM call with temperature ~0.3
        self.clinical_summary = f"""
CLINICAL SUMMARY
Generated: {datetime.now().isoformat()}

Patient Information:
- Based on conversation history and parent confirmation
- Topics covered: {self._check_topics_coverage()}

Key Findings:
[Extracted from conversation and parent summary]

Clinical Notes:
[Formatted for specialist review]
"""
        
        return {
            "clinical_summary": self.clinical_summary,
            "status": "clinical_summary_ready",
            "trigger_prompt_4": True
        }
    
    def prompt_4_specialist_matching(self, specialist_database: List[Dict]) -> Dict[str, Any]:
        """
        Prompt 4: Reads clinical summary, analyzes patient needs, and matches
        with the best-fitting specialist from the database.
        
        Evaluation: Automated comparison against goldset (70 patient summaries)
        Required accuracy: >80%
        
        Temperature: Moderate (0.6-0.7) for reasoning and selection
        
        Args:
            specialist_database: List of available specialists
            
        Returns:
            Selected specialist with rationale, or human-in-loop signal
        """
        if not self.clinical_summary:
            raise ValueError("Clinical summary must be generated before specialist matching")
        
        # Check for emergency cases
        if self.emergency_detected:
            return {
                "specialist": None,
                "rationale": "Emergency case detected - requires immediate human intervention",
                "human_in_loop": True,
                "status": "emergency"
            }
        
        # Placeholder for actual LLM reasoning call with temperature ~0.6-0.7
        
        # Filter available specialists
        available_specialists = [
            spec for spec in specialist_database 
            if spec.get("availability", False)
        ]
        
        if not available_specialists:
            return {
                "specialist": None,
                "rationale": "No specialists currently available",
                "human_in_loop": True,
                "status": "no_availability"
            }
        
        # Placeholder matching logic
        matched_specialist = available_specialists[0] if available_specialists else None
        self.selected_specialist = matched_specialist
        
        return {
            "specialist": matched_specialist,
            "rationale": f"Selected based on: specialty match, patient needs, and availability",
            "human_in_loop": False,
            "status": "matched"
        }
    
    def save_output(self, output_dir: str):
        """Save all outputs to files for evaluation and record-keeping."""
        os.makedirs(output_dir, exist_ok=True)
        
        output_data = {
            "conversation_history": self.conversation_history,
            "parent_summary": self.parent_summary,
            "clinical_summary": self.clinical_summary,
            "selected_specialist": self.selected_specialist,
            "topics_covered": self._check_topics_coverage(),
            "human_in_loop_triggered": self.human_in_loop_triggered,
            "emergency_detected": self.emergency_detected,
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = os.path.join(
            output_dir, 
            f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return output_file


def main():
    """Main execution function demonstrating the 4-prompt pipeline."""
    
    # Configuration
    config = {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model_name": "gpt-4",
        "temperature_prompt1": 0.7,  # Moderate for conversational flow
        "temperature_prompt2": 0.4,  # Lower for factual summary
        "temperature_prompt3": 0.3,  # Lowest for clinical precision
        "temperature_prompt4": 0.6,  # Moderate for reasoning
        "max_tokens": 2000,
        "required_topics": list(range(1, 9))  # 8 topics
    }
    
    # Initialize system
    system = PromptSystem(config)
    
    # Simulate conversation flow
    print("=== Prompt 1: Information Collection ===")
    # Simulate collecting information until all topics covered
    
    # Trigger Prompt 2 when ready
    print("\n=== Prompt 2: Parent Summary ===")
    summary_result = system.prompt_2_parent_summary_confirmation()
    print(summary_result["summary"])
    
    # Simulate confirmation
    confirmation_result = system.confirm_parent_summary(True)
    
    if confirmation_result["trigger_prompt_3"]:
        print("\n=== Prompt 3: Clinical Summary ===")
        clinical_result = system.prompt_3_clinical_summary_generation()
        print(clinical_result["clinical_summary"])
        
        if clinical_result["trigger_prompt_4"]:
            print("\n=== Prompt 4: Specialist Matching ===")
            specialist_db = [
                {"name": "Dr. Smith", "specialty": "Pediatrics", "availability": True},
                {"name": "Dr. Jones", "specialty": "Cardiology", "availability": False}
            ]
            match_result = system.prompt_4_specialist_matching(specialist_db)
            print(f"Matched: {match_result['specialist']}")
            print(f"Rationale: {match_result['rationale']}")
    
    # Save outputs
    system.save_output("outputs")


if __name__ == "__main__":
    main()

