// Greek New Testament Bible Study App - Frontend JavaScript

// Load initial data
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadBooks();
    loadMorphologyOptions();
    
    // Event listeners
    document.getElementById('search-btn').addEventListener('click', performSearch);
    document.getElementById('clear-btn').addEventListener('click', clearForm);
    document.getElementById('advanced-search-btn').addEventListener('click', performAdvancedSearch);
    document.getElementById('show-help-btn').addEventListener('click', toggleHelp);
    
    // Enable search on Enter key
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                if (input.id === 'advanced-search') {
                    performAdvancedSearch();
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
        
        const select = document.getElementById('book-filter');
        books.forEach(book => {
            const option = document.createElement('option');
            option.value = book.book_code;
            option.textContent = book.book_name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading books:', error);
    }
}

// Load morphology filter options
async function loadMorphologyOptions() {
    try {
        const response = await fetch('/api/morphology/options');
        const options = await response.json();
        
        // Populate each dropdown
        populateSelect('pos-filter', options.pos);
        populateSelect('tense-filter', options.tense);
        populateSelect('voice-filter', options.voice);
        populateSelect('mood-filter', options.mood);
        populateSelect('case-filter', options.case);
        populateSelect('number-filter', options.number);
        populateSelect('gender-filter', options.gender);
        populateSelect('person-filter', options.person);
    } catch (error) {
        console.error('Error loading morphology options:', error);
    }
}

// Helper to populate select dropdowns
function populateSelect(selectId, values) {
    const select = document.getElementById(selectId);
    values.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = capitalize(value);
        select.appendChild(option);
    });
}

// Capitalize first letter
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Perform search
async function performSearch() {
    const searchParams = {
        text: document.getElementById('text-search').value.trim(),
        lemma: document.getElementById('lemma-exact').value.trim(),
        book: document.getElementById('book-filter').value,
        pos: document.getElementById('pos-filter').value,
        tense: document.getElementById('tense-filter').value,
        voice: document.getElementById('voice-filter').value,
        mood: document.getElementById('mood-filter').value,
        case: document.getElementById('case-filter').value,
        number: document.getElementById('number-filter').value,
        gender: document.getElementById('gender-filter').value,
        person: document.getElementById('person-filter').value,
    };
    
    // Check if at least one criterion is provided
    const hasSearchCriteria = Object.values(searchParams).some(val => val !== '');
    
    if (!hasSearchCriteria) {
        displayResults({ results: [], count: 0 });
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('results-count').textContent = '';
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchParams),
        });
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Search error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-container').innerHTML = 
            '<div class="no-results"><p>Error performing search. Please try again.</p></div>';
    }
}

// Display search results
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

// Clear search form
function clearForm() {
    document.getElementById('text-search').value = '';
    document.getElementById('lemma-exact').value = '';
    document.getElementById('book-filter').value = '';
    document.getElementById('pos-filter').value = '';
    document.getElementById('tense-filter').value = '';
    document.getElementById('voice-filter').value = '';
    document.getElementById('mood-filter').value = '';
    document.getElementById('case-filter').value = '';
    document.getElementById('number-filter').value = '';
    document.getElementById('gender-filter').value = '';
    document.getElementById('person-filter').value = '';
    document.getElementById('advanced-search').value = '';
    
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('results-count').textContent = '';
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
        
        displayResults(data);
    } catch (error) {
        console.error('Advanced search error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-container').innerHTML = 
            '<div class="no-results"><p>Error performing search. Please try again.</p></div>';
    }
}
