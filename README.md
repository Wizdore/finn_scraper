# Finn Scraper
This application scrapes, stores and notifies the user through Discord bot of scraping process. I wrote it to collect data for a data analysis task as finn doesnt show more than 50 pages of house at a time so it collects new house data everyday. I have done some preliminary data exploration in the jupyter notebook but there wasnt enough data make prediction models so I wrote a script that can collect new data every day.

#### What it does
* Mines house on sale data from finn
* Stores the data in a database in `datastore/` directory
* Notifies the user over discord on how many houses has been scraped

The project also includes a bash script `cronjob.sh` that can be used to periodically run the application using crontab on linux. 
Im using `pipenv` for package and environment management, `TinyDB` for database and Discord's webhook to send message to discord server. The webhook needs to be saved in a `.env` file in the project directory as an environment variable named `DISCORD_WEBHOOK`, pipenv will load the environment variable.
