"""
Utility functions and helpers for SDML system.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path


# Common symptom to canonical name mappings
SYMPTOM_MAPPINGS = {
    "fever": ["high fever", "elevated temperature", "temp", "burning up"],
    "cough": ["dry cough", "persistent cough", "hacking cough", "coughing"],
    "fatigue": ["extreme tiredness", "exhaustion", "being tired", "fatigue", "weakness"],
    "nausea": ["feeling sick", "queasy", "nauseous", "stomach upset"],
    "headache": ["head pain", "migraine", "pounding head"],
    "chest pain": ["chest tightness", "chest pressure", "angina"],
    "shortness of breath": ["difficulty breathing", "breathlessness", "SOB", "dyspnea"],
    "abdominal pain": ["stomach pain", "belly ache", "gut pain"],
    "diarrhea": ["loose stools", "runs", "diarrheal"],
    "vomiting": ["throwing up", "being sick", "regurgitation"],
}

# Red flag symptoms that warrant emergency care
EMERGENCY_RED_FLAGS = {
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "loss of consciousness",
    "severe bleeding",
    "severe allergic reaction",
    "choking",
    "severe head injury",
    "poisoning",
    "severe burns",
    "signs of stroke",
    "severe abdominal pain",
    "uncontrolled seizures",
}

# Symptom clusters mapping to common conditions
SYMPTOM_CLUSTERS = {
    "respiratory": ["cough", "fever", "fatigue", "sore throat", "runny nose"],
    "gastrointestinal": ["nausea", "vomiting", "diarrhea", "abdominal pain", "loss of appetite"],
    "cardiovascular": ["chest pain", "shortness of breath", "palpitations", "dizziness"],
    "neurological": ["headache", "dizziness", "numbness", "tingling", "confusion"],
    "allergic": ["itching", "rash", "swelling", "difficulty breathing", "sneezing"],
}


def normalize_symptom(symptom: str) -> str:
    """
    Normalize a symptom string to canonical form.
    
    Args:
        symptom: Raw symptom input
    
    Returns:
        Canonical symptom name
    """
    symptom_lower = symptom.lower().strip()
    
    for canonical, variations in SYMPTOM_MAPPINGS.items():
        if symptom_lower == canonical or symptom_lower in variations:
            return canonical
    
    return symptom_lower


def normalize_symptoms(symptoms: List[str]) -> List[str]:
    """Normalize a list of symptoms."""
    return [normalize_symptom(s) for s in symptoms]


def check_emergency_flags(symptoms: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if symptoms contain emergency red flags.
    
    Args:
        symptoms: List of symptoms
    
    Returns:
        Tuple of (is_emergency, list_of_red_flags)
    """
    normalized = normalize_symptoms(symptoms)
    flags = [s for s in normalized if s in EMERGENCY_RED_FLAGS]
    
    return len(flags) > 0, flags


def identify_symptom_clusters(symptoms: List[str]) -> Dict[str, List[str]]:
    """
    Identify which symptom clusters are present.
    
    Args:
        symptoms: List of symptoms
    
    Returns:
        Dictionary mapping cluster names to matched symptoms
    """
    normalized = normalize_symptoms(symptoms)
    clusters = {}
    
    for cluster_name, cluster_symptoms in SYMPTOM_CLUSTERS.items():
        matched = [s for s in normalized if s in cluster_symptoms]
        if matched:
            clusters[cluster_name] = matched
    
    return clusters


def parse_confidence_percentage(text: str, default: float = 0.6) -> float:
    """
    Extract confidence percentage from text.
    
    Args:
        text: Text containing percentage
        default: Default confidence if not found
    
    Returns:
        Confidence score between 0 and 1
    """
    # Look for percentage patterns
    matches = re.findall(r'(\d+)%', text)
    if matches:
        try:
            return min(100, int(matches[0])) / 100.0
        except (ValueError, IndexError):
            pass
    
    return default


def extract_conditions_from_text(text: str) -> List[Tuple[str, float]]:
    """
    Extract condition/diagnosis pairs from text.
    
    Args:
        text: Text containing diagnoses
    
    Returns:
        List of (condition, confidence) tuples
    """
    conditions = []
    lines = text.split('\n')
    
    # Labels to skip (should not be treated as actual conditions)
    skip_labels = {
        'primary diagnosis', 'differential diagnoses', 'differential diagnosis',
        'next steps', 'recommendations', 'recommendation', 'testing', 'self-care',
        'specialist', 'timeline', 'key factors', 'reasoning', 'urgency level',
        'red flags detected', 'recommendation'
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove leading bullet points
        for prefix in ['-', '•', '*']:
            if line.startswith(prefix):
                line = line[1:].strip()
                break
        
        # Pattern: "Condition: XX%" or "Condition - XX%"
        if ':' in line:
            parts = line.split(':')
            condition = parts[0].strip()
            confidence_part = ':'.join(parts[1:]).strip()
        elif ' - ' in line:
            parts = line.split(' - ')
            condition = parts[0].strip()
            confidence_part = ' - '.join(parts[1:]).strip()
        else:
            # No separator found - check if line itself has a condition with percentage
            match = re.search(r'(\d+)%', line)
            if match:
                try:
                    conf = float(match.group(1)) / 100.0
                    # Extract condition name without the percentage
                    cond_name = re.sub(r'\s*\(\d+%\)', '', line).strip()
                    if 0 <= conf <= 1 and cond_name and cond_name.lower() not in skip_labels:
                        if not any(c[0].lower() == cond_name.lower() for c in conditions):
                            conditions.append((cond_name, conf))
                except ValueError:
                    pass
            continue
        
        # If condition is a label and we have more content, recursively extract from confidence_part
        if condition.lower() in skip_labels and confidence_part:
            # Recursively extract from the remaining text
            nested = extract_conditions_from_text(confidence_part)
            for c, conf in nested:
                # Add if not already present (duplicate check)
                if not any(x[0].lower() == c.lower() for x in conditions):
                    conditions.append((c, conf))
            continue
        
        # Extract percentage from confidence part
        match = re.search(r'(\d+)%', confidence_part)
        if match:
            try:
                conf = float(match.group(1)) / 100.0
                if 0 <= conf <= 1 and condition and condition.lower() not in skip_labels:
                    # Check for duplicates
                    if not any(c[0].lower() == condition.lower() for c in conditions):
                        conditions.append((condition, conf))
            except ValueError:
                pass
    
    return conditions


def create_symptom_report(
    symptoms: List[str],
    duration: Optional[str] = None,
    severity: Optional[str] = None
) -> str:
    """
    Create a formatted symptom report.
    
    Args:
        symptoms: List of symptoms
        duration: How long symptoms have been present
        severity: Severity level
    
    Returns:
        Formatted report string
    """
    report = "SYMPTOM REPORT\n"
    report += "=" * 40 + "\n\n"
    
    normalized = normalize_symptoms(symptoms)
    report += f"Symptoms ({len(normalized)}):\n"
    for symptom in normalized:
        report += f"  • {symptom}\n"
    
    if duration:
        report += f"\nDuration: {duration}\n"
    
    if severity:
        report += f"Severity: {severity}\n"
    
    clusters = identify_symptom_clusters(symptoms)
    if clusters:
        report += f"\nSymptom Clusters:\n"
        for cluster, matched in clusters.items():
            report += f"  • {cluster.capitalize()}: {', '.join(matched)}\n"
    
    is_emergency, flags = check_emergency_flags(symptoms)
    if is_emergency:
        report += f"\n⚠️  EMERGENCY FLAGS DETECTED:\n"
        for flag in flags:
            report += f"  • {flag}\n"
        report += "\n🚨 SEEK IMMEDIATE EMERGENCY CARE\n"
    
    report += "\n" + "=" * 40 + "\n"
    
    return report


def save_analysis_json(
    result_dict: Dict,
    filepath: str
) -> None:
    """
    Save analysis result to JSON file.
    
    Args:
        result_dict: Dictionary to save
        filepath: Output file path
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(result_dict, f, indent=2)


def load_analysis_json(filepath: str) -> Dict:
    """
    Load analysis result from JSON file.
    
    Args:
        filepath: Input file path
    
    Returns:
        Loaded dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)


class SymptomValidator:
    """Validate and clean symptom inputs."""
    
    @staticmethod
    def validate_symptom(symptom: str) -> Tuple[bool, str]:
        """
        Validate a single symptom.
        
        Returns:
            Tuple of (is_valid, message)
        """
        symptom = symptom.strip()
        
        if not symptom:
            return False, "Symptom cannot be empty"
        
        if len(symptom) < 2:
            return False, "Symptom description too short"
        
        if len(symptom) > 200:
            return False, "Symptom description too long"
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z\s\-(),./]*$', symptom):
            return False, "Symptom contains invalid characters"
        
        return True, "Valid"
    
    @staticmethod
    def validate_symptoms(symptoms: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a list of symptoms.
        
        Returns:
            Tuple of (all_valid, error_messages)
        """
        errors = []
        
        if not symptoms:
            return False, ["At least one symptom required"]
        
        if len(symptoms) > 20:
            return False, ["Too many symptoms (max 20)"]
        
        for symptom in symptoms:
            is_valid, msg = SymptomValidator.validate_symptom(symptom)
            if not is_valid:
                errors.append(f"'{symptom}': {msg}")
        
        return len(errors) == 0, errors


def demo_utilities():
    """Demonstrate utility functions."""
    print("\n" + "="*60)
    print("SDML UTILITIES DEMO")
    print("="*60 + "\n")
    
    # Test symptom normalization
    print("1. SYMPTOM NORMALIZATION")
    print("-" * 40)
    test_symptoms = ["High Fever", "dry COUGH", "extreme tiredness"]
    normalized = normalize_symptoms(test_symptoms)
    print(f"Original: {test_symptoms}")
    print(f"Normalized: {normalized}\n")
    
    # Test emergency flag detection
    print("2. EMERGENCY FLAG DETECTION")
    print("-" * 40)
    symptoms_with_flag = ["cough", "chest pain", "fatigue"]
    is_emergency, flags = check_emergency_flags(symptoms_with_flag)
    print(f"Symptoms: {symptoms_with_flag}")
    print(f"Is Emergency: {is_emergency}")
    print(f"Red Flags: {flags}\n")
    
    # Test symptom clustering
    print("3. SYMPTOM CLUSTERING")
    print("-" * 40)
    test_symptoms = ["cough", "fever", "sore throat", "nausea", "diarrhea"]
    clusters = identify_symptom_clusters(test_symptoms)
    print(f"Symptoms: {test_symptoms}")
    print(f"Clusters: {clusters}\n")
    
    # Test symptom report
    print("4. SYMPTOM REPORT")
    print("-" * 40)
    report = create_symptom_report(
        ["high fever", "dry cough", "fatigue"],
        duration="3 days",
        severity="moderate"
    )
    print(report)
    
    # Test confidence extraction
    print("5. CONFIDENCE EXTRACTION")
    print("-" * 40)
    test_text = "Influenza: 78% confidence"
    conf = parse_confidence_percentage(test_text)
    print(f"Text: {test_text}")
    print(f"Extracted confidence: {conf:.1%}\n")
    
    # Test symptom validator
    print("6. SYMPTOM VALIDATION")
    print("-" * 40)
    valid, msg = SymptomValidator.validate_symptom("high fever")
    print(f"'high fever': Valid={valid}, Message='{msg}'")
    
    invalid, msg = SymptomValidator.validate_symptom("x")
    print(f"'x': Valid={invalid}, Message='{msg}'\n")


if __name__ == "__main__":
    demo_utilities()
