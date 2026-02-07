eCourts Scraper
===============

A Python-based automation tool built with **Selenium** and **Pytesseract** to scrape case details from the Indian eCourts services portal. This script navigates through state, district, and court complex hierarchies to extract comprehensive case information based on party names.

🚀 Features
-----------

*   **Automated Navigation**: Systematically iterates through all districts and court complexes for a given state.
    
*   **CAPTCHA Solving**: Utilizes OCR (Optical Character Recognition) via Tesseract to solve portal challenges automatically.
    
*   **Deep Extraction**: Goes beyond the summary table to click into individual cases and extract:
    
    *   CNR Number
        
    *   Hearing Dates (First & Next)
        
    *   Case Stage
        
    *   Petitioner/Respondent details
        
    *   Acts and Sections
        
*   **Data Export**: Saves all extracted records into a structured ecourts\_detailed\_data.csv file.
    

🛠️ Prerequisites
-----------------

Before running the script, ensure you have the following installed:

1.  **Python 3.x**
    
2.  **Google Chrome Browser**
    
3.  **Tesseract OCR Engine**:
    
    *   Download and install from [Tesseract at UB Mannheim](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki&authuser=1).
        
    *   Pythonpytesseract.pytesseract.tesseract\_cmd = r"C:\\Tesseract\\Tesseract-OCR\\tesseract.exe"
        

📦 Installation
---------------

1.  Bashgit clone https://github.com/yourusername/ecourts-scraper.gitcd ecourts-scraper
    
2.  Bashpip install pandas pytesseract selenium webdriver-manager Pillow
    

🔧 Configuration & Usage
------------------------

1.  Pythonif \_\_name\_\_ == "\_\_main\_\_": scrape\_ecourts(party\_name="Your Party Name", year="2024")
    
2.  Pythonstate\_sel.select\_by\_visible\_text("Your State")
    
3.  Bashpython ecourts-scraper.py
    

📊 Output
---------

The script generates a CSV file named ecourts\_detailed\_data.csv containing the following columns:

*   sr\_no, case\_number, court\_name, cnr\_number, first\_hearing, next\_hearing, case\_stage, petitioner, respondent, act, section.
    

⚠️ Disclaimer
-------------

This tool is for educational purposes only. Automated scraping of government portals should be done responsibly and in compliance with the website's robots.txt and terms of service. The eCourts portal often updates its UI; if the script fails, verify the XPATHs and ID selectors in the source code.
