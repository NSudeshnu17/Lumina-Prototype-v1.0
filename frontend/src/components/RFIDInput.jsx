import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * Reusable RFID Input Component
 * - Displays current RFID Reader Mode
 * - Autofocuses input
 * - Accepts HID keyboard input (physical RFID reader) and manual entry
 * - Debounces duplicate scans within 2 seconds
 * - Submits on Enter
 */
export default function RFIDInput({ mode, label, onScan, disabled, placeholder }) {
  const [uid, setUid] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [lastScan, setLastScan] = useState({ uid: '', time: 0 });
  const inputRef = useRef(null);

  useEffect(() => {
    if (inputRef.current && !disabled) {
      inputRef.current.focus();
    }
  }, [mode, disabled]);

  const handleSubmit = useCallback(async (e) => {
    e && e.preventDefault();
    const trimmed = uid.trim();
    if (!trimmed) {
      setFeedback({ type: 'error', text: 'RFID UID cannot be empty.' });
      return;
    }

    // Debounce: ignore same UID within 2 seconds
    const now = Date.now();
    if (trimmed === lastScan.uid && now - lastScan.time < 2000) {
      setFeedback({ type: 'warning', text: 'Duplicate scan ignored (debounce).' });
      setUid('');
      return;
    }

    setLastScan({ uid: trimmed, time: now });
    setFeedback(null);

    try {
      const result = await onScan(trimmed);
      if (result && result.feedback) {
        setFeedback(result.feedback);
      }
    } catch (err) {
      setFeedback({ type: 'error', text: err.error || err.message || 'Scan failed.' });
    }

    setUid('');
    if (inputRef.current) inputRef.current.focus();
  }, [uid, onScan, lastScan]);

  const modeColors = {
    'EMPLOYEE_REGISTRATION': '#2563eb',
    'PRODUCT_REGISTRATION': '#7c3aed',
    'SALESPERSON_LOGIN': '#059669',
    'MANAGER_LOGIN': '#0891b2',
    'ITEM_HANDLING': '#d97706',
    'BILLING': '#dc2626',
    'TAG_REASSIGNMENT': '#9333ea',
  };

  return (
    <div className="rfid-input-container">
      <div className="rfid-mode-badge" style={{ borderColor: modeColors[mode] || '#6b7280' }}>
        <span className="rfid-mode-dot" style={{ background: modeColors[mode] || '#6b7280' }}></span>
        <span className="rfid-mode-label">RFID READER MODE</span>
        <span className="rfid-mode-value">{mode?.replace(/_/g, ' ') || 'IDLE'}</span>
      </div>
      <p className="rfid-hint">{label || 'Waiting for RFID scan...'}</p>
      <form onSubmit={handleSubmit} className="rfid-form">
        <input
          ref={inputRef}
          type="text"
          value={uid}
          onChange={(e) => setUid(e.target.value)}
          placeholder={placeholder || 'Scan or enter RFID UID...'}
          className="rfid-input"
          disabled={disabled}
          autoComplete="off"
        />
        <button type="submit" className="rfid-submit-btn" disabled={disabled}>
          Submit
        </button>
      </form>
      {feedback && (
        <div className={`rfid-feedback rfid-feedback-${feedback.type}`}>
          {feedback.text}
        </div>
      )}
    </div>
  );
}
