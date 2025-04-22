/**
 * Jimo Travel Landing Page
 * 
 * Features:
 * - Multi-language switching (JP, zh-TW, zh-CN, ko, en)
 * - Lazy image loading
 * - Simple slider for testimonials
 */
(function() {
  'use strict';
  
  const languageSelect = document.getElementById('language-select');
  const storiesSlider = document.getElementById('stories-slider');
  const storyCards = storiesSlider ? Array.from(storiesSlider.querySelectorAll('.story-card')) : [];
  const prevButton = document.querySelector('.stories__control--prev');
  const nextButton = document.querySelector('.stories__control--next');
  const indicators = Array.from(document.querySelectorAll('.stories__indicator'));
  
  let currentLanguage = 'jp';
  let currentSlide = 0;
  let translations = {};
  let isSliderAnimating = false;
  
  /**
   * Initialize the application
   */
  function init() {
    loadLanguage(currentLanguage);
    
    setupEventListeners();
    
    if (storyCards.length > 0) {
      updateSlider();
    }
    
    setupLazyLoading();
  }
  
  /**
   * Set up event listeners
   */
  function setupEventListeners() {
    if (languageSelect) {
      languageSelect.addEventListener('change', function(e) {
        loadLanguage(e.target.value);
      });
    }
    
    if (prevButton) {
      prevButton.addEventListener('click', function() {
        if (!isSliderAnimating) {
          currentSlide = (currentSlide - 1 + storyCards.length) % storyCards.length;
          updateSlider();
        }
      });
    }
    
    if (nextButton) {
      nextButton.addEventListener('click', function() {
        if (!isSliderAnimating) {
          currentSlide = (currentSlide + 1) % storyCards.length;
          updateSlider();
        }
      });
    }
    
    indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', function() {
        if (!isSliderAnimating && currentSlide !== index) {
          currentSlide = index;
          updateSlider();
        }
      });
    });
  }
  
  /**
   * Load language file and update UI
   * @param {string} lang - Language code
   */
  function loadLanguage(lang) {
    currentLanguage = lang;
    
    if (languageSelect) {
      languageSelect.value = lang;
    }
    
    if (translations[lang]) {
      updateTranslations(translations[lang]);
      return;
    }
    
    fetch(`assets/lang/${lang}.json`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to load language file: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        translations[lang] = data;
        updateTranslations(data);
      })
      .catch(error => {
        console.error('Error loading language file:', error);
        if (lang !== 'jp') {
          loadLanguage('jp');
        }
      });
  }
  
  /**
   * Update all elements with data-i18n attribute
   * @param {Object} data - Translation data
   */
  function updateTranslations(data) {
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
      const key = element.getAttribute('data-i18n');
      if (data[key]) {
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
          element.placeholder = data[key];
        } else if (element.tagName === 'IMG') {
          element.alt = data[key];
        } else {
          element.textContent = data[key];
        }
      }
    });
    
    document.documentElement.lang = currentLanguage;
    
    document.title = `Jimo Travel - ${data.heroTitle || '沖縄観光アプリ'}`;
  }
  
  /**
   * Update slider to show current slide
   */
  function updateSlider() {
    if (storyCards.length === 0) return;
    
    isSliderAnimating = true;
    
    storyCards.forEach(card => {
      card.style.display = 'none';
    });
    
    storyCards[currentSlide].style.display = 'block';
    storyCards[currentSlide].classList.add('fade-in');
    
    indicators.forEach((indicator, index) => {
      if (index === currentSlide) {
        indicator.classList.add('stories__indicator--active');
      } else {
        indicator.classList.remove('stories__indicator--active');
      }
    });
    
    setTimeout(() => {
      isSliderAnimating = false;
      storyCards[currentSlide].classList.remove('fade-in');
    }, 500);
  }
  
  /**
   * Set up lazy loading for images
   */
  function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
      const lazyImageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const lazyImage = entry.target;
            
            if (lazyImage.tagName === 'PICTURE') {
              const sources = lazyImage.querySelectorAll('source');
              sources.forEach(source => {
                if (source.dataset.srcset) {
                  source.srcset = source.dataset.srcset;
                  delete source.dataset.srcset;
                }
              });
              
              const img = lazyImage.querySelector('img');
              if (img && img.dataset.src) {
                img.src = img.dataset.src;
                delete img.dataset.src;
              }
            } 
            else if (lazyImage.dataset.src) {
              lazyImage.src = lazyImage.dataset.src;
              delete lazyImage.dataset.src;
            }
            
            lazyImage.classList.remove('lazy');
            lazyImageObserver.unobserve(lazyImage);
          }
        });
      });
      
      const lazyImages = document.querySelectorAll('img[loading="lazy"], picture');
      lazyImages.forEach(lazyImage => {
        lazyImageObserver.observe(lazyImage);
      });
    } 
    else {
      let lazyLoadThrottleTimeout;
      
      function lazyLoad() {
        if (lazyLoadThrottleTimeout) {
          clearTimeout(lazyLoadThrottleTimeout);
        }
        
        lazyLoadThrottleTimeout = setTimeout(() => {
          const scrollTop = window.pageYOffset;
          const lazyImages = document.querySelectorAll('img[loading="lazy"]');
          
          lazyImages.forEach(img => {
            if (img.offsetTop < window.innerHeight + scrollTop) {
              if (img.dataset.src) {
                img.src = img.dataset.src;
                delete img.dataset.src;
              }
              img.classList.remove('lazy');
            }
          });
          
          if (lazyImages.length === 0) {
            document.removeEventListener('scroll', lazyLoad);
            window.removeEventListener('resize', lazyLoad);
            window.removeEventListener('orientationChange', lazyLoad);
          }
        }, 20);
      }
      
      document.addEventListener('scroll', lazyLoad);
      window.addEventListener('resize', lazyLoad);
      window.addEventListener('orientationChange', lazyLoad);
    }
  }
  
  let sliderInterval;
  
  function startSliderAutoRotation() {
    sliderInterval = setInterval(() => {
      if (!isSliderAnimating && storyCards.length > 0) {
        currentSlide = (currentSlide + 1) % storyCards.length;
        updateSlider();
      }
    }, 5000); // Change slide every 5 seconds
  }
  
  function stopSliderAutoRotation() {
    clearInterval(sliderInterval);
  }
  
  if (storiesSlider) {
    storiesSlider.addEventListener('mouseenter', stopSliderAutoRotation);
    storiesSlider.addEventListener('mouseleave', startSliderAutoRotation);
    
    storiesSlider.addEventListener('touchstart', stopSliderAutoRotation);
    storiesSlider.addEventListener('touchend', startSliderAutoRotation);
  }
  
  startSliderAutoRotation();
  
  document.addEventListener('DOMContentLoaded', init);
})();
