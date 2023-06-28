import time
from bs4 import BeautifulSoup
import requests
import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor
import uuid

def immo(pages):
    links = []

    for i in range(pages):
        url = f"https://www.immoweb.be/en/search/house/for-sale?countries=BE&page={i+1}&orderBy=relevance"
        immolist = requests.get(url)
        soup = BeautifulSoup(immolist.content, 'html.parser')
        memories = soup.find_all(class_='card__title-link')
        
        for link in memories:
            if link.find_parent('h3'):
                continue
            else:
                links.append(link.get('href'))

        url2 = f"https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&page={i+1}&orderBy=relevance"
        immolist2 = requests.get(url2)
        soup2 = BeautifulSoup(immolist2.content, 'html.parser')
        memors = soup2.find_all(class_='card__title-link')

        for link2 in memors:
            if link2.find_parent('h3'):
                continue
            else:
                links.append(link2.get('href'))

    filename = "property_data.csv"
    # Prepare the headers
    data_dict = {
        "Raw num:": None,
        "Locality": None,
        "Zip code": None,
        "Kitchen": None,
        "Type of property": None,
        "Subtype of property": None,
        "Price of property in euro": None,
        "Type of Sale": None,
        "Number of bedrooms": None,
        "Living area": None,
        "Terrace": None,
        "Garden": None,
        "Garden area": None,
        "Surface of the land(or plot of land)": None,
        "Number of facades": None,
        "Swimming pool": None,
        "ID number": None,
        "State of the building": None,
        "URL": None
    }
    # Write the headers to the CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        writer.writeheader()
    

    num_workers = 16 #cores your CPU has
    #However the code is primarily I/O-bound, not CPU-bound
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(main, links)


def main(urlq):
    response = requests.get(urlq)

    # Parse the response content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # HTML element that contains the JavaScript code with window.dataLayer
    # need to inspect the web page source code to find the right selector
    script = soup.find("script", string=lambda t: "window.dataLayer" in t).string # Script element

    # json.loads method to convert the text into a Python dictionary
    # remove some extra characters or lines from the text before parsing it
    data = json.loads(script.split("window.dataLayer = ")[1].strip().rstrip(";")) # Data dictionary

    # Access the dictionary keys and values to get the information you want
    classified_url = urlq
    user_login_status = data[0]["user"]["loginStatus"] # User login status
    classified_id = data[0]["classified"]["id"] # Classified id
    classified_type = data[0]["classified"]["type"] # Classified type
    classified_subtype = data[0]["classified"]["subtype"] # Classified subtype
    classified_price = data[0]["classified"]["price"] # Classified price
    classified_kitchen = data[0]["classified"]["kitchen"]["type"]
    classified_room = data[0]["classified"]["bedroom"]["count"]
    classified_terrace = data[0]["classified"]["outdoor"]["terrace"]["exists"]
    classified_garden = data[0]["classified"]["outdoor"]["garden"]["surface"]
    classified_surface_land = data[0]["classified"]["land"]["surface"]
    classified_swimming_pool = data[0]["classified"]["wellnessEquipment"]["hasSwimmingPool"]
    classified_state_of_building = data[0]["classified"]["building"]["condition"]
    classidied_zip_code = data[0]["classified"]["zip"]

    # Access the dictionary keys and values to get the information you want from second data layer
    """ classified_frontages = soup.find(string="Number of frontages").find_next_sibling('td').contents[0] """
    
    #extrating data from secods data dictionary
    scripts = soup.find_all('script')

    data_class = None
    for script in scripts:
        if 'window.classified' in script.text:  # The variable containing the JSON data
            clas_sting = re.search('window.classified = ({.*?});', script.text).group(1)
            data_class = json.loads(clas_sting)
            break
    
    #example:
    #province = data_clas["customers"][0]["location"]["province"]
    #district = data_clas["customers"][0]["location"]["district"]
    classified_cityname = data_class['property']['location']['locality']
    classified_living_area = data_class['property']["netHabitableSurface"]
    classified_number_of_facades = data_class['property']['building']['facadeCount']

    #classified types of sales
    flags = data_class['flags']
    sales_types = ['isPublicSale', 'isNotarySale', 'isLifeAnnuitySale', 'isInvestmentProject', 'isSoldOrRented', "isAnInteractiveSale","isUnderOption"]
    classified_sales_type = None

    for sales_type in sales_types:
        if sales_type in flags and flags[sales_type]:
            classified_sales_type = sales_type
            break

    #check number of rums
    if classified_room == "":
        classified_room = None

    # Print the information
    #print("Locality:", classified_cityname)
    print("Zip code:", classidied_zip_code)

    # check kitchen
    if classified_kitchen == "not installed":
        classified_kitchen = 0
    elif classified_kitchen == "":
        classified_kitchen = None
    else:
        classified_kitchen = 1 

    print("Kitchen:", classified_kitchen)

    print("Type of property:", classified_type)
    print("Subtype of property:", classified_subtype)
    print("Price of property:", classified_price, "euro")
    print("Number of bedrooms:", classified_room)

    #check terrace
    if classified_terrace == "false": 
        classified_terrace = 0
    elif classified_terrace == "":
        classified_terrace = None
    else:
        classified_terrace = 1
    print("Terrace:", classified_terrace)

    #check garden
    if classified_garden == "false": 
        classified_garden = 0
    elif classified_garden == "":
        classified_garden = None
        classified_garden_area = None
    else:
        classified_garden_area = classified_garden
        classified_garden = 1

    print("garden:", classified_garden)
    print("garden area m2:", classified_garden_area)

    print("Surface of the land(plot of land):", classified_surface_land, "m²")
    """ print("Number of frontages:", classified_frontages) """

    #check swimming pool data
    if classified_swimming_pool == "true":
        classified_swimming_pool = 1
    elif classified_swimming_pool == "":
        classified_swimming_pool = None
    else:
        classified_swimming_pool = 0

    print("Swimming pool:", classified_swimming_pool)


    print("ID number:", classified_id)
    print("State of the building:", classified_state_of_building)
    print("Url:", urlq)


    #using dictory to store info for csv file
    data_dict = {
        "Raw num:": None,
        "Locality": classified_cityname,
        "Zip code:": classidied_zip_code,
        "Kitchen": classified_kitchen,
        "Type of property": classified_type,
        "Subtype of property": classified_subtype,
        "Price of property in euro": classified_price,
        "Type of Sale": classified_sales_type,
        "Number of bedrooms": classified_room,
        "Living area": classified_living_area,
        "Terrace": classified_terrace,
        "Garden": classified_garden,
        "Garden area": classified_garden_area,
        "Surface of the land(or plot of land)": classified_surface_land,
        "Number of facades": classified_number_of_facades,
        "Swimming pool": classified_swimming_pool,
        "ID number": classified_id,
        "State of the building": classified_state_of_building,
        "URL": classified_url
    }

    # Specify the name of the CSV file
    filename = "property_data.csv"

    # Write the dictionary to the CSV file
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        writer.writerow(data_dict)

if __name__ == "__main__":
    start_time = time.time()  # Record the start time
    pages = 1
    print("Starting scaping...")
    immo(pages)
    end_time = time.time()  # Record the end time
    print("Execution time: ", end_time - start_time, "seconds")  # Print the execution time

