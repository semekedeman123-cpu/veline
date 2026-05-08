document.addEventListener("DOMContentLoaded", () => {
  const revealItems = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.14 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add("is-visible"));
  }

  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const input = document.getElementById(button.dataset.copyTarget);
      if (!input) return;
      try {
        await navigator.clipboard.writeText(input.value);
        const original = button.textContent;
        button.textContent = "Copied";
        setTimeout(() => {
          button.textContent = original;
        }, 1800);
      } catch (_error) {
        input.select();
      }
    });
  });

  const previewMap = {
    id_full_name: '[data-preview-text="full_name"]',
    id_position_title: '[data-preview-text="position_title"]',
    id_business_name: '[data-preview-text="business_name"]',
    id_bio: '[data-preview-text="bio"]',
  };

  Object.entries(previewMap).forEach(([fieldId, selector]) => {
    const input = document.getElementById(fieldId);
    const target = document.querySelector(selector);
    if (!input || !target) return;
    input.addEventListener("input", () => {
      target.textContent = input.value || target.dataset.fallback || "";
    });
  });

  document.querySelectorAll(".file-input").forEach((input) => {
    input.addEventListener("change", () => {
      const nameTarget = input.closest(".upload-shell")?.querySelector("[data-file-name]");
      if (!nameTarget) return;
      const fileName = input.files?.[0]?.name || "No file chosen";
      nameTarget.textContent = fileName;
    });
  });

  const cascades = document.querySelectorAll("[data-cascade]");
  if (cascades.length) {
    const updateCascade = () => {
      const viewportHeight = window.innerHeight || 1;
      cascades.forEach((section) => {
        const rect = section.getBoundingClientRect();
        const progress = Math.min(Math.max((-rect.top) / (viewportHeight * 0.9), 0), 1);
        const opacity = 1 - progress * 0.28;
        const translateY = progress * -36;
        section.style.opacity = opacity.toFixed(3);
        section.style.transform = `translateY(${translateY}px)`;
      });
    };

    updateCascade();
    window.addEventListener("scroll", updateCascade, { passive: true });
    window.addEventListener("resize", updateCascade);
  }
});
