/* Copyright (c) 2026 Daniel Ari Friedman */
(() => {
  "use strict";
  const panels = [...document.querySelectorAll(".panel")];
  const tabs = [...document.querySelectorAll(".views a")];
  const form = document.getElementById("filters");
  try {
    const query = document.getElementById("query");
    const plane = document.getElementById("plane");
    const role = document.getElementById("role");
    const count = document.getElementById("result-count");
    const empty = document.getElementById("empty");
    const rows = [...document.querySelectorAll("#coverage-rows tr")];
    const appearance = document.getElementById("appearance");
    const media = matchMedia("(prefers-color-scheme: dark)");
    let composing = false;
    let timer;
    const apply = () => {
      clearTimeout(timer);
      const needle = query.value.trim().toLocaleLowerCase();
      let shown = 0;
      rows.forEach(row => {
        const visible = row.dataset.query.toLocaleLowerCase().includes(needle) && (!plane.value || row.dataset.plane === plane.value) && (!role.value || row.dataset.role === role.value);
        row.hidden = !visible;
        if (visible) shown += 1;
      });
      empty.hidden = shown !== 0;
      timer = setTimeout(() => { count.textContent = shown + " of " + rows.length + " saved aggregate cells shown."; }, 200);
    };
    const activate = index => {
      tabs.forEach((tab, i) => { tab.setAttribute("aria-selected", String(i === index)); tab.tabIndex = i === index ? 0 : -1; panels[i].hidden = i !== index; });
    };
    const theme = () => { document.documentElement.dataset.theme = appearance.value === "system" ? (media.matches ? "dark" : "light") : appearance.value; };
    query.addEventListener("compositionstart", () => { composing = true; });
    query.addEventListener("compositionend", () => { composing = false; apply(); });
    query.addEventListener("input", () => { if (!composing) apply(); });
    plane.addEventListener("change", apply);
    role.addEventListener("change", apply);
    form.addEventListener("submit", event => event.preventDefault());
    document.getElementById("clear").addEventListener("click", () => { query.value = ""; apply(); query.focus(); });
    document.getElementById("reset").addEventListener("click", event => { query.value = ""; plane.value = ""; role.value = ""; apply(); event.currentTarget.focus(); });
    tabs.forEach((tab, index) => {
      tab.addEventListener("click", event => { event.preventDefault(); activate(index); });
      tab.addEventListener("keydown", event => {
        let next;
        if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
        if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); tabs[next].focus(); }
        if (event.key === " " || event.key === "Enter") { event.preventDefault(); activate(index); }
      });
    });
    appearance.addEventListener("change", theme);
    media.addEventListener("change", theme);
    tabs[0].parentElement.setAttribute("role", "tablist");
    tabs.forEach((tab, i) => { tab.setAttribute("role", "tab"); tab.setAttribute("aria-controls", panels[i].id); panels[i].setAttribute("role", "tabpanel"); panels[i].tabIndex = 0; });
    const initial = panels.findIndex(panel => "#" + panel.id === location.hash);
    activate(initial < 0 ? 0 : initial);
    form.hidden = false;
    appearance.parentElement.hidden = false;
    theme();
    apply();
  } catch (error) {
    panels.forEach(panel => { panel.hidden = false; panel.removeAttribute("role"); });
    tabs[0].parentElement.removeAttribute("role");
    tabs.forEach(tab => { tab.removeAttribute("role"); tab.removeAttribute("aria-selected"); tab.removeAttribute("aria-controls"); tab.tabIndex = 0; tab.replaceWith(tab.cloneNode(true)); });
    document.querySelectorAll("#coverage-rows tr").forEach(row => { row.hidden = false; });
    document.querySelector(".appearance").hidden = true;
    form.hidden = true;
    document.getElementById("enhancement-error").hidden = false;
    console.error("Workbench enhancement failed", error);
  }
})();
