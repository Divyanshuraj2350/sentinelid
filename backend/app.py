from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv

from database import db, User, BehavioralProfile, Session, BehavioralEvent, AnomalyAlert

load_dotenv()

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/sentinelid.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()


# ========== AUTHENTICATION ROUTES ==========

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    try:
        user = User(username=data['username'], email=data['email'], password_hash=generate_password_hash(data['password']))
        db.session.add(user)
        db.session.commit()
        profile = BehavioralProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'user_id': user.id, 'username': user.username}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing credentials'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=user.id)
    session = Session(user_id=user.id)
    db.session.add(session)
    db.session.commit()
    return jsonify({'access_token': access_token, 'user_id': user.id, 'username': user.username, 'session_id': session.id, 'message': 'Login successful'}), 200


@app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
@jwt_required()
def logout():
    if request.method == 'OPTIONS':
        return '', 204
    user_id = get_jwt_identity()
    active_session = Session.query.filter_by(user_id=user_id, is_active=True).first()
    if active_session:
        active_session.is_active = False
        db.session.commit()
    return jsonify({'message': 'Logged out successfully'}), 200


# ========== BEHAVIORAL LOGGING ROUTES ==========

@app.route('/api/behavioral/keystroke', methods=['POST', 'OPTIONS'])
@jwt_required()
def log_keystroke():
    if request.method == 'OPTIONS':
        return '', 204
    user_id = get_jwt_identity()
    data = request.get_json()
    session = Session.query.filter_by(user_id=user_id, is_active=True).first()
    if not session:
        return jsonify({'error': 'No active session'}), 401
    try:
        event = BehavioralEvent(session_id=session.id, event_type='keystroke', keystroke_dwell_time=data.get('dwell_time'), keystroke_flight_time=data.get('flight_time'), keystroke_pressure=data.get('pressure'), anomaly_score=data.get('anomaly_score', 0.0))
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Keystroke logged', 'event_id': event.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/behavioral/mouse', methods=['POST', 'OPTIONS'])
@jwt_required()
def log_mouse():
    if request.method == 'OPTIONS':
        return '', 204
    user_id = get_jwt_identity()
    data = request.get_json()
    session = Session.query.filter_by(user_id=user_id, is_active=True).first()
    if not session:
        return jsonify({'error': 'No active session'}), 401
    try:
        event = BehavioralEvent(session_id=session.id, event_type='mouse', mouse_x=data.get('x'), mouse_y=data.get('y'), mouse_speed=data.get('speed'), mouse_acceleration=data.get('acceleration'), click_type=data.get('click_type'), anomaly_score=data.get('anomaly_score', 0.0))
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Mouse event logged', 'event_id': event.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/behavioral/train_baseline', methods=['POST', 'OPTIONS'])
@jwt_required()
def train_baseline():
    """Train anomaly detection model on user's baseline behavior"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Expected: {"features": [[wpm, dwell_avg, ...], [wpm, ...], ...]}
        features_list = data.get('features', [])
        
        if len(features_list) < 10:
            return jsonify({
                'msg': f'Need at least 10 samples, got {len(features_list)}',
                'status': 'error'
            }), 400
        
        from ml_models import behavioral_model
        success = behavioral_model.train(features_list)
        
        if success:
            return jsonify({
                'msg': f'✅ Model trained on {len(features_list)} samples',
                'user_id': user_id,
                'status': 'ok'
            }), 200
        else:
            return jsonify({'msg': 'Training failed', 'status': 'error'}), 500
    
    except Exception as e:
        print(f"❌ Error in train_baseline: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/behavioral/text-quality', methods=['POST', 'OPTIONS'])
@jwt_required()
def text_quality():
    """Check text quality and spelling"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        from spell_check import check_text_quality, is_gibberish
        
        quality = check_text_quality(text)
        gibberish = is_gibberish(text)
        
        # Reduce confidence if gibberish
        confidence_penalty = 0 if not gibberish else 50
        
        return jsonify({
            'text_quality': quality,
            'is_gibberish': gibberish,
            'confidence_penalty': confidence_penalty
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== ANOMALY DETECTION ROUTES ==========

@app.route('/api/anomaly/check', methods=['POST', 'OPTIONS'])
@jwt_required()
def check_anomaly():
    """Check current behavior against baseline and detect anomalies"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get active session
        session = Session.query.filter_by(user_id=user_id, is_active=True).first()
        if not session:
            return jsonify({'error': 'No active session'}), 401
        
        # Extract features if provided
        features = data.get('features', [])
        
        # Calculate anomaly score
        if features and len(features) > 0:
            # Use ML model if features provided
            from ml_models import behavioral_model
            confidence = behavioral_model.score(features)
            anomaly_score = 1.0 - (confidence / 100.0)  # Convert confidence to anomaly score
            print(f"[ANOMALY CHECK] User: {user_id}, Features: {features}, Confidence: {confidence}, Anomaly Score: {anomaly_score}")
        else:
            # Use provided anomaly score or default
            anomaly_score = data.get('anomaly_score', 0.0)
        
        # Determine if anomalous
        is_anomalous = anomaly_score > 0.7
        
        # Log anomaly if detected
        if is_anomalous:
            alert = AnomalyAlert(
                session_id=session.id, 
                alert_type=data.get('type', 'behavioral_anomaly'), 
                severity='medium' if anomaly_score < 0.85 else 'high', 
                description=f"Anomaly detected: {data.get('description', 'Unusual behavior pattern detected')}", 
                anomaly_score=anomaly_score
            )
            db.session.add(alert)
            session.anomaly_count += 1
            session.current_confidence = max(0, 100 - (anomaly_score * 100))
            db.session.commit()
        
        # Determine action
        action = 'BLOCK' if is_anomalous and anomaly_score > 0.9 else 'MONITOR'
        
        return jsonify({
            'is_anomalous': is_anomalous, 
            'anomaly_score': round(anomaly_score, 3), 
            'confidence': round(session.current_confidence, 2),
            'session_confidence': round(session.current_confidence, 2), 
            'action': action,
            'status': 'ok',
            'anomaly_detected': is_anomalous
        }), 200
    
    except Exception as e:
        print(f"❌ Error in check_anomaly: {e}")
        return jsonify({'error': str(e)}), 500


# ========== ADMIN ROUTES ==========

@app.route('/api/admin/active-sessions', methods=['GET', 'OPTIONS'])
def get_active_sessions():
    if request.method == 'OPTIONS':
        return '', 204
    active_sessions = Session.query.filter_by(is_active=True).all()
    return jsonify({
        'total_active': len(active_sessions), 
        'sessions': [{
            'session_id': s.id, 
            'user_id': s.user_id, 
            'login_time': s.login_time.isoformat(), 
            'current_confidence': s.current_confidence, 
            'anomaly_count': s.anomaly_count, 
            'is_compromised': s.is_compromised, 
            'event_count': len(s.behavioral_events)
        } for s in active_sessions]
    }), 200


@app.route('/api/admin/alerts', methods=['GET', 'OPTIONS'])
def get_alerts():
    if request.method == 'OPTIONS':
        return '', 204
    limit = request.args.get('limit', 20, type=int)
    alerts = AnomalyAlert.query.filter_by(resolved=False).order_by(AnomalyAlert.created_at.desc()).limit(limit).all()
    return jsonify({
        'total_alerts': len(alerts), 
        'alerts': [{
            'alert_id': a.id, 
            'session_id': a.session_id, 
            'alert_type': a.alert_type, 
            'severity': a.severity, 
            'description': a.description, 
            'anomaly_score': a.anomaly_score, 
            'created_at': a.created_at.isoformat()
        } for a in alerts]
    }), 200


@app.route('/api/admin/model-status', methods=['GET', 'OPTIONS'])
@jwt_required()
def model_status():
    """Check if ML model is trained"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        from ml_models import behavioral_model
        is_trained = behavioral_model.model is not None
        return jsonify({
            'model_trained': is_trained,
            'model_path': behavioral_model.model_path
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ========== MAIN ENTRY POINT ==========

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
