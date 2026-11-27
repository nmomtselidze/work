# SDML Enhancement Guide

## Overview

The Small Disease Language Model (SDML) has been significantly enhanced with production-ready features, multi-agent architecture, and comprehensive tooling.

## Key Enhancements

### 1. **Modular Multi-Agent Architecture**

The enhanced SDML system uses specialized agents for different aspects of medical analysis:

- **TriageAgent**: Safety assessment and emergency detection
- **DiagnosticAgent**: Medical diagnosis and differential analysis
- **RecommendationAgent**: Clinical recommendations and next steps
- **PatientCommunicationAgent**: Patient-friendly report generation

Each agent has its own system prompt optimized for its role.

### 2. **Structured Data Models**

#### SymptomInput
Represents patient symptoms with comprehensive context:
```python
symptoms_input = SymptomInput(
    symptoms=["high fever", "dry cough"],
    duration="3 days",
    severity="moderate",
    medical_history=["hypertension"],
    medications=["Lisinopril"],
    allergies=["Penicillin"]
)
```

#### DiagnosisResult
Structured output with medical analysis:
```python
result = DiagnosisResult(
    primary_condition="Influenza",
    confidence_score=0.78,
    differential_diagnoses=[("COVID-19", 0.65)],
    reasoning="Clinical reasoning here",
    red_flags=["Severe shortness of breath"],
    recommendations=["See doctor", "Rest"]
)
```

### 3. **Configuration Management**

Centralized configuration with sensible defaults:
```python
config = SDMLConfig(
    model_id="HuggingFaceTB/SmolLM2-1.7B-Instruct",
    max_new_tokens=300,
    temperature=0.15,
    device_map="auto",
    min_confidence_threshold=0.6
)

system = SDMLSystem(config)
```

### 4. **Confidence Scoring**

All diagnoses include confidence scores (0.0-1.0) and differential diagnoses with individual scores.

### 5. **Emergency Detection**

Built-in red flag detection for life-threatening symptoms:
- Chest pain
- Difficulty breathing
- Loss of consciousness
- Severe bleeding
- And 15+ other critical symptoms

### 6. **Symptom Validation and Normalization**

- Input validation (length, characters, count)
- Automatic symptom normalization
- Symptom clustering (respiratory, GI, cardiovascular, etc.)
- Canonical symptom mapping

### 7. **Logging and Monitoring**

Comprehensive logging at all levels:
```python
logger.info("Analysis started")
logger.error("Failed to initialize model")
```

### 8. **Report Generation**

Multiple output formats:
- Structured JSON for integration
- Formatted clinical reports
- Patient-friendly summaries

## File Structure

```
SDML_pro/
├── SDML_enhanced.py          # Main system with multi-agent architecture
├── sdml_utils.py             # Utility functions and validators
├── sdml_cli.py               # Command-line interface
├── test_sdml.py              # Comprehensive test suite
├── SDML_ENHANCEMENT_GUIDE.md # This file
├── requirements.txt          # Dependencies
└── results/                  # Analysis results (auto-created)
```

## Usage

### 1. **Python API**

```python
from SDML_enhanced import SDMLSystem, SymptomInput

# Initialize system
system = SDMLSystem()

# Create symptom input
symptoms = SymptomInput(
    symptoms=["high fever", "dry cough", "fatigue"],
    duration="3 days",
    severity="moderate"
)

# Run analysis
result = system.analyze_symptoms(symptoms)

# Display report
print(result.to_report())

# Save to JSON
import json
with open('analysis.json', 'w') as f:
    json.dump(result.to_dict(), f)
```

### 2. **CLI - Interactive Mode**

```bash
python sdml_cli.py --interactive
```

Features:
- Interactive symptom collection
- Multi-step medical questionnaire
- Real-time analysis
- History tracking
- Result saving

### 3. **CLI - Demo Mode**

```bash
python sdml_cli.py --demo
```

Runs automated demonstration with example cases.

### 4. **Utilities**

```python
from sdml_utils import (
    normalize_symptoms,
    check_emergency_flags,
    identify_symptom_clusters,
    create_symptom_report,
    SymptomValidator
)

# Normalize symptoms
normalized = normalize_symptoms(["HIGH FEVER", "extreme tiredness"])
# Output: ["fever", "fatigue"]

# Check for emergencies
is_emergency, flags = check_emergency_flags(["chest pain", "cough"])
# Output: (True, ["chest pain"])

# Identify clusters
clusters = identify_symptom_clusters(["fever", "cough", "nausea"])
# Output: {"respiratory": ["fever", "cough"], "gastrointestinal": ["nausea"]}

# Create report
report = create_symptom_report(
    ["fever", "cough"],
    duration="3 days",
    severity="moderate"
)
print(report)
```

## Medical Features

### Confidence Scoring
- Each diagnosis includes a confidence percentage
- Differential diagnoses ranked by probability
- Threshold-based filtering (default: 60%)

### Red Flag Detection
Automatic detection of emergency symptoms:
- Respiratory: Difficulty breathing, severe shortness of breath
- Cardiovascular: Chest pain, severe chest pressure
- Neurological: Loss of consciousness, signs of stroke
- Other: Severe bleeding, uncontrolled seizures

### Symptom Clusters
Automatic grouping by medical specialty:
- **Respiratory**: Fever, cough, sore throat
- **Gastrointestinal**: Nausea, vomiting, diarrhea
- **Cardiovascular**: Chest pain, palpitations, dizziness
- **Neurological**: Headache, numbness, confusion
- **Allergic**: Itching, rash, swelling

### Medical Context
- Medical history integration
- Current medications tracking
- Allergy information
- Symptom duration and severity

## Testing

Run comprehensive test suite:

```bash
python test_sdml.py
```

Tests cover:
- Symptom normalization
- Emergency detection
- Symptom clustering
- Confidence extraction
- Input validation
- Data structures
- Report generation

## Configuration Options

### SDMLConfig Parameters

```python
class SDMLConfig:
    model_id: str                           # Model to use
    max_new_tokens: int = 300              # Max response length
    temperature: float = 0.15              # Generation temperature
    do_sample: bool = True                 # Use sampling
    device_map: str = "auto"               # Device selection
    clean_up_tokenization: bool = False    # Tokenizer cleanup
    disable_progress: bool = True          # Suppress progress bars
    min_confidence_threshold: float = 0.6  # Minimum confidence
```

Lower temperature (0.1-0.2) = more consistent, deterministic
Higher temperature (0.5-0.9) = more varied, creative

## Error Handling

The system includes robust error handling:
- Input validation with detailed error messages
- Model initialization error reporting
- Agent execution error logging
- Graceful degradation on failures

## Performance Considerations

- **Model Size**: SmolLM2-1.7B is lightweight (~3GB)
- **Inference Time**: ~5-30 seconds per analysis (CPU/GPU dependent)
- **Memory**: ~4-8GB recommended
- **Device Support**: CUDA, MPS (Apple), CPU

## Safety Features

1. **Emergency Detection**: Automatic red flag identification
2. **Disclaimer Inclusion**: All reports include medical disclaimer
3. **Multi-Agent Verification**: Multiple agents cross-check analysis
4. **Input Validation**: Comprehensive symptom validation
5. **Confidence Thresholding**: Low-confidence diagnoses flagged

## Extension Points

### Adding Custom Agents

```python
from SDML_enhanced import MedicalAgent

class CustomAgent(MedicalAgent):
    def get_system_prompt(self) -> str:
        return "Your custom prompt here"

# Then in SDMLSystem:
self.custom_agent = CustomAgent(self.pipe, self.tokenizer, self.config, "CustomAgent")
```

### Custom Symptom Mappings

Edit `SYMPTOM_MAPPINGS` in `sdml_utils.py`:

```python
SYMPTOM_MAPPINGS = {
    "your_canonical_symptom": ["variation1", "variation2"],
    # ...
}
```

### Adding Red Flags

Edit `EMERGENCY_RED_FLAGS` in `sdml_utils.py`:

```python
EMERGENCY_RED_FLAGS = {
    "existing_flag",
    "new_critical_symptom",
    # ...
}
```

## Best Practices

1. **Always include medical history** when available
2. **Document medication and allergies** for drug interaction awareness
3. **Monitor confidence scores** - low scores indicate uncertainty
4. **Review red flags immediately** - escalate to emergency care
5. **Never replace professional medical advice** with AI analysis
6. **Save analyses** for record-keeping and follow-up
7. **Report adverse outcomes** to improve system

## Troubleshooting

### Model Loading Issues
```
Error: "Failed to download model"
Solution: Check internet connection, HF_TOKEN, disk space
```

### Out of Memory
```
Error: "CUDA out of memory"
Solution: Use device_map="cpu" or reduce max_new_tokens
```

### Slow Inference
```
Symptom: Analysis takes >60 seconds
Solution: Check device, consider CPU->GPU, reduce token count
```

## Future Enhancements

Potential additions:
- [ ] Medical knowledge base integration
- [ ] Drug interaction checker
- [ ] Prescription management
- [ ] Insurance/cost estimation
- [ ] Specialist referral suggestions
- [ ] Multi-language support
- [ ] Integration with EHR systems
- [ ] Real-time patient monitoring
- [ ] Clinical trial matching
- [ ] Medical literature citations

## Contributing

To improve the SDML system:

1. Run existing tests: `python test_sdml.py`
2. Add test cases for new features
3. Update documentation
4. Validate with example cases
5. Submit improvements

## Disclaimer

**This is an AI-powered medical analysis tool, NOT a substitute for professional medical diagnosis or treatment. Always consult with qualified healthcare professionals for medical advice, diagnosis, and treatment.**

---

For questions or issues, refer to the main repository documentation or contact the development team.
