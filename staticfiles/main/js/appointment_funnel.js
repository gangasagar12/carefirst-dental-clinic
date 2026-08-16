/**
 * CareFirst Dental Clinic — Smart Appointment & Patient Conversion Funnel
 * Multi-Step Frontend Controller & Attribution Engine
 */

(function() {
  'use strict';

  // State
  let currentStep = 1;
  const totalSteps = 5;

  const funnelState = {
    treatmentSlug: '',
    treatmentTitle: 'General Dental Check-up',
    appointmentType: 'consultation',
    appointmentTypeLabel: 'Book a Consultation',
    preferredDate: '',
    preferredDateFormatted: '',
    preferredTime: 'morning',
    preferredTimeLabel: 'Morning (7:30 AM - 12:00 PM)',
    doctorId: '',
    doctorName: 'Any Available Specialist',
    fullName: '',
    phone: '',
    email: '',
    message: '',
    pricingOption: '',
    quantity: 1,
    estimatedAmount: '',
    // Attribution
    utmSource: '',
    utmMedium: '',
    utmCampaign: '',
    utmContent: '',
    utmTerm: '',
    landingPage: window.location.pathname + window.location.search,
    referrer: document.referrer || '',
    chatUsed: false,
    estimatorUsed: false,
    sessionId: localStorage.getItem('carefirst_chat_session') || ('cf-sess-' + Math.random().toString(36).substring(2, 12))
  };

  // Helper: Cookie getter
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Initialize UTM & Session Attribution
  function initAttribution() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // UTM parameters
    funnelState.utmSource = urlParams.get('utm_source') || sessionStorage.getItem('cf_utm_source') || '';
    funnelState.utmMedium = urlParams.get('utm_medium') || sessionStorage.getItem('cf_utm_medium') || '';
    funnelState.utmCampaign = urlParams.get('utm_campaign') || sessionStorage.getItem('cf_utm_campaign') || '';
    funnelState.utmContent = urlParams.get('utm_content') || sessionStorage.getItem('cf_utm_content') || '';
    funnelState.utmTerm = urlParams.get('utm_term') || sessionStorage.getItem('cf_utm_term') || '';

    // Cache UTM in session storage so attribution is preserved across navigation
    if (funnelState.utmSource) sessionStorage.setItem('cf_utm_source', funnelState.utmSource);
    if (funnelState.utmCampaign) sessionStorage.setItem('cf_utm_campaign', funnelState.utmCampaign);

    // Source context tags
    if (urlParams.get('source') === 'chatbot' || sessionStorage.getItem('cf_chat_used')) {
      funnelState.chatUsed = true;
    }
    if (urlParams.get('source') === 'estimator' || urlParams.get('est')) {
      funnelState.estimatorUsed = true;
      funnelState.pricingOption = urlParams.get('option') || '';
      funnelState.quantity = parseInt(urlParams.get('qty')) || 1;
      funnelState.estimatedAmount = urlParams.get('est') || '';
    }

    // Preselected Treatment Context from URL
    const treatmentParam = urlParams.get('treatment');
    if (treatmentParam) {
      funnelState.treatmentSlug = treatmentParam;
      const targetCard = document.querySelector(`.cf-treatment-card[data-slug="${treatmentParam}"]`);
      if (targetCard) {
        selectTreatmentCard(targetCard);
      }
    }

    // Preselected Doctor from URL
    const doctorParam = urlParams.get('doctor');
    if (doctorParam) {
      funnelState.doctorId = doctorParam;
      const docSelect = document.getElementById('cfDocSelect');
      if (docSelect) docSelect.value = doctorParam;
    }
  }

  // Send Event to Analytics API
  function trackEvent(eventType, metadata = {}) {
    try {
      fetch('/appointment/track-event/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
          session_id: funnelState.sessionId,
          event_type: eventType,
          treatment_slug: funnelState.treatmentSlug,
          source: funnelState.utmSource || (funnelState.chatUsed ? 'chatbot' : 'direct'),
          metadata: metadata
        })
      });
    } catch (e) {}
  }

  // Step Navigation
  function goToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > totalSteps) return;

    // Validate current step before progressing forward
    if (stepNumber > currentStep) {
      if (!validateStep(currentStep)) return;
    }

    currentStep = stepNumber;
    updateUI();
    window.scrollTo({ top: document.getElementById('cfFunnelCard').offsetTop - 30, behavior: 'smooth' });

    // Track step view
    const stepNames = ['STARTED', 'TYPE_SELECTED', 'DATE_SELECTED', 'DETAILS_STARTED', 'REVIEW_VIEWED'];
    trackEvent(stepNames[currentStep - 1] || 'STEP_' + currentStep);
  }

  // Validation
  function validateStep(step) {
    if (step === 1) {
      // Reason / Treatment: auto-defaults if not chosen
      if (!funnelState.treatmentSlug) {
        funnelState.treatmentSlug = 'general-consultation';
        funnelState.treatmentTitle = 'General Dental Consultation';
      }
      return true;
    }

    if (step === 2) {
      return true; // Appointment type is preselected
    }

    if (step === 3) {
      // Date & Time
      const dateInput = document.getElementById('cfPreferredDate');
      if (!dateInput || !dateInput.value) {
        alert('Please select your preferred appointment date.');
        if (dateInput) dateInput.focus();
        return false;
      }
      funnelState.preferredDate = dateInput.value;
      const d = new Date(dateInput.value);
      funnelState.preferredDateFormatted = isNaN(d) ? dateInput.value : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      return true;
    }

    if (step === 4) {
      // Patient Details
      const nameInput = document.getElementById('cfFullName');
      const phoneInput = document.getElementById('cfPhone');
      const emailInput = document.getElementById('cfEmail');
      const messageInput = document.getElementById('cfMessage');
      const docSelect = document.getElementById('cfDocSelect');

      const name = nameInput ? nameInput.value.trim() : '';
      const phone = phoneInput ? phoneInput.value.trim() : '';

      if (!name || name.length < 2) {
        alert('Please enter your full name.');
        if (nameInput) nameInput.focus();
        return false;
      }

      // Nepal phone validation (mobile 98/97/96 or standard 7-10 digits)
      const cleanPhone = phone.replace(/[\s\-\(\)\+]/g, '');
      if (!cleanPhone || cleanPhone.length < 7 || cleanPhone.length > 15 || isNaN(cleanPhone)) {
        alert('Please enter a valid contact phone number (e.g. 98XXXXXXXX).');
        if (phoneInput) phoneInput.focus();
        return false;
      }

      funnelState.fullName = name;
      funnelState.phone = phone;
      funnelState.email = emailInput ? emailInput.value.trim() : '';
      funnelState.message = messageInput ? messageInput.value.trim() : '';
      funnelState.doctorId = docSelect ? docSelect.value : '';
      if (docSelect && docSelect.selectedIndex > 0) {
        funnelState.doctorName = docSelect.options[docSelect.selectedIndex].text;
      } else {
        funnelState.doctorName = 'Any Available Specialist';
      }

      return true;
    }

    return true;
  }

  // Update DOM UI for active step
  function updateUI() {
    // 1. Update Stepper Header
    document.querySelectorAll('.cf-step-item').forEach((item, index) => {
      const stepIdx = index + 1;
      item.classList.remove('active', 'completed');
      if (stepIdx === currentStep) {
        item.classList.add('active');
      } else if (stepIdx < currentStep) {
        item.classList.add('completed');
      }
    });

    // 2. Switch Step Panes
    document.querySelectorAll('.cf-step-pane').forEach(pane => {
      pane.classList.remove('active');
    });
    const activePane = document.getElementById(`cfStep${currentStep}`);
    if (activePane) activePane.classList.add('active');

    // 3. Update Footer Buttons
    const backBtn = document.getElementById('cfBtnBack');
    const nextBtn = document.getElementById('cfBtnNext');

    if (backBtn) {
      backBtn.style.visibility = currentStep === 1 ? 'hidden' : 'visible';
    }

    if (nextBtn) {
      if (currentStep === totalSteps) {
        nextBtn.innerHTML = '<i class="bi bi-shield-check me-2"></i> Submit Appointment Request';
        nextBtn.classList.add('btn-submit');
      } else {
        nextBtn.innerHTML = 'Continue <i class="bi bi-arrow-right ms-2"></i>';
        nextBtn.classList.remove('btn-submit');
      }
    }

    // 4. Update Summary Review when reaching Step 5
    if (currentStep === 5) {
      renderReviewSummary();
    }
  }

  // Render Review Summary Screen (Step 5)
  function renderReviewSummary() {
    const revTreatment = document.getElementById('cfRevTreatment');
    const revType = document.getElementById('cfRevType');
    const revSchedule = document.getElementById('cfRevSchedule');
    const revDoctor = document.getElementById('cfRevDoctor');
    const revPatient = document.getElementById('cfRevPatient');
    const revEstimateRow = document.getElementById('cfRevEstimateRow');
    const revEstimate = document.getElementById('cfRevEstimate');

    if (revTreatment) revTreatment.textContent = funnelState.treatmentTitle;
    if (revType) revType.textContent = funnelState.appointmentTypeLabel;
    if (revSchedule) revSchedule.textContent = `${funnelState.preferredDateFormatted} • ${funnelState.preferredTimeLabel}`;
    if (revDoctor) revDoctor.textContent = funnelState.doctorName;
    if (revPatient) revPatient.textContent = `${funnelState.fullName} (${funnelState.phone})`;

    if (funnelState.estimatedAmount && revEstimateRow && revEstimate) {
      revEstimateRow.style.display = 'flex';
      revEstimate.textContent = `NPR ${funnelState.estimatedAmount} (${funnelState.quantity} teeth)`;
    } else if (revEstimateRow) {
      revEstimateRow.style.display = 'none';
    }
  }

  // Card Selection Handlers
  function selectTreatmentCard(card) {
    document.querySelectorAll('.cf-treatment-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    funnelState.treatmentSlug = card.getAttribute('data-slug') || '';
    funnelState.treatmentTitle = card.getAttribute('data-title') || card.querySelector('.cf-treatment-title').textContent.trim();
  }

  function selectTypeCard(card) {
    document.querySelectorAll('.cf-type-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    funnelState.appointmentType = card.getAttribute('data-type') || 'consultation';
    funnelState.appointmentTypeLabel = card.querySelector('.cf-type-title').textContent.trim();
  }

  function selectTimeCard(card) {
    document.querySelectorAll('.cf-time-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    funnelState.preferredTime = card.getAttribute('data-time') || 'morning';
    funnelState.preferredTimeLabel = card.querySelector('.cf-time-title').textContent.trim();
  }

  // Final AJAX Submission
  async function submitAppointment() {
    const nextBtn = document.getElementById('cfBtnNext');
    if (nextBtn) {
      nextBtn.disabled = true;
      nextBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Submitting Request...';
    }

    try {
      const response = await fetch('/appointment/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
          full_name: funnelState.fullName,
          phone: funnelState.phone,
          email: funnelState.email,
          treatment: funnelState.treatmentSlug,
          appointment_type: funnelState.appointmentType,
          preferred_date: funnelState.preferredDate,
          preferred_time: funnelState.preferredTime,
          doctor_id: funnelState.doctorId,
          message: funnelState.message,
          pricing_option: funnelState.pricingOption,
          quantity: funnelState.quantity,
          estimated_amount: funnelState.estimatedAmount,
          // Attribution
          utm_source: funnelState.utmSource,
          utm_medium: funnelState.utmMedium,
          utm_campaign: funnelState.utmCampaign,
          utm_content: funnelState.utmContent,
          utm_term: funnelState.utmTerm,
          landing_page: funnelState.landingPage,
          referrer: funnelState.referrer,
          chat_used: funnelState.chatUsed,
          estimator_used: funnelState.estimatorUsed,
          session_id: funnelState.sessionId
        })
      });

      const res = await response.json();

      if (res.success) {
        // Redirect to dedicated receipt confirmation page
        if (res.redirect_url) {
          window.location.href = res.redirect_url;
        } else {
          window.location.href = `/appointment/confirmation/${res.appointment_number}/`;
        }
      } else {
        alert(res.error || 'Could not submit your request. Please check details or call us directly.');
        if (nextBtn) {
          nextBtn.disabled = false;
          nextBtn.innerHTML = '<i class="bi bi-shield-check me-2"></i> Submit Appointment Request';
        }
      }
    } catch (err) {
      alert('A network error occurred. Please call +977 980-7464136 to book directly.');
      if (nextBtn) {
        nextBtn.disabled = false;
        nextBtn.innerHTML = '<i class="bi bi-shield-check me-2"></i> Submit Appointment Request';
      }
    }
  }

  // DOM Loaded Listener
  document.addEventListener('DOMContentLoaded', function() {
    initAttribution();

    // Treatment Card clicks
    document.querySelectorAll('.cf-treatment-card').forEach(card => {
      card.addEventListener('click', () => selectTreatmentCard(card));
    });

    // Appointment Type Card clicks
    document.querySelectorAll('.cf-type-card').forEach(card => {
      card.addEventListener('click', () => selectTypeCard(card));
    });

    // Time Card clicks
    document.querySelectorAll('.cf-time-card').forEach(card => {
      card.addEventListener('click', () => selectTimeCard(card));
    });

    // Stepper header jumps
    document.querySelectorAll('.cf-step-item').forEach((item, idx) => {
      item.addEventListener('click', () => {
        if (item.classList.contains('completed') || idx + 1 <= currentStep) {
          goToStep(idx + 1);
        }
      });
    });

    // Back / Next Buttons
    const backBtn = document.getElementById('cfBtnBack');
    const nextBtn = document.getElementById('cfBtnNext');

    if (backBtn) {
      backBtn.addEventListener('click', () => goToStep(currentStep - 1));
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (currentStep === totalSteps) {
          submitAppointment();
        } else {
          goToStep(currentStep + 1);
        }
      });
    }

    // Flatpickr Date picker initialization
    const dateInput = document.getElementById('cfPreferredDate');
    if (dateInput && typeof flatpickr !== 'undefined') {
      flatpickr(dateInput, {
        minDate: 'today',
        dateFormat: 'Y-m-d',
        altInput: true,
        altFormat: 'F j, Y (l)',
        defaultDate: new Date().fp_incr(1), // defaults to tomorrow
        onChange: function(selectedDates, dateStr) {
          funnelState.preferredDate = dateStr;
          if (selectedDates[0]) {
            funnelState.preferredDateFormatted = selectedDates[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
          }
        }
      });
    }

    // Track funnel launch
    trackEvent('STARTED');
  });

  // Global window hook for edit chips in Review Step
  window.cfGoToFunnelStep = function(step) {
    goToStep(step);
  };

})();
