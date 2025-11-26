# Conflict Detection Investigation & Troubleshooting Guide

## Overview

This document explains how conflict detection works in our system, identifies known issues, and provides troubleshooting strategies for improving accuracy.

## How Conflict Detection Works

### Our Implementation

1. **Finding Extraction** (`extract_key_findings`):
   - Extracts "key findings" from paper abstracts or full text
   - Uses keyword-based scoring to prioritize specific, quantitative claims
   - Filters out generic descriptive phrases
   - Returns top N findings per paper

2. **Contradiction Detection** (`find_contradictions`):
   - Compares every finding from paper 1 against every finding from paper 2
   - Uses Natural Language Inference (NLI) model to classify relationships
   - Flags pairs where the model predicts "contradiction" with confidence ≥ threshold (default 0.8)

3. **NLI Model**: `cross-encoder/nli-deberta-v3-base`
   - Cross-encoder architecture (encodes both inputs together)
   - Fine-tuned on MNLI (Multi-Genre Natural Language Inference) dataset
   - Classifies relationships as: contradiction, entailment, or neutral

### Current Input Format

```python
result = self.nli_pipeline(f"{f1} [SEP] {f2}")
```

**⚠️ POTENTIAL ISSUE**: This format may not be correct for cross-encoder models. Cross-encoder models typically expect inputs in a specific format, often as a tuple or using the model's tokenizer directly.

## Known Issues

### 1. False Positives: Different Topics Flagged as Contradictions

**Problem**: Findings about different research questions/interventions are being flagged as contradictory.

**Example**:
- Finding 1: "Peer tutoring improved reading comprehension"
- Finding 2: "Multimedia instruction improved history knowledge"
- Model flags as 99% confident contradiction

**Why this happens**:
- NLI models are trained to detect logical contradictions (e.g., "The cat is black" vs "The cat is white")
- They are NOT trained to understand that different interventions studying different outcomes are not contradictory
- The model may interpret "different" as "contradictory" when findings address different topics
- Cross-encoder models can be overconfident, producing high scores even for edge cases

### 2. Input Format May Be Incorrect

**Issue**: Using `f"{f1} [SEP] {f2}"` as a string may not be the correct format for `cross-encoder/nli-deberta-v3-base`.

**Expected format for cross-encoder models**:
- Cross-encoder models typically expect inputs as a list of tuples: `[(premise, hypothesis), ...]`
- Or using the model's tokenizer with special tokens
- The `[SEP]` token might not be properly recognized when passed as a plain string

### 3. Model Training Context Mismatch

**Issue**: The model was trained on MNLI, which contains:
- Premise-hypothesis pairs designed for logical inference
- Examples like: "The man is sleeping" (premise) vs "The man is awake" (hypothesis) → contradiction

**Our use case**:
- Comparing research findings from different studies
- Findings may be about different interventions, populations, or outcomes
- Not designed for this type of comparison

### 4. Overconfident Scores

**Issue**: Model reports 99% confidence for what are clearly false positives.

**Possible reasons**:
- Cross-encoder models can be overconfident, especially on out-of-distribution data
- The model may be picking up on surface-level differences rather than true logical contradictions
- High confidence doesn't necessarily mean the model is correct

## Troubleshooting Strategies

### 1. Verify Input Format

**Check**: Is the input format correct for cross-encoder models?

**Action**: Research the correct usage for `cross-encoder/nli-deberta-v3-base`:
- Check Hugging Face model card/documentation
- Verify if it should be used with `pipeline()` or directly with tokenizer
- Test with known contradiction/entailment examples to verify it works

**Expected format might be**:
```python
# Option 1: Direct model usage
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tokenizer = AutoTokenizer.from_pretrained("cross-encoder/nli-deberta-v3-base")
model = AutoModelForSequenceClassification.from_pretrained("cross-encoder/nli-deberta-v3-base")
inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
outputs = model(**inputs)

# Option 2: Using sentence-transformers (if it's a sentence-transformers model)
from sentence_transformers import CrossEncoder
model = CrossEncoder('cross-encoder/nli-deberta-v3-base')
scores = model.predict([(f1, f2)])
```

### 2. Add Topic/Intervention Filtering

**Strategy**: Filter out comparisons between findings about different topics.

**Implementation ideas**:
- Extract intervention type, outcome, or population from findings
- Only compare findings that address the same or similar research questions
- Use keyword matching or simple NLP to detect topic similarity before NLI comparison

**Example**:
```python
def are_same_topic(finding1: str, finding2: str) -> bool:
    """Check if findings are about the same topic/intervention."""
    # Extract key terms (intervention, outcome, population)
    # Compare similarity
    # Return True only if they're comparable
    pass
```

### 3. Increase Confidence Threshold

**Current**: 0.8 (80%)

**Suggestion**: Try higher thresholds (0.9, 0.95) to reduce false positives.

**Trade-off**: May miss some true contradictions, but reduces noise.

### 4. Add Post-Processing Filters

**Strategy**: Add heuristics to filter obvious false positives.

**Examples**:
- If findings mention different interventions → likely not contradictory
- If findings mention different outcomes → likely not contradictory
- If findings mention different populations → likely not contradictory
- Only flag if findings are about the same intervention/outcome/population AND model says contradiction

### 5. Use a Different Model or Approach

**Alternatives**:
- **Sentence similarity models**: Use semantic similarity to detect when findings are about different topics
- **Fine-tune on research findings**: Train/fine-tune a model specifically on research paper contradictions
- **Rule-based pre-filtering**: Use keyword matching to identify same-topic findings before NLI
- **Hybrid approach**: Combine NLI with topic modeling or keyword extraction

### 6. Improve Finding Extraction

**Current issue**: Extracted findings may be too generic or not specific enough.

**Improvements**:
- Extract findings that include specific outcomes, effect sizes, or quantitative results
- Ensure findings are complete sentences with clear claims
- Filter findings to only include testable, specific claims (not descriptions of what was studied)

### 7. Add Context to Findings

**Strategy**: Include more context when comparing findings.

**Example**: Instead of comparing:
- "Peer tutoring improved reading"
- "Multimedia improved history"

Compare with context:
- "Peer tutoring improved reading comprehension in elementary students"
- "Multimedia instruction improved history knowledge in high school students"

This might help the model recognize they're about different topics.

### 8. Manual Review Flag

**Strategy**: Add a flag for "requires manual review" when:
- Confidence is high but findings are about different topics
- Model confidence is high but findings don't clearly contradict
- Findings are about different interventions/outcomes

## Testing & Validation

### Test Cases to Verify

1. **True contradiction**: "Intervention A increased scores" vs "Intervention A decreased scores" (same intervention, opposite effects)
2. **Different topics (should NOT flag)**: "Intervention A improved reading" vs "Intervention B improved math"
3. **Same topic, different results (edge case)**: "Intervention A improved reading in elementary" vs "Intervention A had no effect on reading in high school"
4. **Entailment (should NOT flag)**: "Intervention A improved reading" vs "Intervention A was effective for reading"

### Debugging Steps

1. **Log raw model outputs**: Print the full model response (all labels and scores, not just contradiction)
2. **Test with known examples**: Use simple test cases to verify the model works correctly
3. **Compare with other models**: Try different NLI models to see if results are consistent
4. **Inspect extracted findings**: Verify that findings are specific and testable

## Recommended Next Steps

1. **Immediate**: Verify the input format is correct for cross-encoder models
2. **Short-term**: Add topic/intervention filtering before NLI comparison
3. **Medium-term**: Implement post-processing filters to remove obvious false positives
4. **Long-term**: Consider fine-tuning or using a model specifically trained for research findings

## References

- Hugging Face Model Card: `cross-encoder/nli-deberta-v3-base`
- MNLI Dataset: Multi-Genre Natural Language Inference
- Cross-encoder architecture: Encodes both inputs together (vs. bi-encoder which encodes separately)

