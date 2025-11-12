import numpy as np

class BehavioralAnalyzer:
    """Advanced behavioral analysis"""
    
    def __init__(self):
        self.user_profiles = {}
    
    def extract_features(self, keystroke_data):
        """Extract features from keystroke data"""
        if not keystroke_data:
            return {}
        
        dwell_times = [k.get('dwell_time', 0) for k in keystroke_data]
        
        features = {
            'avg_dwell_time': np.mean(dwell_times) if dwell_times else 0,
            'keystroke_count': len(keystroke_data),
        }
        return features
    
    def calculate_anomaly_score(self, current_features, user_profile):
        """Calculate anomaly score"""
        if not user_profile:
            return 0.0
        
        distance = 0
        for key in current_features:
            if key in user_profile:
                diff = abs(current_features[key] - user_profile[key])
                distance += diff ** 2
        
        anomaly_score = min(1.0, np.sqrt(distance) / 100)
        return anomaly_score

analyzer = BehavioralAnalyzer()
