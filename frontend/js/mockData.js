const defaultUsers = [
    {
        id: 1,
        username: "admin",
        email: "admin@bluenova.com",
        role: "admin",
        token: "admin-session-token",
        avatar: "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=150&q=80"
    },
    {
        id: 2,
        username: "johndoe",
        email: "john.doe@example.com",
        role: "user",
        token: "user-session-token-john",
        track: "Software Engineering",
        status: "approved",
        full_name: "John Doe",
        phone: "+1 (555) 019-2834",
        bio: "Passionate software developer interested in scalable cloud solutions, full stack web apps, and databases. Excited to learn at BlueNova Technologies.",
        academic_background: "B.S. in Computer Science, Stanford University",
        skills: "Python, Javascript, React, SQL, HTML/CSS",
        avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80",
        resume: "john_doe_resume.pdf"
    },
    {
        id: 3,
        username: "alicesmith",
        email: "alice.s@example.com",
        role: "user",
        token: "user-session-token-alice",
        track: "UI/UX Design",
        status: "pending",
        full_name: "Alice Smith",
        phone: "+1 (555) 048-9381",
        bio: "Visual designer who loves creating clean layouts, designing custom design systems, and improving overall user conversion rates.",
        academic_background: "B.A. in Digital Media, Rhode Island School of Design",
        skills: "Figma, Adobe XD, HTML/CSS, Prototyping",
        avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
        resume: "alice_smith_portfolio.pdf"
    },
    {
        id: 4,
        username: "bobbrown",
        email: "bob.brown@example.com",
        role: "user",
        token: "user-session-token-bob",
        track: "Data Analytics",
        status: "rejected",
        full_name: "Bob Brown",
        phone: "+1 (555) 091-8422",
        bio: "Data enthusiast focused on building machine learning regression tools and statistical analysis metrics.",
        academic_background: "M.S. in Statistics, NYU",
        skills: "R, Python, Pandas, Tableau, Excel",
        avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
        resume: "bob_brown_resume.docx"
    }
];

const defaultFiles = [
    { id: 1, user_id: 2, file_name: "john_doe_resume.pdf", file_size: 1536000, file_type: "pdf", uploaded_at: "2026-06-25T14:32:00.000Z" },
    { id: 2, user_id: 2, file_name: "milestone1_project_code.zip", file_size: 12450000, file_type: "zip", uploaded_at: "2026-06-27T09:15:00.000Z" },
    { id: 3, user_id: 3, file_name: "alice_smith_portfolio.pdf", file_size: 5120000, file_type: "pdf", uploaded_at: "2026-06-28T11:45:00.000Z" }
];

const defaultNotifications = [
    { id: 1, user_id: 2, title: "Internship Approved", message: "Congratulations! Your internship application for the Software Engineering track has been approved.", level: "success", is_read: false, created_at: "2026-06-25T15:00:00.000Z" },
    { id: 2, user_id: 2, title: "Upcoming Review", message: "Your first mid-term performance evaluation is scheduled for next Tuesday.", level: "info", is_read: false, created_at: "2026-06-28T08:00:00.000Z" },
    { id: 3, user_id: 3, title: "Application Under Review", message: "Your application is currently being evaluated by the BlueNova recruiting team.", level: "warning", is_read: false, created_at: "2026-06-28T11:46:00.000Z" },
    { id: 4, user_id: 4, title: "Application Rejected", message: "Unfortunately, we cannot proceed with your candidacy for this cohort.", level: "danger", is_read: true, created_at: "2026-06-28T16:22:00.000Z" }
];

const defaultMessages = [
    { id: 1, sender_id: 2, receiver_id: 1, subject: "Question regarding milestone", body: "Hello Admin, is it okay if I upload the zip file for task 1 tomorrow morning? Thank you.", is_read: true, created_at: "2026-06-26T17:00:00.000Z" },
    { id: 2, sender_id: 1, receiver_id: 2, subject: "Re: Question regarding milestone", body: "Sure John. Late uploads are fine as long as they are completed before the weekly review on Friday.", is_read: false, created_at: "2026-06-27T08:30:00.000Z" }
];

const defaultLogs = [
    { id: 1, user_id: 2, action: "User Logged In", ip_address: "192.168.1.45", user_agent: "Mozilla/5.0 Chrome/124.0", timestamp: "2026-06-28T09:00:00.000Z" },
    { id: 2, user_id: 2, action: "Uploaded file milestone1_project_code.zip", ip_address: "192.168.1.45", user_agent: "Mozilla/5.0 Chrome/124.0", timestamp: "2026-06-27T09:15:00.000Z" },
    { id: 3, user_id: 3, action: "User Signed Up", ip_address: "192.168.1.12", user_agent: "Mozilla/5.0 Safari/605.1", timestamp: "2026-06-28T11:45:00.000Z" },
    { id: 4, user_id: 1, action: "Admin viewed log page", ip_address: "127.0.0.1", user_agent: "Mozilla/5.0 Chrome/124.0", timestamp: "2026-06-29T10:00:00.000Z" }
];

const defaultFeedback = [
    { id: 1, user_id: 2, subject: "Great program!", message: "The mentors are super helpful, and the tasks are challenging but highly relevant.", rating: 5, created_at: "2026-06-28T10:00:00.000Z" }
];

const defaultHistory = [
    { id: 1, user_id: 2, milestone_name: "Onboarding Completed", description: "Successfully set up the ERP account, completed profile info, and uploaded initial documents.", achieved_at: "2026-06-25T14:35:00.000Z" },
    { id: 2, user_id: 2, milestone_name: "Milestone 1 Submitted", description: "Uploaded project plan and codebase zip files for initial grading review.", achieved_at: "2026-06-27T09:16:00.000Z" }
];

// Initialize LocalStorage Data if not present
function initializeMockDatabase() {
    if (!localStorage.getItem("erp_users")) localStorage.setItem("erp_users", JSON.stringify(defaultUsers));
    if (!localStorage.getItem("erp_files")) localStorage.setItem("erp_files", JSON.stringify(defaultFiles));
    if (!localStorage.getItem("erp_notifications")) localStorage.setItem("erp_notifications", JSON.stringify(defaultNotifications));
    if (!localStorage.getItem("erp_messages")) localStorage.setItem("erp_messages", JSON.stringify(defaultMessages));
    if (!localStorage.getItem("erp_logs")) localStorage.setItem("erp_logs", JSON.stringify(defaultLogs));
    if (!localStorage.getItem("erp_feedback")) localStorage.setItem("erp_feedback", JSON.stringify(defaultFeedback));
    if (!localStorage.getItem("erp_history")) localStorage.setItem("erp_history", JSON.stringify(defaultHistory));
}

initializeMockDatabase();
