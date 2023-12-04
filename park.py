import requests
from tinydb import TinyDB, Query
from bs4 import BeautifulSoup
import os
from email.message import EmailMessage
import ssl
import smtplib

# db = TinyDB('db.json')
# todo = Query()

# all_records = db.all()
# for record in all_records:
#     license = record["license_plate"]
#     name = record["name"]
    # print(license)

#creates a new session and stores it in the s variable
s = requests.session()
r = s.get("https://cincinnati.citationportal.com/") # creates a get request and stores it in the r variable for later
url = "https://cincinnati.citationportal.com/Citation/Search"

#Adam's license plate number
licensePlate = "JGA7846"
    
email_body = ""

has_closed_tickets = False


soup = BeautifulSoup(r.text, 'html.parser')

#this stores the information gathered by beautiful soup into a tag
#attributes of the tag are: name, type, attrs
tag = soup.find("input", attrs={"name":"__RequestVerificationToken","type":"hidden"}).attrs["value"] #attrs[] is what displays the token

#payload is setting up a dictionary
payload = {
    "__RequestVerificationToken": tag,
    "Type": "PlateStrict",
    "Term": licensePlate
}
    # Send the POST request
response = s.post("https://cincinnati.citationportal.com/Citation/Search", data=payload)

    # Parse the response to extract the information you need
result_soup = BeautifulSoup(response.text, 'html.parser')
        # This prints out just the information about the tickets you have (paid or unpaid)
table_div = result_soup.find("div", class_="table-responsive")

table = table_div.find("table")


# Iterate through rows in the table
for row in table.find_all("tr", class_="k-master-row"):
    # Find td elements within the current row
    td_elements = row.find_all("td", class_="k-table-td")

    # Check if there are enough td elements in the row
    if len(td_elements) >= 7:
        location = td_elements[1].get_text(strip=True)
        plate = td_elements[2].get_text(strip=True)
        issue_date = td_elements[4].get_text(strip=True)

        # Extract the text directly from the td element for the "Status"
        status = td_elements[6].text.strip()

        if status.lower() == "CLOSED PAID":
            has_closed_tickets == True

        # Print the extracted information
        email_body += (f"Location: {location}, Plate: {plate}, Issue Date: {issue_date}, Status: {status}\n\n")
      
    else:
        print("Not enough td elements in the row.")

# Save the HTML response to a file
with open("output.html", "w+") as f:
    f.write(response.text)




#The email sender
email_sender = 'webba7099@gmail.com'
email_password = 'gruw aanp wpao gfmz'
email_reciever = 'adamwebb846@gmail.com'


subject = 'Check this'

if not has_closed_tickets:
    email_body == "No open tickets, You are good!"

body = email_body


em = EmailMessage()
em['From'] = email_sender
em['To'] = email_reciever
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_reciever, em.as_string())
