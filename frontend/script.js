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
// EXAM MANAGEMENT
// ============================================

let exams = [];

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadExams();
    displayExams();
    updateStats();
    updateDashboardStats();
    
    // ===== DAY 18: Auto-backup on load =====
    createBackup();
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
// ============================================
// DAY 18: ADVANCED LOCALSTORAGE FEATURES
// ADD ALL DAY 18 CODE BELOW THIS LINE
// ============================================
// ============================================

// ============================================
// 1. EXPORT EXAMS TO JSON FILE
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

// ============================================
// 2. IMPORT EXAMS FROM JSON FILE
// ============================================

function importExams() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    
    fileInput.onchange = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
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
                data.exams.forEach(exam => {
                    if (exam.subject && exam.date && exam.time) {
                        exam.id = getNextId();
                        exams.push(exam);
                        importedCount++;
                    }
                });
                
                saveExams();
                displayExams();
                updateStats();
                updateDashboardStats();
                showNotification(`✅ Imported ${importedCount} exams successfully!`);
                
            } catch (error) {
                showNotification('❌ Import failed: ' + error.message, 'error');
            }
        };
        reader.readAsText(file);
    };
    
    fileInput.click();
}

// ============================================
// 3. BACKUP EXAMS (Auto-save to localStorage)
// ============================================

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

// ============================================
// 4. RESTORE FROM BACKUP
// ============================================

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
        saveExams();
        displayExams();
        updateStats();
        updateDashboardStats();
        showNotification(`✅ Restored ${exams.length} exams from backup!`);
        
    } catch (error) {
        showNotification('❌ Restore failed: ' + error.message, 'error');
    }
}

// ============================================
// 5. CLEAR ALL DATA (With Confirmation)
// ============================================

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
    saveExams();
    displayExams();
    updateStats();
    updateDashboardStats();
    showNotification('🗑️ All exams cleared!');
}

// ============================================
// 6. SHOW DATA STATISTICS
// ============================================

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
// 7. KEYBOARD SHORTCUTS
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
});

console.log('📚 Exam Buddy loaded successfully!');
console.log(`📊 ${exams.length} exams loaded from storage.`);
console.log('💾 Day 18 features: Export, Import, Backup, Restore, Clear All');