async function submitScore(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const score = document.getElementById('score').value;
    
    // Client-side validation
    if (!/^[A-Za-z0-9\s_-]*$/.test(name)) {
        showError("Only letters, numbers, spaces, underscores, and hyphens allowed");
        return;
    }
    
    if (name.length > 20) {
        showError("Name must be 20 characters or less");
        return;
    }
    
    try {
        const response = await fetch('/api/scores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                score: parseInt(score),
                submission_time: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            if (data.detail && data.detail.error_type === 'profanity') {
                showError("Please choose a nice player name");
            } else {
                showError("Error submitting score");
            }
            return;
        }
        
        // Show success message
        const successMessage = document.getElementById('successMessage');
        if (successMessage) {
            successMessage.style.display = 'block';
            
            // Hide success message after animation
            setTimeout(() => {
                successMessage.style.display = 'none';
            }, 3000);
        }
        
        // Reset form
        document.getElementById('name').value = '';
        document.getElementById('score').value = '';
        
        // If we're on the homepage, refresh the scores
        if (typeof loadScores === 'function') {
            await loadScores();
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError("Error submitting score");
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = '❌ ' + message;
    
    const form = document.querySelector('form');
    // Remove any existing error messages
    const existingError = form.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    form.insertBefore(errorDiv, form.firstChild);
    
    // Automatically remove the error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Auto-focus name field on page load
window.onload = function() {
    const nameInput = document.getElementById('name');
    if (nameInput) {
        nameInput.focus();
    }
};
