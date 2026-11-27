"""
Command-line interface for SDML system.
Interactive CLI for medical symptom analysis.
"""

import sys
import json
from typing import Optional
from pathlib import Path
from datetime import datetime

from SDML_enhanced import SDMLSystem, SymptomInput, SDMLConfig
from sdml_utils import (
    normalize_symptoms,
    check_emergency_flags,
    identify_symptom_clusters,
    create_symptom_report,
    SymptomValidator,
    save_analysis_json,
)


class SDMLCliInterface:
    """Command-line interface for SDML."""
    
    def __init__(self):
        self.system = None
        self.last_analysis = None
        self.analysis_history = []
    
    def print_header(self, title: str):
        """Print formatted header."""
        print("\n" + "="*70)
        print(f"  {title.center(66)}")
        print("="*70 + "\n")
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{title}")
        print("-" * len(title))
    
    def initialize_system(self):
        """Initialize the SDML system."""
        self.print_header("SDML MEDICAL ANALYSIS SYSTEM")
        print("Loading model and initializing agents...\n")
        
        try:
            self.system = SDMLSystem()
            print("✓ System initialized successfully!")
            print(f"✓ Model: {self.system.config.model_id}")
            print(f"✓ Device: {self.system.config.device_map}")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize system: {str(e)}")
            return False
    
    def collect_symptoms(self) -> Optional[SymptomInput]:
        """Interactively collect symptom information."""
        self.print_section("Step 1: Symptom Collection")
        
        # Get symptoms
        print("\nEnter symptoms (comma-separated).")
        print("Examples: fever, cough, fatigue")
        print("(or type 'back' to return to menu)\n")
        
        symptom_input = input("Symptoms: ").strip()
        
        if symptom_input.lower() == 'back':
            return None
        
        if not symptom_input:
            print("✗ No symptoms provided")
            return None
        
        symptoms = [s.strip() for s in symptom_input.split(',')]
        
        # Validate symptoms
        is_valid, errors = SymptomValidator.validate_symptoms(symptoms)
        if not is_valid:
            print("\n✗ Validation errors:")
            for error in errors:
                print(f"  • {error}")
            return None
        
        # Normalize symptoms
        normalized = normalize_symptoms(symptoms)
        print(f"\n✓ Normalized symptoms: {', '.join(normalized)}")
        
        # Check for emergency flags
        is_emergency, flags = check_emergency_flags(symptoms)
        if is_emergency:
            print(f"\n⚠️  EMERGENCY FLAGS DETECTED: {', '.join(flags)}")
            print("🚨 PLEASE SEEK IMMEDIATE EMERGENCY CARE!")
            if input("\nContinue with analysis? (y/n): ").lower() != 'y':
                return None
        
        # Optional: Get duration
        self.print_section("Step 2: Duration (Optional)")
        print("How long have you had these symptoms?")
        print("(Examples: 2 days, 1 week, started yesterday)")
        duration = input("Duration: ").strip() or None
        
        # Optional: Get severity
        self.print_section("Step 3: Severity (Optional)")
        print("What is the severity level?")
        print("Options: mild, moderate, severe")
        severity = input("Severity: ").strip() or None
        
        # Optional: Get medical history
        self.print_section("Step 4: Medical History (Optional)")
        print("Any relevant medical conditions?")
        print("(Examples: diabetes, hypertension - or press Enter to skip)")
        medical_history_input = input("Medical History: ").strip()
        medical_history = None
        if medical_history_input:
            medical_history = [h.strip() for h in medical_history_input.split(',')]
        
        # Optional: Get medications
        self.print_section("Step 5: Current Medications (Optional)")
        print("Are you taking any medications?")
        print("(Examples: Aspirin, Lisinopril - or press Enter to skip)")
        medications_input = input("Medications: ").strip()
        medications = None
        if medications_input:
            medications = [m.strip() for m in medications_input.split(',')]
        
        # Optional: Get allergies
        self.print_section("Step 6: Allergies (Optional)")
        print("Do you have any drug allergies?")
        print("(Examples: Penicillin, Sulfa - or press Enter to skip)")
        allergies_input = input("Allergies: ").strip()
        allergies = None
        if allergies_input:
            allergies = [a.strip() for a in allergies_input.split(',')]
        
        return SymptomInput(
            symptoms=normalized,
            duration=duration,
            severity=severity,
            medical_history=medical_history,
            medications=medications,
            allergies=allergies
        )
    
    def run_analysis(self, symptoms: SymptomInput):
        """Run medical analysis."""
        self.print_header("RUNNING MEDICAL ANALYSIS")
        print("Processing symptoms through multi-agent pipeline...\n")
        
        try:
            result = self.system.analyze_symptoms(symptoms)
            self.last_analysis = result
            self.analysis_history.append(result)
            
            # Display result
            print(result.to_report())
            
            # Offer to save
            save = input("\nSave analysis to file? (y/n): ").lower() == 'y'
            if save:
                self._save_analysis(result)
            
            return result
            
        except Exception as e:
            print(f"✗ Analysis failed: {str(e)}")
            return None
    
    def _save_analysis(self, result):
        """Save analysis to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.json"
        filepath = Path("/media/user/dsk64/monowork/SDML_pro/results") / filename
        
        try:
            save_analysis_json(result.to_dict(), str(filepath))
            print(f"✓ Analysis saved to: {filepath}")
        except Exception as e:
            print(f"✗ Failed to save: {str(e)}")
    
    def view_history(self):
        """View analysis history."""
        self.print_header("ANALYSIS HISTORY")
        
        if not self.analysis_history:
            print("No analyses performed yet.\n")
            return
        
        print(f"Total analyses: {len(self.analysis_history)}\n")
        
        for i, analysis in enumerate(self.analysis_history, 1):
            print(f"{i}. {analysis.timestamp}")
            print(f"   Primary: {analysis.primary_condition} ({analysis.confidence_score:.1%})")
            print()
    
    def show_menu(self):
        """Display main menu."""
        self.print_header("MAIN MENU")
        print("1. Run symptom analysis")
        print("2. View history")
        print("3. Display last analysis")
        print("4. Exit")
        print()
    
    def run_interactive(self):
        """Run interactive CLI."""
        if not self.initialize_system():
            return
        
        while True:
            self.show_menu()
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                symptoms = self.collect_symptoms()
                if symptoms:
                    self.run_analysis(symptoms)
                else:
                    print("Analysis cancelled.")
            
            elif choice == '2':
                self.view_history()
            
            elif choice == '3':
                if self.last_analysis:
                    print(self.last_analysis.to_report())
                else:
                    print("No analysis to display yet.")
            
            elif choice == '4':
                print("\nThank you for using SDML. Stay healthy!\n")
                break
            
            else:
                print("✗ Invalid option. Please try again.")
    
    @staticmethod
    def run_demo():
        """Run automated demo."""
        cli = SDMLCliInterface()
        
        if not cli.initialize_system():
            return
        
        cli.print_header("AUTOMATED DEMO")
        
        # Demo case 1
        print("Demo Case 1: Upper Respiratory Symptoms\n")
        
        symptoms_case1 = SymptomInput(
            symptoms=["high fever", "dry cough", "severe fatigue"],
            duration="3 days",
            severity="moderate"
        )
        
        # Print symptom report
        symptom_report = create_symptom_report(
            symptoms_case1.symptoms,
            symptoms_case1.duration,
            symptoms_case1.severity
        )
        print(symptom_report)
        
        print("\nRunning analysis...\n")
        cli.run_analysis(symptoms_case1)
        
        print("\n" + "="*70)
        print("Demo completed. Run with --interactive for full CLI experience.")
        print("="*70 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        SDMLCliInterface.run_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        cli = SDMLCliInterface()
        cli.run_interactive()
    else:
        # Print usage
        print("""
SDML Command-Line Interface
Usage:
  python sdml_cli.py --interactive    Run interactive mode
  python sdml_cli.py --demo           Run automated demo
  python sdml_cli.py --help           Show this help

Interactive mode allows you to:
  • Enter your symptoms
  • Provide medical history
  • Receive multi-agent medical analysis
  • View analysis history
  • Save results to JSON
        """)


if __name__ == "__main__":
    main()
