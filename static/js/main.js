document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Switcher Logic
    const themeToggleBtn = document.getElementById('theme-toggle');
    const getPreferredTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) return savedTheme;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update icon
        if (themeToggleBtn) {
            const icon = themeToggleBtn.querySelector('i');
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
            } else {
                icon.className = 'fas fa-moon';
            }
        }
    };

    // Apply preferred theme on load
    setTheme(getPreferredTheme());

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            setTheme(currentTheme === 'dark' ? 'light' : 'dark');
        });
    }

    // 2. Drag and Drop File Upload
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('resume-file');
    const fileInfo = document.getElementById('file-info');

    if (uploadArea && fileInput) {
        // Trigger file input click when clicking on upload area
        uploadArea.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadArea.classList.remove('dragover');
            }, false);
        });

        uploadArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileInfo(files[0]);
            }
        }, false);

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateFileInfo(fileInput.files[0]);
            }
        });
    }

    function updateFileInfo(file) {
        if (file && fileInfo) {
            if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
                fileInfo.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-circle me-1"></i> Only PDF files are supported!</span>`;
                fileInput.value = ''; // Reset input
                return;
            }
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            fileInfo.innerHTML = `
                <div class="alert alert-success d-inline-block py-1 px-3 mt-2 mb-0">
                    <i class="fas fa-file-pdf me-2"></i><strong>${file.name}</strong> (${sizeMB} MB)
                </div>
            `;
        }
    }

    // 3. Loading Overlay on Form Submit
    const analyzerForm = document.getElementById('analyzer-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (analyzerForm) {
        analyzerForm.addEventListener('submit', (e) => {
            // Validate file presence
            if (!fileInput || fileInput.files.length === 0) {
                e.preventDefault();
                alert("Please upload a PDF resume file first!");
                return;
            }
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
        });
    }

    // 4. Circular Progress Rings
    const circles = document.querySelectorAll('.score-circle');
    circles.forEach(circle => {
        const ring = circle.querySelector('.progress-ring');
        const score = parseInt(circle.getAttribute('data-score')) || 0;
        
        if (ring) {
            const radius = ring.r.baseVal.value;
            const circumference = 2 * Math.PI * radius;
            
            // Set up initial dasharray and offset
            ring.style.strokeDasharray = `${circumference} ${circumference}`;
            ring.style.strokeDashoffset = circumference;
            
            // Set color based on score value
            if (score >= 80) {
                ring.style.stroke = 'var(--accent-success)';
            } else if (score >= 50) {
                ring.style.stroke = 'var(--accent-warning)';
            } else {
                ring.style.stroke = 'var(--accent-danger)';
            }

            // Animate stroke
            setTimeout(() => {
                const offset = circumference - (score / 100) * circumference;
                ring.style.strokeDashoffset = offset;
            }, 100);
        }
    });

    // 5. Skills Pie Chart (using Chart.js)
    const chartCanvas = document.getElementById('skillsChart');
    if (chartCanvas) {
        const techSkillsCount = parseInt(chartCanvas.getAttribute('data-tech-count')) || 0;
        const softSkillsCount = parseInt(chartCanvas.getAttribute('data-soft-count')) || 0;
        
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? '#475569' : '#cbd5e1';
        const labelColor = isDark ? '#f8fafc' : '#0f172a';

        new Chart(chartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Technical Skills', 'Soft Skills'],
                datasets: [{
                    data: [techSkillsCount, softSkillsCount],
                    backgroundColor: [
                        'rgba(37, 99, 235, 0.85)',  // Blue 600
                        'rgba(16, 185, 129, 0.85)'  // Emerald 500
                    ],
                    borderColor: isDark ? '#1e293b' : '#ffffff',
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: labelColor,
                            font: {
                                family: 'Outfit',
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }

    // 6. Resume Keyword Highlighting
    const resumeContainer = document.getElementById('resumeRawText');
    if (resumeContainer) {
        let text = resumeContainer.innerHTML;
        
        // Retrieve skills to highlight from attributes
        const matchingSkills = JSON.parse(resumeContainer.getAttribute('data-matching') || '[]');
        
        // Highlight matching skills
        matchingSkills.forEach(skill => {
            if (skill.length > 1) {
                // Escape regex special chars
                const escapedSkill = skill.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                // Word boundary check, but also handle common technical notations like C++, C#, .NET
                // If it ends with special characters like ++ or #, standard \b might fail at the end.
                let regexStr = `\\b${escapedSkill}\\b`;
                if (escapedSkill.endsWith('\\+\\+') || escapedSkill.endsWith('\\#')) {
                    regexStr = `\\b${escapedSkill}`;
                }
                try {
                    const regex = new RegExp(regexStr, 'gi');
                    text = text.replace(regex, (match) => `<mark class="keyword-match">${match}</mark>`);
                } catch(e) {
                    console.error("Regex error for skill:", skill, e);
                }
            }
        });
        
        resumeContainer.innerHTML = text;
    }

    // 7. Clientside History Search Filter
    const historySearchInput = document.getElementById('history-search');
    if (historySearchInput) {
        historySearchInput.addEventListener('input', () => {
            const query = historySearchInput.value.toLowerCase().trim();
            const rows = document.querySelectorAll('.history-table-row');
            
            rows.forEach(row => {
                const name = row.getAttribute('data-filename').toLowerCase();
                const skills = row.getAttribute('data-skills').toLowerCase();
                
                if (name.includes(query) || skills.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
