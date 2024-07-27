from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import os

app = Flask(__name__)
csv_file_path = 'reviews.csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_reviews', methods=['POST'])
def fetch_reviews():
    url = request.form['url']
    
    # Set up WebDriver (Ensure you provide the correct path to the ChromeDriver)

    driver = webdriver.Chrome()
    
    try:
        # Open the URL
        driver.get(url)
        
        # Wait for the page to load and reviews to be available
        wait = WebDriverWait(driver, 10)
        #wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-hook="review"]')))

        # Scroll to load more reviews if necessary
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        body.send_keys(Keys.PAGE_DOWN)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-hook="review"]')))
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all review blocks
        reviews = soup.find_all('div', {'data-hook': 'review'})
        
        # Extract customer names, review dates, review text, and ratings
        reviews_data = []
        for review in reviews:
            # Customer name
            name_element = review.find('span', {'class': 'a-profile-name'})
            name = name_element.text.strip() if name_element else 'N/A'
            
            # Review date
            date_element = review.find('span', {'data-hook': 'review-date'})
            date = date_element.text.strip() if date_element else 'N/A'
            
            # Review text
            review_text_element = review.find('span', {'data-hook': 'review-body'})
            review_text = review_text_element.text.strip() if review_text_element else 'N/A'
            
            # Rating (corrected to reflect potential issues in the data-hook)
            rating_element = review.find('a', {'data-hook': 'review-title'})
            rating = rating_element.text.strip() if rating_element else 'N/A'
            
            reviews_data.append({
                'name': name,
                'date': date,
                'rating': rating,
                'review_text': review_text
            })
        
        #write reviews to csv
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'date', 'rating', 'review_text'])
            writer.writeheader()
            writer.writerows(reviews_data)        
    finally:
        # Ensure the WebDriver is always closed
        driver.quit()
    return render_template('result.html', reviews=reviews_data)
@app.route('/download_csv')
def download_csv():
    if os.path.exists(csv_file_path):
        return send_file(csv_file_path, as_attachment=True, download_name='reviews.csv')
    return "CSV file not found.", 404
    

if __name__ == '__main__':
    app.run(debug=True)
