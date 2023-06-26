from bs4 import BeautifulSoup
import requests
import json

# Send a GET request to the web page URL
url = "https://www.immoweb.be/en/classified/house/for-sale/libin/6890/10657263"
response = requests.get(url)

# Parse the response content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the HTML element that contains the JavaScript code with window.dataLayer
# You may need to inspect the web page source code to find the right selector
script = soup.find("script", string=lambda t: "window.dataLayer" in t).string # Script element # Script element
# Use the json.loads method to convert the text into a Python dictionary
# You may need to remove some extra characters or lines from the text before parsing it
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

""" classified_frontages = soup.find(string="Number of frontages").find_next_sibling('td').contents[0] """

# Modify the values of some variables based on some conditions
if classified_kitchen == "not installed":
    classified_kitchen = "Yes"
elif classified_kitchen == "installed":
    classified_kitchen = "No"
else:
    classified_kitchen = "Unknown information"

#m2 it's not ready
if classified_terrace == "true":
    classified_terrace = "Yes, " + "m²"
elif classified_terrace == "false":
    classified_terrace = "No"
else:
    classified_terrace = "Unknown information"

if classified_swimming_pool != "":
    classified_swimming_pool = "No"
else:
    classified_swimming_pool = "Yes"

# Print the information

print("Fully equipped kitchen:", classified_kitchen)
print("Type of property:", classified_type)
print("Subtype of property:", classified_subtype)
print("Price of property:", classified_price, "euro")
print("Number of bedrooms:", classified_room)
print("Is terrace exists:", classified_terrace)
print("Is garden exists: Yes,", classified_garden, "m²")#we only can get m2, tommorow i will do it better
print("Surface of the land(plot of land):", classified_surface_land, "m²")
""" print("Number of frontages:", classified_frontages) """
print("Is swimming pool exists:", classified_swimming_pool)
print("ID number:", classified_id)
print("State of the building:", classified_state_of_building)