/**
 * Format a duration in seconds to a human-readable string.
 * @param {number} seconds
 * @returns {string} e.g. "1h 2m 3s" or "5m 30s"
 */
export function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '—';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

/**
 * Format an ISO 8601 date string to a readable date.
 * @param {string} isoString
 * @returns {string} e.g. "Oct 11, 2026"
 */
export function formatDate(isoString) {
  if (!isoString) return '—';
  try {
    return new Date(isoString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return '—';
  }
}

/**
 * Format a relative time string.
 * @param {string} isoString
 * @returns {string} e.g. "2 hours ago"
 */
export function formatRelativeTime(isoString) {
  if (!isoString) return '';
  const diff = Date.now() - new Date(isoString).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'Just now';
}

/**
 * Format a progress percentage.
 * @param {number} percent 0-100
 * @returns {string}
 */
export function formatProgress(percent) {
  if (percent === null || percent === undefined) return '0%';
  return `${Math.round(Math.min(100, Math.max(0, percent)))}%`;
}

/**
 * Truncate a string to maxLen with ellipsis.
 * @param {string} str
 * @param {number} maxLen
 * @returns {string}
 */
export function truncate(str, maxLen = 100) {
  if (!str) return '';
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + '...';
}

/**
 * Format seconds as MM:SS for video display.
 * @param {number} seconds
 * @returns {string}
 */
export function formatVideoTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
