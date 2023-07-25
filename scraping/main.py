from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import csv
import undetected_chromedriver as uc
from colour import Color
import re
import requests


class Scraper:
    def __init__(self):
        """
        When we initialize a scraper object, we need to create our webdriver
        instance
        """
        # Please note that this is the directory of my webdriver instance
        co = uc.ChromeOptions()

        co.add_argument("--disable-extensions")
        co.add_argument("--disable-popup-blocking")
        co.add_argument("--profile-directory=Default")
        co.add_argument("--disable-plugins-discovery")
        co.add_argument("--incognito")
        # co.add_argument("--headless")
        co.add_argument('--no-sandbox')
        co.add_argument("--disable-setuid-sandbox")
        co.add_argument("user_agent=DN")
        co.add_argument("--start-maximized")
        # pxy = "2.56.46.10:8800"

        # co.add_argument('--proxy-server=%s' % pxy)

        # driver = uc.Chrome(options=co)
        self.browser = uc.Chrome(options=co)
        self.browser.delete_all_cookies()
    
    
    def search(self, searchUrl):
        """
        This method is used to fetch the ibba.org address and find the search
        bar element to enter in a search that we are concerned with, in this
        case, we are searching for all brokers in the Los Angeles area
        """
        self.browser.get(searchUrl)
        time.sleep(1)

    def get_info(self):
        """
        This method is the meat and potatoes of this program, it tries to
        collect all of the key parameters we track:name, phone number, address,
        company and email of the broker on the profile page we are currently
        navigated to. In the case where there is no such information to be
        displayed (the broker didn't input that parameter), it adds an empty
        string to the list of info (translates to an empty cell in the CSV file
        this generates)
        """
        time.sleep(1)

        def check_color(color):
            """
            This method is used to catch color in string
            """
            try:
                Color(color)
                return color
            except ValueError:
                return False
            
        info = []
        # Full Auction title
        try:
            info += [self.browser.find_element(By.CLASS_NAME, "listing-post-title").
                     text]
        except (NoSuchElementException, AttributeError):
            info += [""]
        # Is it "no reserve"?
        try:
            self.browser.find_element(By.CLASS_NAME, "item-tag-noreserve")
            info += ["Y"]
        except (NoSuchElementException, AttributeError):
            info += ["N"]
        # Year
        try:
            make_txt1 = self.browser.find_element(By.CLASS_NAME, "listing-post-title").text
            year_pattern = r"\b\d{4}\b"
            make_txt = re.findall(year_pattern, make_txt1)
            make_txt = ' '.join(make_txt)
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #     Make
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/button").text
            info += [make_txt[4:]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Model Family
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/button").text
            if make_txt[0:4] == 'Make':
                make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/div/button").text
            info += [make_txt[5:]]
        except (NoSuchElementException, AttributeError):
            info += [""]
        
        #    Model Identifier
        try:
            make_txt = self.browser.find_element(By.CLASS_NAME, "listing-nicknames").text
            info += [make_txt[13:]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Era
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/div/button").text
            info += [make_txt[3:]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Origin
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[2]/div[2]/div/div/div[4]/div/button").text
            info += [make_txt[6:]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Category
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[2]/div[2]/div/div/div[5]/div/button").text
            info += [make_txt[8:]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Number of comments
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div[1]/a/span/span[1]").text
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Seller
        try:
            make_txt1 = self.browser.find_element(By.CLASS_NAME, "item-seller").text
            make_txt1 = make_txt1[8:]
            make_txt2 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[1]/a[1]").get_attribute('href')
            make_txt = make_txt1 + " " + make_txt2
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Private party or dealer
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[3]").text
            info += [make_txt[25:]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Ext. Color Group, Ext. Color Group
        try:
            make_txt1 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[5]").text
            make_txt2 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[6]").text
            make_txt = [i for i in make_txt1.split(' ') if check_color(i)]
            make_txtA = [i for i in make_txt2.split(' ') if check_color(i)]
            if make_txt == False: 
                make_txt1 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[6]").text
                make_txt2 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[7]").text
                make_txt = [i for i in make_txt1.split(' ') if check_color(i)]
                make_txtA = [i for i in make_txt2.split(' ') if check_color(i)]
            
            if make_txt == False:
                make_txt1 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[7]").text
                make_txt2 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[8]").text
                make_txt = [i for i in make_txt1.split(' ') if check_color(i)]
                make_txtA = [i for i in make_txt2.split(' ') if check_color(i)]
            
            make_txt = ' '.join(make_txt)
            make_txtA = ' '.join(make_txtA)
            info += [make_txt]
            info += [make_txtA]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Buyer
        try:
            make_txt1 = self.browser.find_element(By.XPATH, '//*[@id="listing-bid"]/tbody/tr[1]/td[2]/span[2]/a').text
            make_txt2 = self.browser.find_element(By.XPATH, '//*[@id="listing-bid"]/tbody/tr[1]/td[2]/span[2]/a').get_attribute('href')
            make_txt = make_txt1 + " " + make_txt2
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Odometer
        try:
            make_full_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[2]").text
            make_txt = make_full_txt.split(' ')
            info += [make_txt[0]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Miles of kilometers
        try:
            make_full_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[2]").text
            make_txt = make_full_txt.split(' ')
            info += [make_txt[1]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Private party or dealer
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/a").text
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Chassis/VIN
        try:
            make_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li[1]/a").text
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Status
        try:
            make_full_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div[1]/span[2]").text
            make_txt = make_full_txt.split(' ')
            if make_txt[0] == 'Sold': info += ['Sold']
            else: info += ['Not Sold']
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Value
        try:
            make_full_txt = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div[1]/span[2]").text
            make_txt = make_full_txt.split(' ')
            info += [make_txt[2]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Auction end day, Auction end month, Auction end day number, Auction end time
        try:
            make_full_txt = self.browser.find_element(By.XPATH, '//*[@id="listing-bid"]/tbody/tr[2]/td[2]').text
            make_txt = make_full_txt.split(' ')
            make_txt_day = make_txt[0]
            make_txt_day = make_txt_day[:-1]
            make_txt_month = make_txt[1]
            make_txt_daynum = make_txt[2]
            make_txt_time = make_txt[4]
            info += [make_txt_day]
            info += [make_txt_month]
            info += [make_txt_daynum]
            info += [make_txt_time]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Auction end Year
        try:
            make_full_txt1 = self.browser.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/div[1]/div/div/div/div/div[2]/div[1]/span[2]").text
            make_full_txt2 = make_full_txt1.split(' ')
            make_txt = make_full_txt2[4].split('/')
            make_txt = '20' + make_txt[2]
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Number of bids
        try:
            make_txt = self.browser.find_element(By.CLASS_NAME, 'number-bids-value').text
            info += [make_txt]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Auction URL
        info += [itemUrl]   

        #    Number of views
        try:
            make_full_txt = self.browser.find_element(By.XPATH, '//*[@id="listing-actions-stats"]/tbody/tr/td/span[1]').text
            make_txt = make_full_txt.split(' ')
            info += [make_txt[0]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        #    Watchers
        try:
            make_full_txt = self.browser.find_element(By.XPATH, '//*[@id="listing-actions-stats"]/tbody/tr/td/span[2]').text
            make_txt = make_full_txt.split(' ')
            info += [make_txt[0]]
        except (NoSuchElementException, AttributeError):
            info += [""]

        
        return info

    def quit(self):
        """
        Call this method to close the browser instance
        """
        self.browser.quit()

# Initialize our scraper and browser instance
scraper = Scraper()

# URL of the target endpoint
url = "https://bringatrailer.com/wp-json/bringatrailer/1.0/data/listings-filter"

# Create and empty list for the raw data to be added to
raw_data = []

i = 8
while i < 12:
    # Data to send in the request body
    data = {
        "page": str(i),
        "per_page": "36",
        "get_items": "1",
        "get_stats": "0",
        "sort": "td",
        "category[]": "434"
    }
    
    # Send the POST request
    response = requests.post(url, data=data)
    
    # get the item url from responce and get info from the url
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Access the response data
        response_data = response.json()
    else:
        # Request failed, handle the error
        print("Request failed with status code:", response.status_code)
    
    itemsInfo = response_data["items"]
    
    for itemInfo in itemsInfo:
        itemUrl = itemInfo["url"]
        # Create the initial search, defined by our search method
        scraper.search(itemUrl)
        raw_data += [scraper.get_info()]

    i += 1



# Close our browser instance, we collected all the data!
scraper.quit()

# Now we want to write all the data we just collected to a CSV file, this
# simply creates a new CSV file and writes a row for every broker. All of the
# information lines up with header containing the tracked parameters
with open('output.csv', 'w', encoding='utf-8', newline='') as new_file:
    csv_writer = csv.writer(new_file)
    # Header
    csv_writer.writerow(['Full Auction title', 'Is it "no reserve"', 'Year', 'Make', 'Model Family', 'Model identifier', 'Era', 'Origin', 'Category', 'Number of comments', 'Seller', 'Private party or dealer', 'Ext. Color Group', 'Int. Color Group', 'Buyer', 'Odometer', 'Miles of kilometers', 'Location', 'Chassis/VIN', 'Status', 'Value', 'Auction end day', 'Auction end month', 'Auction end day number', 'Auction end time','Auction end year', 'Number of bids', 'Auction URL', 'Number of views', 'Watchers'])
    for line in raw_data:
        csv_writer.writerow(line)
