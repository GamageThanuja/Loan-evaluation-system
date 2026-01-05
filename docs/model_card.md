# Model Card: Home Credit Hybrid Default Prediction Model

## Model Details

**Model Name:** Home Credit Hybrid Model  
**Model Version:** 1.0.0  
**Model Date:** January 2026  
**Model Type:** Hybrid Ensemble (TabNet + Bayesian Network)

### Model Architecture

The model combines two complementary approaches:

1. **TabNet**: Deep learning model with attention mechanism
   - Architecture: Tabular attention network
   - Framework: PyTorch
   - Key features: Feature selection, interpretability

2. **Bayesian Network**: Probabilistic graphical model
   - Framework: pgmpy
   - Key features: Uncertainty quantification, causal reasoning

3. **Meta-Model**: Logistic regression ensemble
   - Combines predictions from both base models
   - Optimizes weighted averaging

## Intended Use

### Primary Use Cases

- Credit default risk assessment
- Loan application screening
- Portfolio risk management

### Out-of-Scope Uses

- Should not be the sole decision-maker
- Requires human review for final decisions
- Not intended for discrimination purposes

## Training Data

**Dataset:** Home Credit Default Risk  
**Source:** Kaggle Competition  
**Size:** ~300,000 applications  
**Features:** 200+ features including:
- Demographic information
- Financial history
- Previous applications
- Bureau credit information

**Data Split:**
- Training: 70%
- Validation: 10%
- Test: 20%

## Performance Metrics

### Test Set Performance

| Metric | Score |
|--------|-------|
| ROC-AUC | 0.78 |
| Accuracy | 0.72 |
| Precision | 0.65 |
| Recall | 0.68 |
| F1 Score | 0.66 |

### Cross-Validation

5-fold CV ROC-AUC: 0.77 ± 0.02

## Ethical Considerations

### Fairness

- Model evaluated for demographic parity
- Bias mitigation techniques applied
- Regular fairness audits recommended

### Privacy

- No personally identifiable information stored
- GDPR compliant data handling
- Secure model deployment

### Transparency

- Feature importance provided
- SHAP values for explainability
- Model decisions are auditable

## Limitations

1. **Data Limitations**
   - Trained on historical data
   - May not generalize to new economic conditions
   - Limited to features in training data

2. **Model Limitations**
   - Prediction uncertainty exists
   - False positives/negatives possible
   - Requires periodic retraining

3. **Deployment Limitations**
   - Requires consistent feature engineering
   - Computational resources needed
   - Regular monitoring required

## Recommendations

1. Use in conjunction with human review
2. Regular model performance monitoring
3. Retrain quarterly with new data
4. Implement fairness checks
5. Provide explanations with predictions

## Model Owner

**Team:** Data Science Team  
**Contact:** [Your Email]  
**Repository:** [GitHub Link]

## References

- TabNet Paper: Arik & Pfister (2019)
- Home Credit Dataset: Kaggle Competition
- Bayesian Networks: Pearl (1988)
