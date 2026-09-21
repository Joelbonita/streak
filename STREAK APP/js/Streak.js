/**
 * Streak
 * Represents the streak domain model, calendar calculations, and check-in rules.
 */
class Streak {
  /**
   * @param {Object} options
   * @param {string} [options.name]
   * @param {number} [options.currentStreak]
   * @param {number} [options.bestStreak]
   * @param {string|null} [options.startDate]
   * @param {string|null} [options.lastCheckInDate]
   * @param {string[]} [options.history]
   */
  constructor({
    name = '',
    currentStreak = 0,
    bestStreak = 0,
    startDate = null,
    lastCheckInDate = null,
    history = []
  } = {}) {
    this.name = name.trim();
    this.currentStreak = Number(currentStreak) || 0;
    this.bestStreak = Number(bestStreak) || 0;
    this.startDate = startDate;
    this.lastCheckInDate = lastCheckInDate;
    this.history = Array.isArray(history) ? [...new Set(history)] : [];
  }

  /**
   * Formats a Date object as a local calendar date string (YYYY-MM-DD).
   * @param {Date} [date]
   * @returns {string}
   */
  static formatDate(date = new Date()) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  /**
   * Parses a YYYY-MM-DD string into a local Date object at midnight.
   * @param {string} dateStr
   * @returns {Date}
   */
  static parseDate(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  /**
   * Calculates the number of calendar days between two YYYY-MM-DD date strings.
   * Positive if toStr is later than fromStr.
   * @param {string} fromStr
   * @param {string} toStr
   * @returns {number}
   */
  static daysBetween(fromStr, toStr) {
    const d1 = Streak.parseDate(fromStr);
    const d2 = Streak.parseDate(toStr);
    const msPerDay = 1000 * 60 * 60 * 24;
    return Math.round((d2 - d1) / msPerDay);
  }

  /**
   * Checks whether the user has already checked in on the specified calendar date.
   * @param {string} [todayStr]
   * @returns {boolean}
   */
  isCheckedInToday(todayStr = Streak.formatDate()) {
    return Boolean(this.lastCheckInDate && this.lastCheckInDate === todayStr);
  }

  /**
   * Returns the current active streak count for display.
   * If the user missed yesterday and hasn't checked in today, returns 0.
   * @param {string} [todayStr]
   * @returns {number}
   */
  getDisplayStreak(todayStr = Streak.formatDate()) {
    if (!this.lastCheckInDate) {
      return 0;
    }

    const diff = Streak.daysBetween(this.lastCheckInDate, todayStr);

    if (diff === 0) {
      // Checked in today
      return this.currentStreak;
    }

    if (diff === 1) {
      // Checked in yesterday; streak is intact awaiting today's check-in
      return this.currentStreak;
    }

    // More than 1 calendar day ago; streak has lapsed
    return 0;
  }

  /**
   * Records a check-in for the specified calendar date (defaults to today).
   * @param {string} [todayStr]
   * @returns {{ success: boolean, reason?: string }}
   */
  checkIn(todayStr = Streak.formatDate()) {
    // 1. Prevent duplicate check-in today
    if (this.isCheckedInToday(todayStr)) {
      return { success: false, reason: 'ALREADY_CHECKED_IN' };
    }

    // 2. Calculate consecutive streak
    if (!this.lastCheckInDate) {
      // First check-in ever
      this.currentStreak = 1;
      this.startDate = todayStr;
    } else {
      const diff = Streak.daysBetween(this.lastCheckInDate, todayStr);

      if (diff === 1) {
        // Consecutive calendar day
        this.currentStreak += 1;
      } else if (diff > 1) {
        // Missed one or more calendar days: reset streak to 1
        this.currentStreak = 1;
      } else if (diff <= 0) {
        // Trying to check in for a date equal to or earlier than last check-in
        return { success: false, reason: 'INVALID_DATE' };
      }
    }

    // 3. Update last check-in date
    this.lastCheckInDate = todayStr;

    // 4. Ensure start date is initialized
    if (!this.startDate) {
      this.startDate = todayStr;
    }

    // 5. Record to history
    if (!this.history.includes(todayStr)) {
      this.history.push(todayStr);
    }

    // 6. Update all-time best streak
    if (this.currentStreak > this.bestStreak) {
      this.bestStreak = this.currentStreak;
    }

    return { success: true, currentStreak: this.currentStreak };
  }

  /**
   * Renames the streak without affecting streak counts.
   * @param {string} newName
   * @returns {boolean}
   */
  rename(newName) {
    const trimmed = (newName || '').trim();
    if (!trimmed) {
      return false;
    }
    this.name = trimmed;
    return true;
  }

  /**
   * Returns current Monday-to-Sunday weekly status.
   * @param {string} [todayStr]
   * @returns {Array<{ dayLabel: string, dateStr: string, isCompleted: boolean, isToday: boolean, isFuture: boolean }>}
   */
  getWeeklyStatus(todayStr = Streak.formatDate()) {
    const today = Streak.parseDate(todayStr);
    // (day + 6) % 7 maps Sunday (0) to 6, Monday (1) to 0, Tuesday (2) to 1, etc.
    const dayIndex = (today.getDay() + 6) % 7;
    const monday = new Date(today.getFullYear(), today.getMonth(), today.getDate() - dayIndex);

    const labels = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    const week = [];

    for (let i = 0; i < 7; i++) {
      const dayDate = new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + i);
      const dateStr = Streak.formatDate(dayDate);
      const diffFromToday = Streak.daysBetween(todayStr, dateStr);
      const isToday = dateStr === todayStr;
      const isFuture = diffFromToday > 0;
      // Future days must never appear completed
      const isCompleted = !isFuture && this.history.includes(dateStr);

      week.push({
        dayLabel: labels[i],
        dateStr,
        isCompleted,
        isToday,
        isFuture
      });
    }

    return week;
  }

  /**
   * Serializes the streak object to plain JSON.
   * @returns {Object}
   */
  toJSON() {
    return {
      name: this.name,
      currentStreak: this.currentStreak,
      bestStreak: this.bestStreak,
      startDate: this.startDate,
      lastCheckInDate: this.lastCheckInDate,
      history: this.history
    };
  }

  /**
   * Hydrates a Streak instance from JSON data.
   * @param {Object} data
   * @returns {Streak}
   */
  static fromJSON(data) {
    if (!data || typeof data !== 'object') {
      return new Streak();
    }
    return new Streak({
      name: data.name || '',
      currentStreak: data.currentStreak || 0,
      bestStreak: data.bestStreak || 0,
      startDate: data.startDate || null,
      lastCheckInDate: data.lastCheckInDate || null,
      history: Array.isArray(data.history) ? data.history : []
    });
  }
}

if (typeof window !== 'undefined') {
  window.Streak = Streak;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Streak;
}

