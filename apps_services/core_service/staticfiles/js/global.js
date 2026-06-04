// Toast Animation Logic
document.addEventListener('DOMContentLoaded', () => {
    const toasts = Array.from(document.querySelectorAll('.message-toast'));
    
    // Logic to prevent redundant messages (e.g., "Você saiu" + "Conectado")
    const texts = toasts.map(t => t.innerText.toLowerCase());
    const hasLogin = texts.some(t => t.includes('conectado') || t.includes('sucesso'));
    
    toasts.forEach((toast, index) => {
        const text = toast.innerText.toLowerCase();
        
        // If logging in, skip the "logged out" stale message
        if (hasLogin && text.includes('saiu')) {
            toast.remove();
            return;
        }

        setTimeout(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
            toast.classList.add('translate-x-0', 'opacity-100');
        }, 100 * index);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('opacity-0', 'scale-95');
            setTimeout(() => toast.remove(), 500);
        }, 5000 + (100 * index));
    });
});

const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebar-overlay');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');

// Sidebar Collapse Logic (Desktop)
function toggleSidebarCollapse() {
    if(!sidebar) return;
    sidebar.classList.toggle('collapsed');
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
}

// Sidebar Mobile Toggle
function toggleSidebarMobile() {
    if(!sidebar || !overlay) return;
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}

if(mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebarMobile);
if(overlay) overlay.addEventListener('click', toggleSidebarMobile);

// Restore state on load
window.addEventListener('DOMContentLoaded', () => {
    if (sidebar && localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
});
