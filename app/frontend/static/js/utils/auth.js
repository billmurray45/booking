/**
 * Authentication Utilities
 * Manages JWT tokens and user authentication state
 */

// Token Management
function setTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

function isAuthenticated() {
    return !!getAccessToken();
}

// Update Navigation Based on Auth State
function updateNavbar() {
    const isAuth = isAuthenticated();

    const navRegister = document.getElementById('nav-register');
    const navLogin = document.getElementById('nav-login');
    const navBookings = document.getElementById('nav-bookings');
    const navProfile = document.getElementById('nav-profile');
    const navLogout = document.getElementById('nav-logout');

    if (isAuth) {
        if (navRegister) navRegister.style.display = 'none';
        if (navLogin) navLogin.style.display = 'none';
        if (navBookings) navBookings.style.display = 'block';
        if (navProfile) navProfile.style.display = 'block';
        if (navLogout) navLogout.style.display = 'block';
    } else {
        if (navRegister) navRegister.style.display = 'block';
        if (navLogin) navLogin.style.display = 'block';
        if (navBookings) navBookings.style.display = 'none';
        if (navProfile) navProfile.style.display = 'none';
        if (navLogout) navLogout.style.display = 'none';
    }
}

// Logout Function
async function logout() {
    const refreshToken = getRefreshToken();

    try {
        // Call logout API
        const response = await fetch('/api/v1/auth/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAccessToken()}`
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            clearTokens();
            window.location.href = '/';
        } else {
            // Even if API call fails, clear tokens and redirect
            clearTokens();
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Clear tokens anyway
        clearTokens();
        window.location.href = '/';
    }
}

// Redirect to login if not authenticated (for protected pages)
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login/';
    }
}

// Redirect to home if already authenticated (for login/register pages)
function redirectIfAuthenticated() {
    if (isAuthenticated()) {
        window.location.href = '/profile/';
    }
}
