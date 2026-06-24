// Shared navigation sidebar javascript
document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
});

const API_BASE = ""; // Relative paths work since static files are mounted on FastAPI

async function initNavigation() {
    // Setup layout wrapper
    setupLayout();
}

function setupLayout() {
    // Get the current page filename
    const path = window.location.pathname;
    const pageName = path.split("/").pop() || "index.html";

    // Create sidebar container
    const sidebar = document.createElement("div");
    sidebar.className = "sidebar";
    
    // Sidebar inner HTML
    sidebar.innerHTML = `
        <div class="sidebar-logo">
            <span class="logo-emoji">⚡</span> Workforce Opt
        </div>
        
        <!-- Nav Links -->
        <ul class="sidebar-links">
            <li><a href="index.html" class="${pageName === 'index.html' || pageName === '' ? 'active' : ''}">🏠 Dashboard</a></li>
            <li><a href="employees.html" class="${pageName === 'employees.html' ? 'active' : ''}">👥 Employees</a></li>
            <li><a href="tasks.html" class="${pageName === 'tasks.html' ? 'active' : ''}">📋 Tasks</a></li>
            <li><a href="search.html" class="${pageName === 'search.html' ? 'active' : ''}">🔍 Skill Search</a></li>
            <li><a href="optimization.html" class="${pageName === 'optimization.html' ? 'active' : ''}">⚙️ Optimization</a></li>
            <li><a href="results.html" class="${pageName === 'results.html' ? 'active' : ''}">📊 Results</a></li>
        </ul>
        
        <div class="sidebar-footer">
            v1.2.0-simple
        </div>
    `;

    // Prepend sidebar to body
    document.body.prepend(sidebar);

    // Create a container wrapper if not already wrapped
    // Make sure we have a div with class container for content
    const existingContainers = document.querySelectorAll(".container, .main-content");
    
    // Let's create a main-content div wrapping everything except the sidebar
    const mainWrapper = document.createElement("div");
    mainWrapper.className = "main-content";
    
    // Move all body children (except the newly prepended sidebar and scripts) into the main wrapper
    const children = Array.from(document.body.children);
    children.forEach(child => {
        if (child !== sidebar && child.tagName !== "SCRIPT" && child.tagName !== "LINK") {
            mainWrapper.appendChild(child);
        }
    });
    
    document.body.appendChild(mainWrapper);

    // Remove old header if present
    const oldHeader = mainWrapper.querySelector("header");
    if (oldHeader) {
        oldHeader.remove();
    }
    
    // Remove old footer if present
    const oldFooter = mainWrapper.querySelector("footer");
    if (oldFooter) {
        oldFooter.remove();
    }

    // Add toast notifications system to body if not exists
    if (!document.getElementById("toast-notification")) {
        const toast = document.createElement("div");
        toast.id = "toast-notification";
        toast.className = "toast";
        document.body.appendChild(toast);
    }
}

// Global Toast notification helper
function showToast(message, type = "success") {
    const toast = document.getElementById("toast-notification");
    if (!toast) return;
    
    toast.textContent = message;
    if (type === "success") {
        toast.style.borderLeft = "4px solid var(--success)";
    } else {
        toast.style.borderLeft = "4px solid var(--danger)";
    }
    toast.style.display = "block";
    
    setTimeout(() => {
        toast.style.display = "none";
    }, 3000);
}

function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

