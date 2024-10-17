import psycopg2
from playwright.sync_api import sync_playwright
import time

#Connect to PostgreSQL
connection = psycopg2.connect(
    dbname="shoe_deals",
    user="kuttoosh",
    password="pgrrn@19",
    host="localhost"
)

cursor=connection.cursor()

def clear_table():
    cursor.execute("TRUNCATE TABLE running_shoe_deals RESTART IDENTITY")
    connection.commit()

def runfree_scraper():
    with sync_playwright() as p: 
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        base_url = 'https://www.runningfree.com/products/All-Mens-66507/Shoes-27/Running-28/'
        pagenumber = 1
        page.goto(base_url)
        time.sleep(1)
        #page.wait_for_load_state('networkidle')

        print(page.title())

        shoes = page.query_selector_all('.prodPreview')

        #shoe_deal = []

        while True : 
            current_url = base_url
            if pagenumber == 1:
                page.goto(base_url)
            else: 
                current_url = f"{base_url}{pagenumber}/"
                page.goto(current_url)

            time.sleep(1)
            print(f"Scraping page {pagenumber}:{current_url}")

            shoes = page.query_selector_all('.prodPreview')

            if not shoes:
                print("No more shoes found on this page. Stopping.")
                break
            
            for shoe in shoes:
                try:
                        name = shoe.query_selector('div.prodName a').inner_text()
                        link = shoe.query_selector('div.prodName a').get_attribute('href')
                        original_price = shoe.query_selector('div.prodPrice').inner_text()
                        new_price_elem = shoe.query_selector('div.prodPriceSale strong') or shoe.query_selector('div.theWarehousePrice')
                        new_price = new_price_elem.inner_text() if new_price_elem else 'N/A'
                        
                        #print(name, original_price, new_price)
                        # shoe_deal.append(
                        #         {
                        #         'name' : name,
                        #         'link' : link,
                        #         'origprice' : original_price,
                        #         'newprice' : new_price,
                        #         }
                        # )

                        cursor.execute("""
                                            INSERT INTO running_shoe_deals (name, original_price, new_price, link)
                                        VALUES (%s, %s, %s, %s)
                                        """, (name, original_price, new_price, link))
                        
                except Exception as e:
                        print(f"Error scraping shoe data: {e}")
                        continue
            
            connection.commit()
            pagenumber += 1
            time.sleep(1)

        browser.close()
        return
    

if __name__ == "__main__" : 
    clear_table()
    runfree_scraper()


# Close database connection
cursor.close()
connection.close()