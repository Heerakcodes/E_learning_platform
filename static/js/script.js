/**
 * script.js — Frontend JavaScript for E-Learning Platform
 *
 * WHAT THIS FILE DOES:
 * 1. Auto-dismisses flash messages after 5 seconds
 * 2. Adds close buttons to messages
 * 3. Confirms before deleting anything (prevents accidents!)
 * 4. Animates progress bars on page load
 * 5. Highlights active nav link
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. AUTO-DISMISS MESSAGES ──────────────────────────────────
    // Flash messages (success/error) disappear after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        // Add a close button to each alert
        const closeBtn = document.createElement('button');
        closeBtn.className = 'alert-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Close');
        closeBtn.addEventListener('click', function () {
            dismissAlert(alert);
        });
        alert.appendChild(closeBtn);

        // Auto-dismiss after 5 seconds
        setTimeout(function () {
            dismissAlert(alert);
        }, 5000);
    });

    function dismissAlert(alert) {
        alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(110%)';
        setTimeout(function () {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }


    // ── 2. DELETE CONFIRMATION ────────────────────────────────────
    // Ask "Are you sure?" before any delete form submission
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.getAttribute('data-confirm') || 'Are you sure you want to delete this? This action cannot be undone.';
            if (!confirm(message)) {
                e.preventDefault();  // Stop form submission if user says "No"
            }
        });
    });


    // ── 3. ANIMATE PROGRESS BARS ─────────────────────────────────
    // Progress bars animate from 0% to their actual value on page load
    // The actual percentage is stored in the 'data-width' attribute
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    progressBars.forEach(function (bar) {
        const targetWidth = bar.getAttribute('data-width') || '0';
        // Start at 0, then animate to target
        bar.style.width = '0%';
        setTimeout(function () {
            bar.style.width = targetWidth + '%';
        }, 100);  // Small delay so the animation is visible
    });


    // ── 4. ACTIVE NAVBAR LINK HIGHLIGHTING ───────────────────────
    // Highlights the current page's nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav a');
    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });


    // ── 5. SCORE INPUT VALIDATION ─────────────────────────────────
    // Ensures score input is between 0 and 100
    const scoreInputs = document.querySelectorAll('input[name="score"]');
    scoreInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            let value = parseFloat(this.value);
            if (isNaN(value)) return;
            if (value < 0) this.value = 0;
            if (value > 100) this.value = 100;
        });
    });


    // ── 6. LOGOUT CONFIRMATION ───────────────────────────────────
    const logoutForm = document.getElementById('logout-form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to log out?')) {
                e.preventDefault();
            }
        });
    }

});
