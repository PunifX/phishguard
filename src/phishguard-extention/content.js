if (
  window.location.protocol !== "chrome:" &&
  window.location.protocol !== "chrome-extension:" &&
  !document.getElementById("phishguard-banner")
) {

  const RAILWAY_URL = "https://phishguard-production-fd3c.up.railway.app";

  const banner = document.createElement("div");
  banner.id = "phishguard-banner";
  banner.style.cssText = `
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 2147483647;
    padding: 10px 16px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    background: #1a1a2e;
    color: #a0a0b0;
    border-bottom: 2px solid #333;
  `;

  banner.innerHTML = `
    <span id="phishguard-text">🔍 PhishGuard is analyzing this page...</span>
    <button id="phishguard-close" style="
      background: none; border: none;
      color: #a0a0b0; font-size: 20px;
      cursor: pointer; padding: 0 4px; line-height: 1;
    ">×</button>
  `;

  document.body.prepend(banner);
  document.getElementById("phishguard-close").onclick = () => banner.remove();

  fetch(`${RAILWAY_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: window.location.href })
  })
  .then(res => res.json())
  .then(data => {
    const prediction  = data.models.random_forest.prediction;
    const confidence  = data.models.random_forest.confidence;
    const isPhishing  = prediction === "phishing";
    const topReason   = data.reasons[0];
    const text        = document.getElementById("phishguard-text");

    if (isPhishing) {
      banner.style.background   = "#2d0a0a";
      banner.style.borderBottom = "2px solid #ff4444";
      banner.style.color        = "#ff4444";
      text.innerHTML = `
        ⚠️ <strong>Phishing Detected</strong> — ${confidence}% confidence
        &nbsp;|&nbsp;
        <span style="color:#ff8080; font-weight:normal">${topReason}</span>
      `;
    } else {
      banner.style.background   = "#0a2d0a";
      banner.style.borderBottom = "2px solid #00cc66";
      banner.style.color        = "#00cc66";
      text.innerHTML = `
        🛡️ <strong>Safe</strong> — ${confidence}% confidence
        &nbsp;|&nbsp;
        <span style="color:#80ffb0; font-weight:normal">No suspicious patterns detected</span>
      `;
    }
  })
  .catch((err) => {
  const text = document.getElementById("phishguard-text");
  if (text) {
    banner.style.borderBottom = "2px solid #ffaa00";
    text.innerHTML = "⚠️ PhishGuard could not reach the server";
  }
    });

}