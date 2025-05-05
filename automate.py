import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load CSV with accounts
df = pd.read_csv("mediaset_accounts.csv")

# Set up WebDriver
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")  # Reduce bot detection
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)  # Explicit wait for elements

def switch_to_iframe_with_element(xpath):
    """Switch to the iframe containing the given element, or return False if not found."""
    driver.switch_to.default_content()  # Reset to main content
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
    for iframe in iframes:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(iframe)
            
            if wait.until(EC.presence_of_element_located((By.XPATH, xpath))):
                return True
        except Exception:
            continue

    driver.switch_to.default_content()
    return False

def select_dropdown_value(name, value):
    """Selects a value from a dropdown list, ensuring it exists."""
    try:
        dropdown = Select(driver.find_element(By.NAME, name))
        options = [opt.get_attribute("value") for opt in dropdown.options]
        value = str(int(value))  # Ensure no leading zeros
        print(f"🔍 Available options for {name}: {options}")
        
        if value in options:
            dropdown.select_by_value(value)
            print(f"✅ Selected {value} for {name}")
        else:
            print(f"⚠️ Value {value} not found in {name}, skipping...")

    except Exception as e:
        print(f"❌ Error selecting {name}: {e}")

def select_consent_radios():
    """Finds and selects the 'yes' option for consent checkboxes."""
    try:
        consent_names = [
            "preferences.profiling.mediaset.isConsentGranted",
            "preferences.marketing.mediaset.isConsentGranted",
            "preferences.data.mediaset.isConsentGranted"
        ]

        for consent in consent_names:
            radio_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//input[@name='{consent}'][@value='true']"))
            )
            driver.execute_script("arguments[0].click();", radio_button)
            print(f"✅ Selected consent: {consent}")

    except Exception as e:
        print(f"❌ Error selecting consent radios: {e}")

def register_account(email, password, nome, cognome, regione, gender, birth_day, birth_month, birth_year):
    max_attempts = 10  # Set the maximum number of retry attempts
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            print(f"🚀 Starting registration for {email}, Attempt {attempt}...")

            driver.get("https://www.grandefratello.mediaset.it/vota/")

            # Click "Go to televoting" button
            vote_button = wait.until(EC.element_to_be_clickable((By.ID, "btnModal")))
            vote_button.click()

            # Locate and click 'Accedi' button inside the correct iframe
            if not switch_to_iframe_with_element("//button[contains(text(), 'Accedi')]"):
                raise Exception("'Accedi' button not found in any iframe")

            accedi_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accedi')]")))
            driver.execute_script("arguments[0].click();", accedi_button)
            driver.switch_to.default_content()

            # Click "Registrati" link inside the correct iframe
            if not switch_to_iframe_with_element("//a[contains(@data-switch-screen, 'gigya-register-screen')]"):
                raise Exception("'Registrati' link not found in any iframe")

            registrati_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@data-switch-screen, 'gigya-register-screen')]")))
            driver.execute_script("arguments[0].click();", registrati_link)
            driver.switch_to.default_content()

            # First registration popup (Email, Password, Confirm Password)
            if not switch_to_iframe_with_element("//input[@name='email']"):
                raise Exception("First registration popup not found")

            driver.find_element(By.NAME, "email").send_keys(email)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.NAME, "passwordRetype").send_keys(password)

            # Click "Invia" button with debugging logs
            invia_button_xpath = "//input[@type='submit' and contains(@class, 'gigya-input-submit')]"
            print("🔍 Checking for 'Invia' button...")

            invia_button = wait.until(EC.element_to_be_clickable((By.XPATH, invia_button_xpath)))
            print("✅ 'Invia' button found.")
            driver.execute_script("arguments[0].scrollIntoView();", invia_button)
            print("🔽 Scrolling 'Invia' button into view...")
            time.sleep(1)  # Small delay to ensure it's in view
            driver.execute_script("arguments[0].click();", invia_button)
            print("✅ 'Invia' button clicked successfully.")

            driver.switch_to.default_content()

            # Second registration popup (Personal details)
            if not switch_to_iframe_with_element("//input[@name='profile.firstName']"):
                raise Exception("Second registration popup not found")
            
            driver.find_element(By.NAME, "profile.firstName").send_keys(nome)
            driver.find_element(By.NAME, "profile.lastName").send_keys(cognome)

            # Ensure region selection matches available options
            valid_regions = [
                "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia",
                "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", 
                "Provincia Autonoma di Bolzano", "Provincia Autonoma di Trento", 
                "Puglia", "Sardegna", "Sicilia", "Toscana", "Umbria", "Veneto"
            ]
            
            if regione not in valid_regions:
                print(f"⚠️ Invalid region '{regione}' for {email}, defaulting to 'Lazio'.")
                regione = "Lazio"
            
            Select(driver.find_element(By.NAME, "data.regione")).select_by_visible_text(regione)

            # Gender Selection
            gender = gender.strip().lower()  # Normalize input
            gender_xpath = f"//input[@name='profile.gender' and @value='{gender}']"
            driver.find_element(By.XPATH, gender_xpath).click()

            # Birthdate selection
            select_dropdown_value("profile.birthDay", birth_day)
            select_dropdown_value("profile.birthMonth", birth_month)
            select_dropdown_value("profile.birthYear", birth_year)

            # Select consent checkboxes
            select_consent_radios()

            # Click final registration button
            final_register_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and contains(@class, 'gigya-input-submit')]")))
            driver.execute_script("arguments[0].scrollIntoView();", final_register_button)  # Scroll the final button into view
            time.sleep(1)  # Small delay to ensure it's clickable
            driver.execute_script("arguments[0].click();", final_register_button)

            print(f"✅ Successfully registered: {email}")
            time.sleep(3)
            break  # Exit the retry loop after successful registration
        
        except Exception as e:
            print(f"❌ Error registering {email} on attempt {attempt}: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print(f"❌ {email} failed to register after {max_attempts} attempts.")

# Register all accounts from CSV
for index, row in df.iterrows():
    register_account(
        row["email"], row["password"], row["nome"], row["cognome"], row["regione"],
        row["sesso"], row["birth_day"], row["birth_month"], row["birth_year"]
    )

# Close browser
driver.quit()
