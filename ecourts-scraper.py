import time
import pandas as pd
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
# Update this path to your local Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Tesseract\Tesseract-OCR\tesseract.exe"

def setup_driver():
    options = webdriver.ChromeOptions()
    # Increase stability with optimized window size
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def solve_captcha(driver):
    """Captures and solves the eCourts CAPTCHA using Pytesseract."""
    try:
        captcha_img = driver.find_element(By.ID, "captcha_image")
        captcha_img.screenshot("captcha.png")
        # Use PSM 8 (single word) and whitelist for better accuracy
        text = pytesseract.image_to_string(
            Image.open("captcha.png"), 
            config="--psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789"
        )
        return text.strip().replace(" ", "").replace("\n", "")
    except Exception as e:
        print(f"      ⚠️ CAPTCHA extraction failed: {e}")
        return ""

def scrape_ecourts(party_name="party_name", year="2024"):
    driver = setup_driver()
    wait = WebDriverWait(driver, 20) # 20s wait for slow portal response
    detailed_cases = []

    try:
        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
        time.sleep(3)
        
        # 1. Close initial alert
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='validateError']/div/div/div[1]/button"))).click()
        except: pass

        # 2. State Selection
        state_sel = Select(wait.until(EC.presence_of_element_located((By.ID, "sess_state_code"))))
        state_sel.select_by_visible_text("Maharashtra")
        time.sleep(3)

        # 3. District Looping
        dist_dropdown = Select(driver.find_element(By.ID, "sess_dist_code"))
        districts = [opt.text for opt in dist_dropdown.options if "Select" not in opt.text]

        for district in districts:
            print(f"\n>>> Processing District: {district}")
            Select(driver.find_element(By.ID, "sess_dist_code")).select_by_visible_text(district)
            time.sleep(3)

            # 4. Court Complex Looping
            court_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "court_complex_code"))))
            courts = [opt.text for opt in court_dropdown.options if "Select" not in opt.text]

            for court in courts:
                print(f"  --- Searching in court: {court}")
                Select(driver.find_element(By.ID, "court_complex_code")).select_by_visible_text(court)
                time.sleep(2)
                
                # Input Search Criteria
                driver.find_element(By.ID, "petres_name").clear()
                driver.find_element(By.ID, "petres_name").send_keys(party_name)
                driver.find_element(By.ID, "rgyearP").clear()
                driver.find_element(By.ID, "rgyearP").send_keys(year)

                # Solve & Submit CAPTCHA
                captcha_text = solve_captcha(driver)
                driver.find_element(By.ID, "fcaptcha_code").send_keys(captcha_text)
                driver.find_element(By.XPATH, "//button[text()='Go']").click()
                time.sleep(3)

                # 5. Extract Results Table
                try:
                    rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@id='dispTable']/tbody/tr")))
                    case_list = []
                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, 'td')
                        if len(cols) >= 4:
                            case_list.append({
                                "sr_no": cols[0].text.strip(),
                                "case_number": cols[1].text.strip(),
                                "view_button": cols[3].find_element(By.TAG_NAME, 'a')
                            })

                    # 6. Deep Extraction (Individual Case View)
                    for case in case_list:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView();", case['view_button'])
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", case['view_button'])
                            
                            # Wait for detailed table
                            wait.until(EC.presence_of_element_located((By.ID, "CSpartyName")))
                            
                            details = {
                                "sr_no": case["sr_no"],
                                "case_number": case["case_number"],
                                "court_name": driver.find_element(By.XPATH, "//*[@id='chHeading']").text.strip(),
                                "cnr_number": driver.find_element(By.XPATH, "//*[@id='CSpartyName']/table[1]/tbody/tr[4]/td[2]/span").text.strip(),
                                "first_hearing": driver.find_element(By.XPATH, "//*[@id='CSpartyName']/table[2]/tbody/tr[1]/td[2]").text.strip(),
                                "next_hearing": driver.find_element(By.XPATH, "//*[@id='CSpartyName']/table[2]/tbody/tr[2]/td[2]/strong").text.strip(),
                                "case_stage": driver.find_element(By.XPATH, "//*[@id='CSpartyName']/table[2]/tbody/tr[3]/td[2]/label/strong").text.strip(),
                                "petitioner": driver.find_element(By.XPATH, "//*[@id='CSpartyName']/table[3]/tbody/tr/td").text.strip(),
                                "respondent": driver.find_element(By.XPATH, "//*[@id='CSpartyName']/table[4]/tbody/tr/td").text.strip(),
                                "act": driver.find_element(By.XPATH, "//*[@id='act_table']/tbody/tr[2]/td[1]").text.strip(),
                                "section": driver.find_element(By.XPATH, "//*[@id='act_table']/tbody/tr[2]/td[2]").text.strip()
                            }
                            detailed_cases.append(details)
                            print(f"    ✅ Extracted: {case['case_number']}")
                        except Exception as e:
                            print(f"    ❌ Failed case {case['case_number']}: {e}")
                        finally:
                            # Navigate back to results table
                            driver.find_element(By.XPATH, "//*[@id='main_back_party']").click()
                            wait.until(EC.presence_of_element_located((By.ID, "dispTable")))

                except:
                    print(f"    ℹ️ No results found for {court}")

    finally:
        # Save to CSV
        if detailed_cases:
            df = pd.DataFrame(detailed_cases)
            df.to_csv("ecourts_detailed_data.csv", index=False)
            print(f"\n🎉 Success! Data saved to 'ecourts_detailed_data.csv'")
        driver.quit()

if __name__ == "__main__":
    scrape_ecourts()