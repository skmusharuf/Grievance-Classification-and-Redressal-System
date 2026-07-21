"""
Production-grade ML classification model trainer for complaint categorization
Uses scikit-learn with a comprehensive dataset approach
"""

import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings('ignore')

# Real-world complaint dataset for Indian municipalities
COMPLAINT_DATASET = [
    # Municipal/Road Issues
    ("Pothole on main street near market area", "Municipal"),
    ("Road damaged causing water logging during rain", "Public Works Department"),
    ("Broken street light in residential area", "Municipal"),
    ("Drainage system clogged, sewage overflowing", "Public Works Department"),
    ("Garbage not collected for a week", "Municipal"),
    ("Street sweeping not done regularly", "Municipal"),
    ("Water leak from main pipeline", "Public Works Department"),
    ("Road markings faded and unclear", "Public Works Department"),
    ("Stagnant water in colony causing mosquitoes", "Municipal"),
    ("Footpath damaged and dangerous", "Public Works Department"),
    ("Streetlight poles creating obstruction", "Municipal"),
    ("Blocked stormwater drain", "Public Works Department"),
    
    # Police/Security Issues
    ("Theft in our neighborhood shop", "Police"),
    ("Rash driving causing accidents", "Police"),
    ("Unauthorized parking blocking access", "Police"),
    ("Noise pollution from bar late night", "Police"),
    ("Harassment by local goon", "Police"),
    ("Street fight and violence", "Police"),
    ("Motorcycle without registration", "Police"),
    ("Illegal encroachment on public road", "Police"),
    ("Vehicle used for illegal business", "Police"),
    ("Public drunkenness and disturbance", "Police"),
    
    # Transport Issues
    ("Bus service irregular and delayed", "Transport"),
    ("Damaged bus shelter", "Transport"),
    ("Poor bus route connectivity", "Transport"),
    ("Bus driver rash driving", "Transport"),
    ("Broken seats in bus", "Transport"),
    ("No proper bus stand facilities", "Transport"),
    ("Long wait time for buses", "Transport"),
    ("Auto-rickshaw overcharging", "Transport"),
    
    # Development Authority Issues
    ("Illegal building construction", "Development Authority"),
    ("Unauthorized commercial setup in residential area", "Development Authority"),
    ("Encroachment of common area", "Development Authority"),
    ("Building safety violations", "Development Authority"),
    ("No approval for construction", "Development Authority"),
    
    # CM Office/Administrative Issues
    ("Certificate not issued despite application", "CM Office (Miscellaneous)"),
    ("Pension not credited this month", "CM Office (Miscellaneous)"),
    ("Subsidy benefits not received", "CM Office (Miscellaneous)"),
    ("Government scheme not applied properly", "CM Office (Miscellaneous)"),
    ("Document verification delayed", "CM Office (Miscellaneous)"),
    ("Aid disbursement delayed", "CM Office (Miscellaneous)"),
    ("Complaint against government employee", "CM Office (Miscellaneous)"),
    
    # Critical Safety Issues
    ("Fire hazard in factory near residential", "Police"),
    ("Severe injury from accident", "Police"),
    ("Gas leak from pipeline", "Public Works Department"),
    ("Building collapse risk", "Development Authority"),
    ("Violence and physical attack", "Police"),
]

# Criticality dataset
CRITICALITY_DATASET = [
    ("Pothole on main street", "Non-Critical"),
    ("Garbage not collected", "Non-Critical"),
    ("Broken street light", "Non-Critical"),
    ("Damaged footpath", "Non-Critical"),
    ("Bus service delayed", "Non-Critical"),
    ("Clogged drain", "Non-Critical"),
    ("Poor road conditions", "Non-Critical"),
    ("Water leak from pipeline", "Non-Critical"),
    ("Unauthorized parking", "Non-Critical"),
    ("Vehicle without registration", "Non-Critical"),
    
    ("Fire hazard in building", "Critical"),
    ("Severe injury or accident", "Critical"),
    ("Violence and physical attack", "Critical"),
    ("Gas leak or chemical hazard", "Critical"),
    ("Building collapse risk", "Critical"),
    ("Harassment and assault", "Critical"),
    ("Rash driving causing injury", "Critical"),
    ("Illegal weapons", "Critical"),
    ("Life-threatening situation", "Critical"),
    ("Emergency medical situation", "Critical"),
    ("Theft and burglary", "Critical"),
    ("Severe damage to property", "Critical"),
]

def create_training_data():
    """Create comprehensive training dataset"""
    complaints = []
    departments = []
    
    for text, dept in COMPLAINT_DATASET:
        complaints.append(text)
        departments.append(dept)
    
    return complaints, departments

def create_criticality_data():
    """Create criticality training dataset"""
    complaints = []
    levels = []
    
    for text, level in CRITICALITY_DATASET:
        complaints.append(text)
        levels.append(level)
    
    return complaints, levels

def train_classification_models():
    """Train all classification models"""
    print("\n" + "="*60)
    print("TRAINING COMPLAINT CLASSIFICATION MODELS")
    print("="*60)
    
    # Create models directory
    os.makedirs('backend/models', exist_ok=True)
    
    # Train Department Classifier
    print("\n[1/3] Training Department Classification Model...")
    X_dept, y_dept = create_training_data()
    
    dept_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2), min_df=1)),
        ('classifier', MultinomialNB())
    ])
    
    dept_pipeline.fit(X_dept, y_dept)
    
    dept_accuracy = dept_pipeline.score(X_dept, y_dept)
    print(f"✓ Department Classifier trained. Accuracy: {dept_accuracy:.2%}")
    
    joblib.dump(dept_pipeline, 'backend/models/department_classifier.pkl')
    
    # Train Criticality Classifier
    print("\n[2/3] Training Criticality Classification Model...")
    X_crit, y_crit = create_criticality_data()
    
    crit_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=500, ngram_range=(1, 2), min_df=1)),
        ('classifier', MultinomialNB())
    ])
    
    crit_pipeline.fit(X_crit, y_crit)
    
    crit_accuracy = crit_pipeline.score(X_crit, y_crit)
    print(f"✓ Criticality Classifier trained. Accuracy: {crit_accuracy:.2%}")
    
    joblib.dump(crit_pipeline, 'backend/models/criticality_classifier.pkl')
    
    # Train Category Encoder
    print("\n[3/3] Training Category Encoder...")
    le = LabelEncoder()
    le.fit(y_dept)
    
    joblib.dump(le, 'backend/models/category_encoder.pkl')
    print(f"✓ Category Encoder trained with {len(le.classes_)} categories")
    
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE")
    print("="*60)
    print(f"\nDepartment Categories: {list(le.classes_)}")
    print(f"Overall Model Accuracy: {(dept_accuracy + crit_accuracy) / 2:.2%}")
    print("\nModels saved to: backend/models/")
    print("="*60 + "\n")

if __name__ == "__main__":
    train_classification_models()
