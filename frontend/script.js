// ============================================
// EXAM BUDDY - COMPLETE JAVASCRIPT
// Authentication & Exam Management
// ============================================

// ============================================
// API CONFIGURATION (DAY 20)
// ============================================

const API_URL = 'http://localhost:5000/api';

// ============================================
// API FUNCTIONS (DAY 20)
// ============================================

async function apiFetch(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showNotification('❌ ' + error.message, 'error');
        throw error;
    }
}

// ============================================
// AUTHENTICATION
// ============================================

function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
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

function checkAuth() {
    const user = localStorage.getItem('user');
    if (!user && window.location.pathname.includes('dashboard.html')) {
        window.location.href = 'login.html';
    }
}

// ============================================
// EXAM MANAGEMENT (UPDATED FOR DAY 20)
// ============================================

let exams = [];

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadExamsFromAPI();  // UPDATED: Load from API
    updateStatsFromAPI(); // UPDATED: Stats from API
    updateDashboardStatsFromAPI(); // UPDATED: Dashboard stats from API
    
    // ===== DAY 18: Auto-backup on load =====
    createBackup();
    
    // ===== DAY 19: Check for reminders =====
    setTimeout(() => {
        checkExamReminders();
    }, 1000);
});

// ============================================
// DAY 20: API FUNCTIONS (REPLACES localStorage)
// ============================================

async function loadExamsFromAPI() {
    try {
        const data = await apiFetch('/exams');
        exams = data.exams;
        displayExams();
        updateStatsFromAPI();
        updateDashboardStatsFromAPI();
        showNotification(`✅ Loaded ${exams.length} exams from database!`);
    } catch (error) {
        console.error('Failed to load exams:', error);
        exams = [];
        displayExams();
        updateStatsFromAPI();
        updateDashboardStatsFromAPI();
    }
}

async function addExam(subject, date, time, location, teacher) {
    try {
        const data = await apiFetch('/exams', {
            method: 'POST',
            body: JSON.stringify({
                subject: subject.trim(),
                date: date,
                time: time,
                location: location.trim() || '',
                teacher: teacher.trim() || ''
            })
        });
        
        if (data.success) {
            await loadExamsFromAPI();
            clearForm();
            showNotification('✅ Exam added successfully!');
        }
    } catch (error) {
        console.error('Failed to add exam:', error);
    }
}

async function deleteExam(id) {
    if (!confirm('Are you sure you want to delete this exam?')) return;
    
    try {
        const data = await apiFetch(`/exams/${id}`, {
            method: 'DELETE'
        });
        
        if (data.success) {
            await loadExamsFromAPI();
            showNotification('🗑️ Exam deleted!');
        }
    } catch (error) {
        console.error('Failed to delete exam:', error);
    }
}

async function updateStatsFromAPI() {
    try {
        const data = await apiFetch('/exams/stats');
        if (data.success) {
            const stats = data.stats;
            
            const totalEl = document.getElementById('totalExams');
            const upcomingEl = document.getElementById('upcomingCount');
            const pastEl = document.getElementById('pastCount');
            
            if (totalEl) totalEl.textContent = `📊 Total: ${stats.total} exam${stats.total !== 1 ? 's' : ''}`;
            if (upcomingEl) upcomingEl.textContent = `🎯 Upcoming: ${stats.upcoming}`;
            if (pastEl) pastEl.textContent = `⏰ Past: ${stats.past}`;
        }
    } catch (error) {
        console.error('Failed to update stats:', error);
    }
}

async function updateDashboardStatsFromAPI() {
    try {
        const data = await apiFetch('/exams/stats');
        if (data.success) {
            const stats = data.stats;
            
            const totalEl = document.getElementById('statTotal');
            const upcomingEl = document.getElementById('statUpcoming');
            const todayEl = document.getElementById('statToday');
            const pastEl = document.getElementById('statPast');
            
            if (totalEl) totalEl.textContent = stats.total;
            if (upcomingEl) upcomingEl.textContent = stats.upcoming;
            if (todayEl) todayEl.textContent = stats.today;
            if (pastEl) pastEl.textContent = stats.past;
        }
    } catch (error) {
        console.error('Failed to update dashboard stats:', error);
    }
}

// ============================================
// LEGACY FUNCTIONS (KEPT FOR BACKWARD COMPATIBILITY)
// But no longer used for primary storage
// ============================================

function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

function getTomorrowDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
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
// SEARCH & FILTER
// ============================================

function searchExams() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const examList = document.getElementById('examList');
    if (!examList) return;
    
    if (!searchTerm) {
        displayExams();
        return;
    }
    
    const filtered = exams.filter(exam => 
        exam.subject.toLowerCase().includes(searchTerm) ||
        exam.location.toLowerCase().includes(searchTerm) ||
        exam.teacher.toLowerCase().includes(searchTerm)
    );
    
    if (filtered.length === 0) {
        examList.innerHTML = `<p class="empty-state">🔍 No exams found for "${searchTerm}"</p>`;
        return;
    }
    
    filtered.sort((a, b) => a.date.localeCompare(b.date));
    
    let html = '';
    filtered.forEach(exam => {
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

function clearSearch() {
    document.getElementById('searchInput').value = '';
    displayExams();
}

function filterExams(filter) {
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    const filterMap = { 'all': 0, 'upcoming': 1, 'past': 2, 'today': 3 };
    if (filterMap[filter] !== undefined && buttons[filterMap[filter]]) {
        buttons[filterMap[filter]].classList.add('active');
    }
    
    displayExams(filter);
}

// ============================================
// FORM HANDLING
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('examForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const subject = document.getElementById('subject').value.trim();
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            const location = document.getElementById('location').value.trim();
            const teacher = document.getElementById('teacher').value.trim();
            
            if (!subject) {
                showNotification('⚠️ Please enter a subject!', 'error');
                document.getElementById('subject').focus();
                return;
            }
            if (!date) {
                showNotification('⚠️ Please select a date!', 'error');
                document.getElementById('date').focus();
                return;
            }
            if (!time) {
                showNotification('⚠️ Please select a time!', 'error');
                document.getElementById('time').focus();
                return;
            }
            
            addExam(subject, date, time, location, teacher);
        });
    }
    
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = getTodayDate();
    }
});

function clearForm() {
    document.getElementById('subject').value = '';
    document.getElementById('date').value = '';
    document.getElementById('time').value = '';
    document.getElementById('location').value = '';
    document.getElementById('teacher').value = '';
    document.getElementById('subject').focus();
    showNotification('🧹 Form cleared!');
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'success') {
    let notification = document.getElementById('notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.5s ease;
            max-width: 400px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        `;
        document.body.appendChild(notification);
    }
    
    const colors = {
        success: '#51cf66',
        error: '#ff6b6b',
        warning: '#ffd93d'
    };
    
    notification.style.background = colors[type] || colors.success;
    notification.style.color = type === 'warning' ? '#333' : 'white';
    notification.textContent = message;
    notification.style.display = 'block';
    
    clearTimeout(notification.timeout);
    notification.timeout = setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// ============================================
// DAY 18: ADVANCED LOCALSTORAGE FEATURES
// Note: Export/Import still work but use current data
// ============================================

function exportExams() {
    if (exams.length === 0) {
        showNotification('📭 No exams to export!', 'warning');
        return;
    }
    
    try {
        const data = {
            exams: exams,
            exportedAt: new Date().toISOString(),
            totalExams: exams.length,
            version: '1.0'
        };
        
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `exam_buddy_backup_${getTodayDate()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showNotification(`✅ Exported ${exams.length} exams successfully!`);
    } catch (error) {
        showNotification('❌ Export failed: ' + error.message, 'error');
    }
}

function importExams() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    
    fileInput.onchange = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = async function(e) {
            try {
                const data = JSON.parse(e.target.result);
                
                if (!data.exams || !Array.isArray(data.exams)) {
                    showNotification('❌ Invalid file format!', 'error');
                    return;
                }
                
                const confirmImport = confirm(
                    `This will add ${data.exams.length} exams to your current list.\n` +
                    `Current exams: ${exams.length}\n` +
                    `Continue?`
                );
                
                if (!confirmImport) return;
                
                let importedCount = 0;
                for (const exam of data.exams) {
                    if (exam.subject && exam.date && exam.time) {
                        await addExam(exam.subject, exam.date, exam.time, exam.location, exam.teacher);
                        importedCount++;
                    }
                }
                
                await loadExamsFromAPI();
                showNotification(`✅ Imported ${importedCount} exams successfully!`);
                
            } catch (error) {
                showNotification('❌ Import failed: ' + error.message, 'error');
            }
        };
        reader.readAsText(file);
    };
    
    fileInput.click();
}

function createBackup() {
    try {
        const backupData = {
            exams: exams,
            createdAt: new Date().toISOString(),
            totalExams: exams.length
        };
        
        localStorage.setItem('exam_buddy_backup', JSON.stringify(backupData));
        showNotification('💾 Backup created successfully!');
    } catch (error) {
        showNotification('❌ Backup failed: ' + error.message, 'error');
    }
}

function restoreFromBackup() {
    try {
        const backupData = localStorage.getItem('exam_buddy_backup');
        if (!backupData) {
            showNotification('📭 No backup found!', 'warning');
            return;
        }
        
        const data = JSON.parse(backupData);
        
        if (!data.exams || !Array.isArray(data.exams)) {
            showNotification('❌ Invalid backup data!', 'error');
            return;
        }
        
        const confirmRestore = confirm(
            `This will REPLACE all current exams with the backup.\n` +
            `Backup has ${data.exams.length} exams.\n` +
            `Current: ${exams.length} exams.\n\n` +
            `Continue?`
        );
        
        if (!confirmRestore) return;
        
        exams = data.exams;
        localStorage.setItem('exams', JSON.stringify(exams));
        displayExams();
        updateStatsFromAPI();
        updateDashboardStatsFromAPI();
        showNotification(`✅ Restored ${exams.length} exams from backup!`);
        
    } catch (error) {
        showNotification('❌ Restore failed: ' + error.message, 'error');
    }
}

function clearAllData() {
    if (exams.length === 0) {
        showNotification('📭 No exams to clear!', 'warning');
        return;
    }
    
    const confirmClear = confirm(
        `⚠️ WARNING: This will delete ALL ${exams.length} exams!\n` +
        `This action CANNOT be undone!\n\n` +
        `Type "DELETE" to confirm.`
    );
    
    if (!confirmClear) return;
    
    const finalConfirm = prompt('Type "DELETE" to confirm:');
    if (finalConfirm !== 'DELETE') {
        showNotification('❌ Clear cancelled - incorrect confirmation', 'error');
        return;
    }
    
    exams = [];
    localStorage.setItem('exams', JSON.stringify(exams));
    displayExams();
    updateStatsFromAPI();
    updateDashboardStatsFromAPI();
    showNotification('🗑️ All exams cleared!');
}

function showDataStats() {
    const total = exams.length;
    const upcoming = exams.filter(e => e.date >= getTodayDate()).length;
    const past = exams.filter(e => e.date < getTodayDate()).length;
    const today = exams.filter(e => e.date === getTodayDate()).length;
    
    const subjectCount = {};
    exams.forEach(e => {
        subjectCount[e.subject] = (subjectCount[e.subject] || 0) + 1;
    });
    
    let statsMessage = `📊 DATA STATISTICS\n`;
    statsMessage += `═'.repeat(40)}\n\n`;
    statsMessage += `Total Exams: ${total}\n`;
    statsMessage += `Upcoming: ${upcoming}\n`;
    statsMessage += `Today: ${today}\n`;
    statsMessage += `Past: ${past}\n\n`;
    statsMessage += `📚 Subjects:\n`;
    
    const sortedSubjects = Object.entries(subjectCount).sort((a, b) => b[1] - a[1]);
    sortedSubjects.forEach(([subject, count]) => {
        statsMessage += `  • ${subject}: ${count}\n`;
    });
    
    alert(statsMessage);
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+E = Export
    if (e.ctrlKey && e.shiftKey && e.key === 'E') {
        e.preventDefault();
        exportExams();
    }
    
    // Ctrl+Shift+I = Import
    if (e.ctrlKey && e.shiftKey && e.key === 'I') {
        e.preventDefault();
        importExams();
    }
    
    // Ctrl+Shift+B = Backup
    if (e.ctrlKey && e.shiftKey && e.key === 'B') {
        e.preventDefault();
        createBackup();
    }
    
    // Ctrl+Shift+R = Restore
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        restoreFromBackup();
    }
    
    // Ctrl+Shift+N = Check reminders now
    if (e.ctrlKey && e.shiftKey && e.key === 'N') {
        e.preventDefault();
        manualReminderCheck();
    }
    
    // Ctrl+Shift+S = Show notification settings
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        showNotificationSettings();
    }
});

// ============================================
// DAY 19: WEB NOTIFICATIONS
// ============================================

function requestNotificationPermission() {
    if (!("Notification" in window)) {
        showNotification('⚠️ This browser does not support notifications!', 'warning');
        return false;
    }
    
    if (Notification.permission === "granted") {
        showNotification('✅ Notifications already enabled!');
        return true;
    }
    
    if (Notification.permission === "denied") {
        showNotification('❌ Notifications blocked. Please enable in browser settings.', 'error');
        return false;
    }
    
    Notification.requestPermission().then(function(permission) {
        if (permission === "granted") {
            showNotification('✅ Notifications enabled!');
            return true;
        } else {
            showNotification('❌ Notification permission denied.', 'error');
            return false;
        }
    });
}

function sendNotification(title, body, icon = '📚') {
    if (!("Notification" in window)) {
        console.warn('Notifications not supported');
        return;
    }
    
    if (Notification.permission === "granted") {
        try {
            const notification = new Notification(title, {
                body: body,
                icon: icon,
                vibrate: [200, 100, 200],
                tag: 'exam-reminder',
                requireInteraction: true,
                silent: false
            });
            
            notification.onclick = function() {
                window.focus();
                this.close();
                if (!window.location.pathname.includes('dashboard.html')) {
                    window.location.href = 'dashboard.html';
                }
            };
            
            return notification;
        } catch (error) {
            console.error('Notification error:', error);
        }
    } else if (Notification.permission === "denied") {
        console.warn('Notifications are blocked');
    } else {
        requestNotificationPermission();
    }
}

function sendExamReminder(exam) {
    const today = new Date();
    const examDate = new Date(exam.date);
    const daysUntil = Math.ceil((examDate - today) / (1000 * 60 * 60 * 24));
    
    let title = '';
    let body = '';
    let urgency = '';
    
    if (daysUntil === 0) {
        title = '🎯 Exam Today!';
        body = `${exam.subject} at ${exam.time}`;
        urgency = 'urgent';
    } else if (daysUntil === 1) {
        title = '⚠️ Exam Tomorrow!';
        body = `${exam.subject} at ${exam.time}`;
        urgency = 'urgent';
    } else if (daysUntil <= 3) {
        title = '📚 Exam Soon!';
        body = `${exam.subject} in ${daysUntil} days at ${exam.time}`;
        urgency = 'soon';
    } else {
        title = '📅 Upcoming Exam';
        body = `${exam.subject} in ${daysUntil} days at ${exam.time}`;
        urgency = 'normal';
    }
    
    if (exam.location && exam.location !== 'Not specified') {
        body += `\n📍 ${exam.location}`;
    }
    if (exam.teacher && exam.teacher !== 'Not specified') {
        body += `\n👨‍🏫 ${exam.teacher}`;
    }
    
    sendNotification(title, body);
    
    if (urgency === 'urgent') {
        playNotificationSound('urgent');
    } else if (urgency === 'soon') {
        playNotificationSound('soon');
    }
}

function checkExamReminders() {
    if (exams.length === 0) {
        console.log('📭 No exams to check');
        return;
    }
    
    const today = new Date();
    let remindersSent = 0;
    
    exams.forEach(exam => {
        const examDate = new Date(exam.date);
        const daysUntil = Math.ceil((examDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntil >= 0 && daysUntil <= 3) {
            const reminderKey = `reminded_${exam.id}_${exam.date}`;
            const alreadyReminded = localStorage.getItem(reminderKey);
            
            if (alreadyReminded === getTodayDate()) {
                return;
            }
            
            sendExamReminder(exam);
            localStorage.setItem(reminderKey, getTodayDate());
            remindersSent++;
        }
    });
    
    if (remindersSent > 0) {
        showNotification(`🔔 Sent ${remindersSent} exam reminders!`);
    }
}

function playNotificationSound(type = 'normal') {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        if (type === 'urgent') {
            playBeep(audioContext, 800, 0.15);
            setTimeout(() => playBeep(audioContext, 800, 0.15), 200);
            setTimeout(() => playBeep(audioContext, 800, 0.15), 400);
        } else if (type === 'soon') {
            playBeep(audioContext, 600, 0.15);
            setTimeout(() => playBeep(audioContext, 600, 0.15), 200);
        } else {
            playBeep(audioContext, 400, 0.1);
        }
    } catch (error) {
        console.log('Audio not supported');
    }
}

function playBeep(audioContext, frequency, duration) {
    try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + duration);
    } catch (error) {
        // Ignore audio errors
    }
}

function manualReminderCheck() {
    if (exams.length === 0) {
        showNotification('📭 No exams to check!', 'warning');
        return;
    }
    
    showNotification('🔍 Checking for upcoming exams...');
    
    exams.forEach(exam => {
        const reminderKey = `reminded_${exam.id}_${exam.date}`;
        localStorage.removeItem(reminderKey);
    });
    
    setTimeout(() => {
        checkExamReminders();
        showNotification('✅ Reminder check complete!');
    }, 1000);
}

function clearReminderHistory() {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('reminded_')) {
            keys.push(key);
        }
    }
    
    if (keys.length === 0) {
        showNotification('📭 No reminder history found!', 'warning');
        return;
    }
    
    const confirmClear = confirm(`Delete ${keys.length} reminder records?`);
    if (confirmClear) {
        keys.forEach(key => localStorage.removeItem(key));
        showNotification(`✅ Cleared ${keys.length} reminder records!`);
    }
}

function showNotificationSettings() {
    let status = '🔔 Notification Settings\n';
    status += '═'.repeat(40) + '\n\n';
    
    if (!("Notification" in window)) {
        status += '❌ Notifications not supported in this browser\n';
    } else {
        status += `📊 Permission: ${Notification.permission}\n\n`;
        
        if (Notification.permission === "granted") {
            status += '✅ Notifications are enabled\n';
            status += '💡 You will receive exam reminders\n';
        } else if (Notification.permission === "denied") {
            status += '❌ Notifications are blocked\n';
            status += '💡 Enable in browser settings\n';
        } else {
            status += '⏳ Notifications not requested yet\n';
            status += '💡 Click "Enable Notifications" to allow\n';
        }
        
        status += '\n📋 Notification Rules:\n';
        status += '• 0 days: Urgent (Today!)\n';
        status += '• 1 day: Urgent (Tomorrow!)\n';
        status += '• 2-3 days: Soon\n';
        status += '• 4+ days: Normal\n';
        status += '• Max 1 notification per day\n';
    }
    
    alert(status);
}

function enableNotifications() {
    requestNotificationPermission();
}

// ============================================
// SCHEDULE REMINDER CHECKS (DAY 19)
// ============================================

// Check reminders every hour
setInterval(() => {
    checkExamReminders();
}, 60 * 60 * 1000);

// Check when page becomes visible again
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        checkExamReminders();
    }
});

console.log('📚 Exam Buddy loaded successfully!');
console.log(`📊 ${exams.length} exams loaded from database.`);
console.log('🔗 Connected to API server at:', API_URL);
console.log('✅ Day 20 Integration Complete!');