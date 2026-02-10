# Part of Speech Color Reference

This document shows the color scheme used for syntactic highlighting in inference search results.

## Color Scheme

| Part of Speech | Color | Example |
|----------------|-------|---------|
| **Noun** | 🔵 Blue | `λόγος` (word) |
| **Verb** | 🔴 Red | `λέγω` (I say) |
| **Adjective** | 🟢 Green | `ἀγαθός` (good) |
| **Adverb** | 🟣 Purple | `νῦν` (now) |
| **Pronoun** | 🟡 Yellow/Gold | `αὐτός` (he/she/it) |
| **Article** | 🟠 Orange | `ὁ, ἡ, τό` (the) |
| **Preposition** | 🔷 Teal | `ἐν` (in) |
| **Conjunction** | ⚪ Gray | `καί` (and) |
| **Particle** | ⚫ Dark Gray | `ἄν` (particle) |
| **Interjection** | 🟧 Deep Orange | `ἰδού` (behold!) |
| **Unknown** | ⬜ Light Gray | (fallback) |

## Visual Design

Each word and pattern element is highlighted with:
- **Background color**: Semi-transparent version of the POS color (25% opacity)
- **Padding**: 2px vertical, 6px horizontal
- **Border radius**: 4px for rounded corners
- **Font weight**: 500 (medium) for subtle emphasis

## Usage in Inference Search

When you perform an inference search (e.g., `*inf Rom. 8:1`), the results display:

1. **Source Verse Text**: Each Greek word is highlighted with its POS color
2. **Source Pattern**: Each POS label in the pattern is highlighted with its color
3. **Result Verses**: Each matched verse shows the same highlighting
4. **Result Patterns**: Pattern sequences are color-coded to match

## Example

For Romans 8:1: *οὐδὲν ἄρα νῦν κατάκριμα τοῖς ἐν Χριστῷ Ἰησοῦ*

You would see:
- `οὐδὲν` (adjective) - 🟢 Green
- `ἄρα` (conjunction) - ⚪ Gray
- `νῦν` (adverb) - 🟣 Purple
- `κατάκριμα` (noun) - 🔵 Blue
- `τοῖς` (article) - 🟠 Orange
- `ἐν` (preposition) - 🔷 Teal
- `Χριστῷ` (noun) - 🔵 Blue
- `Ἰησοῦ` (noun) - 🔵 Blue

And the pattern would show:
🟢 **adjective** → ⚪ **conjunction** → 🟣 **adverb** → 🔵 **noun** → 🟠 **article** → 🔷 **preposition** → 🔵 **noun** → 🔵 **noun**

## Benefits

This color-coding makes it easy to:
- Quickly identify parts of speech at a glance
- Compare syntactic structures visually
- Understand how sentence patterns work
- See similarities between verses immediately
- Learn Greek grammar through visual patterns

## Accessibility

The colors were chosen to:
- Be distinguishable from each other
- Work well with the light background
- Not be too bright or distracting
- Use sufficient opacity for readability
- Maintain good contrast with black text
