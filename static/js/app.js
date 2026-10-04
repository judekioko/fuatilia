// Small progressive enhancements. Everything works without JavaScript.
document.addEventListener("click", (event) => {
  const printButton = event.target.closest("[data-print]");
  if (printButton) {
    event.preventDefault();
    window.print();
    return;
  }

  const copyButton = event.target.closest("[data-copy]");
  if (copyButton) {
    event.preventDefault();
    const source = document.querySelector(copyButton.dataset.copy);
    const text = source ? (source.value ?? source.textContent) : "";
    navigator.clipboard.writeText(text).then(() => {
      const original = copyButton.textContent;
      copyButton.textContent = "Copied";
      setTimeout(() => (copyButton.textContent = original), 1600);
    });
    return;
  }

  const confirmButton = event.target.closest("[data-confirm]");
  if (confirmButton && !window.confirm(confirmButton.dataset.confirm)) {
    event.preventDefault();
  }
});

// Email the current letter: opens the user's own mail app with the letter filled in.
document.addEventListener("click", (event) => {
  const mail = event.target.closest("[data-mailto]");
  if (!mail) return;
  event.preventDefault();
  const to = document.querySelector("#id_recipient")?.value || "";
  const subject = document.querySelector("#id_subject")?.value || "";
  const body = document.querySelector("#id_body")?.value || "";
  const address = (to.match(/<([^>]+)>/) || [null, to.includes("@") ? to : ""])[1];
  window.location.href = `mailto:${encodeURIComponent(address)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
});
