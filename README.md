# exp_reviews

EXP Reviews is a site for video game reviews akin to Rotten Tomatoes.

## Table of Contents

* [Tech Stack](#tech-stack)
* [Features](#features)
* [Setup/Installation](#installation)
* [To-Do](#future)
* [License](#license)

## <a name="tech-stack"></a>Tech Stack

__Frontend:__ HTML5, CSS, Jinja, Javascript, jQuery, Bootstrap <br/>
__Backend:__ Python, Flask, PostgreSQL, SQLAlchemy, Unirest <br/>
__APIs:__ IGDB, Apifier, Chart.js <br/>

## <a name="features"></a>Features

View popular games (both based on critic reviews and user reviews), recently reviewed, and upcoming games.

![Homepage Header](/static/img/_readme-img/homepage-header.png)
![Homepage Popular](/static/img/_readme-img/homepage-popular.png)
![Homepage Upcoming](/static/img/_readme-img/homepage-upcoming.png)
<br/><br/><br/>
Login and review a couple games to receive recommendations based on your scores and demographic info.
  
![Recommended Games](/static/img/_readme-img/homepage-reclist.png)
<br/><br/><br/>
Search for users, games, genres, platforms, franchises, and developers.
  
![Search No Toggle](/static/img/_readme-img/search-no-toggle.png)
![Search No Toggle](/static/img/_readme-img/search-toggle.png)
<br/><br/><br/>
Check out info about a game, the average player score, critic scores linked back to their site, and add or edit a review.
  
![Game Page Upper](/static/img/_readme-img/game-page-upper.png)
<br/><br/><br/>
Look at other reviews, screenshots, video, and a review breakdown on age and gender demographics.

![Game Page Reviews](/static/img/_readme-img/game-page-reviews.png)
![Game Page Screenshots](/static/img/_readme-img/game-page-screenshot.png)
![Game Page Videos](/static/img/_readme-img/game-page-video.png)
![Game Page Breakdown](/static/img/_readme-img/game-page-breakdown.png)
<br/><br/><br/>
Look at games the user is currently playing, take notes, and edit recommendation preferences.

![Profile Currently Playing](/static/img/_readme-img/user-current-list.png)
![Profile Rec Preferences](/static/img/_readme-img/user-toggle-prefs.png)

## <a name="installation"></a>Setup/Installation ⌨️

####Requirements:

- PostgreSQL
- Python 2.7
- IGDB API keys

To have this app running on your local computer, please follow the below steps:

Clone repository:
```
$ git clone https://github.com/subwavesignals/exp_reviews.git
```
Create a virtual environment:
```
$ virtualenv env
```
Activate the virtual environment:
```
$ source env/bin/activate
```
Install dependencies:
```
$ pip install -r requirements.txt
```
Get your own key for [IGDB](https://www.igdb.com/api) and create a secrets.sh that exports that key.
```
$ source secrets.sh
```
Create database 'games'.
```
$ createdb games
```
Create your database tables and add data using games.sql
```
$ python model.py
$ psql games < games.sql
```
If you'd prefer to pull your own data (fair warning this can take a while), edit seed.py to load the data you'd like and run.
```
$ python model.py
$ python seed.py
```
Run the app from the command line.
```
$ python server.py
```
If you want to use SQLAlchemy to query the database, run in interactive mode
```
$ python -i model.py
```

## <a name="future"></a>TODO✨
* Add ability for users to communicate
* Add community edited "Known Issues" section for each game
* Add connection with TwitchTV to show gameplay streams

## <a name="license"></a>License

The MIT License (MIT)
Copyright (c) 2017 Emily Need 

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
