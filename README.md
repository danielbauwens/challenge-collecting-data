# challenge-collecting-data
by Oleksandr, Bram and Daniel


![dataset](./assets/csvfile.png)


## Installation and Requirements
Using Python 3.11 and 'pip install -m requirements.txt' to get all required packages to run.


## Usage
To run the code, simply open your command prompt(cmd), powershell or vscode terminal window and type "python main.py" or use the path to both the python.exe and the main.py file. That would look something like this:    

'c:/Users/Daniel/Documents/GitHub/Challenge-Data/.challenge_data_env/Scripts/python.exe c:/Users/Daniel/Documents/GitHub/Challenge-Data/main.py'   
   
To correctly run the data-collection program, you need to specify a number between 1 - 333(333 is the maximum value the website we use to scrape from can handle for page numbers). This will provide slightly less than 20.000 scraped listings.


## Timeline
Project 1(out of 4) was started on the 26th of June 2023, and completed on 30/06/2023.     

Overview of timeline:    
Day 1: Delagation of tasks; Oleksandr main code structure, Bram creates a flowchart for required parameters, Daniel looks into the page elements for extractable information.    
Day 2: Bram finishes up with flowchart and researches Concurrency for improvements in speed, Oleksandr extracts most required data from javascript dictionaries, Daniel creates code to grab the list of URLs that need to be scraped.     
Day 3: Bram starts work on duplication checking code, Oleksandr focuses on data extraction speed(concurrency/threading) + structuring the CSV file, Daniel troubleshoots problems. The whole group also discusses the project together to gain a better understanding of it.   
Day 4: Career coach day, no progress towards the data assignement project.   
Day 5: Bram continues work on duplication checking code, discussing with Coach and rest of team, Oleksandr cleans up code and improves structure with functions + more comments, Daniel troubleshoots code and other (merging)issues together with team + finishes up on README. Finishing touches: created a requirements.txt file for easy installation.


![dataset](./assets/flowchart_group5.PNG)


## About
This is the first out of a four part study project to make a working data model that analyses the current Belgian housing market, and is able to predict House- and Apartment pricing accurately. Our dataset uses +10.000 listings.     

## Potential Improvements

- More Data     
- Selenium function to extract missing area values    
- Fix duplicate checking code     
- Better interface (G)UI     
- Async requests for faster data extraction     
- Expand property data   
- Safety check if user exceeds max value input  
- ...    


## Credits
Credits for this project goes to:    

 Oleksandr Tsepukh: https://www.linkedin.com/in/oleksandr-tsepukh-ba4985279?   - Main Developer    
Bram Michielsen: https://www.linkedin.com/in/brammichielsen?   - Repository Manager      
Daniel Bauwens: https://www.linkedin.com/in/daniel-bauwens-5515a8256/?   - Project Lead    

