# Overview

A fork of [Arxiv-filter](https://github.com/gkahn13/arxiv-filter) updated to the latest Arxiv API and with some quality of life updates.

ArxivFilter checks the Arxiv for you each day, filtering by both your chosen and categories and then by keyword. You supply a list of keywords and it will only send you articles where the abtract, title or author list contains at least one of those keywords.

# Installation

You should install this on a machine that is always on and has internet access. Many Arxiv readers will have access to an institute machine which is configured with email access, this allows us to use smtplib to send the result and is recommended.

#### Choose categories and keywords

Arxiv filter works by finding all articles that
1. Were submitted in the past day
2. Are in one of the categories listed in categories.txt
3. Have at least one of the keywords listed in keywords.txt in either the title, author list, or abstract

You should change categories.txt and keywords.txt based on your interests. Keywords are not case-sensitive.

#### Setup Email

For simplicity, we just use the smtplib library. Create an email_config.py file with the following contents

SERVER = "localhost"
FROM = "your_email_on_the_server"
TO =["recipient_address","2nd_recipient_address"]
SUBJECT ="Your Arxiv Report"

This will allow  smtplib to send an email from your address if you can send mail from your terminal (almost certainly the case if you run this on a university server).

#### Setup the script

Run the following to install the necessary python libraries:
```
$ pip install -r requirements.txt
```
Next, we want the script to be called once a day. Edit crontab by running
```
$crontab -e
```
and add the following line
```
0 7 * * * python /path/to/arxiv-filter/run.py
```
which will run the script once a day at 7:00am.

If you want to immediately test if the installation works, do
```
$ python /path/to/arxiv-filter/run.py
```
(Note: arxiv filter searches over submissions from the past week and---after filtering---only emails you submissions that it has not sent you before. If you want to start from scratch, delete the file previous_arxivs.txt)
