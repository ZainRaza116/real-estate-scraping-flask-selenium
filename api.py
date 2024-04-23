from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from deep_translator import GoogleTranslator
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mysql.connector


app = Flask(__name__)

option = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=option)

def translate_arabic_to_english(text):
    return GoogleTranslator(source='ar', target='en').translate(text)

def scrape_data():
    try:
        driver.get('https://sa.aqar.fm')
        sleep(0)

        parent_div_element_xpath = '//*[@id="__next"]/main/div/div[2]/div/div/div[2]/div[2]/div[1]'
        base_child_xpath = '//*[@id="__next"]/main/div/div[2]/div/div/div[2]/div[2]/div[1]/div[{}]'
                            # '//*[@id="__next"]/main/div/div[2]/div/div/div[2]/div[2]/div[1]/div[2]'
                            # '//*[@id="__next"]/main/div/div[2]/div/div/div[2]/div[2]/div[1]/div[3]'
                            

        start_number = 1
        end_number = 100

        child_div_xpaths = [base_child_xpath.format(i) for i in range(start_number, end_number + 1)]
        
        for i in range(start_number, end_number + 1):
            child_xpath = base_child_xpath.format(i)

        scraped_data = []

        for child_xpath in child_div_xpaths:
            try:
                print('Clicking on the element:', child_xpath)
                parent_divs=WebDriverWait(driver, 0).until(EC.presence_of_element_located((By.XPATH, parent_div_element_xpath)))

                # parent_divs = driver.find_element(By.XPATH, parent_div_element_xpath)
                child_divs = parent_divs.find_elements(By.XPATH, child_xpath)
                
                for div in child_divs:
                    div.click()

                header_element = driver.find_element(By.CLASS_NAME, '_title__eliuu')
                price_element = driver.find_element(By.CLASS_NAME, '_price__EH7rC')
                content_element = driver.find_element(By.CLASS_NAME, '_content__om2Q_')

                header = translate_arabic_to_english(header_element.text)
                price = translate_arabic_to_english(price_element.text)
                content = translate_arabic_to_english(content_element.text)

                
                print("Header:", header)
                print("Price:", price)
                print("Content:", content)

                table_data_divs = driver.find_element(By.CLASS_NAME, '_specs__Ag0l9')
                list_data = table_data_divs.find_elements(By.CLASS_NAME, '_item___4Sv8')
                # table_items = [div.text for div in list_data]
                table_items = [translate_arabic_to_english(div.text) for div in list_data]
                sleep(1)
                
                scraped_data.append({
                    "header": header,
                    "price": price,
                    "content": content,
                    "table_data": table_items
                    # last_update

                })

            except Exception as e:
                print("Error clicking on the element:", e)

        return scraped_data
    except Exception as e:
        print("Error during scraping:", e)
        return None
    
def insert_sql(data):
    conn = mysql.connector.connect(
    host="localhost",
    user="****t",
    password="2******8",
    database="scrape_db"
    )

    print(conn)

    cursor = conn.cursor()
    table_name = "scrape_table"
    
    sql_ddl = """
    CREATE TABLE IF NOT EXISTS {table} (
    header VARCHAR(255),
    price VARCHAR(255),
    content TEXT,
    load_timestamp TIMESTAMP
    )
    """.format(table=table_name)
    cursor.execute(sql_ddl)
    
    for row in data:
        row_data = (row['header'], row['price'], row['content'])
        print(row_data)
        
        # SQL query to insert data into a table
        sql = "INSERT INTO {table_name} (header, price, content, load_timestamp) VALUES (%s, %s, %s, NOW())".format(table_name=table_name)

        # Extracting values from the dictionary and inserting into the table
        values = row_data

        # Executing the SQL query
        cursor.execute(sql, values)

    # Committing the transaction
    conn.commit()

    # Closing the cursor and database connection
    cursor.close()
    conn.close()

@app.route("/scrape", methods=["GET"])
def scrape_route():
    """
    Returns scraped data as API response.
    """
    scraped_data = scrape_data()
    print(scrape_data)
    
    insert_sql(scraped_data)
    

        
    if scraped_data is not None:
        return jsonify({"data": scraped_data})
    else:
        return jsonify({"error": "Failed to scrape data"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)




