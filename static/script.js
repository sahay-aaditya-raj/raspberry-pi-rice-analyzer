// script.js

function captureImage() {
    fetch("/capture", { method: "POST" })
      .then(response => response.json())
      .then(data => {
        if (data.image_url) {
          document.getElementById('displayImage').src = data.image_url + "?t=" + new Date().getTime();
          document.getElementById('retakeButton').classList.remove('d-none');
        }
      })
      .catch(error => console.error("Capture failed:", error));
  }
  
  function retakeImage() {
    document.getElementById('displayImage').src = "/video_feed";
    document.getElementById('retakeButton').classList.add('d-none');
    document.getElementById('resultsContent').innerHTML = `
      <div class="empty-state">
        <i class="fas fa-clipboard-list"></i>
        <p>No results available yet.</p>
      </div>
    `;
  }
  
  function analyzeSelection() {
    const overlay = document.getElementById('loadingOverlay');
    const analyzeBtn = document.getElementById('analyzeBtn');
  
    overlay.style.display = 'flex';
    analyzeBtn.disabled = true;
  
    let displayedImage = document.getElementById('displayImage').src;
    let imagePath = new URL(displayedImage, window.location.origin).pathname;
  
    fetch("/process_image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_path: imagePath })
    })
    .then(response => response.json())
    .then(data => {
      if (data.processed_image_url) {
        document.getElementById('displayImage').src = data.processed_image_url + "?t=" + new Date().getTime();
      }
      document.getElementById('resultsContent').innerHTML = `
        <div><strong>Total:</strong> ${data.total_objects}</div>
        <div><strong>Full Rice:</strong> ${data.full_grain_count}</div>
        <div><strong>Broken Rice:</strong> ${data.broken_grain_count}</div>
        <div><strong>Stone:</strong> ${data.stone_count}</div>
        <div><strong>Husk:</strong> ${data.husk_count}</div>
      `;
    })
    .catch(error => {
      console.error("Error processing image:", error);
      document.getElementById('resultsContent').innerHTML = "<p class='text-danger'>Error processing image</p>";
    })
    .finally(() => {
      overlay.style.display = 'none';
      analyzeBtn.disabled = false;
    });
  }
  