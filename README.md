# Filimo Data Analyser
### a djagno+scrapy project to collect data of  20,000 movies and tv-shows and over 1.2 million comments from filimo.com website. 
## Installation
after cloning, create an virtualenv and activate it by :
` pip3 install virtualenv`
and 

` virtualenv venv`
note that python 3.8 is required.

`source venv/bin/activate`

install the requirements by:

`pip3 install -r requirements.txt`

after changing setting run the django service. since genres are limited number you can just use `./manage.py genres.json` to save all 14 genres into db.
for starting the crawl process `cd` to `scrapy_app` and simply run 
`scrapy crawl fimilo_links`.
by now you should see logs for movies and comments. based on your device and internet speed it might take two hours more or less to collent ten thousand movie data.
in case of getting data for new movies uploaded in filimo, run the scrapy again and spider avoid saving duplicate data using unique code for each movie.
for front end I'm using bootstrap and some custom css. In case optimizing the search process you can use elasticcsearch. just install it and then run 
`./manage.py search_index --rebuild` to store all the data in you elastic db. note that search bar uses elastic engine at the moment. if you tend to use postgre as 
the search engine just comment the elastic query in search view and uncomment the query writen for postgre.

A brief summary of project description and documentation is in file `filimo_report.pdf` check it  for more techninal details.
Any technical recommendation will be appricated kindly.

special thanks to Dr.AmirKhani.

