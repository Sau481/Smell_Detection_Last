// Results page animations and interactions
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scroll animations for cards
    const cards = document.querySelectorAll('.issue-card, .ml-card, .results-section');

    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Apply initial styles and observe elements
    cards.forEach((card, index) => {
        // card.style.opacity = '0';
        // card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Add click-to-expand functionality for issue cards
    const issueCards = document.querySelectorAll('.issue-card');
    issueCards.forEach(card => {
        const header = card.querySelector('.issue-header');
        const body = card.querySelector('.issue-body');

        if (header && body) {
            // Make header clickable
            header.style.cursor = 'pointer';

            // Add expand/collapse icon
            const expandIcon = document.createElement('span');
            expandIcon.innerHTML = '▼';
            expandIcon.style.marginLeft = 'auto';
            expandIcon.style.transition = 'transform 0.3s ease';
            header.appendChild(expandIcon);

            // Toggle body visibility
            header.addEventListener('click', () => {
                const isExpanded = body.style.display !== 'none';
                body.style.display = isExpanded ? 'none' : 'block';
                expandIcon.style.transform = isExpanded ? 'rotate(-90deg)' : 'rotate(0deg)';
            });
        }
    });

    // Add copy functionality for code suggestions
    const fixSections = document.querySelectorAll('.fix');
    fixSections.forEach(fix => {
        const copyBtn = document.createElement('button');
        copyBtn.textContent = '📋 Copy Fix';
        copyBtn.className = 'copy-btn';
        copyBtn.style.cssText = `
            background: var(--success);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
            margin-top: 0.5rem;
            transition: all 0.3s ease;
        `;

        copyBtn.addEventListener('mouseover', () => {
            copyBtn.style.background = '#059669';
        });

        copyBtn.addEventListener('mouseout', () => {
            copyBtn.style.background = 'var(--success)';
        });

        copyBtn.addEventListener('click', () => {
            const text = fix.querySelector('p').textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✓ Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            });
        });

        fix.appendChild(copyBtn);
    });

    // Calculate and display summary statistics
    const analysisSummaryDiv = document.getElementById('analysis-summary');
    let summary = { smell_count: 0, status: "No Issues Found" };
    if (analysisSummaryDiv && analysisSummaryDiv.textContent) {
        try {
            summary = JSON.parse(analysisSummaryDiv.textContent);
        } catch (e) {
            console.error("Error parsing analysis summary:", e);
        }
    }

    // Add summary badge to header
    const resultsHeader = document.querySelector('.results-header');
    if (resultsHeader && summary) {
        const summaryBadge = document.createElement('div');
        const isClean = summary.status === "Clean Code";
        summaryBadge.style.cssText = `
            display: inline-block;
            background: ${isClean ? '#d1fae5' : '#fee2e2'};
            color: ${isClean ? '#065f46' : '#991b1b'};
            padding: 0.5rem 1rem;
            border-radius: 1rem;
            font-weight: 600;
            margin-top: 1rem;
        `;
        summaryBadge.textContent = isClean ? "No Code Smells Detected" : `${summary.smell_count} Code Smells Detected`;
        resultsHeader.appendChild(summaryBadge);
    }

    // AI Assistant Functionality
    const aiExplainBtn = document.getElementById('ai-explain-btn');
    const aiOptimizeBtn = document.getElementById('ai-optimize-btn');
    const aiRefactorBtn = document.getElementById('ai-refactor-btn');
    const aiOutputContainer = document.getElementById('ai-output-container');
    const aiOutputTitle = document.getElementById('ai-output-title');
    const aiOutputContent = document.getElementById('ai-output-content');
    const aiCloseBtn = document.getElementById('ai-close-btn');
    const codeContentDiv = document.getElementById('code-content');
    const code = codeContentDiv ? codeContentDiv.textContent.trim() : '';

    const getAISuggestion = async (endpoint, code, smellType = null) => {
        aiOutputTitle.textContent = 'Loading...';
        aiOutputContent.textContent = 'Please wait while the AI is thinking...';
        aiOutputContainer.style.display = 'block';

        try {
            const payload = { code };
            if (smellType) {
                payload.smell_type = smellType;
            }

            const response = await fetch(`/api/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                aiOutputTitle.textContent = `${data.type.charAt(0).toUpperCase() + data.type.slice(1)} Result`;
                aiOutputContent.textContent = data.result;
            } else {
                aiOutputTitle.textContent = 'Error';
                aiOutputContent.textContent = data.error || 'An unknown error occurred.';
            }
        } catch (error) {
            aiOutputTitle.textContent = 'Error';
            aiOutputContent.textContent = `Failed to fetch AI suggestion: ${error.message}`;
        }
    };

    if (aiExplainBtn) {
        aiExplainBtn.addEventListener('click', () => getAISuggestion('explain', code));
    }

    if (aiOptimizeBtn) {
        aiOptimizeBtn.addEventListener('click', () => getAISuggestion('optimize', code));
    }

    if (aiRefactorBtn) {
        aiRefactorBtn.addEventListener('click', () => getAISuggestion('refactor', code));
    }

    if (aiCloseBtn) {
        aiCloseBtn.addEventListener('click', () => {
            aiOutputContainer.style.display = 'none';
        });
    }

    // Event delegation for "Ask AI" buttons
    document.addEventListener('click', (event) => {
        if (event.target.matches('.btn-ask-ai')) {
            const button = event.target;
            const smellType = button.dataset.smellType;
            const codeSnippet = button.dataset.codeSnippet;
            getAISuggestion('refactor', codeSnippet, smellType);
        }
    });
});