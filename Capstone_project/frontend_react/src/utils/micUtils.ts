/**
 * Robust microphone activation for Web Speech API and getUserMedia, with diagnostics for iframe, sandbox, HTTPS, and permissions.
 */
export async function activateMicrophone(onAllowed: (stream: MediaStream|null) => void) {
  // 1. Check if in iframe and warn if allow="microphone" is missing
  if (window.self !== window.top) {
    console.warn('App is running inside an iframe. Ensure the iframe has allow="microphone" and proper sandbox attributes.');
  }
  // 2. Check protocol
  if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
    alert('Microphone access requires HTTPS or localhost.');
    onAllowed(null);
    return;
  }
  // 3. Check permission state if supported
  if (navigator.permissions && navigator.permissions.query) {
    try {
      const status = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      console.log('Mic permission status:', status.state);
      if (status.state === 'denied') {
        alert('Microphone access is blocked. Please allow it in your browser settings.');
        onAllowed(null);
        return;
      }
    } catch (e) {
      // Permissions API not available or failed, continue to request
    }
  }
  // 4. Request mic access (must be from user gesture)
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    onAllowed(stream);
  } catch (err: any) {
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      alert('Microphone access was denied. Please check your browser and OS settings.');
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      alert('No microphone was found. Please connect a microphone.');
    } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
      alert('Microphone is already in use by another application.');
    } else {
      alert('An unknown error occurred while accessing the microphone.');
    }
    console.error('Mic access denied:', err);
    onAllowed(null);
  }
}

/**
 * Requests microphone access with robust permission and context checks.
 * Must be called from a user gesture (e.g., click handler).
 */
export async function requestMicrophoneAccess(): Promise<MediaStream|null> {
  // 1. Check if running inside an iframe and warn if allow="microphone" is missing
  if (window.self !== window.top) {
    console.warn('App is running inside an iframe. Ensure the iframe has allow="microphone" and proper sandbox attributes.');
  }
  // 2. Check protocol
  if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
    alert('Microphone access requires HTTPS or localhost.');
    return null;
  }
  // 3. Check permission state if supported
  if (navigator.permissions && navigator.permissions.query) {
    try {
      const status = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      console.log('Mic permission status:', status.state);
      if (status.state === 'denied') {
        alert('Microphone access is blocked. Please allow it in your browser settings.');
        return null;
      }
    } catch (e) {
      // Permissions API not available or failed, continue to request
    }
  }
  // 4. Request mic access (must be from user gesture)
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return stream;
  } catch (err: any) {
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      alert('Microphone access was denied. Please check your browser and OS settings.');
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      alert('No microphone was found. Please connect a microphone.');
    } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
      alert('Microphone is already in use by another application.');
    } else {
      alert('An unknown error occurred while accessing the microphone.');
    }
    console.error('Mic access denied:', err);
    return null;
  }
}

