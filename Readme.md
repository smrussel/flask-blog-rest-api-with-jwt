## Blog Rest API by flask with JWT authentication 

Flask, FLask-Restful, and Flask SQLAlchemy were used to create a blog API with CRUD operations. The title, author, content, and database generated id of each blog post are stored in a database. A unique title is required. When a user posts a blog, a url for the blog is returned to the user for future access, so the user does not need to know the id.

The blog pages are password-protected, and users must first register before viewing any of them. In accordance with REST standards, the register and login processes employ JWT tokens rather than cookie sessions.

The explanations and test methods for operations are listed below.

### Install
virtualenv -p python3 venv\
source venv/bin/activate\
pip install -r requirements.txt

### Start server
You can start server with :

`python run.py`

### User registration
The blog pages are protected, before view any page, user needs register, here use curl command for example to test:

`curl -i -H "Content-Type: application/json" -X POST -d '{"username":"test", "password":"test"}' http://localhost:5000/registration`

### User login
Use registered user and password to login:

`curl -i -H "Content-Type: application/json" -X POST -d '{"username":"test", "password":"test"}' http://localhost:5000/login`

The API will return an access token and a refresh token.

### View all blogs
Use returned access token to view blog page:

`curl -i -H "Authorization:Bearer <your access token>"  http://localhost:5000/blogapi/blogs`

### Refresh Token
The access token will expire after 15 minutes, when that happens, refresh the user with refresh token.

`curl -i -H "Authorization:Bearer <your refresh token>" -X POST http://localhost:5000/token/refresh`

### View specific blogs
`curl -i -H "Authorization:Bearer <your access token>"  http://localhost:5000/blogapi/blogs/3`

### Post new blog
`curl -i -H "Authorization:Bearer <your access token>" -H "Content-Type: application/json" -X POST -d '{"title":"How to"}' http://localhost:5000/blogapi/blogs`

### Update a blog
`curl -i -H "Authorization:Bearer <your access token>" -H "Content-Type: application/json" -X PUT -d '{"title":"head","content":"content"}' http://localhost:5000/blogapi/blogs/5`

### Delete a blog
`curl -i -H "Authorization:Bearer <your access token>" -X DELETE  http://localhost:5000/blogapi/v1.0/blogs/5`

### User logout
When user logout, the access token will be added to a blacklist. 

Test logout using access token:

`curl -i -H "Authorization:Bearer <your access token>" -X POST http://localhost:5000/logout/access`

Test logout using refresh token:

`curl -i -H "Authorization:Bearer <your access token>" -X POST http://localhost:5000/logout/refresh`



