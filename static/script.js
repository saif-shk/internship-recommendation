// Modern JavaScript for PM Internship Recommendation System

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all components
    initializeFormValidation();
    initializeAnimations();
    initializeInteractiveElements();
    initializeMobileOptimizations();
    initializeApplyButtons();
});

// ===============================
// APPLY BUTTON HANDLER
// ===============================
function initializeApplyButtons() {
    const applyButtons = document.querySelectorAll('.apply-btn');
    if (applyButtons.length === 0) return;

    applyButtons.forEach(button => {
        button.addEventListener('click', async function (event) {
            event.preventDefault();

            const internshipId = this.dataset.id;
            const sessionId = localStorage.getItem('session_id');

            if (!sessionId) {
                showToast("⚠️ Please create a profile before applying!", "error");
                return;
            }

            try {
                const formData = new FormData();
                formData.append("session_id", sessionId);

                const response = await fetch(`/apply/${internshipId}`, {
                    method: "POST",
                    body: formData
                });

                if (response.redirected) {
                    window.location.href = response.url; // Redirect to applications page
                } else if (!response.ok) {
                    const data = await response.json();
                    showToast(`❌ ${data.detail || "Failed to apply."}`, "error");
                }
            } catch (err) {
                showToast("❌ Network error. Please try again.", "error");
            }
        });
    });
}

// ===============================
// FORM VALIDATION
// ===============================
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearErrors);
        });

        form.addEventListener('submit', handleFormSubmission);
    });
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();

    field.classList.remove('error', 'success');
    let isValid = true;
    let errorMessage = '';

    switch (field.name) {
        case 'name':
            if (value.length < 2) {
                isValid = false;
                errorMessage = 'Name must be at least 2 characters long';
            }
            break;
        case 'age':
            const age = parseInt(value);
            if (age < 16 || age > 35) {
                isValid = false;
                errorMessage = 'Age must be between 16 and 35';
            }
            break;
        case 'skills':
            if (value.split(',').filter(s => s.trim()).length < 1) {
                isValid = false;
                errorMessage = 'Please enter at least one skill';
            }
            break;
        case 'interests':
            if (value.split(',').filter(i => i.trim()).length < 1) {
                isValid = false;
                errorMessage = 'Please enter at least one interest';
            }
            break;
    }

    if (isValid) {
        field.classList.add('success');
        removeErrorMessage(field);
    } else {
        field.classList.add('error');
        showErrorMessage(field, errorMessage);
    }

    return isValid;
}

function clearErrors(event) {
    const field = event.target;
    field.classList.remove('error');
    removeErrorMessage(field);
}

function showErrorMessage(field, message) {
    removeErrorMessage(field);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = "#ff6b6b";
    errorDiv.style.fontSize = "0.85rem";
    field.parentNode.appendChild(errorDiv);
}

function removeErrorMessage(field) {
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) existingError.remove();
}

function handleFormSubmission(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    const fields = form.querySelectorAll('.form-control[required]');
    let isFormValid = true;

    fields.forEach(field => {
        if (!validateField({ target: field })) {
            isFormValid = false;
        }
    });

    if (!isFormValid) {
        event.preventDefault();
        showFormError('Please fix the errors above before submitting.');
        return;
    }

    if (submitButton) {
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.innerHTML = `<span class="loading"></span> Processing...`;

        setTimeout(() => {
            if (submitButton.disabled) {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        }, 30000);
    }
}

function showFormError(message) {
    showToast(message, "error");
}

// ===============================
// TOAST NOTIFICATIONS
// ===============================
function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;

    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.padding = "12px 18px";
    toast.style.borderRadius = "10px";
    toast.style.fontWeight = "600";
    toast.style.color = "#fff";
    toast.style.zIndex = "2000";
    toast.style.opacity = "0";
    toast.style.transition = "all 0.3s ease";

    if (type === "error") {
        toast.style.background = "linear-gradient(135deg, #ff6b6b, #ff8e8e)";
    } else if (type === "success") {
        toast.style.background = "linear-gradient(135deg, #4ecdc4, #2ecc71)";
    } else {
        toast.style.background = "linear-gradient(135deg, #667eea, #764ba2)";
    }

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(-10px)";
    }, 10);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(0)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ===============================
// ANIMATIONS, UI ENHANCEMENTS, ETC
// (kept as in your version)
// ===============================
function initializeAnimations() {
    const observer = new IntersectionObserver(handleIntersection, { threshold: 0.1 });
    document.querySelectorAll('.card, .feature-card, .recommendation-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(50px)';
        observer.observe(el);
    });
}
function handleIntersection(entries, observer) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}
function initializeInteractiveElements() {
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', createRippleEffect);
        button.addEventListener('click', createClickEffect);
    });
}
function createRippleEffect(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.cssText = `
        position:absolute;width:${size}px;height:${size}px;
        left:${event.clientX - rect.left - size / 2}px;
        top:${event.clientY - rect.top - size / 2}px;
        background:radial-gradient(circle,rgba(255,255,255,0.6)0%,transparent70%);
        border-radius:50%;transform:scale(0);animation:ripple 0.6s linear;
    `;
    button.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
}
function createClickEffect(event) {
    const button = event.currentTarget;
    button.style.transform = 'scale(0.95)';
    setTimeout(() => { button.style.transform = ''; }, 150);
}
function initializeMobileOptimizations() {
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }
}
/* ============================
  Theme toggle + persistence
  Append to static/script.js
============================*/

(function(){
  const root = document.documentElement;
  const storageKey = 'pm_theme_pref';

  function applyTheme(theme){
    if(theme === 'dark'){
      root.setAttribute('data-theme','dark');
    } else {
      root.removeAttribute('data-theme');
    }
  }

  function getSaved() {
    return localStorage.getItem(storageKey) || null;
  }

  function save(theme) {
    localStorage.setItem(storageKey, theme);
  }

  // init
  const saved = getSaved();
  if(saved) applyTheme(saved);
  else {
    // auto-detect system pref
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
  }

  // expose toggle for header button
  window.toggleTheme = function(){
    const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    save(next);
  };
})();

