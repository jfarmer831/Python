import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as bs
import urllib.request
import json
import re
import requests
from django.shortcuts import get_object_or_404

from .models import HockeyTeam, BaseballTeam

class WeatherScraper:

    def __init__ (self, zip):
        self.zipcode = zip

    #  Use Selenium to navigate to Weather.gov site.  The specific browser driver location
    #  required for instantiation is provided as a path in the call to Chrome().

        browser = webdriver.Chrome('DataApp/bin/chromedriver.exe')
        browser.get('http://weather.gov/')

        #  Upon landing at Weather.gov, the "Local forecast by" search box must be clicked to
        #  remove default "Enter location" text before sending the user's zipcode.
        browser.find_element_by_name('inputstring').click()
        browser.find_element_by_name('inputstring').send_keys(self.zipcode)

        #  Wait a while until the "Local forecast" search returns with alternate results for the
        #  user's zipcode before clicking the "Go" button to actually begin the search for local data.
        time.sleep(1)
        browser.find_element_by_name('btnSearch').click()

        #  Again wait a while until the page refreshes from the local data search before getting the
        #  URL info from the results page.
        time.sleep(1)
        url = browser.current_url

        #  Open the URL above for local forecast and get the HTML to parse with Beautiful Soup 4 (BS4)
        with urllib.request.urlopen(url) as response:
            page = response.read()
        soup = bs(page, 'html.parser')

        #  Close the browser opened for Weather.gov. 
        #  ToDo:  Can the whole operation of opening the browser be made silent, so the user doesn't see it?
        browser.quit()

        # BS4 allows easy extraction of local temperature data by looking at a unique class identifier.
        self.temp = soup.find(class_='myforecast-current-lrg').get_text()

        #  For the humidity and last update info a slightly more sophisticated drill down is required.
        #  For the only table on the results page, find all <td> tags.  These table cells contain either
        #  label text for the type of weather data, or the data value as text.
        condensed_soup = soup.table.find_all('td')
        for index,item in enumerate(condensed_soup):
            #  Since the weather data value is always in the cell to the right of the data type label, when
            #  we find the desired data type we're looking for, enumerating the iterable allows us to use
            #  index + 1 to get the data value.
            if item.get_text() == 'Humidity':
                self.humidity = condensed_soup[index + 1].get_text().strip()
       
            if item.get_text() == 'Last update':
                self.last_update = condensed_soup[index + 1].get_text().strip()


        #  Search entire local weather page for detailed forecast section and find available "days" listed
        #  uniquely in <b> tags.  In addition, find all accompanying weather description text (short_desc)
        #  which also contains the predicted high temperature for the day.
        forecast = soup.find_all("div", {"id":"detailed-forecast-body"})
        days = forecast[0].find_all('b')
        short_desc = forecast[0].find_all('div', class_="col-sm-10 forecast-text")

        #  Initialize "offset" to track if date of 3 day forecast should start with today's date (0) or tomorrow's (1).
        #  Initialize "three_day" to track and limit the number of forecast days extracted.
        offset = 1
        three_day = 0
        self.desc_text = []
        self.day_date = []

        #  Iterate through the forecast days found above and if the text is "Today" or a regular day of the week (DOW),
        #  then add the forecast data to the respective attributes.  Note:  If day text is "Today", reset "offset" to 0
        # so that datetime object will start at today's date as opposed to tomorrow's date (offset=1)
        DOW = ['Today', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for index, day in enumerate(days):
            if day.get_text() in DOW and three_day < 3:
                if day.get_text() == 'Today':
                    offset = 0
                self.desc_text.append(short_desc[index].get_text())
                date = datetime.datetime.now() + datetime.timedelta(days=offset + three_day)
                date = date.strftime('%A %B %d %Y')
                self.day_date.append(date)
                three_day += 1


class MovieScraper:

    def __init__ (self):

        #  Open the URL for the Imdb top box office page and get the HTML to parse with Beautiful Soup 4 (BS4)
        with urllib.request.urlopen('https://www.imdb.com/chart/boxoffice') as response:
            page = response.read()
        soup = bs(page, 'html.parser')
        
        #  In typical French culinary tradition, perform a soup reduction to narrow the parsed HTML results
        #  to only the anchor tags within a single table element.
        movies = soup.table.find_all('a')
        pattern = re.compile(r'\w+')
        self.movie_list = []
        
        #  Not all anchor tags in the top box office table have text (only those that link to the movie name).
        #  Loop through the first ten anchors and add only those with movie name text to the movie_list attribute.
        for index in range(0,10):
            if re.search(pattern, movies[index].get_text()):
                self.movie_list.append(movies[index].get_text())
        

class NewsScraper:

    def __init__ (self):     
        
        content = requests.get('https://www.theverge.com/features').content
        soup = bs(content, 'html.parser')
        articles = soup.find_all('div', class_='c-compact-river__entry' ) # overall div class for articles
        title_list = [] # list to iterate in below for loop.
        url_list = []
        img_list = []
        
        for index in range(0,3): # for top 3 articles list the following

            title_list.append(articles[index].h2.get_text())
            url_list.append(articles[index].a['href'])
            img_list.append(articles[index].noscript.img['src'])
    
        all_list = zip(title_list, url_list, img_list) #group iterations through zip function
        self.all_list = all_list   
        
       
      

class EventScraper:
    def __init__(self, city, state):
        self.city = city
        self.state = state

        # Use Selenium to navigate to livenation site using chrome driver at the specified path.
        browser = webdriver.Chrome('DataApp/bin/chromedriver.exe')
        browser.get('https://www.livenation.com/')

        # A popup will appear when the page loads which can be closed by clicking outside of the entity.
        initial_load = ActionChains(browser).move_by_offset(50, 0).double_click()
        initial_load.perform()

        time.sleep(1)

        # Find the element using copy => xpath from chrome dev tools, and hover over the element to activate the dropdown.
        city_state = browser.find_element_by_xpath('//*[@id="ember693"]')
        hover = ActionChains(browser).move_to_element(city_state)
        hover.perform()

        time.sleep(1)
        # populate the appropriate input field with the user's information.
        user_info = self.city + ', ' + self.state
        send_user_info = browser.find_element_by_xpath('//*[@id="ember712"]')
        send_user_info.send_keys(user_info)
        
        time.sleep(1)
        # wait for the dropdown menu to populate and then press enter
        send_user_info.send_keys(Keys.RETURN)

        # the page needs time to load the new data for the specified city and state.
        time.sleep(1)

        # the new page with events generated for the user's city and state will be stored using Selenium's page_source function
            # we need to use .page_source because urllib's request method only returns html and not JavaScript related code? (I read this somewhere along the way, will have to go back and clarify).
        # then, the information will be parsed with Beautiful Soup, at which point we can grab all of the divs that hold relevant event data.
        html = browser.page_source
        soup = bs(html, 'html.parser')
        # find_all returns a Beautiful Soup ResultSet (list)
        target = soup.find_all('div', class_='event-feed-item')

        # we'll create new lists to hold each sub-target(s) data
        days = []
        dates = []
        months = []
        events = []
        venues = []

        # each each element returned in the ResultSet
        for results in target:

            day = results.find('span', class_='day').text # find the corresponding element, convert it to a string...
            days.append(day) # and store it in the appropriate new list we defined above.

            date = results.find('span', class_='date').text
            dates.append(date)

            month = results.find('span', class_='month').text
            months.append(month)

            event = results.h3.text
            events.append(event)
            
            venue = results.h4.text
            venues.append(venue)

        # using zip, we can pass in our lists, and return a list of tuples; zip infers that each index in one list will correspond to the same index in another list (or this is nonsense and I'm totally wrong)
        final = zip(days, dates, months, events, venues)
        self.final_list = list(final)

        # exit the browser and load the events_data.html page with the top events in the user's city and state.
        browser.quit()


class NasaScraper:

    def __init__ (self):

        #  Open the URL for the NASA API endpoint for their Astronomy Picture of the Day (APOD) and provide required
        #  API key to allow limited rate access to this resource.
        url = 'https://api.nasa.gov/planetary/apod?api_key=kK4OwaUtVghqi9A1m40BsWAueYlagAIUQFM6FYlw'
        serialized_data = urllib.request.urlopen(url).read()

        #  Load JSON response into data object and access known key names in order to set NasaScraper attributes.
        data = json.loads(serialized_data)
        self.image_src = data['url']
        self.title = data['title']
        self.detail = data['explanation']
        self.date = data['date']
            
class TechUpcomingScraper:

    def __init__(self):

        #  creating a variable of our link
        self.page_link = 'https://blog.bizzabo.com/technology-events'

        #here we are getting the actual content from this page
        self.page_response = requests.get(self.page_link, timeout=5)

        # this will parse the content and put it in the content variable
        self.page_content = bs(self.page_response.content, "html.parser")

        #we create an empty array, then loop through the page to store the
        #h2 elements which are the event titles
        self.eventList = [] 
        for i in range(6,11):
            pageItems = self.page_content.find_all("tr")[i].text
            self.eventList.append(pageItems)
        

class PodcastScraper: 

    def __init__(self):
        
        # URL for an RSS Feed of the top 10 podcasts on iTunes. Generated at https://rss.itunes.apple.com/en-us
        url = 'https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/10/explicit.json'
        # Open the URL and save the content to a variable. Note that the data is in JSON format
        json_data = urllib.request.urlopen(url).read()

        # Use the json module to convert the JSON data into a python dictionary
        python_dict = json.loads(json_data)
        # Access the list of podcasts from the newly created dictionary. Note that each podcast has its own dictionary with various keys, including "name" and "artistName"
        podcast_dicts = python_dict['feed']['results']

        # Create a list of strings with each podcast's name and artist name
        self.top_podcasts = []
        for podcast_dict in podcast_dicts:
            self.top_podcasts.append( '%s - %s' % (podcast_dict['name'], podcast_dict['artistName']) )

        
        
class NHLScraper:
    
    def __init__ (self, team):

        #  set the user's passed favorite team name to an attribute of the instance.
        self.team = team
        self.team_logo = 'img/NHL_Team_Logos/' + team + '.gif'

        #  from the user's favorite NHL team name, retrieve the team's ID (used by TheSportsDB.com api)
        #  from the record stored in the HockeyTeam model.
        nhl_team_data = get_object_or_404(HockeyTeam, team_name=team)
        nhl_team_id = nhl_team_data.team_id

        #  concatenate the team ID with the appropriate url prefix from TheSportsDB.com api to form
        #  the query for the user's favorite NHL team and read the data.
        url = 'https://www.thesportsdb.com/api/v1/json/1/eventsnext.php?id=' + nhl_team_id
        json_data = json.loads(urllib.request.urlopen(url).read())
        self.event_list = []

        #  pull strings (strFilename) from the JSON data which contain event descriptions for the team
        #  and process them to remove the "NHL " text segment at the start of each before appending to 
        #  the event_list attribute.
        for index in range(0,5):
            event_str = json_data['events'][index]['strFilename']
            strip_NHL = event_str[4:]
            self.event_list.append(strip_NHL)
            

class MLBScraper:
    
    def __init__ (self, team):

        #  set the user's passed favorite team name to an attribute of the instance.
        self.team = team

        #  from the user's favorite MLB team name, retrieve the team's ID (used by TheSportsDB.com api)
        #  from the record stored in the HockeyTeam model.
        team_db_record = get_object_or_404(BaseballTeam, team_name=team)
        team_id = team_db_record.team_id

        # Retrieving the url for the team's logo from TheSportsDB.com api
        # Create the url where data on the user's favorite team can be found
        team_data_url = 'https://www.thesportsdb.com/api/v1/json/1/lookupteam.php?id=' + team_id
        # Open the url and save its content
        json_team_data = urllib.request.urlopen(team_data_url).read()
        # Convert the data from JSON to a python dictionary
        team_data = json.loads(json_team_data)
        # Access and save the relevant dictionary value
        self.team_logo_url = team_data['teams'][0]['strTeamBadge']

        #  concatenate the team ID with the appropriate url prefix from TheSportsDB.com api to form
        #  the query for the user's favorite mlb team and read the data.
        events_url = 'https://www.thesportsdb.com/api/v1/json/1/eventsnext.php?id=' + team_id
        converted_json_data = json.loads(urllib.request.urlopen(events_url).read())
        
        self.events = []
        for index in range(0,5):
            event_str = converted_json_data['events'][index]['strEvent']
            event_date = converted_json_data['events'][index]['dateEvent']
            # Creating a dictionary for each event, rather than a string, will give us more flexibility in the template, since we'll be able to easily access each event's individual attributes
            event = {
              'name': event_str,
              'date': event_date
            }
            self.events.append(event)