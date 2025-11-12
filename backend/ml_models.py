
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

class BehavioralModel:
    """Real anomaly detection using Isolation Forest"""
    
    def __init__(self, model_path='instance/model_baseline.joblib'):
        self.model_path = model_path
        self.model = None
        self.baseline_count = 0
        self.load_model()
    
    def load_model(self):
        """Load existing model if it exists"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ Model loaded from {self.model_path}")
            except:
                self.model = None
    
    def train(self, features_list):
        """
        Train the model on baseline features
        features_list: list of feature vectors like [[wpm, dwell_avg, flight_avg], ...]
        """
        if len(features_list) < 10:
            print(f"⚠️ Need at least 10 samples, got {len(features_list)}")
            return False
        
        X = np.array(features_list)
        print(f"📊 Training on {len(features_list)} samples with {X.shape[1]} features")
        
        self.model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"✅ Model trained and saved to {self.model_path}")
        return True
    
    def score(self, feature_vector):
        """
        Score a single feature vector
        Returns confidence score (0-100)
        - High confidence (80-100): Normal behavior
        - Medium confidence (50-80): Slightly unusual
        - Low confidence (<50): Highly suspicious
        """
        if self.model is None:
            print("⚠️ Model not trained yet, returning default confidence")
            return 85.0
        
        try:
            X = np.array(feature_vector).reshape(1, -1)
            # Get anomaly score (negative means more anomalous)
            anomaly_score = -self.model.decision_function(X)[0]
            # Convert to confidence: higher anomaly = lower confidence
            confidence = max(0, 100 - (anomaly_score * 100))
            return round(confidence, 2)
        except Exception as e:
            print(f"❌ Error scoring: {e}")
            return 85.0

# Global model instance
behavioral_model = BehavioralModel()

