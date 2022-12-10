Installation :

1. Python 3.8.10
2. pip install -r requirements.txt
3. python main.py
4. http://localhost:5000/getQR
5. http://localhost:5000/login?token=aefa102d-6da9-48ea-b978-409f1a00fb5d
6. http://localhost:5000/pollLoginStatus
7. /frontend/index.html

STEPS:

1. Start the api server (python main.py)
2. It will create the default user & password (admin,a)
3. Open the UI in the browser (Inside /frontend/index.html)
4. scan the QR using mobile (it should also be connected to the same wifi of the computer)
5. Type the username & passowrd (admin,a)
6. On success login, the browser will allow you into the application

NOTE :
1. Pls run the main.py file locally in your system 
    1.1 It will use your local wifi ip for api call's
    1.2 If the user logged one time, we need to re-start the server again (python main.py)
    1.3 If the token is used more than one time, it will be in-valid/expired token, so we need to get the new-token again (/getQR)
    1.4 All the data are in-memory, so on restart it will clear all the data
    1.5 We can create the new user , using createUser endpoint.
    
