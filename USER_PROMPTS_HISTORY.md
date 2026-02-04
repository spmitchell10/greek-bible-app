# User Prompts History - Greek Bible Study App Development

This document contains all user prompts from the development session of the Greek Bible Study App.

---

## Session Start - Initial Setup

### 1. Project Recognition
> Do you remember this app?

### 2. Requirements Installation
> What is the python command for installing the requirements?

### 3. Missing Module Error
> I'm getting this error when trying to initialize the database: ModuleNotFoundError: No module named 'requests'

### 4. Installation Error
> I'm getting this error when I try to install the requirements: @powershell (551-553)

---

## Initial Issues & Debugging

### 5. Dropdown Population Issue
> It doesn't look like the dropdowns for the app are not populated.

### 6. Search Not Returning Results
> When I do a search nothing is returning from the database.

---

## Advanced Search Feature Request

### 7. Search Bar Feature Request (Part 1)
> I want to add a search bar. Here are the features I want for searching.
> - I want to be able to search a greek lemma followed by search options.
> - An example would be *λόγος@nsg. So that would search for all instances of λόγος in the entire New Testament indicated by the wildcard character *. And specifically looking for a noun = n, singular = s, and genitive = g. The @ character is there to specify or start the search options after a word.
> - For a verb it would be *εἰμί@vaAi3s. That would search for all instances of εἰμί in the entire New Testament indicated by the wildcard *. And specifically look for a verb =v, aorist = a, active =a, indicative = i, third person = 3, singular = s.
> - All parts of speech and morphological features must have a single letter or number option to search by. Example: noun = n, verb = v, aorist tense = a, present tense = p, indicative mood = i, subjunctive mood = s, passive voice = P, active voice = A, genetive noun = g, etc. The '@' is what would come after the greek word and signify a search.

### 8. Multi-Word Search & Proximity (Part 2)
> Now if I wanted to search for 2 words I would join them together with &. Example: *[article] & λόγος@nsg. So that would search for all instances (indicated by the wildcard '*') instances of an article = [article], and = &, the word λόγος that is a noun = n, singular = s, and genitive = g. This search would return any instance of an article followed directly by a noun. But what if I wanted to search for an article and a noun that occur within 2 words of each other, or 5, or any number of words? For that, I would want to add to my search option. Example: *[article] & λόγος@nsg W2. For this search it would look for all instances of an article, plus the noun, within = W, 2 words of one another = 2.

### 9. Book Filtering (Part 3)
> Now if I wanted to search for a word in a particular book instead of using the wildcard '*'. In that search, I want to specify the book or books at the beginning. Example: [Matt.] + [verb]@aAI3s. That would search for all of the instances of all present active indicative verbs, 3rd person singular in the book of Matthew = [Matt.]. The plus sign designates the word search after the book is specified. Now if I wanted to search in multiple books it would look like: [Matt., Mk, Lk] + [verb]@aAI3s. That would look for all instances of present active indicative verbs, 3rd person singular in the book of Matthew, Mark, and Luke.

---

## Code Cleanup

### 10. Test Files Removal
> Do we need all of the test files? If not can we delete them?

---

## LXX Integration

### 11. LXX Search Feature
> Now I would like search the Septuagent (LXX) and the Greek New Testament. Can you add the option to search the Septuagent (LXX)? And below the search bar add a check box for what corpus I am searching in. Example: a check box for the Greek New Testament, and a check box for the Septuagent (LXX). If I have both checked, my search includes both. If I only have the Septuagent (LXX) checked, it only searches in the Septuagent.

### 12. Disable LXX Checkbox
> Disable the checkbox for now.

---

## GitHub Integration Attempts

### 13. First GitHub Connection Attempt
> Can you link this project with my github? https://github.com/spmitchell10

### 14. Repository Created
> I created the repo: https://github.com/spmitchell10/greek-bible-app

### 15. Pause GitHub Setup (First Time)
> Let's stop for now on the github connection.

### 16. Lemma Search Issue
> It looks like it's not searching by lemma. For instance when I search for ἀγάπη@gsf it should return every instance of ἀγάπης since ἀγάπης is the genitive singular feminine declension of ἀγάπη.

### 17. Resume Work
> Pick back up where you left off.

### 18. Second GitHub Connection Attempt
> Ok. Let's set this up in github. Here is the repo I created for this: https://github.com/spmitchell10/greek-bible-app.git

### 19. SSH Key Setup
> Let's do the SSH key setup.

### 20. Pause GitHub Setup (Second Time)
> Let's stop for now on the github connection.

### 21. Lemma Search Issue (Repeated)
> It looks like it's not searching by lemma. For instance when I search for ἀγάπη@gsf it should return every instance of ἀγάπης since ἀγάπης is the genitive singular feminine declension of ἀγάπη.

### 22. Resume Work (Repeated)
> Pick back up where you left off.

---

## LXX Importer Development

### 23. Build LXX Importer (First Request)
> Build the full LXX importer

### 24. Corpora Error
> I'm getting this error: "Error: name 'corpora' is not defined" when I try to run this search: [Matt., Rom.] + [article] & [noun] & [noun]@gs

### 25. Gender Search Issue
> It doesn't look like I'm able to search a noun when I add gender. For this returns data: *[noun]@gs, but this does not return data: *[noun]@gsm. When I add the m for Masculine, it does not return anything.

### 26. Hosting Platform Question
> If I wanted to host this app, what platform would you recommend

### 27. LXX Data Source Found
> I found a download of the Septuagint (LXX). It's now on my user drive here: C:\Users\stmitchell\LXX. Is this something I can use for the project?

### 28. CCAT Files Search
> Can you find the original CCAT plain text files online

### 29. Build LXX Importer (Second Request)
> Build the full LXX importer

### 30. Ready to Run Importer
> Ok. I'm ready to run the importer

### 31. Import Progress Check
> Where did the import leave off.

### 32. Installer Failure
> Why did the installer fail?

---

## Relative Search Feature

### 33. Relative Search Request
> Ok. Now I want to add a more complex search option. I want to add a relative search option. rel = relative. For this search, we will take all of the words in a given verse and look for those same words in other verses. For instance, if I search *rel Rom. 8:1, the results should be all of the verses in the Greek New Testament or the LXX that contain the same words (use Lemma). Don't take into account sequence of words, just if they appear. However, each part of speech should be more important in the search than others. Verbs, adverbs, adjectives and nouns should be weighted more than prepositions or pronouns. So, if we search *rel Rom. 8:1, and there are verses that contain the same verbs and nouns, but no other parts of speech we would still want to display those. When we execute this 'relative' search, we need to give the user the option to include all of the words in a search or only some of them. Example, if we search *rel Rom. 8:1, we need to execute the search with more weight (think importance) on the verbs and nouns, but also give the user the option to include other parts of speech and re-run the search. This should be a checkbox option that breaks down the words in the verse and allows the user to check or uncheck words and re-run the 'rel' search.

### 34. Integrate into Advanced Search
> I like the search output, but I would prefer it not be a separate search bar. Can it be part of the 'Advanced Search' search bar? To activate a relative search, a user would use 'rel' as the trigger. For instance, *rel John 1:1 would perform the relative search. Does that make sense?

### 35. Bold Matching Words
> Ok. Now for the words that do match in the output, can you put those words in bold so they are easier to see?

### 36. Duplicate Words Issue
> This is great. I do see one issue. In the 'Select which words to include in the search:' section, there is quite a few duplicate words. That list should not contain any duplicate words and there should just be lemmas listed to check or uncheck.

### 37. Scrolling Issue
> Another issue I am having is that once I execute the search, only the output list of verses scrolls. The right hand side doesn't move. However, if I need to check or uncheck words in the 'rel' search I need to be able to see them. Right now, I can't scroll down to see the words listed.

### 38. Too Many Words Returned
> Ok. There are still way too many words being returned in the 'Select which words to include in the search:' section. I just ran "*rel John 1:1" and had 26 words returned to check or uncheck. There are only 17 words total in John 1:1 and only 8 unique words. Can you check the logic on the relative search?

### 39. Database Rebuild Confirmation
> Yes do the rebuild process

### 40. Rebuild Verification
> You might want to run that again? Looks like there was an issue.

---

## Documentation & Architecture

### 41. Architecture Question
> What is the architecture of this app so far?

### 42. Push Changes to GitHub
> lets push all of the changes to the repo

---

## Reading View Feature

### 43. Reading View Request
> Ok. I would like to now add the ability to read the Greek New Testament. Above the Advanced Search, can you add the ability to choose the Book, Chapter, and Verses to read from. Display in on the right side like we are doing for the search results. For instance, if I choose Matthew 5, you would display all of the Greek of Matthew 5 so I can read it. But, since I want it to have the ability to scroll up and down to read what comes before and after, you will need to display what comes before and after a selected text. So, if I choose Matthew 5, I should see Matthew 5, but have the ability to scroll up and see the text of Matthew 4 and 3, and so on. Likewise, Matthew 6, 7, 8, etc.
> 
> Would you be able to do that?

### 44. Display Mode Options
> Instead of displaying it verse by verse, can I have the option to choose verse by verse display or paragraph?

### 45. Push Reading View Changes
> Ok. Let's push all of the changes to github.

### 46. Architecture Documentation Request
> Can you make a Markdown file to describe the architecture of this app?

---

## Discourse Features Planning

### 47. Discourse Features Request
> I would like to add Discourse Greek Grammar features. Here is an example of some of the key features: https://scholars.sil.org/sites/scholars/files/stephen_h_levinsohn/bart/enhancedbartdisplaynt.pdf .
> 
> And here is how those features are used on the book of Matthew: https://scholars.sil.org/sites/scholars/files/stephen_h_levinsohn/bart/matthewbart.pdf 
> 
> How can I implement this into this project? Recommend suggestions.

### 48. Matthew Example PDF Question
> Are you able to see this link as an example of how this is done in Matthew? https://scholars.sil.org/sites/scholars/files/stephen_h_levinsohn/bart/matthewbart.pdf

### 49. Prompts History Request
> Create a Markdown file with all of the prompts I have used so far.

---

## Summary Statistics

- **Total Prompts**: 49
- **Categories**:
  - Initial Setup & Debugging: 6 prompts
  - Advanced Search Feature: 3 prompts
  - Code Cleanup: 1 prompt
  - LXX Integration: 10 prompts
  - GitHub Integration: 8 prompts
  - Relative Search Feature: 8 prompts
  - Documentation: 2 prompts
  - Reading View Feature: 3 prompts
  - Discourse Features: 3 prompts
  - Meta (this file): 1 prompt

---

## Key Development Milestones

1. ✅ Initial app setup and database population
2. ✅ Advanced search with custom syntax (*λόγος@Nsg)
3. ✅ Multi-word and proximity search (& and W#)
4. ✅ Book filtering ([Matt.] + ...)
5. ✅ LXX (Septuagint) integration
6. ✅ Relative search for parallel passages (*rel Rom. 8:1)
7. ✅ Reading view with infinite scroll
8. ✅ Dual display modes (verse-by-verse and paragraph)
9. ✅ Comprehensive architecture documentation
10. 🔄 Discourse features planning (in progress)

---

*Generated: 2026-02-04*
*Project: Greek Bible Study App*
*Repository: https://github.com/spmitchell10/greek-bible-app*
