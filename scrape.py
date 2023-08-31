import requests
import re
import time
import sqlite3

def scrape_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_data(html):
    row_pattern = r'<tr>.*?<label\s+for="pricesForm:productID">(.*?)<\/label>.*?' \
                  r'<label\s+class="royalblue"[^>]*>(.*?)<\/label>.*?' \
                  r'<label\s+class="darkteal"[^>]*>(.*?)<\/label>.*?<\/tr>'
    
    extracted_data = []
    matches = re.finditer(row_pattern, html, re.DOTALL)
    for match in matches:
        product_name = match.group(1).strip()
        price_royalblue = match.group(2).strip()
        price_darkteal = match.group(3).strip()
        extracted_data.append({
            "product_name": product_name,
            "price_royalblue": price_royalblue,
            "price_darkteal": price_darkteal
        })
    
    return extracted_data

def create_database():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       image_path TEXT,
                       product_name TEXT,
                       price_royalblue INTEGER,
                       price_darkteal INTEGER,
                       additional_price INTEGER
                       )''')

    conn.commit()
    conn.close()

def update_or_insert_into_database(data):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    for entry in data:
        cursor.execute('''SELECT * FROM products WHERE product_name = ?''', (entry['product_name'],))
        existing_data = cursor.fetchone()
        if existing_data:
            price_royalblue = entry['price_royalblue'].replace(" ","")
            price_darkteal = entry['price_darkteal'].replace(" ","")      

            cursor.execute('''UPDATE products
                              SET price_royalblue = ?, price_darkteal = ?
                              WHERE product_name = ?''', (price_royalblue, price_darkteal, entry['product_name']))
    conn.commit()
    conn.close()


def update_price_cards(data):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    for entry in data:
        cursor.execute('''SELECT * FROM cards WHERE product_name = ?''', (entry['product_name'],))
        existing_data = cursor.fetchone()
        if existing_data:
            price_darkteal = entry['price_darkteal'].replace(" ","")      

            cursor.execute('''UPDATE cards
                              SET price_darkteal = ?
                              WHERE product_name = ?''', (price_darkteal, entry['product_name']))
    conn.commit()
    conn.close()

def graph_data_insert():
    conn = sqlite3.connect('products.db')
    cursor= conn.cursor()
    cursor.execute("SELECT price_darkteal, additional_price FROM products WHERE id=?",(1,))
    test = cursor.fetchall()
    result = test[0][0] + test[0][1]
    
    cursor.execute("INSERT INTO price_graph (price) VALUES (?)",(result,))
    conn.commit()
    conn.close()



if __name__ == "__main__":
    website_url = "https://www.mkspamp.com.my/m/prices.xhtml"
    
    create_database()
    
    while True:
        html_content = scrape_website(website_url)
        if html_content:
            graph_data_insert()

            extracted_data = extract_data(html_content)            
            for data in extracted_data: 
                update_or_insert_into_database(extracted_data) 
                update_price_cards(extracted_data)

        time.sleep(10)  