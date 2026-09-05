// Confetti burst on the welcome banner when the dashboard loads
document.addEventListener("DOMContentLoaded", () => {
  const layer = document.getElementById("confettiLayer");
  if (layer) {
    const colors = ["#6c5ce7", "#00d2ff", "#ff6b9d", "#ffffff", "#4834d4"];
    for (let i = 0; i < 40; i++) {
      const piece = document.createElement("span");
      piece.className = "confetti-piece";
      piece.style.left = Math.random() * 100 + "%";
      piece.style.background = colors[Math.floor(Math.random() * colors.length)];
      piece.style.animationDuration = 1.5 + Math.random() * 1.5 + "s";
      piece.style.animationDelay = Math.random() * 0.6 + "s";
      piece.style.borderRadius = Math.random() > 0.5 ? "50%" : "2px";
      layer.appendChild(piece);
    }
    // Clean up confetti after the animation finishes
    setTimeout(() => { layer.innerHTML = ""; }, 4000);
  }

  // Subtle 3D tilt for note cards, following the mouse
  const cards = document.querySelectorAll(".note-card-inner");
  cards.forEach((card) => {
    const maxTilt = 8;
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const rotateY = ((x - rect.width / 2) / (rect.width / 2)) * maxTilt;
      const rotateX = -((y - rect.height / 2) / (rect.height / 2)) * maxTilt;
      card.style.transform = `translateY(-10px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });
});
