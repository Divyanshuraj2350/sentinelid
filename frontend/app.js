
const API_URL = 'http://127.0.0.1:5000/api';
let authToken = null;
let currentUserId = null;
let currentSessionId = null;
let sessionActive = false;

function toggleForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    loginForm.style.display = loginForm.style.display === 'none' ? 'block' : 'none';
    registerForm.style.display = registerForm.style.display === 'none' ? 'block' : 'none';
}

function showError(message) {
    const errorEl = document.getElementById('error');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    setTimeout(() => errorEl.style.display = 'none', 5000);
}

function showSuccess(message) {
    const successEl = document.getElementById('success');
    successEl.textContent = message;
    successEl.style.display = 'block';
    setTimeout(() => successEl.style.display = 'none', 5000);
}

async function handleRegister() {
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    
    if (!username || !email || !password) {
        showError('All fields are required');
        return;
    }
    
    if (password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showError(data.error || 'Registration failed');
            return;
        }
        
        showSuccess('Account created! Please login.');
        document.getElementById('regUsername').value = '';
        document.getElementById('regEmail').value = '';
        document.getElementById('regPassword').value = '';
        
        setTimeout(() => toggleForm(), 1000);
        
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

async function handleLogin() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        showError('Username and password required');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showError(data.error || 'Login failed');
            return;
        }
        
        authToken = data.access_token;
        currentUserId = data.user_id;
        currentSessionId = data.session_id;
        sessionActive = true;
        
        document.getElementById('authForm').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        document.getElementById('username').textContent = data.username;
        
        startBehaviorMonitoring();
        showSuccess(`Welcome, ${data.username}!`);
        
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

function startBehaviorMonitoring() {
    document.addEventListener('keydown', trackKeystroke);
    document.addEventListener('mousemove', trackMouse);
    setInterval(checkAnomalies, 5000);
    addLogEntry('🔍 Behavioral monitoring started');
}

let lastKeystrokeTime = 0;
let keyDownTime = 0;

document.addEventListener('keydown', function(e) {
    keyDownTime = performance.now();
});

document.addEventListener('keyup', function(e) {
    const keyUpTime = performance.now();
    const dwellTime = keyUpTime - keyDownTime;
    const flightTime = keyDownTime - lastKeystrokeTime;
    lastKeystrokeTime = keyUpTime;
    
    if (authToken && sessionActive) {
        fetch(`${API_URL}/behavioral/keystroke`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                dwell_time: dwellTime,
                flight_time: flightTime,
                pressure: 0.5
            })
        }).catch(e => console.error('Keystroke logging failed:', e));
    }
});

let lastMouseTime = 0;
let lastMouseX = 0;
let lastMouseY = 0;

document.addEventListener('mousemove', function(e) {
    if (!authToken || !sessionActive) return;
    
    const now = performance.now();
    if (now - lastMouseTime < 100) return;
    
    const dx = e.clientX - lastMouseX;
    const dy = e.clientY - lastMouseY;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const timeDiff = (now - lastMouseTime) / 1000;
    const speed = timeDiff > 0 ? distance / timeDiff : 0;
    
    fetch(`${API_URL}/behavioral/mouse`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            x: e.clientX,
            y: e.clientY,
            speed: speed,
            acceleration: 0
        })
    }).catch(e => console.error('Mouse logging failed:', e));
    
    lastMouseTime = now;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
});

async function checkAnomalies() {
    if (!authToken || !sessionActive) return;
    
    try {
        const response = await fetch(`${API_URL}/anomaly/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                anomaly_score: Math.random() * 0.3
            })
        });
        
        const data = await response.json();
        
        document.getElementById('confidence').textContent = Math.round(data.session_confidence);
        document.getElementById('confidenceBar').style.width = data.session_confidence + '%';
        document.getElementById('confidenceBar').textContent = Math.round(data.session_confidence) + '%';
        
        if (data.is_anomalous) {
            addLogEntry(`⚠️ Anomaly detected (Score: ${data.anomaly_score.toFixed(2)})`, true);
        }
        
    } catch (error) {
        console.error('Anomaly check failed:', error);
    }
}

function addLogEntry(message, isAnomaly = false) {
    const eventsList = document.getElementById('eventsList');
    const entry = document.createElement('div');
    entry.className = 'event-item' + (isAnomaly ? ' anomaly' : '');
    
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    
    eventsList.insertBefore(entry, eventsList.firstChild);
    
    while (eventsList.children.length > 20) {
        eventsList.removeChild(eventsList.lastChild);
    }
}

async function handleLogout() {
    try {
        await fetch(`${API_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        authToken = null;
        currentUserId = null;
        sessionActive = false;
        
        document.getElementById('authForm').style.display = 'block';
        document.getElementById('dashboard').style.display = 'none';
        
        document.getElementById('loginUsername').value = '';
        document.getElementById('loginPassword').value = '';
        
        showSuccess('Logged out successfully');
        
    } catch (error) {
        showError('Logout error: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    addLogEntry('🚀 SentinelID initialized');
});
