const API_BASE_URL = 'http://127.0.0.1:8000/api/users/';

// HANDLE REGISTRATION
async function registerUser(userData) {
    try {
        console.log("Attempting to register:", userData.user_id);
        const response = await fetch(`${API_BASE_URL}register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        const result = await response.json();

        if (response.ok) {
            const successDiv = document.getElementById('successMessage');
            if (successDiv) {
                successDiv.style.display = 'block';
                successDiv.innerHTML = 'Registration successful! <a href="./login.html">Login here</a>';
            }
            // Redirect after 2 seconds
            setTimeout(() => { window.location.href = './login.html'; }, 2000);
        } else {
            alert("Error: " + (result.error || "Registration failed"));
        }
    } catch (error) {
        console.error("Registration error:", error);
        alert("Cannot connect to server. Is Django running?");
    }
}

// HANDLE LOGIN
async function loginUser(userData) {
    try {
        console.log("Attempting login for:", userData.user_id);
        const response = await fetch(`${API_BASE_URL}login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        const result = await response.json();

        if (response.ok) {
            console.log("Login successful! Saving session...");
            // Save user data to localStorage for dashboard use
            localStorage.setItem('user_id', result.user.user_id);
            localStorage.setItem('user_role', result.user.role);
            localStorage.setItem('user_name', result.user.name);

            // Role-Based Redirection (Authorization)
            if (result.user.role === 'Student') {
                console.log("Redirecting to Student Dashboard");
                window.location.href = './student_dashboard.html';
            } else if (result.user.role === 'Instructor') {
                console.log("Redirecting to Teacher Dashboard");
                window.location.href = './teacher_dashboard.html';
            } else if (result.user.role === 'Admin') {
                console.log("Redirecting to Admin Dashboard");
                window.location.href = './admin_dashboard.html';
            } else {
                console.warn("Unknown role detected:", result.user.role);
                alert("Account role not recognized. Contact support.");
            }
        } else {
            alert(result.error || "Login failed");
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("Server error. Is Django running?");
    }
}

// EVENT LISTENERS
document.addEventListener('DOMContentLoaded', () => {
    console.log("TrackIT Auth script initialized.");

    // Registration Form Listener
    const regForm = document.getElementById('registrationForm');
    if (regForm) {
        regForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // We pull the value from the hidden input field in register.html
            const roleValue = document.getElementById('role').value;

            registerUser({
                user_id: document.getElementById('userId').value,
                name: document.getElementById('name').value,
                role: roleValue, // This will be 'Student' based on our hidden input
                password: document.getElementById('password').value
            });
        });
    }

    // Login Form Listener
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            loginUser({
                user_id: document.getElementById('userId').value,
                password: document.getElementById('password').value
            });
        });
    }
});