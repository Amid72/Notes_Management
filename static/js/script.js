// Auto-dismiss flash alerts after 4 seconds
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".glass-alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.classList.remove("show");
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });
});
