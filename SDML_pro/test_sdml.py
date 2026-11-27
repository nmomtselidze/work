"""
Test suite for SDML system.
Unit tests for core functionality and medical logic.
"""

import unittest
from SDML_enhanced import SymptomInput, DiagnosisResult, SDMLConfig
from sdml_utils import (
    normalize_symptom,
    normalize_symptoms,
    check_emergency_flags,
    identify_symptom_clusters,
    parse_confidence_percentage,
    extract_conditions_from_text,
    create_symptom_report,
    SymptomValidator,
)


class TestSymptomNormalization(unittest.TestCase):
    """Test symptom normalization."""
    
    def test_normalize_exact_match(self):
        """Test exact symptom match."""
        result = normalize_symptom("fever")
        self.assertEqual(result, "fever")
    
    def test_normalize_case_insensitive(self):
        """Test case-insensitive normalization."""
        result = normalize_symptom("HIGH FEVER")
        self.assertEqual(result, "fever")
    
    def test_normalize_variation(self):
        """Test symptom variation mapping."""
        result = normalize_symptom("extreme tiredness")
        self.assertEqual(result, "fatigue")
    
    def test_normalize_unknown_symptom(self):
        """Test unknown symptom passthrough."""
        result = normalize_symptom("rare symptom xyz")
        self.assertEqual(result, "rare symptom xyz")
    
    def test_normalize_multiple_symptoms(self):
        """Test normalizing multiple symptoms."""
        symptoms = ["HIGH FEVER", "Dry Cough", "extreme tiredness"]
        result = normalize_symptoms(symptoms)
        expected = ["fever", "cough", "fatigue"]
        self.assertEqual(result, expected)


class TestEmergencyDetection(unittest.TestCase):
    """Test emergency red flag detection."""
    
    def test_emergency_flag_detected(self):
        """Test detection of emergency symptoms."""
        symptoms = ["high fever", "chest pain", "cough"]
        is_emergency, flags = check_emergency_flags(symptoms)
        self.assertTrue(is_emergency)
        self.assertIn("chest pain", flags)
    
    def test_no_emergency_flags(self):
        """Test non-emergency symptoms."""
        symptoms = ["mild cough", "fatigue"]
        is_emergency, flags = check_emergency_flags(symptoms)
        self.assertFalse(is_emergency)
        self.assertEqual(len(flags), 0)
    
    def test_difficulty_breathing_flag(self):
        """Test difficulty breathing detection."""
        symptoms = ["shortness of breath", "cough"]
        is_emergency, flags = check_emergency_flags(symptoms)
        self.assertTrue(is_emergency)
        self.assertIn("shortness of breath", flags)
    
    def test_multiple_emergency_flags(self):
        """Test multiple emergency flags."""
        symptoms = ["chest pain", "difficulty breathing", "nausea"]
        is_emergency, flags = check_emergency_flags(symptoms)
        self.assertTrue(is_emergency)
        self.assertEqual(len(flags), 2)


class TestSymptomClustering(unittest.TestCase):
    """Test symptom clustering."""
    
    def test_respiratory_cluster(self):
        """Test respiratory symptom clustering."""
        symptoms = ["cough", "fever", "sore throat"]
        clusters = identify_symptom_clusters(symptoms)
        self.assertIn("respiratory", clusters)
    
    def test_gastrointestinal_cluster(self):
        """Test GI symptom clustering."""
        symptoms = ["nausea", "vomiting", "diarrhea"]
        clusters = identify_symptom_clusters(symptoms)
        self.assertIn("gastrointestinal", clusters)
    
    def test_multiple_clusters(self):
        """Test multiple symptom clusters."""
        symptoms = ["cough", "fever", "nausea", "vomiting"]
        clusters = identify_symptom_clusters(symptoms)
        self.assertIn("respiratory", clusters)
        self.assertIn("gastrointestinal", clusters)
    
    def test_no_clusters(self):
        """Test unknown symptoms produce no clusters."""
        symptoms = ["rare symptom a", "rare symptom b"]
        clusters = identify_symptom_clusters(symptoms)
        self.assertEqual(len(clusters), 0)


class TestConfidenceExtraction(unittest.TestCase):
    """Test confidence score extraction."""
    
    def test_extract_percentage(self):
        """Test percentage extraction."""
        text = "Influenza: 78%"
        result = parse_confidence_percentage(text)
        self.assertAlmostEqual(result, 0.78, places=2)
    
    def test_extract_high_percentage(self):
        """Test extracting high percentages."""
        text = "95% confidence"
        result = parse_confidence_percentage(text)
        self.assertAlmostEqual(result, 0.95, places=2)
    
    def test_default_when_no_percentage(self):
        """Test default value when no percentage found."""
        text = "Some diagnosis"
        result = parse_confidence_percentage(text, default=0.6)
        self.assertEqual(result, 0.6)
    
    def test_clamp_above_100(self):
        """Test that percentages above 100 are clamped."""
        text = "150% confidence"
        result = parse_confidence_percentage(text)
        self.assertEqual(result, 1.0)


class TestConditionExtraction(unittest.TestCase):
    """Test condition/diagnosis extraction."""
    
    def test_extract_condition_with_colon(self):
        """Test extracting condition with colon format."""
        text = "Influenza: 75%"
        result = extract_conditions_from_text(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "Influenza")
        self.assertAlmostEqual(result[0][1], 0.75, places=2)
    
    def test_extract_multiple_conditions(self):
        """Test extracting multiple conditions."""
        text = """
        - Influenza: 75%
        - COVID-19: 60%
        """
        result = extract_conditions_from_text(text)
        self.assertGreaterEqual(len(result), 2)
    
    def test_extract_no_duplicates(self):
        """Test that duplicate conditions are not extracted."""
        text = """
        Influenza: 75%
        Influenza - 75%
        """
        result = extract_conditions_from_text(text)
        self.assertEqual(len(result), 1)


class TestSymptomInput(unittest.TestCase):
    """Test SymptomInput data structure."""
    
    def test_symptom_input_basic(self):
        """Test basic SymptomInput creation."""
        input_data = SymptomInput(
            symptoms=["fever", "cough"]
        )
        self.assertEqual(len(input_data.symptoms), 2)
        self.assertIsNone(input_data.duration)
    
    def test_symptom_input_full(self):
        """Test SymptomInput with all fields."""
        input_data = SymptomInput(
            symptoms=["fever", "cough"],
            duration="3 days",
            severity="moderate",
            medical_history=["hypertension"],
            medications=["Lisinopril"],
            allergies=["Penicillin"]
        )
        self.assertEqual(input_data.duration, "3 days")
        self.assertEqual(input_data.severity, "moderate")
        self.assertEqual(len(input_data.medical_history), 1)
    
    def test_symptom_input_to_text(self):
        """Test converting SymptomInput to text."""
        input_data = SymptomInput(
            symptoms=["fever", "cough"],
            duration="3 days",
            severity="moderate"
        )
        text = input_data.to_text()
        self.assertIn("fever", text)
        self.assertIn("cough", text)
        self.assertIn("3 days", text)
        self.assertIn("moderate", text)


class TestDiagnosisResult(unittest.TestCase):
    """Test DiagnosisResult data structure."""
    
    def test_diagnosis_result_creation(self):
        """Test DiagnosisResult creation."""
        result = DiagnosisResult(
            primary_condition="Influenza",
            confidence_score=0.78,
            differential_diagnoses=[
                ("COVID-19", 0.65),
                ("Common Cold", 0.45)
            ],
            reasoning="High fever and cough suggest viral respiratory infection"
        )
        self.assertEqual(result.primary_condition, "Influenza")
        self.assertEqual(result.confidence_score, 0.78)
        self.assertIsNotNone(result.timestamp)
    
    def test_diagnosis_result_to_dict(self):
        """Test converting DiagnosisResult to dictionary."""
        result = DiagnosisResult(
            primary_condition="Influenza",
            confidence_score=0.78,
            differential_diagnoses=[
                ("COVID-19", 0.65)
            ],
            reasoning="Test reasoning"
        )
        result_dict = result.to_dict()
        self.assertEqual(result_dict["primary_condition"], "Influenza")
        self.assertEqual(len(result_dict["differential_diagnoses"]), 1)
    
    def test_diagnosis_result_to_report(self):
        """Test generating report from DiagnosisResult."""
        result = DiagnosisResult(
            primary_condition="Influenza",
            confidence_score=0.78,
            differential_diagnoses=[
                ("COVID-19", 0.65)
            ],
            reasoning="High fever and cough",
            red_flags=["Severe shortness of breath"],
            recommendations=["See doctor", "Rest"]
        )
        report = result.to_report()
        self.assertIn("INFLUENZA", report.upper())
        self.assertIn("78", report)  # Check for 78% in report
        self.assertIn("COVID-19", report)
        self.assertIn("DISCLAIMER", report)


class TestSymptomValidator(unittest.TestCase):
    """Test symptom validation."""
    
    def test_valid_symptom(self):
        """Test valid symptom."""
        is_valid, msg = SymptomValidator.validate_symptom("high fever")
        self.assertTrue(is_valid)
    
    def test_empty_symptom(self):
        """Test empty symptom validation."""
        is_valid, msg = SymptomValidator.validate_symptom("")
        self.assertFalse(is_valid)
    
    def test_too_short_symptom(self):
        """Test too short symptom."""
        is_valid, msg = SymptomValidator.validate_symptom("x")
        self.assertFalse(is_valid)
    
    def test_too_long_symptom(self):
        """Test too long symptom."""
        long_symptom = "a" * 300
        is_valid, msg = SymptomValidator.validate_symptom(long_symptom)
        self.assertFalse(is_valid)
    
    def test_invalid_characters(self):
        """Test symptom with invalid characters."""
        is_valid, msg = SymptomValidator.validate_symptom("fever@#$%")
        self.assertFalse(is_valid)
    
    def test_validate_multiple_symptoms(self):
        """Test validating multiple symptoms."""
        symptoms = ["fever", "cough", "fatigue"]
        is_valid, errors = SymptomValidator.validate_symptoms(symptoms)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_empty_list(self):
        """Test validating empty symptom list."""
        is_valid, errors = SymptomValidator.validate_symptoms([])
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)
    
    def test_validate_too_many_symptoms(self):
        """Test validating too many symptoms."""
        symptoms = [f"symptom_{i}" for i in range(25)]
        is_valid, errors = SymptomValidator.validate_symptoms(symptoms)
        self.assertFalse(is_valid)


class TestSymptomReport(unittest.TestCase):
    """Test symptom report generation."""
    
    def test_simple_report(self):
        """Test generating simple report."""
        report = create_symptom_report(["fever", "cough"])
        self.assertIn("SYMPTOM REPORT", report)
        self.assertIn("fever", report)
        self.assertIn("cough", report)
    
    def test_report_with_duration_and_severity(self):
        """Test report with optional fields."""
        report = create_symptom_report(
            ["fever"],
            duration="3 days",
            severity="moderate"
        )
        self.assertIn("3 days", report)
        self.assertIn("moderate", report)
    
    def test_report_with_clusters(self):
        """Test report showing symptom clusters."""
        report = create_symptom_report(["fever", "cough", "nausea"])
        self.assertIn("Symptom Clusters", report)
    
    def test_report_with_emergency_flags(self):
        """Test report with emergency warnings."""
        report = create_symptom_report(["chest pain"])
        self.assertIn("EMERGENCY", report)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSymptomNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestEmergencyDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestSymptomClustering))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestConditionExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestSymptomInput))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagnosisResult))
    suite.addTests(loader.loadTestsFromTestCase(TestSymptomValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestSymptomReport))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
