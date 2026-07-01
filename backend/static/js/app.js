// Core ERP Utility and Interaction Layer
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    setupSidebarToggle();
    handleNotificationsBadge();
    
    // Page specific handlers
    const pathName = window.location.pathname;
    
    if (pathName.includes("dashboard.html") || pathName.endsWith("/dashboard/")) {
        renderUserDashboard();
    } else if (pathName.includes("admin-dashboard.html") || pathName.endsWith("/admin-dashboard/")) {
        renderAdminDashboard();
    } else if (pathName.includes("user-management.html") || pathName.endsWith("/user-management/")) {
        renderUserManagement();
    } else if (pathName.includes("upload-files.html") || pathName.endsWith("/upload-files/")) {
        setupFileUploader();
    } else if (pathName.includes("messages.html") || pathName.endsWith("/messages/")) {
        setupMessagesSystem();
    } else if (pathName.includes("edit-profile.html") || pathName.endsWith("/edit-profile/")) {
        setupEditProfileForm();
    } else if (pathName.includes("settings.html") || pathName.endsWith("/settings/")) {
        setupSettings();
    } else if (pathName.includes("activity-logs.html") || pathName.endsWith("/activity-logs/")) {
        renderActivityLogs();
    } else if (pathName.includes("data-management.html") || pathName.endsWith("/data-management/")) {
        setupDataManagement();
    } else if (pathName.includes("reports.html") || pathName.endsWith("/reports/")) {
        renderReportsPage();
    } else if (pathName.includes("analytics.html") || pathName.endsWith("/analytics/")) {
        renderAnalyticsPage();
    } else if (pathName.includes("search.html") || pathName.endsWith("/search/")) {
        setupSearchPage();
    } else if (pathName.includes("history.html") || pathName.endsWith("/history/")) {
        renderHistoryPage();
    } else if (pathName.includes("notifications.html") || pathName.endsWith("/notifications/")) {
        renderNotificationsPage();
    } else if (pathName.includes("profile.html") || pathName.endsWith("/profile/") || (pathName.includes("/profile/") && !pathName.includes("/edit-profile/"))) {
        renderProfilePage();
    } else if (pathName.includes("feedback.html") || pathName.endsWith("/feedback/")) {
        setupFeedbackForm();
    } else if (pathName.includes("help-center.html") || pathName.endsWith("/help-center/")) {
        setupHelpCenter();
    }
});

// Toast Notifier
function showToast(message, type = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    
    const toast = document.createElement("div");
    toast.className = `custom-toast border-start border-4`;
    
    let icon = "💡";
    let borderClass = "border-info";
    if (type === "success") { icon = "✅"; borderClass = "border-success"; }
    else if (type === "danger") { icon = "❌"; borderClass = "border-danger"; }
    else if (type === "warning") { icon = "⚠️"; borderClass = "border-warning"; }
    
    toast.classList.add(borderClass);
    toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%) scale(0.9)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Global Auth Getters
function getLoggedInUser() {
    const session = localStorage.getItem("erp_session");
    if (!session) return null;
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    return users.find(u => u.token === session) || null;
}

function checkAuthentication(requiredRole) {
    const user = getLoggedInUser();
    if (!user) {
        window.location.href = "login.html";
        return null;
    }
    if (requiredRole && user.role !== requiredRole) {
        window.location.href = "404.html";
        return null;
    }
    return user;
}

// Theme Engine
function initTheme() {
    const currentTheme = localStorage.getItem("erp_theme") || "dark";
    document.documentElement.setAttribute("data-theme", currentTheme);
    
    const switchers = document.querySelectorAll(".theme-toggle-btn");
    switchers.forEach(btn => {
        btn.addEventListener("click", () => {
            const nextTheme = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", nextTheme);
            localStorage.setItem("erp_theme", nextTheme);
            showToast(`Theme switched to ${nextTheme} mode!`, "success");
        });
    });
}

// Sidebar responsive drawer and toggle collapse
function setupSidebarToggle() {
    const togglers = document.querySelectorAll(".sidebar-toggle-btn");
    const sidebar = document.querySelector(".app-sidebar");
    
    togglers.forEach(btn => {
        btn.addEventListener("click", () => {
            if (sidebar) {
                if (window.innerWidth < 992) {
                    sidebar.classList.toggle("show");
                } else {
                    sidebar.classList.toggle("collapsed");
                }
            }
        });
    });
}

function handleNotificationsBadge() {
    const user = getLoggedInUser();
    if (!user) return;
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    const unreadCount = notifications.filter(n => n.user_id === user.id && !n.is_read).length;
    
    const badges = document.querySelectorAll(".notif-badge");
    badges.forEach(badge => {
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    });
}

// Dynamic dashboard loader for standard user (Intern)
function renderUserDashboard() {
    const user = checkAuthentication("user");
    if (!user) return;
    
    // Set Profile Summary Details
    document.getElementById("user-fullname").textContent = user.full_name || user.username;
    document.getElementById("user-track").textContent = user.track || "Not Assigned";
    document.getElementById("user-status").textContent = user.status;
    
    const statusBadge = document.getElementById("user-status");
    statusBadge.className = `badge-status status-${user.status}`;
    
    const avatarImg = document.getElementById("user-avatar");
    if (avatarImg && user.avatar) avatarImg.src = user.avatar;
    
    // Render logs count
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]").filter(f => f.user_id === user.id);
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]").filter(n => n.user_id === user.id);
    
    document.getElementById("stat-files").textContent = files.length;
    document.getElementById("stat-notifications").textContent = notifications.length;
    
    // Draw dummy metrics graph using Chart.js
    const ctx = document.getElementById("userDashboardChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Milestone Progress (%)',
                    data: [25, 50, 75, 100],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }
    
    // Render dynamic tables
    renderRecentActivities(user.id);
}

function renderRecentActivities(userId) {
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]").filter(l => l.user_id === userId);
    const tbody = document.getElementById("recent-activities-table");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">No recent activities found.</td></tr>`;
        return;
    }
    
    logs.slice(0, 5).forEach(log => {
        const tr = document.createElement("tr");
        const formattedDate = new Date(log.timestamp).toLocaleDateString();
        tr.innerHTML = `
            <td>${log.action}</td>
            <td>${log.ip_address}</td>
            <td>${formattedDate}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Dynamic dashboard loader for System Admin
function renderAdminDashboard() {
    checkAuthentication("admin");
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]");
    
    document.getElementById("admin-stat-interns").textContent = users.length;
    document.getElementById("admin-stat-pending").textContent = users.filter(u => u.status === "pending").length;
    document.getElementById("admin-stat-uploads").textContent = files.length;
    document.getElementById("admin-stat-logs").textContent = logs.length;
    
    // Admin charts
    const ctx = document.getElementById("adminCohortChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Software Eng', 'UI/UX Design', 'Data Analytics'],
                datasets: [{
                    label: 'Intern Count',
                    data: [
                        users.filter(u => u.track === 'Software Engineering').length,
                        users.filter(u => u.track === 'UI/UX Design').length,
                        users.filter(u => u.track === 'Data Analytics').length
                    ],
                    backgroundColor: ['#6366f1', '#a855f7', '#10b981'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }
    
    renderRecentUsers();
}

function renderRecentUsers() {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    const tbody = document.getElementById("recent-users-table");
    if (!tbody) return;
    
    tbody.innerHTML = "";
    users.slice(0, 5).forEach(u => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <div class="d-flex align-items-center gap-3">
                    <img src="${u.avatar}" class="rounded-circle" width="36" height="36" alt="">
                    <div>
                        <div class="fw-bold">${u.full_name || u.username}</div>
                        <div class="small text-muted">${u.email}</div>
                    </div>
                </div>
            </td>
            <td>${u.track || "N/A"}</td>
            <td><span class="badge-status status-${u.status}">${u.status}</span></td>
            <td>
                <button class="btn btn-sm btn-success me-2" onclick="changeUserStatus(${u.id}, 'approved')">Approve</button>
                <button class="btn btn-sm btn-danger" onclick="changeUserStatus(${u.id}, 'rejected')">Reject</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Global user management helpers
window.changeUserStatus = function(userId, newStatus) {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const userIndex = users.findIndex(u => u.id === userId);
    
    if (userIndex !== -1) {
        users[userIndex].status = newStatus;
        localStorage.setItem("erp_users", JSON.stringify(users));
        showToast(`User status updated to ${newStatus}`, "success");
        
        // Add log
        addActivityLog(userId, `Profile marked ${newStatus}`);
        
        // Add notification
        addNotification(userId, `Application status updated`, `Your internship application has been marked as ${newStatus}.`, newStatus === 'approved' ? 'success' : 'danger');
        
        // Refresh appropriate view
        if (window.location.pathname.includes("admin-dashboard.html")) {
            renderAdminDashboard();
        } else if (window.location.pathname.includes("user-management.html")) {
            renderUserManagement();
        }
    }
};

function addActivityLog(userId, action) {
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]");
    const newLog = {
        id: logs.length + 1,
        user_id: userId,
        action: action,
        ip_address: "127.0.0.1",
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString()
    };
    logs.unshift(newLog);
    localStorage.setItem("erp_logs", JSON.stringify(logs));
}

function addNotification(userId, title, message, level) {
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    const newNotif = {
        id: notifications.length + 1,
        user_id: userId,
        title: title,
        message: message,
        level: level,
        is_read: false,
        created_at: new Date().toISOString()
    };
    notifications.unshift(newNotif);
    localStorage.setItem("erp_notifications", JSON.stringify(notifications));
}

// Render dynamic User CRUD List (Admin Panel)
function renderUserManagement() {
    checkAuthentication("admin");
    const tbody = document.getElementById("users-list");
    if (!tbody) return;
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    tbody.innerHTML = "";
    
    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No users found in database.</td></tr>`;
        return;
    }
    
    users.forEach(u => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${u.id}</td>
            <td>
                <div class="d-flex align-items-center gap-3">
                    <img src="${u.avatar}" class="rounded-circle" width="36" height="36">
                    <div>
                        <div class="fw-bold">${u.full_name || u.username}</div>
                        <div class="small text-muted">${u.email}</div>
                    </div>
                </div>
            </td>
            <td>${u.track || "N/A"}</td>
            <td><span class="badge-status status-${u.status}">${u.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-info me-1" onclick="viewUserProfile(${u.id})"><i class="bi bi-eye"></i></button>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="editUserModal(${u.id})"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${u.id})"><i class="bi bi-trash"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Admin CRUD functions
window.deleteUser = function(userId) {
    if (confirm("Are you sure you want to delete this user from database?")) {
        let users = JSON.parse(localStorage.getItem("erp_users") || "[]");
        users = users.filter(u => u.id !== userId);
        localStorage.setItem("erp_users", JSON.stringify(users));
        showToast("User deleted from database", "danger");
        renderUserManagement();
    }
};

window.viewUserProfile = function(userId) {
    // Redirect to profile page with query param
    window.location.href = `profile.html?id=${userId}`;
};

window.editUserModal = function(userId) {
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    const u = users.find(usr => usr.id === userId);
    if (!u) return;
    
    // Dynamic overlay form injector
    const modalHtml = `
        <div class="modal fade show d-block" id="editUserModal" tabindex="-1" style="background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-panel p-4" style="border: 1px solid var(--card-hover-border)">
                    <div class="modal-header border-0 pb-0">
                        <h4 class="modal-title">Edit User (#${u.id})</h4>
                        <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('editUserModal').remove()"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editUserAdminForm">
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Full Name</label>
                                <input type="text" class="form-control form-control-premium" id="m-fullname" value="${u.full_name || ''}">
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Track</label>
                                <select class="form-select form-control-premium" id="m-track">
                                    <option value="Software Engineering" ${u.track === 'Software Engineering' ? 'selected' : ''}>Software Engineering</option>
                                    <option value="UI/UX Design" ${u.track === 'UI/UX Design' ? 'selected' : ''}>UI/UX Design</option>
                                    <option value="Data Analytics" ${u.track === 'Data Analytics' ? 'selected' : ''}>Data Analytics</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label text-secondary small">Status</label>
                                <select class="form-select form-control-premium" id="m-status">
                                    <option value="pending" ${u.status === 'pending' ? 'selected' : ''}>Pending</option>
                                    <option value="approved" ${u.status === 'approved' ? 'selected' : ''}>Approved</option>
                                    <option value="rejected" ${u.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                                </select>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary-premium me-2" onclick="document.getElementById('editUserModal').remove()">Cancel</button>
                                <button type="submit" class="btn btn-premium">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    document.getElementById("editUserAdminForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const updatedFullName = document.getElementById("m-fullname").value;
        const updatedTrack = document.getElementById("m-track").value;
        const updatedStatus = document.getElementById("m-status").value;
        
        const usersList = JSON.parse(localStorage.getItem("erp_users") || "[]");
        const idx = usersList.findIndex(usr => usr.id === u.id);
        
        if (idx !== -1) {
            usersList[idx].full_name = updatedFullName;
            usersList[idx].track = updatedTrack;
            usersList[idx].status = updatedStatus;
            
            localStorage.setItem("erp_users", JSON.stringify(usersList));
            showToast("User updated successfully", "success");
            document.getElementById('editUserModal').remove();
            renderUserManagement();
        }
    });
};

// Setup dynamic file uploader drag & drop
// Setup dynamic file uploader drag & drop
function setupFileUploader() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    
    // Prevent default drag & drop behaviors on window level to avoid opening files
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        window.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    if (dropZone) {
        dropZone.addEventListener("click", () => fileInput.click());
        
        dropZone.addEventListener("dragenter", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
        
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
        
        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });
        
        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            const files = e.dataTransfer.files;
            handleFilesUpload(files, user.id);
        });
        
        fileInput.addEventListener("change", () => {
            handleFilesUpload(fileInput.files, user.id);
        });
    }
    
    renderFilesList(user.id);
}

function handleFilesUpload(filesList, userId) {
    if (filesList.length === 0) return;
    
    const allowedTypes = ["pdf", "docx", "zip", "png", "jpg", "jpeg"];
    const filesToUpload = [];
    
    for (let i = 0; i < filesList.length; i++) {
        const file = filesList[i];
        const ext = file.name.split(".").pop().toLowerCase();
        
        if (!allowedTypes.includes(ext)) {
            showToast(`Extension .${ext} is not allowed. Upload PDF, DOCX, ZIP, or Images.`, "danger");
            continue;
        }
        
        if (file.size > 10485760) {
            showToast(`File ${file.name} is too large. Limit is 10MB.`, "danger");
            continue;
        }
        
        filesToUpload.push(file);
    }
    
    if (filesToUpload.length === 0) return;
    
    let uploadIndex = 0;
    
    function uploadNext() {
        if (uploadIndex >= filesToUpload.length) {
            document.getElementById("upload-progress-container").classList.add("d-none");
            document.getElementById("upload-status-text").classList.add("d-none");
            document.getElementById("drop-zone").style.pointerEvents = "auto";
            return;
        }
        
        const file = filesToUpload[uploadIndex];
        const formData = new FormData();
        formData.append("file", file);
        
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfInput ? csrfInput.value : '';
        
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/erp/upload-files/", true);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        if (csrfToken) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
        }
        
        document.getElementById("upload-progress-container").classList.remove("d-none");
        document.getElementById("upload-status-text").classList.remove("d-none");
        document.getElementById("drop-zone").style.pointerEvents = "none";
        
        xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                document.getElementById("upload-progress-bar").style.width = `${percent}%`;
                document.getElementById("upload-progress-bar").setAttribute("aria-valuenow", percent);
                document.getElementById("upload-status-text").textContent = `Uploading ${file.name}: ${percent}%`;
            }
        });
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200 || xhr.status === 201) {
                    try {
                        const res = JSON.parse(xhr.responseText);
                        if (res.success) {
                            showToast(res.message || "File uploaded successfully!", "success");
                            const erpFiles = JSON.parse(localStorage.getItem("erp_files") || "[]");
                            erpFiles.push(res.file);
                            localStorage.setItem("erp_files", JSON.stringify(erpFiles));
                            renderFilesList(userId);
                        } else {
                            showToast(res.message || "Upload failed.", "danger");
                        }
                    } catch (e) {
                        showToast("Response processing error.", "danger");
                    }
                } else {
                    try {
                        const res = JSON.parse(xhr.responseText);
                        showToast(res.message || "Upload error.", "danger");
                    } catch (e) {
                        showToast("Upload failed.", "danger");
                    }
                }
                
                uploadIndex++;
                uploadNext();
            }
        };
        
        xhr.send(formData);
    }
    
    uploadNext();
}

function renderFilesList(userId) {
    const tableBody = document.getElementById("uploaded-files-table");
    if (!tableBody) return;
    
    const currentUser = getLoggedInUser();
    if (!currentUser) return;
    
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    const visibleFiles = currentUser.role === 'admin' ? files : files.filter(f => f.user_id === userId);
    tableBody.innerHTML = "";
    
    if (visibleFiles.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No files uploaded.</td></tr>`;
        return;
    }
    
    visibleFiles.forEach(f => {
        const tr = document.createElement("tr");
        const formattedSize = (f.file_size / (1024 * 1024)).toFixed(2) + " MB";
        const formattedDate = new Date(f.uploaded_at).toLocaleString();
        
        let iconClass = "bi-file-earmark-arrow-up";
        const type = (f.file_type || "").toLowerCase();
        if (type === "pdf") iconClass = "bi-file-earmark-pdf text-danger";
        else if (["png", "jpg", "jpeg"].includes(type)) iconClass = "bi-file-earmark-image text-warning";
        else if (type === "zip") iconClass = "bi-file-earmark-zip text-info";
        else if (type === "docx") iconClass = "bi-file-earmark-word text-primary";
        
        const isPreviewable = ["pdf", "png", "jpg", "jpeg"].includes(type);
        const uploadedBy = f.uploaded_by || "System";
        
        let previewBtn = "";
        if (isPreviewable) {
            previewBtn = `<button class="btn btn-sm btn-outline-info me-1" onclick="previewFile('${f.file_url}', '${type}')"><i class="bi bi-eye"></i> Preview</button>`;
        }
        
        tr.innerHTML = `
            <td>
                <div class="d-flex align-items-center gap-2">
                    <i class="bi ${iconClass} fs-5"></i>
                    <span>${f.file_name}</span>
                </div>
            </td>
            <td>${formattedSize}</td>
            <td>${uploadedBy}</td>
            <td>${formattedDate}</td>
            <td>
                ${previewBtn}
                <a href="${f.file_url}" class="btn btn-sm btn-outline-success me-1" download="${f.file_name}"><i class="bi bi-download"></i> Download</a>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteUserFile(${f.id}, ${userId})"><i class="bi bi-trash"></i> Delete</button>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

window.previewFile = function(url, type) {
    if (type === 'pdf') {
        window.open(url, '_blank');
        return;
    }
    
    const container = document.getElementById("preview-container");
    if (!container) return;
    
    container.innerHTML = `<img src="${url}" class="img-fluid rounded border border-secondary" style="max-height: 500px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);">`;
    const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
    previewModal.show();
};

window.deleteUserFile = function(fileId, userId) {
    if (confirm("Are you sure you want to delete this file physically and from database?")) {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfInput ? csrfInput.value : '';
        
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `/erp/delete-file/${fileId}/`, true);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        if (csrfToken) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
        }
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200 || xhr.status === 201) {
                    try {
                        const res = JSON.parse(xhr.responseText);
                        if (res.success) {
                            showToast(res.message || "File deleted successfully!", "success");
                            let files = JSON.parse(localStorage.getItem("erp_files") || "[]");
                            files = files.filter(f => f.id !== fileId);
                            localStorage.setItem("erp_files", JSON.stringify(files));
                            renderFilesList(userId);
                        } else {
                            showToast(res.message || "Deletion failed.", "danger");
                        }
                    } catch (e) {
                        showToast("Deletion processing error.", "danger");
                    }
                } else {
                    showToast("Failed to delete file. Check permissions.", "danger");
                }
            }
        };
        
        xhr.send();
    }
};

// Interactive Messenger Layout
function setupMessagesSystem() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const inboxList = document.getElementById("inbox-list");
    const chatWindow = document.getElementById("chat-window");
    const msgForm = document.getElementById("message-reply-form");
    
    if (inboxList) {
        renderInbox(user);
    }
    
    if (msgForm) {
        msgForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const messageBody = document.getElementById("message-input").value;
            if (!messageBody.trim()) return;
            
            const messages = JSON.parse(localStorage.getItem("erp_messages") || "[]");
            const activeChatUserId = parseInt(chatWindow.dataset.activeUser || "1");
            
            const newMsg = {
                id: messages.length + 1,
                sender_id: user.id,
                receiver_id: activeChatUserId,
                subject: "Direct ERP Message",
                body: messageBody,
                is_read: false,
                created_at: new Date().toISOString()
            };
            
            messages.push(newMsg);
            localStorage.setItem("erp_messages", JSON.stringify(messages));
            document.getElementById("message-input").value = "";
            renderChatHistory(user.id, activeChatUserId);
            
            // Auto simulate reply if admin is sending message or user is sending message
            setTimeout(() => {
                if (user.role === "user") {
                    // Simulate Admin reply
                    const autoReply = {
                        id: messages.length + 2,
                        sender_id: 1, // Admin
                        receiver_id: user.id,
                        subject: "Re: Direct ERP Message",
                        body: "Hello, this is BlueNova Admin. Your query has been logged. We will review your files shortly.",
                        is_read: false,
                        created_at: new Date().toISOString()
                    };
                    const msgs = JSON.parse(localStorage.getItem("erp_messages") || "[]");
                    msgs.push(autoReply);
                    localStorage.setItem("erp_messages", JSON.stringify(msgs));
                    renderChatHistory(user.id, activeChatUserId);
                    showToast("New message received from admin!", "info");
                }
            }, 2000);
        });
    }
}

function renderInbox(currentUser) {
    const inboxList = document.getElementById("inbox-list");
    if (!inboxList) return;
    
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    inboxList.innerHTML = "";
    
    // Identify who the user can communicate with
    // Admin communicates with everyone. User communicates with Admin.
    let contacts = [];
    if (currentUser.role === "admin") {
        contacts = users.filter(u => u.role !== "admin");
    } else {
        contacts = users.filter(u => u.role === "admin");
    }
    
    contacts.forEach(contact => {
        const item = document.createElement("div");
        item.className = "p-3 mb-2 glass-panel glass-panel-hover" + (contact.id === 1 ? " border-primary" : "");
        item.style.cursor = "pointer";
        item.innerHTML = `
            <div class="d-flex align-items-center gap-3">
                <img src="${contact.avatar}" class="rounded-circle" width="40" height="40">
                <div class="flex-grow-1 overflow-hidden">
                    <div class="fw-bold">${contact.full_name || contact.username}</div>
                    <div class="small text-muted text-truncate">${contact.role === "admin" ? "Systems Administrator" : (contact.track || "")}</div>
                </div>
            </div>
        `;
        
        item.addEventListener("click", () => {
            document.querySelectorAll("#inbox-list > div").forEach(d => d.style.borderColor = "var(--card-border)");
            item.style.borderColor = "var(--primary)";
            openChatWith(currentUser.id, contact.id, contact.full_name || contact.username);
        });
        
        inboxList.appendChild(item);
    });
    
    // Auto load first contact
    if (contacts.length > 0) {
        openChatWith(currentUser.id, contacts[0].id, contacts[0].full_name || contacts[0].username);
    }
}

function openChatWith(currentUserId, targetUserId, name) {
    const chatWindow = document.getElementById("chat-window");
    if (!chatWindow) return;
    
    chatWindow.dataset.activeUser = targetUserId;
    document.getElementById("chat-partner-name").textContent = name;
    renderChatHistory(currentUserId, targetUserId);
}

function renderChatHistory(currentUserId, targetUserId) {
    const chatBody = document.getElementById("chat-history");
    if (!chatBody) return;
    
    const messages = JSON.parse(localStorage.getItem("erp_messages") || "[]");
    
    // Filter messages between user and target
    const thread = messages.filter(m => 
        (m.sender_id === currentUserId && m.receiver_id === targetUserId) ||
        (m.sender_id === targetUserId && m.receiver_id === currentUserId)
    ).sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
    
    chatBody.innerHTML = "";
    if (thread.length === 0) {
        chatBody.innerHTML = `<div class="text-center text-muted py-5">No correspondence history. Start chat below.</div>`;
        return;
    }
    
    thread.forEach(msg => {
        const bubble = document.createElement("div");
        const isSent = msg.sender_id === currentUserId;
        bubble.className = `chat-bubble ${isSent ? 'sent' : 'received'}`;
        bubble.textContent = msg.body;
        chatBody.appendChild(bubble);
    });
    
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Edit Profile Form Controls
function setupEditProfileForm() {
    const user = getLoggedInUser();
    if (!user) return;
    
    document.getElementById("p-fullname").value = user.full_name || "";
    document.getElementById("p-phone").value = user.phone || "";
    document.getElementById("p-bio").value = user.bio || "";
    document.getElementById("p-academic").value = user.academic_background || "";
    document.getElementById("p-skills").value = user.skills || "";
    if (document.getElementById("p-track")) {
        document.getElementById("p-track").value = user.track || "";
    }
    
    const form = document.getElementById("editProfileForm");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = "Saving...";
        
        const formData = new FormData();
        formData.append("fullname", document.getElementById("p-fullname").value);
        formData.append("phone", document.getElementById("p-phone").value);
        formData.append("bio", document.getElementById("p-bio").value);
        formData.append("academic", document.getElementById("p-academic").value);
        formData.append("skills", document.getElementById("p-skills").value);
        if (document.getElementById("p-track")) {
            formData.append("track", document.getElementById("p-track").value);
        }
        
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfInput ? csrfInput.value : '';
        
        fetch("/erp/edit-profile/", {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast("Profile settings updated successfully!", "success");
                
                const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
                const idx = users.findIndex(u => u.id === user.id);
                if (idx !== -1) {
                    users[idx].full_name = document.getElementById("p-fullname").value;
                    users[idx].phone = document.getElementById("p-phone").value;
                    users[idx].bio = document.getElementById("p-bio").value;
                    users[idx].academic_background = document.getElementById("p-academic").value;
                    users[idx].skills = document.getElementById("p-skills").value;
                    if (document.getElementById("p-track")) {
                        users[idx].track = document.getElementById("p-track").value;
                    }
                    localStorage.setItem("erp_users", JSON.stringify(users));
                }
                
                setTimeout(() => window.location.href = "/erp/profile/", 800);
            } else {
                btn.disabled = false;
                btn.textContent = "Save Changes";
                showToast(data.message || "Failed to update profile details.", "danger");
            }
        })
        .catch(err => {
            btn.disabled = false;
            btn.textContent = "Save Changes";
            showToast("Server communication error.", "danger");
        });
    });
}

// Render dynamic Activity Logs (Admin Panel)
function renderActivityLogs() {
    checkAuthentication("admin");
    const tbody = document.getElementById("activity-logs-tbody");
    if (!tbody) return;
    
    const logs = JSON.parse(localStorage.getItem("erp_logs") || "[]");
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    tbody.innerHTML = "";
    
    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No activity recorded.</td></tr>`;
        return;
    }
    
    logs.forEach(log => {
        const u = users.find(usr => usr.id === log.user_id);
        const name = u ? (u.full_name || u.username) : "Guest";
        const role = u ? u.role : "N/A";
        const formattedTime = new Date(log.timestamp).toLocaleString();
        
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${log.id}</td>
            <td><strong>${name}</strong> <span class="small text-muted">(${role})</span></td>
            <td>${log.action}</td>
            <td><code>${log.ip_address}</code></td>
            <td>${formattedTime}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Settings
function setupSettings() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const emailNotifCheck = document.getElementById("settings-email-notify");
    if (emailNotifCheck) {
        emailNotifCheck.checked = true;
        emailNotifCheck.addEventListener("change", () => {
            showToast("Email notifications preference updated", "success");
            addActivityLog(user.id, "Changed notification preferences");
        });
    }
}

// Data Management panel backups
function setupDataManagement() {
    checkAuthentication("admin");
    
    const exportBtn = document.getElementById("export-db-btn");
    const backupBtn = document.getElementById("backup-db-btn");
    
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            showToast("Simulating data extraction... CSV download triggered", "success");
        });
    }
    
    if (backupBtn) {
        backupBtn.addEventListener("click", () => {
            showToast("Created a complete JSON backup point in downloads", "success");
        });
    }
}

// Reports PDF / CSV Generator
function renderReportsPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const csvBtn = document.getElementById("report-csv-btn");
    const pdfBtn = document.getElementById("report-pdf-btn");
    
    if (csvBtn) {
        csvBtn.addEventListener("click", () => {
            showToast("Downloading formatted CSV statistics report...", "success");
        });
    }
    
    if (pdfBtn) {
        pdfBtn.addEventListener("click", () => {
            showToast("Generating document layout PDF for download...", "success");
        });
    }
}

// Analytics graph generator page
function renderAnalyticsPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
    
    const ctx = document.getElementById("analyticsReportChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Approved', 'Pending', 'Rejected'],
                datasets: [{
                    label: 'Application Statuses',
                    data: [
                        users.filter(u => u.status === 'approved').length,
                        users.filter(u => u.status === 'pending').length,
                        users.filter(u => u.status === 'rejected').length
                    ],
                    backgroundColor: ['#10b981', '#f59e0b', '#f43f5e']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Global search results filtering simulation
function setupSearchPage() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get("q") || "";
    
    document.getElementById("search-input-field").value = query;
    performSearch(query);
    
    document.getElementById("search-form").addEventListener("submit", (e) => {
        e.preventDefault();
        const val = document.getElementById("search-input-field").value;
        performSearch(val);
    });
}

function performSearch(q) {
    const resultsContainer = document.getElementById("search-results-list");
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = "";
    
    if (!q.trim()) {
        resultsContainer.innerHTML = `<div class="text-center text-muted py-5">Enter search keywords above.</div>`;
        return;
    }
    
    const query = q.toLowerCase();
    const users = JSON.parse(localStorage.getItem("erp_users") || "[]").filter(u => u.role !== "admin");
    const files = JSON.parse(localStorage.getItem("erp_files") || "[]");
    
    const filteredUsers = users.filter(u => 
        (u.full_name && u.full_name.toLowerCase().includes(query)) ||
        u.email.toLowerCase().includes(query) ||
        (u.track && u.track.toLowerCase().includes(query))
    );
    
    const filteredFiles = files.filter(f => f.file_name.toLowerCase().includes(query));
    
    if (filteredUsers.length === 0 && filteredFiles.length === 0) {
        resultsContainer.innerHTML = `<div class="text-center text-muted py-5">No records matching "${q}" found.</div>`;
        return;
    }
    
    filteredUsers.forEach(u => {
        const item = document.createElement("div");
        item.className = "p-3 mb-3 glass-panel d-flex justify-content-between align-items-center";
        item.innerHTML = `
            <div>
                <span class="badge bg-primary me-2">User Profile</span>
                <strong>${u.full_name || u.username}</strong> - ${u.email}
                <div class="small text-secondary mt-1">Track: ${u.track || "N/A"} | Status: ${u.status}</div>
            </div>
            <a href="profile.html?id=${u.id}" class="btn btn-sm btn-outline-primary">View</a>
        `;
        resultsContainer.appendChild(item);
    });
    
    filteredFiles.forEach(f => {
        const item = document.createElement("div");
        item.className = "p-3 mb-3 glass-panel d-flex justify-content-between align-items-center";
        item.innerHTML = `
            <div>
                <span class="badge bg-secondary me-2">File</span>
                <strong>${f.file_name}</strong>
                <div class="small text-secondary mt-1">Size: ${(f.file_size/1024).toFixed(0)} KB | Format: ${f.file_type}</div>
            </div>
            <button class="btn btn-sm btn-outline-info" onclick="showToast('Simulating download...', 'info')">Download</button>
        `;
        resultsContainer.appendChild(item);
    });
}

// User History Milestone Logger
function renderHistoryPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const list = document.getElementById("milestone-list");
    if (!list) return;
    
    const history = JSON.parse(localStorage.getItem("erp_history") || "[]").filter(h => h.user_id === user.id);
    list.innerHTML = "";
    
    if (history.length === 0) {
        list.innerHTML = `<div class="text-center text-muted py-5">No achievements recorded yet.</div>`;
        return;
    }
    
    history.forEach(item => {
        const div = document.createElement("div");
        div.className = "mb-4 border-start border-3 border-primary ps-4 relative";
        const dateStr = new Date(item.achieved_at).toLocaleDateString();
        div.innerHTML = `
            <div class="fw-bold fs-5">${item.milestone_name}</div>
            <div class="small text-muted mb-2">${dateStr}</div>
            <div>${item.description}</div>
        `;
        list.appendChild(div);
    });
}

// Notifications listing page
function renderNotificationsPage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const list = document.getElementById("notifications-list");
    if (!list) return;
    
    const notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]").filter(n => n.user_id === user.id);
    list.innerHTML = "";
    
    if (notifications.length === 0) {
        list.innerHTML = `<div class="text-center text-muted py-5">No notifications.</div>`;
        return;
    }
    
    notifications.forEach(n => {
        const div = document.createElement("div");
        div.className = `p-3 mb-3 glass-panel border-start border-4 border-${n.level === 'danger' ? 'danger' : n.level === 'success' ? 'success' : n.level === 'warning' ? 'warning' : 'info'}`;
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h5 class="mb-1">${n.title}</h5>
                    <p class="mb-0 text-secondary small">${n.message}</p>
                </div>
                <button class="btn btn-sm btn-link text-muted" onclick="deleteNotification(${n.id})">Clear</button>
            </div>
        `;
        list.appendChild(div);
    });
    
    // Mark notifications as read
    const allNotifs = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    allNotifs.forEach(not => {
        if (not.user_id === user.id) not.is_read = true;
    });
    localStorage.setItem("erp_notifications", JSON.stringify(allNotifs));
    handleNotificationsBadge();
}

window.deleteNotification = function(notifId) {
    let notifications = JSON.parse(localStorage.getItem("erp_notifications") || "[]");
    notifications = notifications.filter(n => n.id !== notifId);
    localStorage.setItem("erp_notifications", JSON.stringify(notifications));
    showToast("Notification cleared", "info");
    renderNotificationsPage();
};

// User Profile display detail page
function renderProfilePage() {
    const user = getLoggedInUser();
    if (!user) return;
    
    // Detect if reading dynamic profile query or personal profile
    const params = new URLSearchParams(window.location.search);
    const requestedId = params.get("id");
    
    let profileUser = user;
    if (requestedId && user.role === "admin") {
        const users = JSON.parse(localStorage.getItem("erp_users") || "[]");
        profileUser = users.find(u => u.id === parseInt(requestedId)) || user;
    }
    
    document.getElementById("prof-name").textContent = profileUser.full_name || profileUser.username;
    document.getElementById("prof-track").textContent = profileUser.track || "N/A";
    document.getElementById("prof-status").textContent = profileUser.status;
    document.getElementById("prof-status").className = `badge-status status-${profileUser.status}`;
    document.getElementById("prof-email").textContent = profileUser.email;
    document.getElementById("prof-phone").textContent = profileUser.phone || "N/A";
    document.getElementById("prof-bio").textContent = profileUser.bio || "No biography provided yet.";
    document.getElementById("prof-academic").textContent = profileUser.academic_background || "N/A";
    document.getElementById("prof-skills").textContent = profileUser.skills || "N/A";
    
    if (profileUser.avatar) {
        document.getElementById("prof-avatar").src = profileUser.avatar;
    }
}

// User Feedback setup
function setupFeedbackForm() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const form = document.getElementById("feedbackForm");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const subj = document.getElementById("fb-subject").value;
        const msg = document.getElementById("fb-message").value;
        const rating = parseInt(document.getElementById("fb-rating").value);
        
        const feedbacks = JSON.parse(localStorage.getItem("erp_feedback") || "[]");
        const newFb = {
            id: feedbacks.length + 1,
            user_id: user.id,
            subject: subj,
            message: msg,
            rating: rating,
            created_at: new Date().toISOString()
        };
        
        feedbacks.unshift(newFb);
        localStorage.setItem("erp_feedback", JSON.stringify(feedbacks));
        
        addActivityLog(user.id, `Submitted feedback: ${subj}`);
        showToast("Thank you for your feedback!", "success");
        form.reset();
    });
}

// User Help ticket system simulation
function setupHelpCenter() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const form = document.getElementById("helpTicketForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            showToast("Troubleshoot ticket submitted to recruitment support team!", "success");
            addActivityLog(user.id, "Logged help center request");
            form.reset();
        });
    }
}
