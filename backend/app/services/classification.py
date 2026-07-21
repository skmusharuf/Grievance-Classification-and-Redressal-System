"""Complaint classification service using trained ML models"""

import joblib
import os
from app.config import DEPARTMENTS

# Load trained models on module import
MODEL_PATH = 'backend/models/'
MODELS_AVAILABLE = False

try:
    dept_classifier = joblib.load(os.path.join(MODEL_PATH, 'department_classifier.pkl'))
    crit_classifier = joblib.load(os.path.join(MODEL_PATH, 'criticality_classifier.pkl'))
    category_encoder = joblib.load(os.path.join(MODEL_PATH, 'category_encoder.pkl'))
    MODELS_AVAILABLE = True
    print("[ML] Models loaded successfully for production use")
except Exception as e:
    print(f"[ML] Warning: Could not load models: {e}")
    print("[ML] Fallback to keyword-based classification will be used")

def classify_complaint(description):
    """
    Classify complaint using trained ML models
    Returns: (department, criticality)
    """
    try:
        if not description or len(description.strip()) < 3:
            return "General", "Non-Critical"

        # Use trained models if available
        if MODELS_AVAILABLE:
            try:
                # Predict department
                dept_pred = dept_classifier.predict([description])[0]
                
                # Predict criticality
                crit_pred = crit_classifier.predict([description])[0]
                
                # Validate predictions
                if dept_pred not in DEPARTMENTS:
                    dept_pred = "General"
                if crit_pred not in ["Critical", "Non-Critical"]:
                    crit_pred = "Non-Critical"
                
                return dept_pred, crit_pred
            except Exception as e:
                print(f"[ML] Prediction error: {e}, using fallback")
                return fallback_classify(description)
        else:
            return fallback_classify(description)

    except Exception as e:
        print(f"[Classification] Error: {e}")
        return "General", "Non-Critical"

def fallback_classify(description):
    """
    Fallback keyword-based classification when ML models unavailable
    """
    description_lower = description.lower()
    
    # Critical keywords
    critical_keywords = [
        "fire", "accident", "injury", "attack", "violence", "assault", "death",
        "emergency", "collapse", "gas leak", "chemical", "severe", "urgent",
        "bleeding", "unconscious", "rape", "murder", "theft", "robbery",
        "threat", "weapon", "dangerous", "critical"
    ]
    
    # Department keywords
    dept_keywords = {
        "Municipal": ["garbage", "sweeping", "waste", "cleaning", "lamp", "light", "drain", "sewer"],
        "Police": ["theft", "violence", "crime", "fight", "attack", "harassment", "accident", "traffic"],
        "Public Works Department": ["road", "pothole", "footpath", "water", "pipeline", "pipeline", "drainage", "street"],
        "Transport": ["bus", "auto", "vehicle", "transport", "taxi", "public", "transit"],
        "Development Authority": ["building", "construction", "encroachment", "illegal", "unauthorized", "structure"],
    }
    
    # Determine criticality
    criticality = "Critical" if any(keyword in description_lower for keyword in critical_keywords) else "Non-Critical"
    
    # Determine department
    department = "General"
    for dept, keywords in dept_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            department = dept
            break
    
    return department, criticality
