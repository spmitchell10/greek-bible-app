# Advanced Search Syntax Guide

## Overview

The Greek NT Bible Study App now includes an advanced search feature with a custom query syntax that allows you to search for Greek words with specific morphological features and proximity constraints.

## Basic Syntax

### Search Scope

**Entire New Testament:**
- `*` - Search the entire New Testament

**Specific Book(s):**
- `[Book] +` - Search in specific book(s)
- Format: `[Matt.] + query` or `[Matt., Mk, Lk] + query`
- Use commas to separate multiple books

### Morphology Codes
- `@` - Specify morphology codes after a word or token
- Format: `word@codes` or `[token]@codes`

### Multiple Terms
- `&` - Join multiple search terms together

### Proximity
- `W#` - Words within # distance (e.g., `W2` = within 2 words)

## Morphology Code Reference

### Part of Speech (Uppercase)
- `N` = noun
- `V` = verb
- `J` = adjective
- `D` = adverb
- `C` = conjunction
- `P` = preposition
- `R` = pronoun
- `T` = particle
- `I` = interjection

### Case (lowercase)
- `n` = nominative
- `g` = genitive
- `d` = dative
- `a` = accusative
- `v` = vocative

### Number (lowercase)
- `s` = singular
- `p` = plural

### Gender (lowercase)
- `m` = masculine
- `f` = feminine
- `u` = neuter

### Tense (lowercase)
- `p` = present
- `i` = imperfect
- `f` = future
- `a` = aorist
- `r` = perfect
- `l` = pluperfect

### Voice (Uppercase)
- `A` = active
- `M` = middle
- `P` = passive

### Mood (Uppercase)
- `I` = indicative
- `S` = subjunctive
- `O` = optative
- `M` = imperative
- `N` = infinitive
- `p` = participle

### Person (number)
- `1` = 1st person
- `2` = 2nd person
- `3` = 3rd person

## Book Abbreviations

You can use any of these abbreviations when specifying books:

- **Gospels & Acts**: Matt, Mark (Mk), Luke (Lk), John (Jn), Acts
- **Paul's Letters**: Rom, 1Cor, 2Cor, Gal, Eph, Phil, Col, 1Thess (1Th), 2Thess (2Th), 1Tim (1Ti), 2Tim (2Ti), Titus (Tit), Phlm (Phm)
- **General Letters**: Heb, Jas, 1Pet (1Pe), 2Pet (2Pe), 1John (1Jn), 2John (2Jn), 3John (3Jn), Jude (Jud)
- **Apocalypse**: Rev (Re)

You can also use full names like "Matthew", "Romans", "Hebrews", etc.

## Special Tokens

Instead of specifying a Greek word, you can use these tokens:
- `[article]` - Greek articles (ὁ, ἡ, τό, etc.)
- `[noun]` - Any noun
- `[verb]` - Any verb
- `[adjective]` - Any adjective
- `[pronoun]` - Any pronoun
- `[preposition]` - Any preposition
- `[conjunction]` - Any conjunction
- `[particle]` - Any particle
- `[adverb]` - Any adverb

## Example Queries

### Simple Searches

**Find all nouns in nominative singular:**
```
*[noun]@Nns
```

**Find all aorist active indicative verbs, 3rd person singular:**
```
*[verb]@aAI3s
```

**Find all present active indicative verbs, 3rd person singular:**
```
*[verb]@pAI3s
```

### Multi-Term Searches

**Find article followed immediately by a noun:**
```
*[article] & [noun]
```

**Find article followed by a noun in genitive singular:**
```
*[article] & [noun]@Nsg
```

**Find article followed by a noun in nominative singular:**
```
*[article] & [noun]@Nns
```

### Proximity Searches

**Find article within 2 words of a noun in genitive singular:**
```
*[article] & [noun]@Nsg W2
```

**Find article within 5 words of a noun:**
```
*[article] & [noun] W5
```

### Searching Specific Greek Words

**Find λόγος in nominative singular:**
```
*λόγος@Nns
```

**Find εἰμί as present active indicative, 3rd person singular:**
```
*εἰμί@pAI3s
```

**Find θεός in genitive singular:**
```
*θεός@Ngs
```

### Book-Specific Searches

**Find all aorist verbs in Matthew only:**
```
[Matt.] + [verb]@aAI3s
```

**Find all present verbs in the Synoptic Gospels:**
```
[Matt., Mk, Lk] + [verb]@pAI3s
```

**Find all nouns in Paul's letters:**
```
[Rom, 1Cor, 2Cor, Gal, Eph, Phil, Col] + [noun]
```

**Find article + noun pattern in John:**
```
[John] + [article] & [noun]@Nsg
```

**Find specific word in multiple books:**
```
[Matt., John] + λόγος@Nns
```

## Special Search Types

### Relative Search (Similar Vocabulary)

The **Relative Search** finds verses that contain similar vocabulary (lemmas) to a reference verse. This is useful for finding parallel passages or thematic connections.

**Syntax:**
```
*rel <verse reference>
rel <verse reference>
```

**Examples:**

**Find verses with similar vocabulary to Romans 8:1:**
```
*rel Rom. 8:1
```

**Find verses similar to John 3:16:**
```
rel John 3:16
```

**How it works:**
1. Extracts all unique lemmas (root words) from the source verse
2. Weights important words (verbs, nouns, adjectives, adverbs) more heavily than function words (articles, prepositions, pronouns)
3. Searches for verses containing these lemmas and scores them by similarity
4. Displays results with matching words highlighted in **bold**
5. Shows a word selection panel where you can include/exclude specific words and re-run the search

**Interactive Features:**
- **Word Selection Panel**: Choose which lemmas to include in the search
- **Filter Options**: Select all, none, or only important words
- **Re-search**: Adjust your search by selecting/deselecting words
- **Match Highlighting**: Matching words appear in bold in the results

### Inference Search (Similar Syntax)

The **Inference Search** finds verses with similar grammatical structure to a reference verse. This is different from relative search—it looks for syntactic patterns, not just shared vocabulary.

**Syntax:**
```
*inf <verse reference>
inf <verse reference>
```

**Examples:**

**Find verses with similar syntax to Romans 8:1:**
```
*inf Rom. 8:1
```

**Find verses with similar structure to John 1:1:**
```
inf John 1:1
```

**How it works:**
1. Extracts the part-of-speech (POS) sequence from the source verse
   - Example: `[noun] → [particle] → [adverb] → [noun] → [article] → [preposition]`
2. Compares this pattern to every verse in the selected corpus
3. Uses sequence matching algorithms to calculate similarity (0-100%)
4. Returns verses ranked by similarity percentage
5. Shows the syntactic pattern for both source and matching verses

**Use Cases:**
- **Finding structural parallels**: Identify verses with similar sentence construction
- **Grammatical analysis**: Study how Greek syntax varies across similar patterns
- **Discourse structure**: Find verses that follow similar rhetorical patterns
- **Translation study**: Compare how different contexts use similar grammatical structures

**Result Details:**
- **Similarity Percentage**: How closely the pattern matches (e.g., 85% similar)
- **Edit Distance**: Number of changes needed to transform one pattern to another
- **Length Difference**: Difference in number of words between verses
- **Pattern Display**: Shows the POS sequence for easy comparison

**Corpus Selection:**
- Use `*` before `inf` to search the entire New Testament (NT)
- Corpus checkboxes allow filtering between NT and LXX (when available)

## Tips

1. **Case Sensitivity**: POS codes use UPPERCASE (N, V, J), while case/number/gender use lowercase (n, s, g)
2. **Voice and Mood**: Voice uses UPPERCASE (A, M, P), most moods use UPPERCASE (I, S, O, M, N) except participle (p)
3. **Order Matters**: Codes are processed in order: POS, tense, voice, mood, person, case, number, gender
4. **Proximity Default**: Without `W#`, terms must be adjacent (next word)
5. **Result Limit**: Searches are limited to 500 results for performance
6. **Book Filtering**: Use `[Book] +` instead of `*` to search specific books. Separate multiple books with commas.
7. **Abbreviations**: You can use short forms (Matt, Mk) or full names (Matthew, Mark) for books

## How to Use

1. Open the app in your browser
2. Find the "Advanced Search" section at the top
3. Enter your query using the syntax above
4. Click "Search" or press Enter
5. Click the "?" button to see the help panel with examples

## Notes

- The morphology codes are designed to be unambiguous - each character maps to exactly one feature
- You can combine as many morphology codes as needed (e.g., `VpAI3s` = verb, present, active, indicative, 3rd, singular)
- Special tokens like `[article]` can also have morphology codes: `[article]@gs` (article, genitive, singular)
