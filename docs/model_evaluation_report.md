# Machine Learning Model Evaluation Report

**Model Version:** `rto-logisticregression-v1.0`  
**Algorithm:** LogisticRegression with Scikit-learn Pipeline  
**Date:** October 30, 2026  
**Holdout Window:** September 2026 (Strict out-of-time evaluation)

---

## 1. Dataset Profiling and Splits

| Metric | Count | Note |
|---|---|---|
| Raw records | 2018 | Supplied in `orders_sample.csv` |
| Deduplicated records | 1988 | 30 duplicate order IDs removed |
| Unresolved records | 5 | `IN_TRANSIT` excluded from supervised training |
| Resolved records | 1983 | Training + Validation + Test |
| Delivered count | 1421 | Target = 0 (71.7%) |
| RTO count | 562 | Target = 1 (28.3%) |

### Chronological Splits
- **Training Period:** April – July 2026 (1294 samples, RTO: 29.1%)
- **Validation Period:** August 2026 (361 samples, RTO: 28.0%)
- **Holdout Evaluation Period:** September 2026 (328 samples, RTO: 25.9%)

---

## 2. Validation Model Comparison

| Model | Validation ROC-AUC | Validation PR-AUC |
|---|---|---|
| Baseline Logistic Regression | 0.7056 | 0.4834 |
| Candidate HistGradientBoosting | 0.6887 | 0.4768 |

**Selected Model:** `LogisticRegression` due to superior calibrated ranking and out-of-time PR-AUC.

---

## 3. September 2026 Holdout Performance

| Metric | Score | Target / Benchmark |
|---|---|---|
| **ROC-AUC** | **0.7393** | Measures ranking capability |
| **PR-AUC** | **0.5168** | Area under precision-recall curve |
| **Precision** | **0.3646** | True RTOs among flagged |
| **Recall** | **0.7765** | Coverage of preventable RTOs |
| **F1 Score** | **0.4962** | Harmonic mean of precision/recall |
| **Brier Score** | **0.2026** | Calibrated probability accuracy |

### Confusion Matrix (September Holdout)
```
                Predicted Delivered    Predicted RTO
Actual Delivered       128                  115
Actual RTO             19                   66
```

---

## 4. Key Takeaways & Limitations
1. **No Data Leakage:** Preprocessors and scalers are fitted exclusively on chronological training slices.
2. **First-Time Customer Protection:** Model score is treated as a probability input to deterministic business rules; first-time buyers are not penalized solely for lack of prior orders.
3. **Small Sample Uncertainty:** Sparse geographical clusters have shrinkage applied towards the prior baseline to prevent overfitting on 1-2 order pincodes.
