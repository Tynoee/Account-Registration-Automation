# Account-Registration-Automation
Python script automating the registration process for Mediaset accounts. It leverages Selenium WebDriver to interact with the web interface, fill in registration forms, and handle consent options. The script reads account details from a CSV file, then iteratively registers each account, ensuring that each field is correctly filled based on the input data.

## Features

- Automates the Mediaset account registration process.
- Uses Selenium WebDriver to interact with the website.
- Handles iframes and dynamic content loading.
- Manages dropdown selection, radio buttons, and consent checkboxes.
- Retries registration for each account in case of failure (configurable retry limit).
- Reads account details from a CSV file for bulk registration.
- Reduces bot detection with options to manipulate browser features.

## Requirements

- Python 3.x
- ChromeDriver (automatically managed via `webdriver_manager`)
- Selenium WebDriver
- Pandas

## Dependencies

- pandas: For reading and processing the CSV file with account data.
- selenium: For automating the browser interaction.
- webdriver_manager: For automatically managing ChromeDriver installation.
