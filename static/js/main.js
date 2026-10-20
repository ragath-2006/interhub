// InternHub Core JS
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {}
        }, 5000);
    });

    // Tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Interactive Star Rating Pickers for Reviews
    const starInputs = document.querySelectorAll('.star-picker');
    starInputs.forEach(picker => {
        const stars = picker.querySelectorAll('.star-icon');
        const hiddenInput = picker.querySelector('input[type="hidden"]');
        
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const val = parseInt(star.getAttribute('data-value'));
                hiddenInput.value = val;
                updateStars(stars, val);
            });
            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.getAttribute('data-value'));
                updateStars(stars, val);
            });
        });

        picker.addEventListener('mouseleave', () => {
            const currentVal = parseInt(hiddenInput.value || 5);
            updateStars(stars, currentVal);
        });
    });

    function updateStars(stars, value) {
        stars.forEach(s => {
            const val = parseInt(s.getAttribute('data-value'));
            if (val <= value) {
                s.classList.remove('bi-star', 'text-muted');
                s.classList.add('bi-star-fill', 'text-warning');
            } else {
                s.classList.remove('bi-star-fill', 'text-warning');
                s.classList.add('bi-star', 'text-muted');
            }
        });
    }

    // Dynamic Live Resume Search / Filter Highlight
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const term = this.value.toLowerCase();
            const rows = document.querySelectorAll('.searchable-row');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }
});
