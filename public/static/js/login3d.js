// Realistic 3D tilt effect for auth cards, following the mouse position
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".tilt-card");

  cards.forEach((card) => {
    const maxTilt = 10; // degrees

    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateY = ((x - centerX) / centerX) * maxTilt;
      const rotateX = -((y - centerY) / centerY) * maxTilt;

      card.style.transform = `perspective(1500px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(1500px) rotateX(0deg) rotateY(0deg) scale(1)";
    });
  });

  // Parallax movement for the floating 3D shapes based on cursor position
  const scene = document.querySelector(".auth-scene");
  const shapes = document.querySelectorAll(".floating-shapes .shape");

  if (scene && shapes.length) {
    scene.addEventListener("mousemove", (e) => {
      const { innerWidth, innerHeight } = window;
      const moveX = (e.clientX - innerWidth / 2) / 40;
      const moveY = (e.clientY - innerHeight / 2) / 40;

      shapes.forEach((shape, i) => {
        const depth = (i + 1) * 0.6;
        shape.style.marginLeft = `${moveX * depth}px`;
        shape.style.marginTop = `${moveY * depth}px`;
      });
    });
  }
});
