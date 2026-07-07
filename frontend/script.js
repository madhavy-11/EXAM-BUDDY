// ============================================
// EXAM BUDDY - COMPLETE JAVASCRIPT
// Authentication & Exam Management
// ============================================

// ============================================
// AUTHENTICATION
// ============================================

function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    // Simple validation (in real app, this would be server-side)
    if (email && password.length >= 6) {
        localStorage.setItem('user', JSON.stringify({ email }));
        showNotification('✅ Login successful!');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    } else {
        showNotification('⚠️ Please enter valid credentials!', 'error');
    }
}

function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirm = document.getElementById('signupConfirm').value;
    
    if (password !== confirm) {
        showNotification('⚠️ Passwords do not match!', 'error');
        return;
    }
    
    if (password.length < 6) {
        showNotification('⚠️ Password must be at least 6 characters!', 'error');
        return;
    }
    
    if (name && email && password) {
        localStorage.setItem('user', JSON.stringify({ name, email }));
        showNotification('✅ Account created!');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    }
}

function logout() {
    localStorage.removeItem('user');
    showNotification('✅ Logged out successfully!');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 500);
}

// Check if user is logged in (for dashboard)
function checkAuth() {
    const user = localStorage.getItem('user');
    if (!user && window.location.pathname.includes('dashboard.html')) {
        window.location.href = 'login.html';
    }
}

// ============================================
// EXAM MANAGEMENT
// ============================================

let exams = [];

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadExams();
    displayExams();
    updateStats();
    updateDashboardStats();
});

function loadExams() {
    const stored = localStorage.getItem('exams');
    if (stored) {
        try {
            exams = JSON.parse(stored);
        } catch (e) {
            exams = [];
        }
    } else {
        exams = [
            {
                id: 1,
                subject: "Mathematics",
                date: getTodayDate(),
                time: "09:00",
                location: "Room 201",
                teacher: "Mr. Smith"
            },
            {
                id: 2,
                subject: "Physics",
                date: getTomorrowDate(),
                time: "14:30",
                location: "Lab 3",
                teacher: "Dr. Johnson"
            }
        ];
        saveExams();
    }
}

function saveExams() {
    localStorage.setItem('exams', JSON.stringify(exams));
}

function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

function getTomorrowDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
}

function getNextId() {
    if (exams.length === 0) return 1;
    const ids = exams.map(e => e.id);
    return Math.max(...ids) + 1;
}

// ============================================
// CRUD OPERATIONS
// ============================================

function addExam(subject, date, time, location, teacher) {
    const exam = {
        id: getNextId(),
        subject: subject.trim(),
        date: date,
        time: time,
        location: location.trim() || "Not specified",
        teacher: teacher.trim() || "Not specified"
    };
    
    exams.push(exam);
    saveExams();
    displayExams();
    updateStats();
    updateDashboardStats();
    clearForm();
    showNotification('✅ Exam added successfully!');
}

function deleteExam(id) {
    if (confirm('Are you sure you want to delete this exam?')) {
        exams = exams.filter(exam => exam.id !== id);
        saveExams();
        displayExams();
        updateStats();
        updateDashboardStats();
        showNotification('🗑️ Exam deleted!');
    }
}

// ============================================
// DISPLAY FUNCTIONS
// ============================================

function displayExams(filter = 'all') {
    const examList = document.getElementById('examList');
    if (!examList) return;
    
    let filteredExams = getFilteredExams(filter);
    
    if (filteredExams.length === 0) {
        examList.innerHTML = `<p class="empty-state">📭 No exams found. Add your first exam above!</p>`;
        return;
    }
    
    filteredExams.sort((a, b) => {
        if (a.date < b.date) return -1;
        if (a.date > b.date) return 1;
        return a.time.localeCompare(b.time);
    });
    
    let html = '';
    filteredExams.forEach(exam => {
        const status = getExamStatus(exam);
        const statusClass = getStatusClass(status);
        
        html += `
            <div class="exam-item">
                <div>
                    <div class="subject">${escapeHtml(exam.subject)}</div>
                    <div class="date-time">📅 ${exam.date} at ⏰ ${exam.time}</div>
                    <div class="date-time">📍 ${escapeHtml(exam.location)} | 👨‍🏫 ${escapeHtml(exam.teacher)}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="status ${statusClass}">${status}</span>
                    <button class="delete-btn" onclick="deleteExam(${exam.id})">🗑️</button>
                </div>
            </div>
        `;
    });
    
    examList.innerHTML = html;
}

function getFilteredExams(filter) {
    const today = getTodayDate();
    
    switch(filter) {
        case 'upcoming':
            return exams.filter(exam => exam.date >= today);
        case 'past':
            return exams.filter(exam => exam.date < today);
        case 'today':
            return exams.filter(exam => exam.date === today);
        default:
            return exams;
    }
}

function getExamStatus(exam) {
    const today = getTodayDate();
    if (exam.date < today) return 'Past';
    if (exam.date === today) return 'Today!';
    return 'Upcoming';
}

function getStatusClass(status) {
    switch(status) {
        case 'Past': return 'status-past';
        case 'Today!': return 'status-today';
        default: return 'status-upcoming';
    }
}

// ============================================
// STATISTICS
// ============================================

function updateStats() {
    const total = exams.length;
    const upcoming = exams.filter(e => e.date >= getTodayDate()).length;
    const past = exams.filter(e => e.date < getTodayDate()).length;
    
    const totalEl = document.getElementById('totalExams');
    const upcomingEl = document.getElementById('upcomingCount');
    const pastEl = document.getElementById('pastCount');
    
    if (totalEl) totalEl.textContent = `📊 Total: ${total} exam${total !== 1 ? 's' : ''}`;
    if (upcomingEl) upcomingEl.textContent = `🎯 Upcoming: ${upcoming}`;
    if (pastEl) pastEl.textContent = `⏰ Past: ${past}`;
}

function updateDashboardStats() {
    const total = exams.length;
    const upcoming = exams.filter(e => e.date >= getTodayDate()).length;
    const today = exams.filter(e => e.date === getTodayDate()).length;
    const past = exams.filter(e => e.date < getTodayDate()).length;
    
    const totalEl = document.getElementById('statTotal');
    const upcomingEl = document.getElementById('statUpcoming');
    const todayEl = document.getElementById('statToday');
    const pastEl = document.getElementById('statPast');
    
    if (totalEl) totalEl.textContent = total;
    if (upcomingEl) upcomingEl.textContent = upcoming;
    if (todayEl) todayEl.textContent = today;
    if (pastEl) pastEl.textContent = past;
}

// ============================================
// SEARCH & FILTER
// ============================================

function searchExams() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().