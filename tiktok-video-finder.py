from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def get_tiktok_video_links():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to TikTok explore page
        print("Accessing TikTok explore page...")
        driver.get("https://www.tiktok.com/explore")
        
        # Wait for the page to load
        time.sleep(5)  # Initial wait for page load
        
        # Scroll a few times to load more content
        print("Scrolling to load more content...")
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Find all video links
        video_links = set()
        elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
        
        for element in elements:
            href = element.get_attribute('href')
            if href and 'tiktok.com' in href and '/video/' in href:
                video_links.add(href)
        
        # Print results
        if video_links:
            print("\nFound TikTok video links:")
            for link in video_links:
                print(link)
            print(f"\nTotal videos found: {len(video_links)}")
        else:
            print("No video links found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    print("Starting TikTok video finder...")
    get_tiktok_video_links()
