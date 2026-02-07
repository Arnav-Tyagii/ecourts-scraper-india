An advanced Python-based automation tool designed to crawl and extract comprehensive case data from the Indian eCourts services portal. This unified version combines multi-district looping with automated CAPTCHA solving for a completely "hands-off" scraping experience.

🚀 Key Features
Dynamic Discovery: Automatically identifies and iterates through all Districts and Court Complexes within a state.

Automated CAPTCHA Solver: Integrated Pytesseract OCR with character whitelisting to handle security codes programmatically.

Deep Data Extraction: Scrapes 11+ fields per case, including CNR numbers, hearing dates, case stages, petitioner/respondent details, and legal acts/sections.

High Stability: Built with 20-second explicit waits and JavaScript-based interaction to handle slow portal responses and prevent session crashes.

Auto-Export: Automatically compiles all results into ecourts_detailed_data.csv upon completion or interruption.

