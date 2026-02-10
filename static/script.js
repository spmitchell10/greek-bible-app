// Greek New Testament Bible Study App - Frontend JavaScript

// Load initial data
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadBooks();
    
    // Event listeners
    document.getElementById('advanced-search-btn').addEventListener('click', performAdvancedSearch);
    document.getElementById('show-help-btn').addEventListener('click', toggleHelp);
    document.getElementById('load-reading-btn').addEventListener('click', loadReadingView);
    
    // Display mode change listener
    document.querySelectorAll('input[name="display-mode"]').forEach(radio => {
        radio.addEventListener('change', handleDisplayModeChange);
    });
    
    // Enable search on Enter key
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                if (input.id === 'advanced-search') {
                    performAdvancedSearch();
                } else if (input.id === 'read-chapter') {
                    loadReadingView();
                } else {
                    performSearch();
                }
            }
        });
    });
});

// Load database statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('stat-words').textContent = 
            `${data.total_words.toLocaleString()} words`;
        document.getElementById('stat-lemmas').textContent = 
            `${data.unique_lemmas.toLocaleString()} unique lemmas`;
        document.getElementById('stat-books').textContent = 
            `${data.total_books} books`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load list of books
async function loadBooks() {
    try {
        const response = await fetch('/api/books');
        const books = await response.json();
        
        // Populate reading view dropdown
        const readSelect = document.getElementById('read-book');
        books.forEach(book => {
            const option = document.createElement('option');
            option.value = book.book_code;
            option.textContent = `${book.book_name} (${book.corpus})`;
            option.dataset.corpus = book.corpus;
            readSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading books:', error);
    }
}

// Display search results (for backward compatibility)
function displayResults(data) {
    document.getElementById('loading').style.display = 'none';
    
    const container = document.getElementById('results-container');
    const countDisplay = document.getElementById('results-count');
    
    if (data.count === 0) {
        container.innerHTML = 
            '<div class="no-results"><p>No results found.</p><p>Try adjusting your search criteria.</p></div>';
        countDisplay.textContent = '';
        return;
    }
    
    countDisplay.textContent = `${data.count} result${data.count !== 1 ? 's' : ''}${data.limited ? ' (limited)' : ''}`;
    
    // Group results by verse
    const groupedResults = groupByVerse(data.results);
    
    container.innerHTML = '';
    groupedResults.forEach(group => {
        const resultItem = createResultItem(group);
        container.appendChild(resultItem);
    });
}

// Group results by verse reference
function groupByVerse(results) {
    const groups = {};
    
    results.forEach(result => {
        const key = `${result.book_code}-${result.chapter}-${result.verse}`;
        
        if (!groups[key]) {
            groups[key] = {
                reference: result.reference,
                verse_text: result.verse_text || '',
                words: []
            };
        }
        
        groups[key].words.push(result);
    });
    
    return Object.values(groups);
}

// Create a result item element
function createResultItem(group) {
    const item = document.createElement('div');
    item.className = 'result-item';
    
    // Reference
    const reference = document.createElement('div');
    reference.className = 'result-reference';
    reference.textContent = group.reference;
    item.appendChild(reference);
    
    // Verse text (if available)
    if (group.verse_text) {
        const verse = document.createElement('div');
        verse.className = 'result-verse';
        verse.innerHTML = highlightWords(group.verse_text, group.words);
        item.appendChild(verse);
    }
    
    // Word details
    group.words.forEach((word, index) => {
        if (index > 0) {
            const divider = document.createElement('hr');
            divider.style.margin = '15px 0';
            divider.style.border = 'none';
            divider.style.borderTop = '1px solid var(--border)';
            item.appendChild(divider);
        }
        
        const details = createWordDetails(word);
        item.appendChild(details);
    });
    
    return item;
}

// Highlight matching words in verse text
function highlightWords(verseText, words) {
    let highlighted = verseText;
    
    words.forEach(word => {
        if (word.word) {
            const regex = new RegExp(`(${escapeRegex(word.word)})`, 'g');
            highlighted = highlighted.replace(regex, '<span class="result-word">$1</span>');
        }
    });
    
    return highlighted;
}

// Escape special regex characters
function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Create word details section
function createWordDetails(word) {
    const details = document.createElement('div');
    details.className = 'result-details';
    
    const fields = [
        { label: 'Word', value: word.word },
        { label: 'Lemma', value: word.lemma },
        { label: 'Part of Speech', value: word.pos },
        { label: 'Tense', value: word.tense },
        { label: 'Voice', value: word.voice },
        { label: 'Mood', value: word.mood },
        { label: 'Case', value: word.case },
        { label: 'Number', value: word.number },
        { label: 'Gender', value: word.gender },
        { label: 'Morph Code', value: word.morph_code },
    ];
    
    fields.forEach(field => {
        if (field.value) {
            const item = document.createElement('div');
            item.className = 'detail-item';
            
            const label = document.createElement('div');
            label.className = 'detail-label';
            label.textContent = field.label;
            
            const value = document.createElement('div');
            value.className = 'detail-value';
            value.textContent = capitalize(field.value);
            
            item.appendChild(label);
            item.appendChild(value);
            details.appendChild(item);
        }
    });
    
    return details;
}

// Capitalize first letter (helper function)
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Toggle help display
function toggleHelp() {
    const helpDiv = document.getElementById('search-help');
    if (helpDiv.style.display === 'none') {
        helpDiv.style.display = 'block';
    } else {
        helpDiv.style.display = 'none';
    }
}

// Perform advanced search
async function performAdvancedSearch() {
    const query = document.getElementById('advanced-search').value.trim();
    
    if (!query) {
        displayResults({ results: [], count: 0 });
        return;
    }
    
    // Get corpus selection
    const corpora = [];
    if (document.getElementById('corpus-nt').checked) {
        corpora.push('NT');
    }
    if (document.getElementById('corpus-lxx').checked) {
        corpora.push('LXX');
    }
    
    if (corpora.length === 0) {
        document.getElementById('results-container').innerHTML = 
            '<div class="no-results"><p>Please select at least one corpus to search.</p></div>';
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('results-count').textContent = '';
    
    try {
        const response = await fetch('/api/advanced-search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: query,
                corpora: corpora
            }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('results-container').innerHTML = 
                `<div class="no-results"><p>Error: ${data.error}</p><p>Check your syntax and try again.</p></div>`;
            return;
        }
        
        // Check if it's a relative search
        if (data.is_relative_search) {
            // Store data for re-search
            currentRelativeSearchData = data;
            
            // Display word selection panel
            displayWordSelectionPanel(data.source_verse);
            
            // Display relative results
            displayRelativeResults(data);
        } else if (data.is_inference_search) {
            // Display inference results
            displayInferenceResults(data);
        } else {
            // Normal advanced search results
            displayResults(data);
        }
    } catch (error) {
        console.error('Advanced search error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-container').innerHTML = 
            '<div class="no-results"><p>Error performing search. Please try again.</p></div>';
    }
}

// Global variable to store current relative search data
let currentRelativeSearchData = null;

// Display word selection panel with checkboxes
function displayWordSelectionPanel(sourceVerse) {
    const panel = document.getElementById('word-selection-panel');
    const refSpan = document.getElementById('source-verse-ref');
    const textP = document.getElementById('source-verse-text');
    const checkboxContainer = document.getElementById('word-checkboxes');
    
    refSpan.textContent = sourceVerse.reference;
    textP.textContent = sourceVerse.text;
    
    // Create checkboxes for each word
    checkboxContainer.innerHTML = '';
    sourceVerse.words.forEach((wordData, index) => {
        const label = document.createElement('label');
        label.className = 'word-checkbox';
        
        // Add weight class for styling
        const weightClass = wordData.weight >= 3 ? 'high-weight' : 'low-weight';
        label.classList.add(weightClass);
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = true;
        checkbox.value = index;
        checkbox.dataset.lemma = wordData.lemma;
        checkbox.dataset.pos = wordData.pos;
        checkbox.dataset.weight = wordData.weight;
        
        const span = document.createElement('span');
        span.textContent = `${wordData.lemma} (${wordData.pos})`;
        
        label.appendChild(checkbox);
        label.appendChild(span);
        checkboxContainer.appendChild(label);
    });
    
    // Show panel
    panel.style.display = 'block';
    
    // Scroll the panel into view smoothly
    setTimeout(() => {
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
    
    // Add event listeners for filter buttons
    document.getElementById('re-search-btn').onclick = performReSearch;
    document.getElementById('select-all-words-btn').onclick = () => selectWords('all');
    document.getElementById('select-none-words-btn').onclick = () => selectWords('none');
    document.getElementById('select-important-words-btn').onclick = () => selectWords('important');
}

// Select/deselect words based on filter
function selectWords(filter) {
    const checkboxes = document.querySelectorAll('#word-checkboxes input[type="checkbox"]');
    
    checkboxes.forEach(cb => {
        if (filter === 'all') {
            cb.checked = true;
        } else if (filter === 'none') {
            cb.checked = false;
        } else if (filter === 'important') {
            // Select only high-weight words (verbs, nouns, adjectives, adverbs)
            cb.checked = parseInt(cb.dataset.weight) >= 3;
        }
    });
}

// Re-search with selected words
async function performReSearch() {
    if (!currentRelativeSearchData) {
        alert('No search data available. Please perform a search first.');
        return;
    }
    
    // Get selected words
    const checkboxes = document.querySelectorAll('#word-checkboxes input[type="checkbox"]:checked');
    const selectedLemmas = Array.from(checkboxes).map(cb => {
        const index = parseInt(cb.value);
        return currentRelativeSearchData.source_verse.words[index];
    });
    
    if (selectedLemmas.length === 0) {
        alert('Please select at least one word');
        return;
    }
    
    // Get selected corpora from main checkboxes
    const corpora = [];
    if (document.getElementById('corpus-nt').checked) corpora.push('NT');
    if (document.getElementById('corpus-lxx').checked) corpora.push('LXX');
    
    // Show loading
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('results-container').innerHTML = '';
    
    try {
        const response = await fetch('/api/advanced-search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                query: `rel ${currentRelativeSearchData.source_verse.reference}`,
                corpora: corpora,
                lemmas: selectedLemmas
            }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('results-container').innerHTML = 
                `<div class="no-results"><p>Error: ${data.error}</p></div>`;
            return;
        }
        
        // Update current data
        currentRelativeSearchData = data;
        
        // Display results
        displayRelativeResults(data);
        
    } catch (error) {
        console.error('Re-search error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-container').innerHTML = 
            '<div class="no-results"><p>Error performing search. Please try again.</p></div>';
    }
}

// Display relative search results
function displayRelativeResults(data) {
    document.getElementById('loading').style.display = 'none';
    
    const container = document.getElementById('results-container');
    const countSpan = document.getElementById('results-count');
    
    if (data.results.length === 0) {
        container.innerHTML = '<div class="no-results"><p>No similar verses found.</p></div>';
        countSpan.textContent = '0 results';
        return;
    }
    
    // Update count
    countSpan.textContent = `${data.results.length} result${data.results.length !== 1 ? 's' : ''}`;
    if (data.limited) {
        countSpan.textContent += ' (showing top 100)';
    }
    
    // Build results HTML
    let html = '<div class="relative-results">';
    html += `<div class="source-verse-display">
                <h3>Source Verse: ${data.source_verse.reference}</h3>
                <p class="verse-text">${data.source_verse.text}</p>
             </div>`;
    
    data.results.forEach(result => {
        html += `
            <div class="result-item relative-result-item">
                <div class="result-header">
                    <span class="reference">${result.reference}</span>
                    <span class="similarity-score" title="Similarity score based on matching lemmas">
                        Score: ${result.score} (${result.match_count} word${result.match_count !== 1 ? 's' : ''})
                    </span>
                </div>
                <div class="result-text">${result.verse_text}</div>
                <div class="matched-lemmas">
                    <strong>Matched lemmas:</strong> ${result.matched_lemmas.join(', ')}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Helper function to create highlighted verse text with POS colors
function buildHighlightedVerseText(words) {
    if (!words || words.length === 0) {
        return '';
    }
    
    return words.map(w => {
        const pos = (w.pos || 'unknown').toLowerCase();
        return `<span class="pos-${pos}">${w.word}</span>`;
    }).join(' ');
}

// Helper function to create highlighted pattern display with POS colors
function buildHighlightedPattern(patterns) {
    if (!patterns || patterns.length === 0) {
        return '';
    }
    
    return patterns.map(p => {
        const posStr = (typeof p === 'string' ? p : p.pattern_str || p.pos || 'unknown').toLowerCase();
        return `<span class="pos-${posStr}">${posStr}</span>`;
    }).join(' → ');
}

function displayInferenceResults(data) {
    document.getElementById('loading').style.display = 'none';
    
    const container = document.getElementById('results-container');
    const countSpan = document.getElementById('results-count');
    
    if (data.results.length === 0) {
        container.innerHTML = '<div class="no-results"><p>No verses with similar syntax found.</p></div>';
        countSpan.textContent = '0 results';
        return;
    }
    
    // Update count
    countSpan.textContent = `${data.results.length} result${data.results.length !== 1 ? 's' : ''}`;
    
    // Build highlighted source verse text
    const sourceVerseHighlighted = data.source_verse.words 
        ? buildHighlightedVerseText(data.source_verse.words)
        : data.source_verse.text;
    
    // Build highlighted source pattern
    const sourcePatternHighlighted = data.source_verse.pattern_objects
        ? buildHighlightedPattern(data.source_verse.pattern_objects)
        : data.source_verse.pattern.join(' → ');
    
    // Build results HTML
    let html = '<div class="inference-results">';
    html += `<div class="source-verse-display">
                <h3>Source Verse: ${data.source_verse.reference}</h3>
                <p class="verse-text">${sourceVerseHighlighted}</p>
                <div class="pattern-display">
                    <strong>Syntactic Pattern:</strong> 
                    <code class="pattern-code">${sourcePatternHighlighted}</code>
                </div>
             </div>`;
    
    data.results.forEach(result => {
        // Build highlighted verse text
        const verseHighlighted = result.verse_words
            ? buildHighlightedVerseText(result.verse_words)
            : result.verse_text;
        
        // Build highlighted pattern
        const patternHighlighted = result.pattern_objects
            ? buildHighlightedPattern(result.pattern_objects)
            : result.pattern.join(' → ');
        
        html += `
            <div class="result-item inference-result-item">
                <div class="result-header">
                    <span class="reference">${result.reference}</span>
                    <span class="similarity-score" title="Similarity percentage based on syntactic structure">
                        ${result.similarity}% similar
                    </span>
                </div>
                <div class="result-text">${verseHighlighted}</div>
                <div class="pattern-info">
                    <strong>Pattern:</strong> <code class="pattern-code">${patternHighlighted}</code>
                    <span class="pattern-stats">
                        (Edit distance: ${result.edit_distance}, Length diff: ${result.length_diff})
                    </span>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// ============================================================================
// READING VIEW FUNCTIONALITY
// ============================================================================

let currentReadingState = {
    bookCode: null,
    currentChapter: null,
    corpus: 'NT',
    displayMode: 'verse',
    loadedChapters: new Set(),
    isLoading: false,
    hasMoreBefore: true,
    hasMoreAfter: true
};

async function loadReadingView() {
    const bookCode = document.getElementById('read-book').value;
    const chapter = parseInt(document.getElementById('read-chapter').value);
    const corpus = document.querySelector('input[name="read-corpus"]:checked').value;
    const displayMode = document.querySelector('input[name="display-mode"]:checked').value;
    
    if (!bookCode || !chapter) {
        alert('Please select a book and enter a chapter number');
        return;
    }
    
    // Reset state for new reading
    currentReadingState = {
        bookCode: bookCode,
        currentChapter: chapter,
        corpus: corpus,
        displayMode: displayMode,
        loadedChapters: new Set(),
        isLoading: false,
        hasMoreBefore: true,
        hasMoreAfter: true
    };
    
    // Clear results and load initial chapter
    const container = document.getElementById('results-container');
    container.innerHTML = '<div class="loading-indicator">Loading...</div>';
    
    // Load the requested chapter with context
    await loadChapters(chapter, true);
    
    // Setup infinite scroll
    setupInfiniteScroll();
}

async function loadChapters(centerChapter, isInitial = false) {
    if (currentReadingState.isLoading) return;
    
    currentReadingState.isLoading = true;
    
    try {
        const response = await fetch('/api/read', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                book_code: currentReadingState.bookCode,
                chapter: centerChapter,
                corpus: currentReadingState.corpus,
                context: 1  // Load 1 chapter before and after
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        if (isInitial) {
            // Initial load - replace content
            displayChapters(data.chapters, true);
            
            // Scroll to the requested chapter
            setTimeout(() => {
                const requestedChapterElem = document.querySelector(`[data-chapter="${centerChapter}"]`);
                if (requestedChapterElem) {
                    requestedChapterElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
        } else {
            // Append or prepend to existing content
            displayChapters(data.chapters, false);
        }
        
        // Mark chapters as loaded
        data.chapters.forEach(ch => {
            currentReadingState.loadedChapters.add(ch.chapter);
        });
        
        // Update bounds
        if (data.chapters.length === 0 || (data.chapters[0] && data.chapters[0].chapter === 1)) {
            currentReadingState.hasMoreBefore = false;
        }
        
    } catch (error) {
        console.error('Error loading chapters:', error);
        showError('Error loading text: ' + error.message);
    } finally {
        currentReadingState.isLoading = false;
    }
}

function displayChapters(chapters, replace = false) {
    const container = document.getElementById('results-container');
    const displayMode = currentReadingState.displayMode || 'verse';
    
    if (replace) {
        container.innerHTML = '';
    }
    
    chapters.forEach(chapter => {
        // Skip if already displayed
        if (document.querySelector(`[data-chapter="${chapter.chapter}"]`)) {
            return;
        }
        
        const chapterDiv = document.createElement('div');
        chapterDiv.className = 'chapter-section';
        if (displayMode === 'paragraph') {
            chapterDiv.classList.add('paragraph-mode');
        }
        chapterDiv.dataset.chapter = chapter.chapter;
        
        let html = `
            <div class="chapter-header">
                ${chapter.book_name} ${chapter.chapter}
            </div>
        `;
        
        if (displayMode === 'paragraph') {
            // Paragraph mode: continuous text with superscript verse numbers
            html += '<div class="paragraph-content">';
            chapter.verses.forEach((verse, index) => {
                html += `<span class="verse-item">`;
                html += `<sup class="verse-number">${verse.verse}</sup>`;
                html += `<span class="verse-text">${verse.text}</span>`;
                // Add space between verses
                if (index < chapter.verses.length - 1) {
                    html += ' ';
                }
                html += `</span>`;
            });
            html += '</div>';
        } else {
            // Verse-by-verse mode: traditional format
            chapter.verses.forEach(verse => {
                html += `
                    <div class="verse-item">
                        <div class="verse-number">${verse.verse}</div>
                        <div class="verse-text">${verse.text}</div>
                    </div>
                `;
            });
        }
        
        chapterDiv.innerHTML = html;
        
        // Determine where to insert
        if (replace || !container.firstChild) {
            container.appendChild(chapterDiv);
        } else {
            // Insert in correct order
            const existingChapters = Array.from(container.querySelectorAll('.chapter-section'));
            const insertBefore = existingChapters.find(el => 
                parseInt(el.dataset.chapter) > chapter.chapter
            );
            
            if (insertBefore) {
                container.insertBefore(chapterDiv, insertBefore);
            } else {
                container.appendChild(chapterDiv);
            }
        }
    });
}

function setupInfiniteScroll() {
    const container = document.getElementById('results-container');
    
    // Remove existing listener if any
    container.removeEventListener('scroll', handleScroll);
    
    // Add new listener
    container.addEventListener('scroll', handleScroll);
}

function handleScroll() {
    const container = document.getElementById('results-container');
    const scrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    
    // Load more when near top (scrolled up)
    if (scrollTop < 300 && currentReadingState.hasMoreBefore && !currentReadingState.isLoading) {
        const firstChapter = getFirstLoadedChapter();
        if (firstChapter > 1) {
            loadAdjacentChapter(firstChapter - 1, 'before');
        }
    }
    
    // Load more when near bottom (scrolled down)
    if (scrollTop + clientHeight > scrollHeight - 300 && currentReadingState.hasMoreAfter && !currentReadingState.isLoading) {
        const lastChapter = getLastLoadedChapter();
        loadAdjacentChapter(lastChapter + 1, 'after');
    }
}

async function loadAdjacentChapter(chapterNum, direction) {
    if (currentReadingState.loadedChapters.has(chapterNum)) return;
    if (currentReadingState.isLoading) return;
    
    currentReadingState.isLoading = true;
    
    // Save current scroll position
    const container = document.getElementById('results-container');
    const scrollBefore = container.scrollHeight;
    
    try {
        const response = await fetch('/api/read', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                book_code: currentReadingState.bookCode,
                chapter: chapterNum,
                corpus: currentReadingState.corpus,
                context: 0  // Just load this chapter
            })
        });
        
        const data = await response.json();
        
        if (data.error || data.chapters.length === 0) {
            // No more chapters in this direction
            if (direction === 'before') {
                currentReadingState.hasMoreBefore = false;
            } else {
                currentReadingState.hasMoreAfter = false;
            }
            return;
        }
        
        displayChapters(data.chapters, false);
        currentReadingState.loadedChapters.add(chapterNum);
        
        // Restore scroll position when loading before
        if (direction === 'before') {
            const scrollAfter = container.scrollHeight;
            container.scrollTop += (scrollAfter - scrollBefore);
        }
        
    } catch (error) {
        console.error('Error loading adjacent chapter:', error);
    } finally {
        currentReadingState.isLoading = false;
    }
}

function getFirstLoadedChapter() {
    const chapters = Array.from(currentReadingState.loadedChapters);
    return Math.min(...chapters);
}

function getLastLoadedChapter() {
    const chapters = Array.from(currentReadingState.loadedChapters);
    return Math.max(...chapters);
}

function handleDisplayModeChange(event) {
    const newMode = event.target.value;
    
    // Only update if we have content loaded
    if (currentReadingState.loadedChapters.size === 0) {
        return;
    }
    
    // Update state
    currentReadingState.displayMode = newMode;
    
    // Get all chapter sections
    const chapterSections = document.querySelectorAll('.chapter-section');
    
    chapterSections.forEach(section => {
        const chapter = parseInt(section.dataset.chapter);
        
        // Toggle paragraph mode class
        if (newMode === 'paragraph') {
            section.classList.add('paragraph-mode');
        } else {
            section.classList.remove('paragraph-mode');
        }
        
        // Get chapter data from the section
        const bookName = section.querySelector('.chapter-header').textContent.trim().split(' ').slice(0, -1).join(' ');
        const verses = [];
        
        if (newMode === 'verse') {
            // Converting from paragraph to verse mode
            const verseElements = section.querySelectorAll('.verse-item');
            verseElements.forEach(elem => {
                const verseNum = elem.querySelector('.verse-number').textContent.trim();
                const verseText = elem.querySelector('.verse-text').textContent.trim();
                verses.push({ verse: verseNum, text: verseText });
            });
            
            // Rebuild in verse mode
            let html = section.querySelector('.chapter-header').outerHTML;
            verses.forEach(verse => {
                html += `
                    <div class="verse-item">
                        <div class="verse-number">${verse.verse}</div>
                        <div class="verse-text">${verse.text}</div>
                    </div>
                `;
            });
            section.innerHTML = html;
            
        } else {
            // Converting from verse to paragraph mode
            const verseElements = section.querySelectorAll('.verse-item');
            verseElements.forEach(elem => {
                const verseNum = elem.querySelector('.verse-number').textContent.trim();
                const verseText = elem.querySelector('.verse-text').textContent.trim();
                verses.push({ verse: verseNum, text: verseText });
            });
            
            // Rebuild in paragraph mode
            let html = section.querySelector('.chapter-header').outerHTML;
            html += '<div class="paragraph-content">';
            verses.forEach((verse, index) => {
                html += `<span class="verse-item">`;
                html += `<sup class="verse-number">${verse.verse}</sup>`;
                html += `<span class="verse-text">${verse.text}</span>`;
                if (index < verses.length - 1) {
                    html += ' ';
                }
                html += `</span>`;
            });
            html += '</div>';
            section.innerHTML = html;
        }
    });
}
