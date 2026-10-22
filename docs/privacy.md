# EIT Privacy & Ethical Computing Policy

## 1. Ethical Stance on Facial Expressions

Facial expressions, micro-expressions, head pose, and approximate gaze **do not reliably indicate**:
- Actual subjective emotion
- Comprehension or understanding of a concept
- Attention or engagement level
- Cognitive capability or intelligence

Scientific literature in affective computing demonstrates that facial muscle configurations vary dramatically across individuals, cultures, and contexts.

**EIT Policy:**
1. Facial expression predictions are strictly treated as **uncertain, secondary, and optional signals**.
2. Predictions are **never** used to evaluate, grade, diagnose, or penalize students.
3. The platform remains **100% usable** when the webcam is disabled or unavailable.

---

## 2. Webcam Stream Privacy & Data Minimization

- **Explicit Informed Consent**: The webcam is never enabled automatically. Students must review the consent notice and click "Enable Webcam".
- **Zero Raw Frame Storage**: Raw video frames are decoded transiently in memory, processed through MobileNetV2, and immediately discarded. No video or image files are written to disk or the database.
- **Hardware Teardown**: Calling `disable()` or navigating away from the lesson immediately invokes `track.stop()` on all hardware media streams.
- **Aggregated Summaries**: Only coarse statistical counts (e.g. `{"neutral": 8, "happy": 2}`) are stored in `expression_summaries` if consent is given. These records feature a MongoDB TTL index that automatically deletes them after 7 days.
