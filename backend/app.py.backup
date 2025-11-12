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

@app.route('/api/anomaly/check', methods=['POST', 'OPTIONS'])
@jwt_required()
def check_anomaly():
    if request.method == 'OPTIONS':
        return '', 204
    user_id = get_jwt_identity()
    data = request.get_json()
    session = Session.query.filter_by(user_id=user_id, is_active=True).first()
    if not session:
        return jsonify({'error': 'No active session'}), 401
    anomaly_score = data.get('anomaly_score', 0.0)
    is_anomalous = anomaly_score > 0.7
    if is_anomalous:
        alert = AnomalyAlert(session_id=session.id, alert_type=data.get('type', 'behavioral_anomaly'), severity='medium' if anomaly_score < 0.85 else 'high', description=f"Anomaly detected: {data.get('description')}", anomaly_score=anomaly_score)
        db.session.add(alert)
        session.anomaly_count += 1
        session.current_confidence = max(0, 100 - (anomaly_score * 100))
        db.session.commit()
    return jsonify({'is_anomalous': is_anomalous, 'anomaly_score': anomaly_score, 'session_confidence': session.current_confidence, 'action': 'BLOCK' if is_anomalous and anomaly_score > 0.9 else 'MONITOR'}), 200

@app.route('/api/admin/active-sessions', methods=['GET', 'OPTIONS'])
def get_active_sessions():
    if request.method == 'OPTIONS':
        return '', 204
    active_sessions = Session.query.filter_by(is_active=True).all()
    return jsonify({'total_active': len(active_sessions), 'sessions': [{'session_id': s.id, 'user_id': s.user_id, 'login_time': s.login_time.isoformat(), 'current_confidence': s.current_confidence, 'anomaly_count': s.anomaly_count, 'is_compromised': s.is_compromised, 'event_count': len(s.behavioral_events)} for s in active_sessions]}), 200

@app.route('/api/admin/alerts', methods=['GET', 'OPTIONS'])
def get_alerts():
    if request.method == 'OPTIONS':
        return '', 204
    limit = request.args.get('limit', 20, type=int)
    alerts = AnomalyAlert.query.filter_by(resolved=False).order_by(AnomalyAlert.created_at.desc()).limit(limit).all()
    return jsonify({'total_alerts': len(alerts), 'alerts': [{'alert_id': a.id, 'session_id': a.session_id, 'alert_type': a.alert_type, 'severity': a.severity, 'description': a.description, 'anomaly_score': a.anomaly_score, 'created_at': a.created_at.isoformat()} for a in alerts]}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)