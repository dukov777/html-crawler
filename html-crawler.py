from bs4 import BeautifulSoup
import argparse
# print today date
from datetime import date
from datetime import date, timedelta
import mysql.connector


def process_html_content(div_advert):
    job_title = ""
    link = ""
    company = ""
    
    div_left = div_advert.find('div', class_='left')
    if div_left:
        a_tag = div_left.find('a', class_='black-link-b')
        if a_tag:
            job_title = a_tag.get('title')
            # print(job_title)    
        else:
            print("No <a> tag found within <div class='left'>")
    else:
        print("No <div class='left'> found in the HTML")

    div_right = div_advert.find('div', class_='right')
    if div_right:
        a_tag = div_right.find('a')
        if a_tag:
            company = a_tag.get('title')
            link = a_tag.get('href')
            
            # print(company)
            # print(link)
        else:
            print("No <a> tag found within <div class='right'>")
    else:
        print("No <div class='right'> found in the HTML")

    return (job_title, company, link)


def __main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('filename', type=str, default='page_content.html', help='HTML content of the page')
    args = parser.parse_args()
    

    try:
        # Read HTML content from file
        with open(args.filename, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')   
    except Exception as e:
        print(f"Error: {e}")
        return
    
    jobs = JobsModel()
    jobs.open_db()

    # Find all job adverts
    for div_advert in soup.find_all('div', class_='mdc-card'):
        job_advert = process_html_content(div_advert)
        jobs.write_jobs(job_advert)
        
    # Compare the job_advert with the previous day job_advert. The comparison is done by job_title and company.
    # If the job_advert is not present in the previous day job_advert, then send an email to the user.
    # If the job_advert is present in the previous day job_advert, then do nothing.

    # Get yesterday's date
    yesterday = date.today() - timedelta(days=1)

    today_job_adverts = jobs.get_job_adverts_by_date(date.today())
    
    # Query the job_advert table for job adverts from yesterday
    previous_day_job_adverts = jobs.get_job_adverts_by_date(yesterday)
    
    new_adverts = set(today_job_adverts) - set(previous_day_job_adverts)
    print(new_adverts)

    jobs.close_db()
    

class JobsModel:
    def __init__(self):
        self.mydb = None
        self.mycursor = None
        
    
    def close_db(self):
        # close mysql connection
        self.mydb.close()
    
    def open_db(self):
        # open mysql connection
        # open job_adverts database
        # open job_advert table

        # Open MySQL connection
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="test_user",
            password="test_user",
            database="job_adverts"
        )

        # Open job_adverts database
        self.mycursor = self.mydb.cursor()

        # Open job_advert table
        # table is organized as follows: id, timestamp (automaticaly filled), job_title, company, link
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS job_advert (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATE, job_title VARCHAR(255), company VARCHAR(255), link VARCHAR(255))")
    
    def write_jobs(self, job_advert):
        # write to sql database automatically adds timestamp to the record
        sql = "INSERT INTO job_advert (timestamp, job_title, company, link) VALUES (NOW(), %s, %s, %s)"
        # write to sql database automatically adds timestamp to the record
        self.mycursor.execute(sql, job_advert)
        self.mydb.commit()

    def get_job_adverts_by_date(self, date):
        # Query the job_advert table for job adverts from today
        self.mycursor.execute("SELECT job_title, company FROM job_advert WHERE DATE(timestamp) = %s", (date,))
        today_job_adverts = self.mycursor.fetchall()
        return today_job_adverts


if __name__ == "__main__":
    __main()    

