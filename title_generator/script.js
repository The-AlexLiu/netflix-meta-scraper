document.addEventListener("DOMContentLoaded", () => {
  // Parse URL parameters
  const urlParams = new URLSearchParams(window.location.search);

  const titleText = urlParams.get("title");
  const subtitleText = urlParams.get("date"); // 'date' param maps to subtitle

  // DOM Elements
  const titleElement = document.getElementById("main-title");
  const subtitleElement = document.getElementById("sub-title");

  // Update content if parameters exist
  if (titleText) {
    titleElement.textContent = titleText;
  }

  if (subtitleText) {
    subtitleElement.textContent = subtitleText;
  }

  // Optional: Log for debugging
  console.log(
    `Rendered with Title: "${titleElement.textContent}", Subtitle: "${subtitleElement.textContent}"`,
  );
});
