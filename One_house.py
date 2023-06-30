import time
import requests
from bs4 import BeautifulSoup
import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor

def get_links(session, pages):
    """
    This function retrieves the links for the property listings.
    
    Parameters:
    session: A requests.Session object for making HTTP requests
    pages: The number of pages to scrape for property links

    Returns:
    links: A list containing the links for each property listing
    """
    
    links = []  # Initialize an empty list to hold the links
    start_time = time.time()  # Start time of the link extraction process

    print("Extracting links...")

    # Loop over the number of pages to scrape
    for i in range(pages):
        # URLs for houses and apartments for sale
        url = f"https://www.immoweb.be/en/search/house/for-sale?countries=BE&page={i+1}&orderBy=relevance"
        url2 = f"https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&page={i+1}&orderBy=relevance"

        # Iterate over both URLs
        for url in [url, url2]:
            response = session.get(url)  # Send a GET request to the URL
            soup = BeautifulSoup(response.content, 'html.parser')  # Parse the response content with BeautifulSoup
            memories = soup.find_all(class_='card__title-link')  # Find all elements with the class 'card__title-link'

            # Loop over all the links found
            for link in memories:
                if link.find_parent('h3'):  # If the link has a parent element of 'h3', ignore it
                    continue
                else:  # If the link does not have a parent element of 'h3', append it to the links list
                    links.append(link.get('href'))

    end_time = time.time()  # End time of the link extraction process
    print("Links extracted successfully!")
    print("Execution time: ", end_time - start_time, "seconds")  

    return links  # Return the list of links



def initialize_csv():
    """
    This function initializes a CSV file with the specified headers.

    It uses the csv module's DictWriter to create a CSV file that can be easily 
    written to using dictionaries. The keys of the dictionaries will correspond 
    to the headers in the CSV file.

    The filename is hardcoded to "property_data.csv", and the headers are a list 
    of strings that correspond to the data that will be written to the file.
    """

    # Define the filename
    filename = "property_data.csv"

    # Define the headers of the CSV file. These are the names of the fields each row will have.
    headers = [
        "Raw num:",
        "Locality",
        "Zip code",
        "Kitchen",
        "Type of property",
        "Subtype of property",
        "Price of property in euro",
        "Type of Sale",
        "Number of bedrooms",
        "Living area",
        "Terrace",
        #"Terrace area",
        "Garden",
        "Garden area",
        "Surface of the land(or plot of land)",
        "Number of facades",
        "Swimming pool",
        "ID number",
        "State of the building",
        "URL"
    ]

    # Open the file in write mode. The newline='' argument is necessary for the csv module to work properly on both 
    # Windows and Unix systems. The file is opened in utf-8 encoding to support a wide range of characters.
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Create a DictWriter object. This object will be used to write rows to the CSV file. The fieldnames 
        # argument defines the order in which values in the dictionary are written to the CSV file.
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # Write the headers to the CSV file. This is done by calling the writeheader method on the DictWriter object.
        writer.writeheader()



def process_link(session, url):
    """
    This function processes a single property link. The steps involved in processing the link are:
    1. Fetching the page content using an HTTP GET request.
    2. Parsing the page content using BeautifulSoup.
    3. Extracting the relevant data from the parsed page content.
    4. Writing the extracted data to a CSV file.

    The `session` parameter is an instance of requests.Session. Using a Session object gains efficiency when making
    multiple requests to the same host by reusing the underlying TCP connection.

    The `url` parameter is a string that contains the URL of the property listing that should be processed.
    """

    # Print a status message to indicate which URL is currently being processed.
    print("Processing: ", url)

    # Use the requests.Session instance to make an HTTP GET request to the provided URL. 
    # This sends a request to the server to return the content located at the specified URL.
    response = session.get(url)

    # Parse the content of the response using BeautifulSoup. The "html.parser" argument tells BeautifulSoup to use 
    # Python's built-in HTML parser to parse the page content.
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the relevant data from the parsed page content. This is done by calling the previously defined 
    # 'extract_relevant_data' function, which returns a dictionary of the relevant data.
    data_dict = extract_relevant_data(soup, url)

    # Write the extracted data to the CSV file. This is done by calling the previously defined 'write_to_csv' function,
    # which takes a dictionary of data and writes it to the CSV file as a new row.
    write_to_csv(data_dict)



def extract_relevant_data(soup, url):
    """
    This function extracts the relevant data from the HTML content of a property listing page. 
    It uses the BeautifulSoup instance of the HTML content (`soup`) and the URL of the page (`url`) as inputs.

    After identifying and extracting the relevant data from the HTML content, the function packages the 
    data into a dictionary and returns it.
    """

    # The data we're interested in is contained within a script tag, serialized as a JSON object. 
    # Find the script tag whose content includes "window.dataLayer".
    script = soup.find("script", string=lambda t: "window.dataLayer" in t).string

    # The script tag's content is a JavaScript command, not just the JSON data, so split the string on 
    # "window.dataLayer = " and take the second part. Remove trailing whitespace and the final semicolon.
    # Then load the resulting string as JSON.
    data = json.loads(script.split("window.dataLayer = ")[1].strip().rstrip(";"))

    # Retrieve the necessary details from the data layer.
    classified_url = url
    classified_id = data[0]["classified"]["id"]  
    classified_type = data[0]["classified"]["type"]
    classified_subtype = data[0]["classified"]["subtype"]  
    classified_price = data[0]["classified"]["price"] 
    classified_kitchen = data[0]["classified"]["kitchen"]["type"]
    classified_room = data[0]["classified"]["bedroom"]["count"]
    classified_terrace = data[0]["classified"]["outdoor"]["terrace"]["exists"]
    classified_garden = data[0]["classified"]["outdoor"]["garden"]["surface"]
    classified_surface_land = data[0]["classified"]["land"]["surface"]
    classified_swimming_pool = data[0]["classified"]["wellnessEquipment"]["hasSwimmingPool"]
    classified_state_of_building = data[0]["classified"]["building"]["condition"]
    classified_zip_code = data[0]["classified"]["zip"]

    # The second part of the data we need is in a different script tag, so again find the script tags 
    # and look for one that contains "window.classified".
    scripts = soup.find_all('script')
    data_class = None
    for script in scripts:
        if 'window.classified' in script.text:  # The variable containing the JSON data
            clas_sting = re.search('window.classified = ({.*?});', script.text).group(1)
            data_class = json.loads(clas_sting)
            break
    

    # Extract the required details from the second data layer.
    classified_cityname = data_class['property']['location']['locality']
    classified_living_area = data_class['property']["netHabitableSurface"]
    classified_number_of_facades = data_class['property']['building']['facadeCount']
    # classified_terrace_area = ["property"]["terraceSurface"] #need to find right key

    # Identify the type of sale based on which sales type flags are set to true.
    flags = data_class['flags']
    sales_types = ['isPublicSale', 'isNotarySale', 'isLifeAnnuitySale', 'isInvestmentProject', 'isSoldOrRented', "isAnInteractiveSale","isUnderOption"]
    classified_sales_type = None

    for sales_type in sales_types:
        if sales_type in flags and flags[sales_type]:
            classified_sales_type = sales_type
            break

    # check number of rooms
    if classified_room == "":
        classified_room = None

    # check kitchen
    if classified_kitchen == "not installed":
        classified_kitchen = 0
    elif classified_kitchen == "":
        classified_kitchen = None
    else:
        classified_kitchen = 1

    # check terrace
    if classified_terrace == "false":
        classified_terrace = 0
    elif classified_terrace == "":
        classified_terrace = None
    else:
        classified_terrace = 1

    # check garden
    if classified_garden == "false":
        classified_garden = 0
        classified_garden_area = None
    elif classified_garden == "":
        classified_garden = None
        classified_garden_area = None
    else:
        classified_garden_area = classified_garden
        classified_garden = 1

    # check swimming pool data
    if classified_swimming_pool == "true":
        classified_swimming_pool = 1
    elif classified_swimming_pool == "":
        classified_swimming_pool = None
    else:
        classified_swimming_pool = 0

    # Return the extracted data as a dictionary.
    return {
        "Raw num:": None,
        "Locality": classified_cityname,
        "Zip code": classified_zip_code,
        "Kitchen": classified_kitchen,
        "Type of property": classified_type,
        "Subtype of property": classified_subtype,
        "Price of property in euro": classified_price,
        "Type of Sale": classified_sales_type,
        "Number of bedrooms": classified_room,
        "Living area": classified_living_area,
        "Terrace": classified_terrace,
        #"Terrace area": classified_terrace_area, its not working. at least now
        "Garden": classified_garden,
        "Garden area": classified_garden_area,
        "Surface of the land(or plot of land)": classified_surface_land,
        "Number of facades": classified_number_of_facades,
        "Swimming pool": classified_swimming_pool,
        "ID number": classified_id,
        "State of the building": classified_state_of_building,
        "URL": classified_url
    }



def write_to_csv(data_dict):
    """
    This function writes a dictionary of property data to a CSV file.
    
    Args:
    data_dict (dict): A dictionary where the keys are the column names and the 
    values are the corresponding data values for a property listing.
    """

    # Specify the name of the CSV file to which data will be written.
    filename = "property_data.csv"

    # Open the specified file in append mode ('a'). This means that data will be added 
    # to the end of the file, instead of overwriting the existing content. 
    # 'newline='' ensures that the writer doesn't add any extra newlines between rows, 
    # and 'encoding='utf-8' ensures that the data is written in UTF-8 encoding.
    with open(filename, 'a', newline='', encoding='utf-8') as f:

        # Create a DictWriter object. This object lets us write dictionaries to a CSV file. 
        # The fieldnames parameter is a list of keys in the dictionary. The writer will 
        # write these keys as the column headers in the CSV file.
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())

        # Write the dictionary as a row in the CSV file.
        writer.writerow(data_dict)



def main():
    """
    Main function to run the scraping script. It initializes the necessary setup,
    scrapes the data from the target site, and finally prints the execution time.
    """

    # Record the start time of the script. This is used to calculate total execution time.
    start_time = time.time()

    # Create a Session object. A Session object will persist certain parameters across requests.
    # For example, if you log into a website, the Session object will keep you logged in for the duration of that session.
    session = requests.Session()

    # Set the number of pages to scrape. This can be modified according to the requirements.
    pages = 5

    # Call the function to initialize the CSV file. It creates the CSV file and writes the column headers.
    initialize_csv()

    # Call the function to get all the property links from the defined number of pages.
    # This function returns a list of URLs, each corresponding to a specific property listing.
    links = get_links(session, pages)

    print("Starting scraping...")

    # Use ThreadPoolExecutor to run multiple threads in parallel. This significantly improves performance when dealing with a large number of links.
    # Here, we specify a max of 16 workers (i.e., 16 threads running in parallel). This value can be adjusted based on the capabilities of the system.
    num_workers = 16
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # For each link in the links list, we use the map function to apply the process_link function.
        # We use a lambda function to pass the session object to the process_link function for each URL.
        executor.map(lambda url: process_link(session, url), links)

    # Record the end time of the script after all the scraping is done.
    end_time = time.time()

    print("Scraping done!")

    # Calculate the total execution time by subtracting the start_time from the end_time.
    # Print this value to see how long the entire script took to run.
    print("Execution time: ", end_time - start_time, "seconds")  

if __name__ == "__main__":
    # This condition ensures that the main function is only run when the script is executed directly (not imported as a module).
    # If this script is being imported from another script, the calling script can choose when to call the main function.
    main()
