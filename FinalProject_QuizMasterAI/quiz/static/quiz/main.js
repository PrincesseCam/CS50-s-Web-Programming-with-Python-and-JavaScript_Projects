document.addEventListener('DOMContentLoaded', function() {

    // Initialize all animations and interactions
    initializeStatisticsCounters();
    initializeProgressBar(); //progressBar in quiz_question.html
    initializeProgressBars(); //progressBars in profile.html
    initializeAchievementAnimations();
    initializeChartAnimations();

    // Add smooth scrolling for better navigation
    initializeSmoothScroll();
    
    // Add answer selection highlighting
    initializeAnswerSelection();
    
    // Animate topics on load
    const topicCards = document.querySelectorAll('.topic-card');
    topicCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Quiz animations
    const questionContainer = document.querySelector('.card');
    if (questionContainer) {
        questionContainer.classList.add('animate__animated', 'animate__fadeIn');
    }

});

// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add tooltip initialization
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});


function initializeProgressBar() {
    const progressBar = document.querySelector('.progress-bar');
    const quizForm = document.getElementById('#quiz-form');
    
    if (progressBar && quizForm) {
        // Get the current progress from the data attribute
        const currentProgress = parseFloat(progressBar.getAttribute('data-progress') || 0);
        const totalQuestions = parseInt(progressBar.getAttribute('data-total-questions') || 1);
        
        // Animate the progress bar from 0 to current progress
        animateProgress(progressBar, 0, currentProgress);
        
        // Update progress text if it exists
        const progressText = document.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `Question ${currentProgress} of ${totalQuestions}`;
        }
    }
}

//progess Animation
function animateProgress(progressBar, start, end) {
    // Duration of the animation in milliseconds
    const duration = 1000;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Calculate current width using easing function
        const currentWidth = start + (end - start) * easeOutQuad(progress);
        
        // Update progress bar width
        progressBar.style.width = `${currentWidth}%`;
        progressBar.setAttribute('aria-valuenow', currentWidth);
        
        // Continue animation if not finished
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Easing function for smoother animation
function easeOutQuad(t) {
    return t * (2 - t);
}

function initializeAnswerSelection() {
    const answerInputs = document.querySelectorAll('.answer-input');
    
    answerInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Remove active class from all labels
            document.querySelectorAll('.answer-label').forEach(label => {
                label.classList.remove('active');
            });
            
            // Add active class to selected answer
            if (this.checked) {
                this.nextElementSibling.classList.add('active');
            }
        });
    });
}


//////////////////////////////////////////////////
function initializeStatisticsCounters() {
    // Animate statistics numbers counting up
    document.querySelectorAll('.display-6').forEach(counter => {
        const targetValue = parseFloat(counter.textContent);
        const duration = 2000; // 2 seconds
        const start = 0;
        
        if (!isNaN(targetValue)) {
            animateCounter(counter, start, targetValue, duration);
        }
    });
}

function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16); // 60 FPS
    let current = start;
    
    const updateCounter = () => {
        current += increment;
        if (current <= end) {
            // Format number based on whether it's a percentage or not
            element.textContent = element.textContent.includes('%') 
                ? current.toFixed(1) + '%'
                : Math.round(current).toString();
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = element.textContent.includes('%')
                ? end.toFixed(1) + '%'
                : Math.round(end).toString();
        }
    };
    
    requestAnimationFrame(updateCounter);
}

//////////////////////////////////////////////////
function initializeProgressBars() {
    // Animate progress bars filling up
    const progressBars = document.querySelectorAll('.progress-bars');
    
    const observerCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBars = entry.target;
                const targetWidth = progressBars.style.width;
                
                // Reset width to 0 before animation
                progressBars.style.width = '0%';
                
                // Add animation class
                progressBars.classList.add('animate-progress');
                
                // Trigger reflow to ensure animation plays
                void progressBars.offsetWidth;
                
                // Set target width to trigger animation
                progressBars.style.width = targetWidth;
                
                // Stop observing this progress bar
                observer.unobserve(progressBars);
            }
        });
    };
    
    const observer = new IntersectionObserver(observerCallback, {
        threshold: 0.1
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

//////////////////////////////////////////////////
function initializeAchievementAnimations() {
    // Add hover animations for achievement items
    document.querySelectorAll('.achievement-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            // Scale up icon slightly
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1.2)';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1)';
            }
        });
    });
}

function initializeChartAnimations() {
    // Add chart animations if using any charts
    const chartElements = document.querySelectorAll('.chart-container');
    
    chartElements.forEach(container => {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
    });
    
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    chartElements.forEach(container => observer.observe(container));
}

function initializeSmoothScroll() {
    // Add smooth scrolling to internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function animateProgressBar(element, startWidth, endWidth) {
    const duration = 600; // Animation duration in milliseconds
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Use for smoother animation
        const currentWidth = startWidth + (endWidth - startWidth) * easeOutQuad(progress);
        element.style.width = `${currentWidth}%`;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}