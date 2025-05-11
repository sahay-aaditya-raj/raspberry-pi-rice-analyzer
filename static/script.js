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
    
    // Format broken rice percentages if available
    let brokenDetails = '';
    if (data.broken_percentages) {
      const bp = data.broken_percentages;
      brokenDetails = `
        <div class="broken-details">
          <div>25% broken: ${bp['25%'] || 0}</div>
          <div>50% broken: ${bp['50%'] || 0}</div>
          <div>75% broken: ${bp['75%'] || 0}</div>
        </div>
      `;
    }
    
    document.getElementById('resultsContent').innerHTML = `
      <div class="result-section">
        <div class="result-section-title">Summary</div>
        <div class="result-item">
          <strong>Total Grain Count:</strong>
          <span class="result-value">${data.total_objects || 0}</span>
        </div>
      </div>
      
      <div class="result-section">
        <div class="result-section-title">Rice Classification</div>
        <div class="result-item">
          <strong>Full Grains:</strong>
          <span class="result-value">${data.full_grain_count || 0}</span>
        </div>
        <div class="result-item">
          <strong>Broken Grains:</strong>
          <span class="result-value">${data.broken_grain_count || 0}</span>
        </div>
        ${brokenDetails}
        <div class="result-item">
          <strong>Chalky Grains:</strong>
          <span class="result-value">${data.chalky_count || 0}</span>
        </div>
        <div class="result-item">
          <strong>Black Grains:</strong>
          <span class="result-value">${data.black_count || 0}</span>
        </div>
        <div class="result-item">
          <strong>Yellow Grains:</strong>
          <span class="result-value">${data.yellow_count || 0}</span>
        </div>
        <div class="result-item">
          <strong>Brown Grains:</strong>
          <span class="result-value">${data.brown_count || 0}</span>
        </div>
      </div>
      
      <div class="result-section">
        <div class="result-section-title">Impurities</div>
        <div class="result-item">
          <strong>Stones:</strong>
          <span class="result-value">${data.stone_count || 0}</span>
        </div>
        <div class="result-item">
          <strong>Husks:</strong>
          <span class="result-value">${data.husk_count || 0}</span>
        </div>
      </div>
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