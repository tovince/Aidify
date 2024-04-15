import pandas as pd
import requests
from bs4 import BeautifulSoup

#Scraping the TDSB website
url = 'https://www.tdsb.on.ca/Find-your/School/By-School-Name/Secondary'
response = requests.get(url)

# Parse the website with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all 'a' tags with class "SchoolNameLink" in the parsed content
school_link_tags = soup.find_all('a', class_="SchoolNameLink")

base_url = "https://www.tdsb.on.ca/"
full_urls = []  # Initialize an empty list to store the full URLs

# Iterate over the 'a' tags
for tag in school_link_tags:
    relative_url = tag.get('href')    # Get the 'href' attribute of the 'a' tag, which is a relative URL
    full_url = base_url + relative_url
    full_urls.append(full_url)  # Add the full URL to the list

# Function to iterate through the list of URLs. Visit the site and then extract Principal and VP info
def school_extract(school_URLs):
    data = []
    for school_url in school_URLs:
        response = requests.get(school_url)     # Send a GET request to the webpage
        soup = BeautifulSoup(response.text, 'html.parser')      # Parse the webpage's content with BeautifulSoup
        
        #Get name of school
        school_name_element = soup.find('span', id="dnn_ctr2796_ViewSPC_ctl00_lblSchoolName")
        if school_name_element:  # If the tag is found, get the text within the tag, which is the school name
            school_name = school_name_element.text
            print(school_name)
        else:
            print("School name not found")

        #Get email of school. 
        # Find the 'a' tag with the specific id for the school email 
        email_element = soup.find('a', id="dnn_ctr2796_ViewSPC_ctl00_lnkEMail")
        if email_element:
            email = email_element.text
            print(f"School Email: {email}")
        else:
            print("School email not found")

        #Get Principal's name:
        principal_name_element = soup.find('span', id="dnn_ctr2796_ViewSPC_ctl00_lblPrincipal")
        if principal_name_element:
            principal_name = principal_name_element.text
            print(principal_name)
        else:
            print("no name")

        #Get Principal's email:
        name_parts = principal_name.split()
        principal_email = '.'.join(name_parts).lower() + '@tdsb.on.ca'
        print(principal_email)


        #Get Vice Principal's name:
        # Find the span tag with the specific id
        vp_element = soup.find('span', id="dnn_ctr2796_ViewSPC_ctl00_lblVicePrincipals")

        if vp_element:
            # Get the vice-principals' names
            vp_names = list(vp_element.stripped_strings)

            # Assign the names to variables
            # If there are less than 4 vice-principals, fill the rest with None
            vp_names += [None] * (4 - len(vp_names))  # Fill the rest with None

            # Create emails for the vice-principals
            vp_emails = ['.'.join(name.split()).lower() + '@tdsb.on.ca' if name else None for name in vp_names]

        else:
            print("Vice-Principals' names not found")

        # # Get Salutation:
        # vp_names_str = ', '.join([f'Vice-Principal {name}' for name in vp_names if name])  # Create a single string of VP names
        # Salutation = f"Dear Principal {principal_name}, {vp_names_str}, and Staff of {school_name}" if vp_names_str else f"Dear Principal {principal_name} and Staff of {school_name}"

        # Get Last Names:
        vp_last_names_str = ', '.join([f'Vice-Principal {name.split()[-1]}' for name in vp_names if name])  # Create a single string of VP last names
        principal_last_name = principal_name.split()[-1] if principal_name else ""
        # Get Salutation:
        Salutation = f"Dear Principal {principal_last_name}, {vp_last_names_str}, and Staff of {school_name}," if vp_last_names_str else f"Dear Principal {principal_last_name} and Staff of {school_name},"

        # Append the data (replace the placeholders with actual values)
        data.append([Salutation, school_name, email, principal_name, principal_email] + vp_names + vp_emails)

        # Clear or reset the variables before the next record
        Salutation = ""
        school_name = ""
        email = ""
        principal_name = ""
        principal_email = ""
        vp_names = [None] * 4
        vp_emails = [None] * 4

        # Create a DataFrame and export to Excel
        df = pd.DataFrame(data, columns=["Salutation","School Name", "School Email", "Principal Name", "principal_email","VP1 Name", "VP2 Name", "VP3 Name", "VP4 Name", "VP1 Email", "VP2 Email", "VP3 Email", "VP4 Email"])
        df.to_excel("TDSB-HighSchool-List1.xlsx", index=False)

#Send into "school_extract" the list of all school URLs to extract info
school_extract(full_urls)
