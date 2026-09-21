/**
 * StreakStorage
 * Handles saving and loading streak data to and from browser localStorage.
 */
class StreakStorage {
  /**
   * @param {string} [storageKey]
   */
  constructor(storageKey = 'streak_app_data_v1') {
    this.storageKey = storageKey;
  }

  /**
   * Checks if streak data exists in localStorage.
   * @returns {boolean}
   */
  hasSavedStreak() {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data !== null && data.trim() !== '';
    } catch (e) {
      console.warn('localStorage is not available:', e);
      return false;
    }
  }

  /**
   * Loads the saved Streak from localStorage.
   * If nothing is saved, returns null.
   * @returns {Streak|null}
   */
  load() {
    try {
      const raw = localStorage.getItem(this.storageKey);
      if (!raw) {
        return null;
      }
      const parsed = JSON.parse(raw);
      return Streak.fromJSON(parsed);
    } catch (e) {
      console.error('Failed to load streak from localStorage:', e);
      return null;
    }
  }

  /**
   * Saves a Streak instance to localStorage.
   * @param {Streak} streak
   * @returns {boolean}
   */
  save(streak) {
    try {
      if (!streak || typeof streak.toJSON !== 'function') {
        throw new Error('Invalid streak object provided to save()');
      }
      const serialized = JSON.stringify(streak.toJSON());
      localStorage.setItem(this.storageKey, serialized);
      return true;
    } catch (e) {
      console.error('Failed to save streak to localStorage:', e);
      return false;
    }
  }

  /**
   * Clears saved streak data from localStorage.
   * @returns {boolean}
   */
  clear() {
    try {
      localStorage.removeItem(this.storageKey);
      return true;
    } catch (e) {
      console.error('Failed to clear streak from localStorage:', e);
      return false;
    }
  }
}

if (typeof window !== 'undefined') {
  window.StreakStorage = StreakStorage;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = StreakStorage;
}

