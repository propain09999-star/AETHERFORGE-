 triggerAbyss() {
  const statusEl = document.getElementById('status');
  const log = document.getElementById('abyss-log');
  const logContent = document.getElementById('log-content');

  // 1. Initiate Biometric Challenge
  statusEl.innerHTML = "● AUTHENTICATING ARCHITECT...";
  
  try {
    // Check if biometric hardware is available
    const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    if (!available) throw new Error("Secure Hardware Not Found");

    // The 'Challenge' - in a real app, this comes from your O2O server
    const challenge = new Uint8Array(32); 
    window.crypto.getRandomValues(challenge);

    // Trigger Native Biometric Prompt
    const credential = await navigator.credentials.get({
      publicKey: {
        challenge,
        rpId: window.location.hostname || "localhost",
        userVerification: "required" // Forces Biometric (Fingerprint/Face)
      }
    });

    if (credential) {
      // 2. Authorization Granted
      statusEl.innerHTML = "● ARCHITECT VERIFIED • ACCESS GRANTED";
      log.classList.add('active');
      logContent.innerHTML += `<br>> [${new Date().toLocaleTimeString()}] Biometric Handshake Successful.`;
      logContent.innerHTML += `<br>> Executing Burst: "${document.getElementById('cmdInput').value}"...`;
    }
  } catch (err) {
    // 3. Authorization Denied
    console.error(err);
    statusEl.innerHTML = "● ACCESS DENIED • INTRUDER DETECTED";
    statusEl.style.color = "#ff4d4d"; // Crimson Alert
    alert("Biometric verification failed. Burst aborted.");
  }
}
