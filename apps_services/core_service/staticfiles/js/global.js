// Toast Animation Logic
document.addEventListener('DOMContentLoaded', () => {
    const toasts = Array.from(document.querySelectorAll('.message-toast'));
    
    // Logic to prevent redundant/stale messages (e.g., "Você saiu" + "Conectado")
    const texts = toasts.map(t => t.innerText.toLowerCase());
    const hasLogin = texts.some(t => t.includes('conectado') || t.includes('sucesso') || t.includes('bem-vindo') || t.includes('olá'));
    
    toasts.forEach((toast, index) => {
        const text = toast.innerText.toLowerCase();
        
        // If logging in, skip the "logged out" stale message and any old access messages
        if (hasLogin && (text.includes('saiu') || text.includes('encerrada') || text.includes('liberado'))) {
            toast.remove();
            return;
        }

        setTimeout(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
            toast.classList.add('translate-x-0', 'opacity-100');
        }, 100 * index);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('opacity-0', 'scale-95');
                setTimeout(() => toast.remove(), 500);
            }
        }, 5000 + (100 * index));
    });
});

// Sidebar Selection with Fallback
const getSidebar = () => document.getElementById('sidebar');
const getOverlay = () => document.getElementById('sidebar-overlay');
const getMobileMenuBtn = () => document.getElementById('mobileMenuBtn');

// Sidebar Collapse Logic (Desktop)
function toggleSidebarCollapse() {
    const sidebar = getSidebar();
    if(!sidebar) return;
    
    sidebar.classList.toggle('collapsed');
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
}

// Sidebar Mobile Toggle
function toggleSidebarMobile() {
    const sidebar = getSidebar();
    const overlay = getOverlay();
    if(!sidebar || !overlay) return;
    
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}

// Global Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuBtn = getMobileMenuBtn();
    const overlay = getOverlay();
    const sidebar = getSidebar();

    if(mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebarMobile);
    if(overlay) overlay.addEventListener('click', toggleSidebarMobile);

    // Restore state on load
    if (sidebar && localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
});
