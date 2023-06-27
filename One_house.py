from bs4 import BeautifulSoup
import requests
import csv
import json
import re

# Send a GET request to the web page URL
url = "https://www.immoweb.be/en/classified/house/for-sale/libin/6890/10657263"
response = requests.get(url)



# Parse the response content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

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

# check kitchen
if classified_kitchen == "not installed":
    classified_kitchen = 0
elif classified_kitchen == "":
    classified_kitchen = None
else:
    classified_kitchen = 1 

#check number of rums
if classified_room == "":
    classified_room = None

#check terrace
if classified_terrace == "false": 
    classified_terrace = 0
elif classified_terrace == "":
    classified_terrace = None
else:
    classified_terrace = 1

#check garden
if classified_swimming_pool != "":
    classified_swimming_pool = "No"
else:
    classified_swimming_pool = "Yes"

# Print the information

print("Locality:", classified_cityname)
print("Zip code:", classidied_zip_code)
print("Fully equipped kitchen:", classified_kitchen)
print("Type of property:", classified_type)
print("Subtype of property:", classified_subtype)
print("Price of property:", classified_price, "euro")
print("Number of bedrooms:", classified_room)
print("Is terrace exists:", classified_terrace)


if classified_garden == "false": 
    classifed_garden = 0
elif classified_garden == "":
    classifed_
else:
    classified_garden_area = classified_garden
    classified_garden = 1

print("Is garder exists:", classifed_garden)

print("Surface of the land(plot of land):", classified_surface_land, "m²")
""" print("Number of frontages:", classified_frontages) """
print("Is swimming pool exists:", classified_swimming_pool)
print("ID number:", classified_id)
print("State of the building:", classified_state_of_building)


#using dictory to store info for csv file
data_dict = {
    "Locality": classified_cityname,
    "Zip code:": classidied_zip_code,
    "Fully equipped kitchen": classified_kitchen,
    "Type of property": classified_type,
    "Subtype of property": classified_subtype,
    "Price of property": classified_price,
    "Number of bedrooms": classified_room,
    "Is terrace exists": classified_terrace,
    "Is garden exists": "Yes, " + str(classified_garden) + " m²",
    "Surface of the land": str(classified_surface_land) + " m²",
    "Is swimming pool exists": classified_swimming_pool,
    "ID number": classified_id,
    "State of the building": classified_state_of_building
}

# Specify the name of the CSV file
filename = "property_data.csv"

# Write the dictionary to the CSV file
with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data_dict.keys())
    writer.writeheader()
    writer.writerow(data_dict)