# Discourse Features Implementation Plan

## Overview
Add Stephen Levinsohn's discourse grammar features to the Greek Bible Study App, based on the BART (Bible Analysis and Research Tool) enhanced displays.

**Reference**: [BART Display Enhanced for Discourse Features](https://scholars.sil.org/sites/scholars/files/stephen_h_levinsohn/bart/enhancedbartdisplaynt.pdf)

---

## Implementation Phases

### Phase 1: Database Schema Enhancement

#### New Table: `discourse_features`
```sql
CREATE TABLE discourse_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_code TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    word_position INTEGER NOT NULL,
    corpus TEXT NOT NULL DEFAULT 'NT',
    
    -- Clause Structure (Indentation)
    clause_level TEXT,              -- 'pre-nuclear', 'nuclear', 'post-nuclear'
    clause_type TEXT,               -- 'main', 'subordinate', 'participial'
    
    -- Constituent Order
    constituent_position TEXT,       -- 'P1', 'P2', 'verb-final', 'postposed'
    constituent_function TEXT,       -- 'Top', 'Sit', 'Art', 'Focus', 'Split', 'Emb', 'Constit', 'Incorp', 'L-Dis', 'T-H', 'DFE', 'Cata', 'CataRef', 'TopGen'
    
    -- Speech Marking
    speech_type TEXT,               -- 'direct', 'embedded', 'ot_quote'
    speech_level INTEGER,           -- 0, 1, 2, 3... for nesting depth
    
    -- Thematic Features
    encoding_type TEXT,             -- 'over-encoded', 'default', 'under-encoded'
    thematic_prominence TEXT,       -- 'Top+', 'Th+' (center of attention)
    
    -- Highlighting Devices
    highlighting_device TEXT,       -- 'presentative', 'egeneto_temporal', 'historical_present', 'intensified_verb'
    
    -- Notes
    discourse_notes TEXT,           -- Additional comments
    
    FOREIGN KEY (book_code, chapter, verse, word_position, corpus) 
        REFERENCES words(book_code, chapter, verse, word_position, corpus)
);
```

#### Indexes
```sql
CREATE INDEX idx_discourse_location ON discourse_features(book_code, chapter, verse, corpus);
CREATE INDEX idx_discourse_features ON discourse_features(constituent_function, speech_type, highlighting_device);
```

---

### Phase 2: Data Acquisition

#### Option A: Manual Annotation (Small Scale)
- Start with a single chapter (e.g., Matthew 5)
- Create an annotation interface
- Manually tag discourse features
- Good for testing and proof-of-concept

#### Option B: Import from Existing Datasets
**Potential Sources:**
1. **Lexham Discourse Greek New Testament** (LOGOS Bible Software)
   - Commercial dataset, may require licensing
   - Most complete source available
   
2. **OpenText.org Discourse Annotations**
   - Academic project with some publicly available data
   - Check: https://opentext.org/
   
3. **Contact Stephen Levinsohn**
   - Email: stephen_levinsohn@sil.org
   - Request permission to use BART annotation data
   - Explain educational/non-commercial purpose

4. **SIL Resources**
   - Check SIL International's resource archives
   - Some BART displays available as PDFs (could be parsed)

#### Option C: Rule-Based Annotation (Partial)
Some features can be detected algorithmically:
- **Historical Present**: Detect present tense verbs in past-tense narratives
- **Constituent Order**: Analyze word order patterns (SV vs VS)
- **Presentatives**: Tag ἰδού, ἴδε automatically
- **OT Quotes**: Cross-reference with OT citation databases

---

### Phase 3: UI Enhancements

#### Reading View Additions

**Control Panel:**
```
📖 Display Options:
   ☐ Verse by Verse
   ☑ Paragraph
   
🎨 Discourse Features:
   ☑ Show Clause Structure (indentation)
   ☑ Highlight Speech (colors)
   ☑ Mark Constituent Order (labels)
   ☑ Show Thematic Prominence (underlining)
   ☑ Highlight Devices (background colors)
   
🔍 Feature Filter:
   [All] [P1/P2] [Speech] [Historical Present] [Custom...]
```

#### Visual Encoding System

Based on Levinsohn's conventions:

**Colors:**
- **Blue background**: Direct speech
- **Magenta/Pink background**: Embedded speech
- **Cyan/Turquoise background**: OT quotations
- **Yellow background**: Over-encoded references
- **Light green background**: Highlighting devices (ἰδού, ἐγένετο)

**Boxes:**
- **Solid red box**: Focal constituents (P2)
- **Dotted red box**: Clause-final focal constituents / Cataphoric references
- **Dashed red box**: Intensified verbs
- **Green box**: Historical present verbs
- **Dark green box**: Negative pro-forms

**Text Formatting:**
- **Underlined**: P1 constituents (topical subjects, points of departure)
- **Dotted underline**: Preposed pronominal genitives
- **Italics**: Tail-head linkage
- **Bold**: (Reserved for search matches)

**Labels:**
- `Top` - Topical subject/point of departure
- `Sit` - Situational point of departure
- `Art` - Articular pronoun
- `Focus` - Focal prominence
- `Split` - Split focal constituent
- `Emb` - Embedded focal constituent
- `DFE` - Default Focus Expression
- `Cata` - Cataphoric expression
- `T-H` - Tail-head linkage
- `Top+` - Thematic prominence
- `Th+` - Thematically prominent

---

### Phase 4: API Enhancements

#### New Endpoint: `/api/read-with-discourse`

**Request:**
```json
{
  "book_code": "01",
  "chapter": 5,
  "corpus": "NT",
  "context": 1,
  "discourse_features": {
    "clause_structure": true,
    "constituent_order": true,
    "speech_marking": true,
    "thematic_prominence": true,
    "highlighting": true
  }
}
```

**Response:**
```json
{
  "chapters": [
    {
      "chapter": 5,
      "verses": [
        {
          "verse": 1,
          "words": [
            {
              "word": "Ἰδὼν",
              "lemma": "ὁράω",
              "position": 1,
              "discourse": {
                "clause_level": "pre-nuclear",
                "clause_type": "participial",
                "constituent_function": "T-H"
              }
            },
            {
              "word": "τοὺς",
              "position": 2,
              "discourse": {
                "clause_level": "pre-nuclear"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

#### Enhanced Search with Discourse Features

**Query Examples:**
```
*[verb]@hp               # Search for historical present verbs
*ἰδού                    # Find all presentatives
*[speech=direct]         # Find direct speech
*[P2] & [noun]          # Find nouns in P2 (focal) position
```

---

### Phase 5: Feature Display Implementation

#### Frontend JavaScript Logic

```javascript
function renderWordWithDiscourse(word, discourseData) {
    let html = '';
    let classes = [];
    let styles = {};
    let tooltip = [];
    
    // Clause Structure (indentation handled at verse level)
    
    // Speech Marking (background colors)
    if (discourseData.speech_type === 'direct') {
        styles.backgroundColor = 'rgba(52, 152, 219, 0.2)'; // Blue
        tooltip.push('Direct Speech');
    } else if (discourseData.speech_type === 'embedded') {
        styles.backgroundColor = 'rgba(219, 52, 152, 0.2)'; // Magenta
        tooltip.push('Embedded Speech');
    } else if (discourseData.speech_type === 'ot_quote') {
        styles.backgroundColor = 'rgba(52, 219, 219, 0.2)'; // Cyan
        tooltip.push('OT Quotation');
    }
    
    // Over-encoding
    if (discourseData.encoding_type === 'over-encoded') {
        styles.backgroundColor = 'rgba(255, 255, 0, 0.3)'; // Yellow
        tooltip.push('Over-encoded Reference');
    }
    
    // Highlighting Devices
    if (discourseData.highlighting_device === 'presentative') {
        styles.backgroundColor = 'rgba(144, 238, 144, 0.4)'; // Light green
        tooltip.push('Presentative');
    } else if (discourseData.highlighting_device === 'historical_present') {
        classes.push('historical-present');
        tooltip.push('Historical Present');
    }
    
    // Constituent Order (boxes and labels)
    let boxClass = null;
    if (discourseData.constituent_position === 'P2' && 
        discourseData.constituent_function === 'Focus') {
        boxClass = 'solid-red-box';
        tooltip.push('Focal Prominence (P2)');
    } else if (discourseData.constituent_function === 'DFE') {
        boxClass = 'dotted-red-box';
        tooltip.push('Default Focus Expression');
    }
    
    // Underlining (P1 constituents)
    if (discourseData.constituent_position === 'P1') {
        classes.push('underlined');
    }
    
    // Build HTML
    if (boxClass) html += `<span class="${boxClass}">`;
    
    html += `<span class="greek-word ${classes.join(' ')}" 
                  style="${Object.entries(styles).map(([k,v]) => `${k}:${v}`).join(';')}"
                  title="${tooltip.join(' | ')}">`;
    html += word;
    html += '</span>';
    
    // Add discourse label if present
    if (discourseData.constituent_function) {
        html += `<sup class="discourse-label">${discourseData.constituent_function}</sup>`;
    }
    
    if (boxClass) html += '</span>';
    
    return html;
}
```

#### CSS for Discourse Features

```css
/* Speech Marking */
.speech-direct { background-color: rgba(52, 152, 219, 0.2); }
.speech-embedded { background-color: rgba(219, 52, 152, 0.2); }
.speech-ot-quote { background-color: rgba(52, 219, 219, 0.2); }

/* Over-encoding */
.over-encoded { background-color: rgba(255, 255, 0, 0.3); }

/* Highlighting Devices */
.presentative { background-color: rgba(144, 238, 144, 0.4); }
.historical-present {
    border: 2px solid #90EE90;
    padding: 2px 4px;
    border-radius: 4px;
}

/* Boxes */
.solid-red-box {
    border: 2px solid #e74c3c;
    padding: 2px 4px;
    border-radius: 3px;
    display: inline-block;
}

.dotted-red-box {
    border: 2px dotted #e74c3c;
    padding: 2px 4px;
    border-radius: 3px;
    display: inline-block;
}

.dashed-red-box {
    border: 2px dashed #e74c3c;
    padding: 2px 4px;
    border-radius: 3px;
    display: inline-block;
}

.green-box {
    border: 2px solid #90EE90;
    padding: 2px 4px;
    border-radius: 3px;
    display: inline-block;
}

/* Text Formatting */
.underlined {
    text-decoration: underline;
    text-decoration-color: #2c3e50;
}

.dotted-underline {
    text-decoration: underline;
    text-decoration-style: dotted;
}

.tail-head {
    font-style: italic;
}

/* Discourse Labels */
.discourse-label {
    font-size: 0.7em;
    color: #e74c3c;
    font-weight: 600;
    margin-left: 2px;
}

/* Clause Structure (Indentation) */
.clause-pre-nuclear { margin-left: 0; }
.clause-nuclear { margin-left: 20px; }
.clause-post-nuclear { margin-left: 40px; }
```

---

### Phase 6: Documentation & Help

#### Discourse Features Help Section

Add to the UI:

```html
<div class="discourse-help">
    <h3>📚 Discourse Features Guide</h3>
    
    <h4>Color Coding:</h4>
    <ul>
        <li><span class="example speech-direct">Blue</span> - Direct speech</li>
        <li><span class="example speech-embedded">Pink</span> - Embedded speech</li>
        <li><span class="example speech-ot-quote">Cyan</span> - Old Testament quotation</li>
        <li><span class="example over-encoded">Yellow</span> - Over-encoded reference</li>
        <li><span class="example presentative">Light green</span> - Highlighting device</li>
    </ul>
    
    <h4>Labels:</h4>
    <ul>
        <li><strong>Top</strong> - Topical subject or point of departure</li>
        <li><strong>Focus</strong> - Constituent given focal prominence</li>
        <li><strong>T-H</strong> - Tail-head linkage</li>
        <li><strong>DFE</strong> - Default focus expression (clause-final)</li>
    </ul>
    
    <h4>Learn More:</h4>
    <p>Based on Stephen Levinsohn's discourse analysis framework. 
    See <a href="https://www.sil.org/resources/archives/68643">NARR</a> 
    and <a href="https://www.sil.org/resources/publications/entry/8935">DFNTG</a>.</p>
</div>
```

---

## Recommended Implementation Order

### **Minimal Viable Product (MVP):**
1. ✅ Add basic `discourse_features` table
2. ✅ Manually annotate Matthew 5 as proof-of-concept
3. ✅ Implement speech marking (colors) only
4. ✅ Add UI toggle for discourse features
5. ✅ Test with users

### **Phase 2 (Core Features):**
6. Add constituent order marking (P1/P2, boxes, labels)
7. Implement historical present highlighting
8. Add presentatives (ἰδού) marking
9. Expand to Matthew 1-7 (Sermon on the Mount)

### **Phase 3 (Advanced Features):**
10. Add clause structure indentation
11. Implement over-encoding marking
12. Add thematic prominence
13. Expand to full book (Matthew)

### **Phase 4 (Full Implementation):**
14. Contact Levinsohn/SIL for data partnership
15. Import complete BART annotations
16. Extend to all NT books
17. Add search by discourse features

---

## Technical Considerations

### Performance
- **Caching**: Cache discourse-annotated chapters in memory
- **Lazy Loading**: Only load discourse features when toggle is enabled
- **Database Indexes**: Ensure fast lookup by book/chapter/verse

### Data Integrity
- **Validation**: Ensure discourse features align with word positions
- **Versioning**: Track annotation version/source
- **Conflict Resolution**: Handle multiple possible annotations

### User Experience
- **Progressive Disclosure**: Start with simple features, reveal complexity gradually
- **Tooltips**: Explain each discourse feature on hover
- **Legend**: Always visible legend for color/symbol meanings
- **Performance**: Ensure rendering doesn't slow down reading view

---

## Alternative: Simplified Approach

If full BART implementation is too complex, start with a **subset of high-value features**:

### **Tier 1: Essential** (Easy to implement)
1. ✅ **Speech Marking** - Color-code direct/embedded speech
2. ✅ **OT Quotations** - Highlight quotations
3. ✅ **Presentatives** - Mark ἰδού, ἴδε
4. ✅ **Historical Present** - Detect and highlight

### **Tier 2: Valuable** (Moderate difficulty)
5. **Constituent Order** - Basic P1/P2 detection
6. **Focal Prominence** - Mark clause-final focus
7. **Clause Structure** - Simple indentation

### **Tier 3: Advanced** (Complex, requires expertise)
8. Over-encoding
9. Thematic prominence
10. Tail-head linkage
11. All P1 functions (Top, Sit, Art, etc.)

---

## Resources & References

### Academic Resources
- **Levinsohn's Materials**: https://www.sil.org/resources/search/contributor/levinsohn-stephen-h
- **DFNTG (Discourse Features of New Testament Greek)**: https://www.sil.org/resources/publications/entry/8935
- **OpenText.org**: https://opentext.org/
- **Lexham Discourse Greek NT**: https://www.logos.com/product/27339/

### Technical Resources
- **MorphGNT**: Already integrated (morphology data)
- **nestle1904**: Public domain Nestle 1904 Greek NT with additional tagging
- **PROIEL Treebank**: Dependency-parsed Greek NT (could derive some discourse features)

### Contact
- Stephen Levinsohn: stephen_levinsohn@sil.org (for BART data)
- SIL International: Ask about educational use licensing

---

## Expected Benefits

### For Students
- **Visual Learning**: See grammar patterns visually
- **Discourse Awareness**: Understand how Greek communicates beyond morphology
- **Translation Help**: Make better translation decisions based on discourse function

### For Scholars
- **Research Tool**: Analyze discourse patterns across books
- **Comparative Studies**: Compare Matthew's vs. John's use of historical present
- **Statistical Analysis**: Query discourse feature frequencies

### For Your App
- **Unique Value**: No other free tool offers this
- **Educational Focus**: Perfect for seminaries and Bible colleges
- **Research Platform**: Could become a standard tool for Greek discourse studies

---

## Next Steps

1. **Decide on scope**: MVP vs. full implementation?
2. **Secure data**: Contact Levinsohn/SIL or start manual annotation?
3. **Create prototype**: Implement Matthew 5 as proof-of-concept
4. **User feedback**: Test with Greek students/scholars
5. **Iterate**: Expand based on feedback

Would you like me to start with the MVP implementation?
