// Apply saved theme early and expose a toggle
(function(){
  var THEME_KEY = 'vpc_theme';
  var STYLE_KEY = 'vpc_style';
  var STYLE_ORDER = ['classic', 'aurora'];
  var STYLE_LABELS = { classic: 'Classic', aurora: 'Aurora' };
  function setCookie(name, value){
    try { document.cookie = name + '=' + value + '; path=/; max-age=31536000; SameSite=Lax'; } catch(e){}
  }
  function getCookie(name){
    try {
      var m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()\[\]\\\/\+^])/g,'\\$1') + '=([^;]*)'));
      return m ? decodeURIComponent(m[1]) : null;
    } catch(e){ return null; }
  }
  try {
    var params = new URLSearchParams(location.search);
    var qTheme = params.get('theme');
    if (qTheme === 'light' || qTheme === 'dark') {
      localStorage.setItem(THEME_KEY, qTheme);
    }
    var qStyle = params.get('style');
    if (qStyle && STYLE_ORDER.indexOf(qStyle) !== -1) {
      localStorage.setItem(STYLE_KEY, qStyle);
    }

    var savedTheme = localStorage.getItem(THEME_KEY) || getCookie('vpc_theme') || 'dark';
    var savedStyle = localStorage.getItem(STYLE_KEY) || getCookie(STYLE_KEY) || 'classic';

    applyTheme(savedTheme);
    applyStyle(savedStyle);

    // Set an immediate background to avoid flash on first paint
    document.documentElement.style.backgroundColor = savedTheme === 'dark' ? '#0e141b' : '#f7f9fc';
  } catch (e) {
    // default to dark
    document.documentElement.setAttribute('data-theme', 'dark');
    document.documentElement.setAttribute('data-style', 'classic');
  }

  function applyTheme(theme){
    var next = (theme === 'light' || theme === 'dark') ? theme : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    document.documentElement.style.backgroundColor = next === 'dark' ? '#0e141b' : '#f7f9fc';
    try { localStorage.setItem(THEME_KEY, next); } catch(e){}
    setCookie('vpc_theme', next);
    var el = document.querySelector('[data-theme-label]');
    if (el) el.textContent = next === 'dark' ? 'Dark' : 'Light';
  }

  function applyStyle(style){
    var cur = STYLE_ORDER.indexOf(style) === -1 ? 'classic' : style;
    document.documentElement.setAttribute('data-style', cur);
    try { localStorage.setItem(STYLE_KEY, cur); } catch(e){}
    setCookie(STYLE_KEY, cur);
    var label = document.querySelector('[data-style-label]');
    if (label) label.textContent = STYLE_LABELS[cur] || cur;
    document.querySelectorAll('[data-style-select]').forEach(function(el){
      if (el.tagName === 'SELECT') {
        el.value = cur;
      } else {
        el.setAttribute('data-style-current', cur);
      }
    });
  }

  window.toggleTheme = function(){
    var cur = document.documentElement.getAttribute('data-theme') || 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  };

  window.setStyleVariant = applyStyle;
  window.cycleStyleVariant = function(){
    var cur = document.documentElement.getAttribute('data-style') || 'classic';
    var idx = STYLE_ORDER.indexOf(cur);
    var next = STYLE_ORDER[(idx + 1) % STYLE_ORDER.length];
    applyStyle(next);
  };

  document.addEventListener('DOMContentLoaded', function(){
    // Attach change listeners for explicit style selectors
    document.querySelectorAll('[data-style-select]').forEach(function(el){
      if (el.tagName === 'SELECT') {
        el.addEventListener('change', function(){ applyStyle(el.value); });
      } else {
        el.addEventListener('click', function(){ window.cycleStyleVariant(); });
      }
    });

    // Auto-inject new integrated theme controls if no theme buttons exist
    if (!document.querySelector('.theme-toggle-btn') && !document.querySelector('.theme-fab')) {
      // Create container for theme controls
      var container = document.createElement('div');
      container.style.cssText = 'position:fixed;top:12px;right:12px;display:flex;gap:8px;z-index:1000;';
      
      // Create theme toggle button
      var themeBtn = document.createElement('button');
      themeBtn.type = 'button';
      themeBtn.className = 'theme-toggle-btn';
      themeBtn.setAttribute('title', 'Toggle theme');
      themeBtn.setAttribute('aria-label', 'Toggle theme');
      themeBtn.innerHTML = '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.364-7.364-1.414 1.414M8.05 16.95l-1.414 1.414m12.728 0-1.414-1.414M8.05 7.05 6.636 5.636"/></svg><span data-theme-label>Light</span>';
      themeBtn.addEventListener('click', function(){ window.toggleTheme(); });
      
      // Add theme button to container and container to page
      container.appendChild(themeBtn);
      document.body.appendChild(container);
    }
  });

  // Auto-dismiss flash messages and notifications
  function initAutoDissmissMessages() {
    // Handle flash messages
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
      var category = '';
      if (message.classList.contains('success')) category = 'success';
      else if (message.classList.contains('error')) category = 'error';
      else if (message.classList.contains('info')) category = 'info';
      
      var timeout = 5000; // Default 5 seconds
      
      // Different timeouts for different message types
      if (category === 'success') timeout = 4000; // Success messages: 4 seconds
      else if (category === 'error') timeout = 8000; // Error messages: 8 seconds (longer to read)
      else if (category === 'info') timeout = 6000; // Info messages: 6 seconds
      
      setTimeout(function() {
        dismissMessage(message);
      }, timeout);
    });
    
    // Handle other success banners (like "Form submitted!")
    var successBanners = document.querySelectorAll('#submitBanner, .ok, .alert-success');
    successBanners.forEach(function(banner) {
      if (banner.style.display !== 'none' && banner.offsetParent !== null) {
        setTimeout(function() {
          dismissMessage(banner);
        }, 3000); // 3 seconds for inline success banners
      }
    });
  }
  
  function dismissMessage(element) {
    if (!element) return;
    
    // Add fade-out class for smooth animation
    element.classList.add('fade-out');
    
    // Remove element after animation completes
    setTimeout(function() {
      if (element.parentNode) {
        element.parentNode.removeChild(element);
      }
    }, 300); // Match the CSS transition duration
  }
  
  // Initialize auto-dismiss when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAutoDissmissMessages);
  } else {
    initAutoDissmissMessages();
  }
  
  // Also initialize when new content is dynamically added
  window.initAutoDissmissMessages = initAutoDissmissMessages;
})();
