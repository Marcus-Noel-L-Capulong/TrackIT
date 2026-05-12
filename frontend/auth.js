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
            // Relative path for redirect
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
            localStorage.setItem('user_id', result.user.user_id);
            localStorage.setItem('user_role', result.user.role);
            localStorage.setItem('user_name', result.user.name);

            // OPTION B: RELATIVE PATHS
            if (result.user.role === 'Student') {
                console.log("Redirecting to Student Dashboard");
                window.location.href = './student_dashboard.html';
            } else {
                console.log("Redirecting to Teacher Dashboard");
                window.location.href = './teacher_dashboard.html';
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

    const regForm = document.getElementById('registrationForm');
    if (regForm) {
        regForm.addEventListener('submit', (e) => {
            e.preventDefault();
            registerUser({
                user_id: document.getElementById('userId').value,
                name: document.getElementById('name').value,
                role: document.getElementById('role').value,
                password: document.getElementById('password').value
            });
        });
    }

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