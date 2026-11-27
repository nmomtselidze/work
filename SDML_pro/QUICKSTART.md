# SDML Enhanced - Quick Start Guide

Get up and running with the enhanced SDML in 5 minutes!

## Installation

1. **Install dependencies** (if not already installed):
   ```bash
   cd /media/user/dsk64/monowork/SDML_pro
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python -c "from SDML_enhanced import SDMLSystem; print('✓ Ready!')"
   ```

## Three Ways to Use SDML

### 1. 🎯 Quick Python API (Fastest)

```python
from SDML_enhanced import SDMLSystem, SymptomInput

# Initialize
system = SDMLSystem()

# Analyze
symptoms = SymptomInput(
    symptoms=["high fever", "dry cough", "fatigue"],
    duration="3 days",
    severity="moderate"
)

result = system.analyze_symptoms(symptoms)

# Display
print(result.to_report())

# Save
import json
with open('result.json', 'w') as f:
    json.dump(result.to_dict(), f, indent=2)
```

### 2. 🖥️ Interactive CLI (Full Experience)

```bash
python sdml_cli.py --interactive
```

Then:
1. Select "Run symptom analysis" 
2. Enter symptoms (e.g., "fever, cough, fatigue")
3. Answer optional questions
4. View multi-agent analysis
5. Save results to JSON

### 3. 🎬 Demo Mode (See Examples)

```bash
python sdml_cli.py --demo
```

Shows pre-configured example cases with full analysis.

## Usage Examples

### Simple One-Liner
```python
from SDML_enhanced import SDMLSystem
system = SDMLSystem()
result = system.analyze_simple("high fever, dry cough, fatigue")
print(result.to_report())
```

### With Medical Context
```python
from SDML_enhanced import SymptomInput, SDMLSystem

system = SDMLSystem()
symptoms = SymptomInput(
    symptoms=["chest pain", "shortness of breath"],
    medical_history=["heart disease"],
    medications=["Aspirin"],
    allergies=["Penicillin"]
)
result = system.analyze_symptoms(symptoms)
print(result.to_report())
```

### JSON Output
```python
result = system.analyze_symptoms(symptoms)
result_dict = result.to_dict()

# Access results
print(f"Primary: {result_dict['primary_condition']}")
print(f"Confidence: {result_dict['confidence_score']:.1%}")
print(f"Differential: {result_dict['differential_diagnoses']}")
```

## Utility Functions

### Quick Symptom Checks

```python
from sdml_utils import (
    normalize_symptoms,
    check_emergency_flags,
    identify_symptom_clusters,
    create_symptom_report
)

# Normalize
normalized = normalize_symptoms(["HIGH FEVER", "extreme tiredness"])
# Output: ["fever", "fatigue"]

# Check emergency
is_emergency, flags = check_emergency_flags(["chest pain", "cough"])
# Output: (True, ["chest pain"])

# Identify clusters
clusters = identify_symptom_clusters(["fever", "cough", "nausea"])
# Output: {"respiratory": [...], "gastrointestinal": [...]}

# Create report
report = create_symptom_report(
    ["fever", "cough"],
    duration="3 days",
    severity="moderate"
)
print(report)
```

## Running Tests

```bash
# Run all 38 tests
python test_sdml.py

# Check specific functionality
python sdml_utils.py    # Utilities demo
```

## Common Scenarios

### 🏥 Patient with Cold Symptoms
```python
from SDML_enhanced import SDMLSystem, SymptomInput

system = SDMLSystem()
symptoms = SymptomInput(
    symptoms=["sore throat", "runny nose", "cough", "mild fever"],
    duration="2 days"
)
result = system.analyze_symptoms(symptoms)
print(result.to_report())
```

### 🚨 Potential Emergency
```python
symptoms = SymptomInput(symptoms=["chest pain", "difficulty breathing"])
result = system.analyze_symptoms(symptoms)
# System automatically flags as EMERGENCY
```

### 📋 Detailed Medical Consultation
```python
symptoms = SymptomInput(
    symptoms=["abdominal pain", "nausea", "vomiting"],
    duration="1 week",
    severity="severe",
    medical_history=["Crohn's disease", "IBS"],
    medications=["Mesalamine"],
    allergies=["Aspirin", "NSAIDs"]
)
result = system.analyze_symptoms(symptoms)
# Full context-aware analysis
```

## Understanding Results

### DiagnosisResult Components

```python
result.primary_condition      # Main diagnosis (string)
result.confidence_score       # 0.0-1.0 (float)
result.differential_diagnoses # [(condition, score), ...] (list)
result.reasoning              # Clinical reasoning (string)
result.red_flags             # ["flag1", "flag2"] or None
result.recommendations       # ["action1", "action2"] or None
result.timestamp             # ISO timestamp (string)
```

### Confidence Scores
- **0.9+**: Very high confidence
- **0.7-0.9**: High confidence
- **0.5-0.7**: Moderate confidence
- **<0.5**: Low confidence (may warrant additional investigation)

## Troubleshooting

### "Model not found" error
```bash
# Install HuggingFace model
pip install transformers huggingface_hub
```

### "CUDA out of memory"
```python
from SDML_enhanced import SDMLConfig, SDMLSystem

config = SDMLConfig(device_map="cpu")
system = SDMLSystem(config)
```

### Slow inference
- Use GPU if available
- Reduce `max_new_tokens` in config
- Smaller model: Use `Qwen/Qwen2.5-0.5B-Instruct` instead

### Analysis seems inaccurate
- Provide more context (medical history, medications)
- Check red flags were detected if serious symptoms
- Remember: This is AI assistance, not medical diagnosis

## Next Steps

1. **Learn more**: Read `SDML_ENHANCEMENT_GUIDE.md`
2. **Explore APIs**: Check `SDML_enhanced.py` docstrings
3. **Customize**: Modify `SDMLConfig` for your needs
4. **Integrate**: Use JSON output for your app
5. **Extend**: Create custom agents for specific domains

## Important Reminder

⚠️ **Medical Disclaimer**: This is an AI-powered analysis tool, not a substitute for professional medical care. Always consult qualified healthcare professionals for diagnosis and treatment.

For emergencies, **call 911** or your local emergency number.

---

Ready to get started? Run:
```bash
python sdml_cli.py --demo
```

