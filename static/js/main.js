// Main JavaScript file for the news scraper

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Loading states for buttons
    var loadingButtons = document.querySelectorAll('[data-loading-text]');
    loadingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var originalText = button.innerHTML;
            var loadingText = button.dataset.loadingText;
            
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' + loadingText;
            button.disabled = true;
            
            // Re-enable after 30 seconds (failsafe)
            setTimeout(function() {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 30000);
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Search form enhancements
    var searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        var searchInput = searchForm.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                var query = this.value.trim();
                if (query.length > 0) {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        }
    }

    // Filter form auto-submit
    var filterForm = document.querySelector('form[action*="index"]');
    if (filterForm) {
        var filterSelects = filterForm.querySelectorAll('select');
        filterSelects.forEach(function(select) {
            select.addEventListener('change', function() {
                // Add small delay to allow multiple selections
                setTimeout(function() {
                    filterForm.submit();
                }, 100);
            });
        });
    }

    // Copy to clipboard functionality
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        }).catch(function(err) {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard', 'error');
        });
    }

    // Add copy buttons to article URLs
    var articleUrls = document.querySelectorAll('.article-url');
    articleUrls.forEach(function(url) {
        var copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary ms-2';
        copyBtn.innerHTML = '<i data-feather="copy"></i>';
        copyBtn.title = 'Copy URL';
        copyBtn.addEventListener('click', function() {
            copyToClipboard(url.href);
        });
        url.parentNode.appendChild(copyBtn);
    });

    // Toast notification system
    function showToast(message, type = 'info') {
        var toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        var toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        var bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    // Article reading time estimation
    function estimateReadingTime(text) {
        var wordsPerMinute = 200;
        var words = text.split(/\s+/).length;
        var minutes = Math.ceil(words / wordsPerMinute);
        return minutes;
    }

    // Add reading time to articles
    var articleContents = document.querySelectorAll('.article-content .content-text');
    articleContents.forEach(function(content) {
        var readingTime = estimateReadingTime(content.textContent);
        var readingTimeElement = document.createElement('small');
        readingTimeElement.className = 'text-muted';
        readingTimeElement.innerHTML = `<i data-feather="clock"></i> ${readingTime} min read`;
        
        var header = content.parentNode.querySelector('h1');
        if (header) {
            header.appendChild(readingTimeElement);
        }
    });

    // Infinite scroll for article lists (optional enhancement)
    var articleList = document.querySelector('.article-list');
    if (articleList) {
        var loadMoreBtn = document.querySelector('.load-more-btn');
        if (loadMoreBtn) {
            var observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        loadMoreBtn.click();
                    }
                });
            });
            observer.observe(loadMoreBtn);
        }
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+/ or Cmd+/ for search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            var searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl+R or Cmd+R for refresh/scrape
        if ((e.ctrlKey || e.metaKey) && e.key === 'r' && e.shiftKey) {
            e.preventDefault();
            var scrapeBtn = document.querySelector('a[href*="scrape"]');
            if (scrapeBtn) {
                scrapeBtn.click();
            }
        }
    });

    // Dark mode toggle (if needed)
    var darkModeToggle = document.querySelector('#darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.documentElement.setAttribute('data-bs-theme', 
                document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark'
            );
        });
    }

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                var perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
                }
            }, 0);
        });
    }

    // Initialize feather icons after dynamic content is added
    function refreshFeatherIcons() {
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    // Call refreshFeatherIcons when needed
    refreshFeatherIcons();
});

// Utility functions
window.NewsScraperUtils = {
    showToast: function(message, type = 'info') {
        // Implementation moved to main scope
    },
    
    copyToClipboard: function(text) {
        // Implementation moved to main scope
    },
    
    formatDate: function(dateString) {
        var date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    truncateText: function(text, length = 100) {
        if (text.length <= length) return text;
        return text.substr(0, length) + '...';
    }
};
