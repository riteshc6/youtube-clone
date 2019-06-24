# Design Document

#### User Story
1) As a Viewer <br>
    I want to be able to <br>
    * Register and login
    * see a list of all vodeos on Youtube when I login
    * view a video from the list
    * I should be able to view a user's profile
2) As Creator <br>
    I want to be able to<br>
    * register and login
    * upload a video on youtube with headline and description of video
    * delete a video uploaded by me
Note : Both User and creator have same permissions to view and upload videos<br>


#### MVP
1) User Registration/ Login
2) Video Upload feature
3) Watch video feature for users
4) Delete video feature

#### URL Design
    * `/` or `/index` : Home Page(Displays list of videos)
    * `/login` : Login page(Displayed when user is not looged in)
    * `/register` : Resgistration Page
    * `/watch/<video_id>` : Video Player Page
    * `\profile` : User Profile
    * '\profile\profile_id' : Other User profiles with videos uploaded by them


#### Forms
    * Video Upload form : {
            "title" : "Title to be provided by the creator"
            "description" : "Description of video in 140 words"
        }
        After upload redirect to cerator's profile page
    *  Register Form : {
            "Username" : "",
            "E-mail" : "",
            "password" : "",
            "confirm password" : ""
        }
    * Login Form : {
            "Username" : "",
            "Password" : ""
        }    

####    Authentication
    * Any registered user can watch all videos 
    * Any registered user can upload videos

#### Database Schema Design
    * User : { "user_id" : primary key, integer, autoincrement;
                "Username" : String;
                "email_id": string;
                "password": string;
                "videos" : db.relationship('Video', backref='user', lazy='dynamic')
        }
    * Video : { "video_id" : primary key, integer, autoincrement;
                 "title" : String;
                 "video_description" : String;
                 "video_path": <directory/video_id>;
                 "user_id" = integer, ForeignKey(user.id)
        }    





