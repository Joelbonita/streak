/**
 * StreakApp
 * Coordinates UI interactions, DOM events, and data synchronization.
 */
class StreakApp {
  constructor() {
    this.storage = new StreakStorage();
    this.streak = null;

    // Cache DOM Elements
    this.dom = {
      streakCount: document.getElementById('streakCount'),
      streakNameBtn: document.getElementById('streakNameBtn'),
      streakNameText: document.getElementById('streakNameText'),
      streakMessage: document.getElementById('streakMessage'),
      checkInBtn: document.getElementById('checkInBtn'),
      checkInBtnText: document.getElementById('checkInBtnText'),
      weeklyGrid: document.getElementById('weeklyGrid'),
      bestStreakVal: document.getElementById('bestStreakVal'),
      startedDateVal: document.getElementById('startedDateVal'),
      editModal: document.getElementById('editModal'),
      modalTitle: document.getElementById('modalTitle'),
      streakForm: document.getElementById('streakForm'),
      streakInput: document.getElementById('streakInput'),
      modalError: document.getElementById('modalError'),
      modalCancelBtn: document.getElementById('modalCancelBtn'),
      modalSaveBtn: document.getElementById('modalSaveBtn')
    };

    this.init();
  }

  /**
   * Initializes the application state, binds listeners, and renders the UI.
   */
  init() {
    // 1. Load existing streak or initialize new
    const saved = this.storage.load();
    if (saved && saved.name) {
      this.streak = saved;
    } else {
      // First-time setup: prompt user to configure their streak
      this.streak = new Streak({ name: '' });
    }

    // 2. Bind all UI event listeners
    this.bindEvents();

    // 3. Render current state
    this.render();

    // 4. Auto-open modal on first launch if no streak name is configured
    if (!this.streak.name) {
      this.openModal(true);
    } else if (window.location.hash === '#open-modal') {
      this.openModal(false);
    }
  }


  /**
   * Registers DOM event handlers.
   */
  bindEvents() {
    // Check-in button click
    this.dom.checkInBtn.addEventListener('click', () => this.handleCheckIn());

    // Streak name edit click
    this.dom.streakNameBtn.addEventListener('click', () => this.openModal(false));

    // Modal form submission
    this.dom.streakForm.addEventListener('submit', (e) => this.handleModalSubmit(e));

    // Modal cancel button
    this.dom.modalCancelBtn.addEventListener('click', () => this.closeModal());

    // Close modal on backdrop click (if streak name already set)
    this.dom.editModal.addEventListener('click', (e) => {
      if (e.target === this.dom.editModal && this.streak.name) {
        this.closeModal();
      }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isModalOpen() && this.streak.name) {
        this.closeModal();
      }
    });

    // Clear validation error while user types
    this.dom.streakInput.addEventListener('input', () => {
      this.clearModalError();
    });
  }

  /**
   * Handles daily check-in action.
   */
  handleCheckIn() {
    if (this.streak.isCheckedInToday()) {
      return;
    }

    const result = this.streak.checkIn();
    if (!result.success) {
      return;
    }

    // Persist updated streak
    this.storage.save(this.streak);

    // Subtle pulse animation on streak number
    this.dom.streakCount.classList.add('pulse');
    setTimeout(() => {
      this.dom.streakCount.classList.remove('pulse');
    }, 240);

    // Re-render UI
    this.render();
  }

  /**
   * Formats an ISO date string (YYYY-MM-DD) into user-friendly short format (e.g. "Sep 10").
   * @param {string|null} dateStr
   * @returns {string}
   */
  formatDisplayDate(dateStr) {
    if (!dateStr) return '—';
    try {
      const [year, month, day] = dateStr.split('-').map(Number);
      const date = new Date(year, month - 1, day);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  }

  /**
   * Renders all visual components based on current Streak model state.
   */
  render() {
    // 1. Current Streak Count
    const displayStreak = this.streak.getDisplayStreak();
    this.dom.streakCount.textContent = displayStreak;

    // 2. Streak Name
    this.dom.streakNameText.textContent = this.streak.name || 'NEW STREAK';

    // 3. Check-In Button State
    const isChecked = this.streak.isCheckedInToday();
    if (isChecked) {
      this.dom.checkInBtn.disabled = true;
      this.dom.checkInBtn.classList.add('checked-in');
      this.dom.checkInBtn.innerHTML = `
        <svg class="btn-check-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Checked In</span>
      `;
      this.dom.checkInBtn.setAttribute('aria-label', 'Already checked in for today');
      this.dom.streakMessage.textContent = "You're all set for today!";
    } else {
      this.dom.checkInBtn.disabled = false;
      this.dom.checkInBtn.classList.remove('checked-in');
      this.dom.checkInBtn.innerHTML = `<span>Check In</span>`;
      this.dom.checkInBtn.setAttribute('aria-label', 'Check in for today');

      if (displayStreak === 0) {
        this.dom.streakMessage.textContent = 'Check in to start your streak.';
      } else {
        this.dom.streakMessage.textContent = 'Keep going.';
      }
    }

    // 4. Weekly Activity Tracker
    this.renderWeeklyActivity();

    // 5. Statistics Footer
    const bestDays = this.streak.bestStreak;
    this.dom.bestStreakVal.textContent = `${bestDays} ${bestDays === 1 ? 'day' : 'days'}`;
    this.dom.startedDateVal.textContent = this.formatDisplayDate(this.streak.startDate);
  }

  /**
   * Renders the 7-day Monday–Sunday activity dots.
   */
  renderWeeklyActivity() {
    const days = this.streak.getWeeklyStatus();
    this.dom.weeklyGrid.innerHTML = '';

    days.forEach((day) => {
      const col = document.createElement('div');
      col.className = 'weekly-day';
      col.setAttribute('role', 'listitem');

      const label = document.createElement('span');
      label.className = `weekly-day-label ${day.isToday ? 'is-today' : ''}`;
      label.textContent = day.dayLabel;

      const dot = document.createElement('span');
      dot.className = 'weekly-dot';

      let accessibilityStatus = 'Incomplete';
      if (day.isCompleted) {
        dot.classList.add('completed');
        accessibilityStatus = 'Completed';
      } else if (day.isFuture) {
        dot.classList.add('future');
        accessibilityStatus = 'Future';
      } else if (day.isToday) {
        dot.classList.add('today-pending');
        accessibilityStatus = 'Today pending check-in';
      } else {
        dot.classList.add('incomplete');
        accessibilityStatus = 'Missed';
      }

      dot.setAttribute('aria-label', `${day.dayLabel} (${day.dateStr}): ${accessibilityStatus}`);

      col.appendChild(label);
      col.appendChild(dot);
      this.dom.weeklyGrid.appendChild(col);
    });
  }

  /**
   * Opens the streak edit or initial setup modal.
   * @param {boolean} isInitialSetup
   */
  openModal(isInitialSetup = false) {
    this.dom.modalTitle.textContent = isInitialSetup
      ? 'What are you streaking?'
      : 'Edit Streak Name';

    this.dom.streakInput.value = this.streak.name || '';
    this.clearModalError();

    // Hide cancel button if no streak exists yet (first setup)
    if (isInitialSetup || !this.streak.name) {
      this.dom.modalCancelBtn.style.display = 'none';
    } else {
      this.dom.modalCancelBtn.style.display = 'inline-block';
    }

    this.dom.editModal.classList.add('is-open');
    this.dom.editModal.setAttribute('aria-hidden', 'false');

    // Auto-focus input
    setTimeout(() => {
      this.dom.streakInput.focus();
      this.dom.streakInput.select();
    }, 50);
  }

  /**
   * Closes the streak modal.
   */
  closeModal() {
    this.dom.editModal.classList.remove('is-open');
    this.dom.editModal.setAttribute('aria-hidden', 'true');
    this.clearModalError();
  }

  /**
   * Returns whether the modal is currently visible.
   * @returns {boolean}
   */
  isModalOpen() {
    return this.dom.editModal.classList.contains('is-open');
  }

  /**
   * Handles modal form submission with validation.
   * @param {Event} e
   */
  handleModalSubmit(e) {
    e.preventDefault();
    const enteredName = this.dom.streakInput.value.trim();

    // Validation: Empty streak name must not be accepted
    if (!enteredName) {
      this.showModalError('Please enter a streak name.');
      this.dom.streakInput.focus();
      return;
    }

    // Rename and persist
    this.streak.rename(enteredName);
    this.storage.save(this.streak);

    this.closeModal();
    this.render();
  }

  /**
   * Displays an error message inside the modal.
   * @param {string} msg
   */
  showModalError(msg) {
    this.dom.modalError.textContent = msg;
    this.dom.modalError.classList.add('visible');
    this.dom.streakInput.classList.add('has-error');
  }

  /**
   * Clears any modal error messages.
   */
  clearModalError() {
    this.dom.modalError.textContent = '';
    this.dom.modalError.classList.remove('visible');
    this.dom.streakInput.classList.remove('has-error');
  }
}

if (typeof window !== 'undefined') {
  window.StreakApp = StreakApp;
}

// Bootstrap application on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.app = new StreakApp();
  });
} else {
  window.app = new StreakApp();
}

