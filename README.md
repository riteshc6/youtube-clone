# YOUTUBE CLONE

In this project following features have been implemented<br>
> `User authentication` : Register, Login, Logout<br>
> `Upload Video` : Any user logged in can upload videos which can be viewed by others<br>
> `Like video` : User logged in can like other users' videos<br>
> `Search Video` : Users can search videos by the title of video. Under the hood elastic search engine is <br> being used for fast search <br>
> `Profile`: Users can see profile of other users on the network and videos uploaded by them<br>
> `Download` : Users can download all the content uploaded by them  as a json file. Under the hood<br>
celery is being used as Task Queue to ofload dowload content work from application to a worker.<br>

## GETTING STARTED

#### Prequisites
1. Install elasticsearch locally or get a cloud deployment of [elastic search](https://www.elastic.co/)
2. Install [redis](https://redis.io/download)
3. Install Postgres and setup your database

#### Quick Setup

1. Clone repository
2. Create vitualenv and install requirements
3. Open a second terminal and start a local redis server
4. Open a third terminal and set environment variable DATABASE_URL to your database url, this
will be used by the worker to access database. 
5. Run the flask app in first terminal



