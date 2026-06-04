let qrInterval;

function handleOpenModal(button) {
    const url = button.getAttribute('data-url');
    const modal = document.getElementById('qrModal');
    const progress = document.getElementById('progressBar');
    
    if(!modal || !progress) return;

    document.getElementById('qrImage').src = url;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    setTimeout(() => {
        const closeBtn = modal.querySelector('button');
        if(closeBtn) closeBtn.focus();
    }, 100);

    const startTimer = () => {
        progress.style.transition = 'none';
        progress.style.width = '100%';
        setTimeout(() => {
            progress.style.transition = 'width 30000ms linear';
            progress.style.width = '0%';
        }, 50);
    };

    startTimer();
    qrInterval = setInterval(() => {
        const qrImage = document.getElementById('qrImage');
        if(qrImage) qrImage.src = url + '?t=' + new Date().getTime();
        startTimer();
    }, 30000);
}

function closeQRModal() {
    const modal = document.getElementById('qrModal');
    if(!modal) return;
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    if (qrInterval) clearInterval(qrInterval);
}

document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('qrModal');
    if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
        closeQRModal();
    }
});
