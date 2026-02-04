// HTMX configuration
document.body.addEventListener("htmx:configRequest", function (event) {
    // Include CSRF token in HTMX requests
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrfToken) {
        event.detail.headers["X-CSRFToken"] = csrfToken.value;
    } else {
        // Fallback: read from cookie
        const cookie = document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="));
        if (cookie) {
            event.detail.headers["X-CSRFToken"] = cookie.split("=")[1];
        }
    }
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
