from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os
import pypdf


current_directory = os.getcwd()
print(current_directory)
reports_folder = os.path.join(current_directory, "reports_pdf")
txt_folder = os.path.join(current_directory, "reports_txt")
if not os.path.exists(reports_folder):
    os.makedirs(reports_folder)
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": current_directory + "\\reports_pdf",
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
})
browser = webdriver.Chrome(options=chrome_options)

countryName = "netherlands"
url = "https://sustainabilityreports.com/country/" + countryName
browser.get(url)

# Wait for the page to load
time.sleep(2)

# Infinite scroll implementation
last_height = browser.execute_script("return document.body.scrollHeight")

while True:
    # Scroll to the bottom of the page
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for new content to load (adjust time as necessary)
    time.sleep(2)

    # Calculate new scroll height
    new_height = browser.execute_script("return document.body.scrollHeight")

    # Break the loop if no new content is loaded
    if new_height == last_height:
        break

    last_height = new_height

print("Reached the bottom of the page.")

# Extract all <h3> elements with class "dynamic"
h3_elements = browser.find_elements(By.CSS_SELECTOR, "h3.dynamic a")

all_links = [element.get_attribute("href") for element in h3_elements]

# Use regex to filter links that start with the desired prefix
links = [link for link in all_links if re.match(r"^https://sustainabilityreports\.com/company", link)]

# Print the collected links
print("Extracted Links:")
for link in links:
    print(link)

print("Found " + str(len(links)) + " companies in " + countryName + " with ESG reports uploaded to sustainabilityreports.com.")

for link in links:
    print(f"Opening link: {link}")
    browser.get(link)
    #zapisz drzewko przed otworzeniem ramki ze zgodą
    #html_content = browser.page_source
    #with open("page_source.txt", "w", encoding="utf-8") as file:
    #    file.write(html_content)

    download_button = browser.find_element(By.CSS_SELECTOR,
                                           'a.wpdm-download-link.wpdm-download-locked.btn.btn-primary.btn-lg')
    download_button.click()
   # time.sleep(2)
    #zapisz drzewko z ramką
    #html_content = browser.page_source
    #with open("page_source_with_frame.txt", "w", encoding="utf-8") as file:
    #    file.write(html_content)
    #time.sleep(5)
    iframe = browser.find_element(By.ID, "wpdm-lock-frame")

    # Extract the URL from the 'src' attribute
    iframe_src = iframe.get_attribute('src')
    print(iframe_src)
    browser.get(iframe_src)
   # time.sleep(1)
    download_link = browser.find_element(By.CSS_SELECTOR, "a.btn.btn-success.btn-lg.btn-block")
    # Wyciągnij URL z atrybutu href
    pdf_url = download_link.get_attribute("href")
    # Otwórz link, aby pobrać PDF
    browser.get(pdf_url)
    time.sleep(5)
browser.quit()
print("Download finished. Now I will convert pdf reports into .txt.\n")

def pdf_to_text(pdf_file_path, txt_file_path):
    # Open the PDF file
    with open(pdf_file_path, "rb") as file:
        reader = pypdf.PdfReader(file)

        # Create or open the txt file to write extracted text
        with open(txt_file_path, "w", encoding="utf-8") as output_file:
            # Loop through each page and extract text
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()

                if text:  # Write only if text is extracted
                    output_file.write(f"Page {page_num + 1}:\n")
                    output_file.write(text)
                    output_file.write("\n\n")

    print(f"Text has been extracted to {txt_file_path}")

for filename in os.listdir(reports_folder):
    # Check if the file is a PDF
    if filename.endswith(".pdf"):
        pdf_file_path = os.path.join(reports_folder, filename)
        txt_file_path = os.path.join(txt_folder, f"{os.path.splitext(filename)[0]}.txt")

        # Call the pdf_to_text function to extract text from each PDF
        pdf_to_text(pdf_file_path, txt_file_path)



