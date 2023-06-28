import time
from bs4 import BeautifulSoup
import requests
import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor

def immo():
    links = []

    for i in range(333):
        url = f"https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i+1}&orderBy=relevance"
        immolist = requests.get(url)
        soup = BeautifulSoup(immolist.content, 'html.parser')
        memories = soup.find_all(class_='card__title-link')

        for link in memories:
            if link.find_parent('li'):
                links.append(link.get('href'))

    filename = "property_data.csv"
    # Prepare the headers
    data_dict = {
        "Locality": None,
        "Zip code": None,
        "Kitchen": None,
        "Type of property": None,
        "Subtype of property": None,
        "Price of property in euro": None,
        "Number of bedrooms": None,
        "Terrace": None,
        "Garden": None,
        "Garden area": None,
        "Surface of the land": None,
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
    #it's better to add name of the city from a dara list which Bo found (in process) but now we need to use regex
    classified_cityname = soup.find("title")
    classified_cityname = re.sub(r'.*?for', "", str(classified_cityname))
    classified_cityname = re.sub('</title>', "", str(classified_cityname))
    classified_cityname = re.sub('sale in ', "", str(classified_cityname))
    classified_cityname = re.sub('rent in ', "", str(classified_cityname))
    classified_cityname = re.sub(' - Immoweb', "", str(classified_cityname))

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

    #check number of rums
    if classified_room == "":
        classified_room = None

    # Print the information
    print("Locality:", classified_cityname)
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
    if classified_swimming_pool == "Yes" or "True".casefold():
        classified_swimming_pool = 1
    else:
        classified_swimming_pool = 0

    print("Swimming pool:", classified_swimming_pool)


    print("ID number:", classified_id)
    print("State of the building:", classified_state_of_building)


    #using dictory to store info for csv file
    data_dict = {
        "Locality": classified_cityname,
        "Zip code:": classidied_zip_code,
        "Kitchen": classified_kitchen,
        "Type of property": classified_type,
        "Subtype of property": classified_subtype,
        "Price of property in euro": classified_price,
        "Number of bedrooms": classified_room,
        "Terrace": classified_terrace,
        "Garden": classified_garden,
        "Garden area": classified_garden_area,
        "Surface of the land": (classified_surface_land),
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
    immo()
    end_time = time.time()  # Record the end time
    print("Execution time: ", end_time - start_time, "seconds")  # Print the execution time

