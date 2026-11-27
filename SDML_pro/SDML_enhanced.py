"""
Small Disease Language Model (SDML) - Enhanced Medical AI Assistant
A production-ready medical AI system with multi-agent architecture,
confidence scoring, and clinical safety features.
"""

import os
import re
import logging
import json
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import lru_cache
from datetime import datetime

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    pipeline,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SDMLConfig:
    """Configuration for SDML model and generation."""
    model_id: str = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    max_new_tokens: int = 300
    temperature: float = 0.15
    do_sample: bool = True
    device_map: str = "auto"
    clean_up_tokenization: bool = False
    disable_progress: bool = True
    min_confidence_threshold: float = 0.6


@dataclass
class SymptomInput:
    """Structured representation of patient symptoms."""
    symptoms: List[str]
    duration: Optional[str] = None
    severity: Optional[str] = None
    medical_history: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    
    def to_text(self) -> str:
        """Convert to natural language description."""
        text = f"Symptoms: {', '.join(self.symptoms)}"
        if self.duration:
            text += f"\nDuration: {self.duration}"
        if self.severity:
            text += f"\nSeverity: {self.severity}"
        if self.medical_history:
            text += f"\nMedical History: {', '.join(self.medical_history)}"
        if self.medications:
            text += f"\nCurrent Medications: {', '.join(self.medications)}"
        if self.allergies:
            text += f"\nAllergies: {', '.join(self.allergies)}"
        return text


@dataclass
class DiagnosisResult:
    """Structured diagnosis output."""
    primary_condition: str
    confidence_score: float
    differential_diagnoses: List[Tuple[str, float]]
    reasoning: str
    red_flags: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "primary_condition": self.primary_condition,
            "confidence_score": self.confidence_score,
            "differential_diagnoses": [
                {"condition": c, "confidence": s} 
                for c, s in self.differential_diagnoses
            ],
            "reasoning": self.reasoning,
            "red_flags": self.red_flags,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp
        }
    
    def to_report(self) -> str:
        """Generate formatted clinical report."""
        report = f"""
{'='*60}
MEDICAL AI ANALYSIS REPORT
{'='*60}
Generated: {self.timestamp}

PRIMARY ASSESSMENT:
  Condition: {self.primary_condition}
  Confidence: {self.confidence_score:.1%}

DIFFERENTIAL DIAGNOSES:
"""
        for condition, confidence in self.differential_diagnoses:
            report += f"  • {condition}: {confidence:.1%}\n"
        
        report += f"\nCLINICAL REASONING:\n{self.reasoning}\n"
        
        if self.red_flags:
            report += f"\n⚠️  RED FLAGS:\n"
            for flag in self.red_flags:
                report += f"  • {flag}\n"
        
        if self.recommendations:
            report += f"\nRECOMMENDATIONS:\n"
            for rec in self.recommendations:
                report += f"  • {rec}\n"
        
        report += f"""
{'='*60}
DISCLAIMER: This is an AI-generated analysis, not a diagnosis.
Always consult with a qualified healthcare professional for
medical advice, diagnosis, and treatment.
{'='*60}
"""
        return report


class MedicalAgent(ABC):
    """Abstract base class for medical analysis agents."""
    
    def __init__(self, pipe, tokenizer, config: SDMLConfig, name: str):
        self.pipe = pipe
        self.tokenizer = tokenizer
        self.config = config
        self.name = name
        self.generation_config = GenerationConfig(
            max_new_tokens=config.max_new_tokens,
            do_sample=config.do_sample,
            temperature=config.temperature,
        )
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    def execute(self, user_input: str) -> str:
        """Execute agent analysis."""
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_input}
            ]
            
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            outputs = self.pipe(prompt, generation_config=self.generation_config)
            generated_text = outputs[0]["generated_text"]
            
            # Extract assistant response
            response = self._extract_response(generated_text)
            
            logger.info(f"{self.name} completed analysis")
            return response
            
        except Exception as e:
            logger.error(f"{self.name} encountered error: {str(e)}")
            raise
    
    def _extract_response(self, full_text: str) -> str:
        """Extract assistant response from generated text."""
        # Handle different response formats
        for delimiter in ["<|im_start|>assistant", "<|assistant|>", "Assistant:"]:
            if delimiter in full_text:
                response = full_text.split(delimiter)[-1]
                for end_marker in ["<|im_end|>", "<|end|>"]:
                    if end_marker in response:
                        response = response.split(end_marker)[0]
                return response.strip()
        
        return full_text.strip()


class TriageAgent(MedicalAgent):
    """Safety triage to identify emergencies."""
    
    def get_system_prompt(self) -> str:
        return """You are an Emergency Medical Triage Specialist. Your role is to:
1. Identify life-threatening symptoms requiring immediate emergency care
2. Flag red flags like difficulty breathing, chest pain, severe bleeding
3. Assess urgency level: EMERGENCY, URGENT, or ROUTINE

Output format:
Urgency Level: [EMERGENCY/URGENT/ROUTINE]
Red Flags Detected: [List any critical symptoms]
Reasoning: [Brief explanation]
Recommendation: [Seek emergency care immediately / See doctor today / Standard care]"""


class DiagnosticAgent(MedicalAgent):
    """Main diagnostic analysis agent."""
    
    def get_system_prompt(self) -> str:
        return """You are an Expert Medical Diagnostician with knowledge of internal medicine,
common conditions, and differential diagnosis methodology. 

For the given symptoms:
1. Identify the most likely primary condition
2. List 2-3 differential diagnoses with reasoning
3. Consider patient factors (age, history, medications)
4. Provide clinical probability estimates

Output format:
Primary Diagnosis: [Condition with confidence %]
Differential Diagnoses:
  - [Condition]: [Reasoning and confidence %]
  - [Condition]: [Reasoning and confidence %]
Reasoning: [Detailed explanation]
Key Factors: [What supports this diagnosis]"""


class RecommendationAgent(MedicalAgent):
    """Generates clinical recommendations."""
    
    def get_system_prompt(self) -> str:
        return """You are a Clinical Recommendations Specialist. Based on the diagnosis:
1. Recommend appropriate next steps for care
2. Suggest tests or evaluations if needed
3. Provide lifestyle/self-care recommendations
4. Indicate when specialist referral is needed

Output format:
Next Steps: [Ordered list of recommended actions]
Testing: [Any diagnostic tests to consider]
Self-Care: [Home management strategies]
Specialist: [If referral to specialist is recommended]
Timeline: [How urgent these actions are]"""


class PatientCommunicationAgent(MedicalAgent):
    """Formats output for patient understanding."""
    
    def get_system_prompt(self) -> str:
        return """You are a Medical Communication Specialist who translates clinical information
into clear, compassionate language for patients.

Create a clear patient-friendly summary that:
1. Explains findings in simple language
2. Avoids jargon or explains technical terms
3. Emphasizes key action items
4. Provides reassurance and next steps

Include a clear disclaimer that this is AI analysis, not medical diagnosis."""


class SDMLSystem:
    """Main SDML system orchestrating multi-agent medical analysis."""
    
    def __init__(self, config: Optional[SDMLConfig] = None):
        self.config = config or SDMLConfig()
        logger.info(f"Initializing SDML with model: {self.config.model_id}")
        
        # Suppress HuggingFace progress bars
        if self.config.disable_progress:
            from huggingface_hub.utils import disable_progress_bars
            disable_progress_bars()
            import transformers
            transformers.logging.set_verbosity_error()
        
        # Initialize model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_id,
            clean_up_tokenization_spaces=self.config.clean_up_tokenization
        )
        self.pipe = pipeline(
            "text-generation",
            model=self.config.model_id,
            tokenizer=self.tokenizer,
            device_map=self.config.device_map
        )
        
        # Initialize agents
        self.triage_agent = TriageAgent(self.pipe, self.tokenizer, self.config, "TriageAgent")
        self.diagnostic_agent = DiagnosticAgent(self.pipe, self.tokenizer, self.config, "DiagnosticAgent")
        self.recommendation_agent = RecommendationAgent(self.pipe, self.tokenizer, self.config, "RecommendationAgent")
        self.communication_agent = PatientCommunicationAgent(self.pipe, self.tokenizer, self.config, "PatientCommunicationAgent")
        
        logger.info("SDML system initialized successfully")
    
    def analyze_symptoms(self, symptoms: SymptomInput) -> DiagnosisResult:
        """
        Perform comprehensive medical analysis of symptoms.
        
        Args:
            symptoms: SymptomInput object with patient information
        
        Returns:
            DiagnosisResult with structured analysis
        """
        symptom_text = symptoms.to_text()
        logger.info(f"Starting analysis for symptoms: {', '.join(symptoms.symptoms)}")
        
        # Step 1: Triage for safety
        logger.info("Step 1: Running triage assessment")
        triage_result = self.triage_agent.execute(symptom_text)
        
        # Check for emergency
        is_emergency = "EMERGENCY" in triage_result.upper()
        logger.warning(f"Emergency detected: {is_emergency}") if is_emergency else None
        
        # Step 2: Diagnostic analysis
        logger.info("Step 2: Running diagnostic analysis")
        diagnostic_result = self.diagnostic_agent.execute(symptom_text)
        
        # Step 3: Extract structured diagnosis
        diagnosis_data = self._parse_diagnostic_output(diagnostic_result)
        
        # Step 4: Get recommendations
        logger.info("Step 3: Generating recommendations")
        combined_context = f"Patient Input:\n{symptom_text}\n\nDiagnostic Assessment:\n{diagnostic_result}"
        recommendations_result = self.recommendation_agent.execute(combined_context)
        
        # Step 5: Format for patient
        logger.info("Step 4: Formatting patient-friendly output")
        patient_summary_input = f"Clinical Summary:\n{diagnostic_result}\n\nTriage Status: {triage_result}\n\nRecommendations: {recommendations_result}"
        patient_message = self.communication_agent.execute(patient_summary_input)
        
        # Construct final result
        result = DiagnosisResult(
            primary_condition=diagnosis_data.get("primary_condition", "Undetermined"),
            confidence_score=diagnosis_data.get("confidence_score", 0.0),
            differential_diagnoses=diagnosis_data.get("differential_diagnoses", []),
            reasoning=diagnostic_result,
            red_flags=self._extract_red_flags(triage_result) if is_emergency else None,
            recommendations=self._extract_recommendations(recommendations_result)
        )
        
        logger.info(f"Analysis complete. Primary diagnosis: {result.primary_condition} ({result.confidence_score:.1%})")
        return result
    
    def _parse_diagnostic_output(self, diagnostic_text: str) -> Dict:
        """Extract structured data from diagnostic agent output."""
        data = {
            "primary_condition": "Undetermined",
            "confidence_score": 0.6,
            "differential_diagnoses": []
        }
        
        lines = diagnostic_text.split('\n')
        
        # First, find primary diagnosis
        for i, line in enumerate(lines):
            if "primary" in line.lower() and "diagnosis" in line.lower():
                # Extract primary diagnosis and confidence
                parts = line.split(':')[1:] if ':' in line else []
                if parts:
                    full_text = ':'.join(parts).strip()
                    
                    # Extract percentage from the full text
                    conf_match = re.search(r'(\d+)%', full_text)
                    if conf_match:
                        try:
                            conf_str = conf_match.group(1)
                            data["confidence_score"] = float(conf_str) / 100
                            # Extract condition name (before the percentage)
                            condition_text = full_text.split(conf_match.group(0))[0].strip()
                            # Remove trailing punctuation and clean up
                            condition_text = re.sub(r'[,\(\):]$', '', condition_text).strip()
                            if condition_text:
                                data["primary_condition"] = condition_text
                        except (ValueError, IndexError):
                            pass
                    else:
                        # No percentage found, try to use the whole text
                        condition_text = re.sub(r'[,\(\):]$', '', full_text).strip()
                        if condition_text:
                            data["primary_condition"] = condition_text
        
        return data
    
    def _extract_red_flags(self, triage_text: str) -> List[str]:
        """Extract red flag symptoms from triage output."""
        flags = []
        lines = triage_text.split('\n')
        capture = False
        
        for line in lines:
            line_lower = line.lower()
            # Look for red flags section
            if any(keyword in line_lower for keyword in ["red flags", "emergency flags", "critical symptoms"]):
                capture = True
                continue
            
            # Capture flag lines
            if capture:
                # Stop capturing on empty line or new section
                if not line.strip() or line.strip().startswith(('Next', 'Recommendation', 'Urgency', 'Timeline')):
                    break
                
                # Extract flag from various formats: "- flag", "• flag", "* flag", etc.
                for prefix in ['-', '•', '*', '►']:
                    if line.strip().startswith(prefix):
                        flag_text = line.strip()[1:].strip()
                        if flag_text:
                            flags.append(flag_text)
                        break
        
        return flags if flags else None
    
    def _extract_recommendations(self, rec_text: str) -> List[str]:
        """Extract recommendations from recommendations output."""
        recommendations = []
        lines = rec_text.split('\n')
        capture = False
        
        for line in lines:
            line_lower = line.lower()
            # Look for recommendations section
            if any(keyword in line_lower for keyword in ["next steps", "recommendations", "recommendation:", "actions:"]):
                capture = True
                continue
            
            # Capture recommendation lines
            if capture:
                # Stop on empty line or new section
                if not line.strip() or any(keyword in line_lower for keyword in ["testing:", "self-care:", "specialist:", "timeline:"]):
                    # Only stop if we already captured some recommendations
                    if recommendations:
                        break
                    continue
                
                # Extract recommendation from various formats
                for prefix in ['-', '•', '*', '►', '→']:
                    if line.strip().startswith(prefix):
                        rec_text = line.strip()[1:].strip()
                        if rec_text:
                            recommendations.append(rec_text)
                        break
                else:
                    # Handle indented lines without prefix
                    if line.startswith("  ") and line.strip():
                        recommendations.append(line.strip())
        
        return recommendations if recommendations else None
    
    def analyze_simple(self, symptom_string: str) -> DiagnosisResult:
        """
        Quick analysis with just a symptom string.
        
        Args:
            symptom_string: Simple symptom description
        
        Returns:
            DiagnosisResult with analysis
        """
        symptoms = SymptomInput(
            symptoms=[s.strip() for s in symptom_string.split(',')]
        )
        return self.analyze_symptoms(symptoms)


def demo_medical_analysis():
    """Demonstrate SDML system with example medical case."""
    print("\n" + "="*70)
    print("SMALL DISEASE LANGUAGE MODEL (SDML) - ENHANCED DEMO")
    print("="*70 + "\n")
    
    # Initialize system
    system = SDMLSystem()
    
    # Example 1: Simple symptom input
    print("EXAMPLE 1: Acute Upper Respiratory Symptoms")
    print("-" * 70)
    
    symptoms_case1 = SymptomInput(
        symptoms=["high fever", "dry cough", "severe fatigue"],
        duration="3 days",
        severity="moderate",
        medical_history=["hypertension (controlled)"],
        medications=["Lisinopril"],
        allergies=["Penicillin"]
    )
    
    result1 = system.analyze_symptoms(symptoms_case1)
    print(result1.to_report())
    
    # Save result to JSON
    with open('/media/user/dsk64/monowork/SDML_pro/analysis_result.json', 'w') as f:
        json.dump(result1.to_dict(), f, indent=2)
    print("✓ Result saved to analysis_result.json")
    
    # Example 2: Simple string input
    print("\n" + "="*70)
    print("EXAMPLE 2: Gastrointestinal Symptoms")
    print("-" * 70)
    
    result2 = system.analyze_simple("persistent nausea, upper abdominal pain, loss of appetite")
    print(result2.to_report())
    
    print("\n" + "="*70)
    print("Demo completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_medical_analysis()
