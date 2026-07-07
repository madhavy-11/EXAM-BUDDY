// ============================================
// EXAM BUDDY - COMPLETE JAVASCRIPT LOGIC
// Add, view, edit, delete exams with LocalStorage
// ============================================

// ============================================
// DATA MANAGEMENT
// ============================================

// Get exams from localStorage or start empty
let exams = [];

// Load data when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadExams();
    displayExams();
    updateStats();
});

// ============================================
// LOCAL STORAGE FUNCTIONS
// ============================================

function loadExams() {
    const stored = localStorage.getItem('exams');
    if (stored) {
        try {
            exams = JSON.parse(stored);
        } catch (e) {
            exams = [];
        }
    } else {
        // Add some sample exams for testing
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
// EXAM CRUD OPERATIONS
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
    clearForm();
    showNotification('✅ Exam added successfully!');
}

function deleteExam(id) {
    if (confirm('Are you sure you want to delete this exam?')) {
        exams = exams.filter(exam => exam.id !== id);
        saveExams();
        displayExams();
        updateStats();
        showNotification('🗑️ Exam deleted!');
    }
}

function clearAllExams() {
    if (exams.length === 0) {
        showNotification('📭 No exams to clear!');
        return;
    }
    
    if (confirm('Delete ALL exams? This cannot be undone!')) {
        exams = [];
        saveExams();
        displayExams();
        updateStats();
        showNotification('🗑️ All exams cleared!');
    }
}

// ============================================
// DISPLAY FUNCTIONS
// ============================================

function displayExams(filter = 'all') {
    const examList = document.getElementById('examList');
    let filteredExams = getFilteredExams(filter);
    
    if (filteredExams.length === 0) {
        examList.innerHTML = `<p class="empty-state">📭 No exams found. Add your first exam above!</p>`;
        return;
    }
    
    // Sort by date
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
    
    document.getElementById('totalExams').textContent = `📊 Total: ${total} exam${total !== 1 ? 's' : ''}`;
    document.getElementById('upcomingCount').textContent = `🎯 Upcoming: ${upcoming}`;
    document.getElementById('pastCount').textContent = `⏰ Past: ${past}`;
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

function searchExams() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const examList = document.getElementById('examList');
    
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

// ============================================
// FORM HANDLING
// ============================================

document.getElementById('examForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const subject = document.getElementById('subject').value.trim();
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const location = document.getElementById('location').value.trim();
    const teacher = document.getElementById('teacher').value.trim();
    
    // Validation
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
// FILTER FUNCTIONALITY
// ============================================

function filterExams(filter) {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Find the clicked button and make it active
    const buttons = document.querySelectorAll('.filter-btn');
    const filterMap = {
        'all': 0,
        'upcoming': 1,
        'past': 2,
        'today': 3
    };
    
    if (filterMap[filter] !== undefined) {
        buttons[filterMap[filter]].classList.add('active');
    }
    
    displayExams(filter);
    updateStats();
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
    // Check if notification div exists
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
    
    // Set colors
    if (type === 'error') {
        notification.style.background = '#ff6b6b';
        notification.style.color = 'white';
    } else if (type === 'warning') {
        notification.style.background = '#ffd93d';
        notification.style.color = '#333';
    } else {
        notification.style.background = '#51cf66';
        notification.style.color = 'white';
    }
    
    notification.textContent = message;
    notification.style.display = 'block';
    
    // Hide after 3 seconds
    clearTimeout(notification.timeout);
    notification.timeout = setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// ============================================
// ADD KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+C = Clear form
    if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        clearForm();
    }
    
    // Escape = Clear search
    if (e.key === 'Escape') {
        clearSearch();
    }
});

// ============================================
// AUTO-SET DATE TO TODAY
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Set default date to today
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = getTodayDate();
    }
});

// ============================================
// ADD CSS ANIMATIONS
// ============================================

// Add slide-in animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

console.log('📚 Exam Buddy loaded successfully!');
console.log(`📊 ${exams.length} exams loaded from storage.`);