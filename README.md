# Jazz standards database

The goal of this project is to create a canonical, accurate, and standardized datase of jazz standards (particularly the 400 standards in The Real Book Volume 1 -- Sixth Edition) with key, tempo, style, composer, year, form, tonality, movement, and difficulty information in json and excel formats

This database will be integrated with other applications to help students track their progress and find tunes to learn that match their practice  interests. More fields may be added later such as extended descriptions list of notable recordings and streaming links, first appearance (album or musical), lyrics, references in pop culture, and/or additional reading links 

The database will also be used for data analsis of the standards:

Currently the database is limited to the 400 standards of The Real Book Volume I Sixth Edition, is incomplete, and is spread across multiple different databases sourced via different techniques such as scraper, LLM, and deep research

# Phase 1: The Real Book Volume 1 Sixth Edition
[x] Generate json lists using llm, deep research, and scrape methods
[] Create scripts for conversion to other formats
[] Choose a most accurate list or synthesize lists into a master list
[] Fill in missing fields
[] Create accuracy report (review 20 randomly chosen standards manually)

# Phase 2: jazzstandards.com Top 300 Standards
[] Create a master list that will serve as single source of truth for other lists adding a new json field "included_in" for books/lists standards are featured in
[] Scrape jazzstandards.com top 300 standards
[] For duplicate entries, add "jazzstandards.com Top 300" to "included_in" fields
[] For unique entries generate json lists using llm, deep research, and scrape methods
[] Consolidate lists from previous step into single list
[] Merge de-duped list into master list
[] Create way to view or generate lists from master list

NOTE: Past this point the methodology should be reconsidered. Phases 3-12 should not take as long as Phases 1 & 2 and by the completion of Phase 2 all the tooling scripts needed to make this process quick should be in place or automated. https://www.seventhstring.com/fbindex.html seems to have already compiled a database of all of the entries in these books sortable by books they appear in perhaps this database can be found or scraped. It is unlikely to contain all of the fields, so those will still have to be generated

# Phase 3: The Real Book Editions 1-5

# Phase 4: New Real Book Volume 1 - Chuck Sher

# Phase 5: The Real Book Volumes II-VI

# Phase 6: New Real Book Volumes II-III

# Phase 7: jazzstandards.com top 1000

# Phase 7: Remaining The Real Book entries

# Phase 8: Additional Chuck Sher fake books

# Phase 9: Additional Hal Leonard fake books

# Phase 10: jazzstandards.com top 1000

# Phase 11: Frank Mantooth fake books

# Phase 12: Warner Bros fake books

# Phase 13: Professional Pianist's Fakebook - Lee Evans

# Phase 14: Wise Publications fake books

# Phase 16: Additional Entries
