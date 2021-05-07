#!/usr/bin/env python3

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests, re, smtplib, sys

def send_text_msg(message,usr,pwd,txt_add1,txt_add2):
    server = smtplib.SMTP( 'smtp.gmail.com', 587 )
    server.starttls()
    server.login(usr,pwd)
    message = '\n' + message
    server.sendmail('Brazil Room Watcher', txt_add1, message)
    server.sendmail('Brazil Room Watcher', txt_add2, message)
    server.quit()

def fetch_html(url):
    return requests.get(url).text

def make_soup(html):
	return BeautifulSoup(html, 'html.parser')

def find_all_weeks(soup):
	return soup.find_all('tr', class_='ip-tr-week')

def find_all_days(week):
    return week.find_all('td', class_='ip-tablecalendar-month-daycell')

def find_date(day):
    return day.find_all('td')[0].get_text()

def find_availability_for_day(day):
    return day.find_all('td')[1].get_text()

def find_availability_for_month(soup):
    weeks = find_all_weeks(soup)
    avail_by_date = {}
    for w in weeks:
        days = find_all_days(w)
        for d in days:
            avail_by_date[find_date(d)] = find_availability_for_day(d)
    return avail_by_date

def find_all_monthly_availability():
    mar_url = 'https://apm.activecommunities.com/ebparks/facility_search?IsCalendar=true&facility_id=150&year=2022&month=3&startyear=2022&endyear=2022'
    apr_url = 'https://apm.activecommunities.com/ebparks/facility_search?IsCalendar=true&facility_id=150&year=2022&month=4&startyear=2022&endyear=2022'
    may_url = 'https://apm.activecommunities.com/ebparks/facility_search?IsCalendar=true&facility_id=150&year=2022&month=5&startyear=2022&endyear=2022'
    jun_url = 'https://apm.activecommunities.com/ebparks/facility_search?IsCalendar=true&facility_id=150&year=2022&month=6&startyear=2022&endyear=2022'
    mar_availability = find_availability_for_month(make_soup(fetch_html(mar_url)))
    apr_availability = find_availability_for_month(make_soup(fetch_html(apr_url)))
    may_availability = find_availability_for_month(make_soup(fetch_html(may_url)))
    jun_availability = find_availability_for_month(make_soup(fetch_html(jun_url)))
    monthly_availability = {
        'mar': mar_availability,
        'apr': apr_availability,
        'may': may_availability,
        'jun': jun_availability,
    }
    return monthly_availability

def find_all_saturday_availability(monthly_availability):
    saturdays = {
        'mar': ['5','12','19','26'],
        'apr': ['2','9','16','23','30'],
        'may': ['7','14','21','28'],
        'jun': ['4','11','18','25']
    }
    sat_avail = {
        'mar': [],
        'apr': [],
        'may': [],
        'jun': []
    }
    for mon in list(monthly_availability.keys()):
        for d in list(monthly_availability[mon].keys()):
            if d in saturdays[mon]:
                sat_avail[mon].append({d: monthly_availability[mon][d]})
    return sat_avail

def send_text_when_available(sat_avail,usr,pwd):
    avail_sats = []
    for mon in sat_avail:
        for s in sat_avail[mon]:
            if list(s.values())[0] != 'Fully Booked':
                message =  mon + ' ' + list(s.keys())[0] + ' has this opening: ' + list(s.values())[0]
                avail_sats.append(message)
    if len(avail_sats) > 0:
        for s in avail_sats:
            message = 'There is an open Sat at the Brazil Room!\n'
            message += s + '\n' + '\n(888-327-2757, option 2) Monday-Friday 9am-3pm to book\n'
            send_text_msg(message,usr,pwd)
    # else:
    #     message = 'No Saturdays at the Brazil room :('
    #     send_text_msg(message,usr,pwd)

sat_avail = find_all_saturday_availability(find_all_monthly_availability())
send_text_when_available(sat_avail, sys.argv[1], sys.argv[2])