from flask import Flask, render_template, send_file, request
import uuid
import sqlite3
from flask import jsonify
import qrcode
import io
from flask_cors import CORS, cross_origin
from PIL import Image
import base64
from io import BytesIO
DEFAULT_USER_NAME="admin"
DEFAULT_USER_PASSWORD="a"
USER_TABLE_NAME="userAuth"
TOKEN_TABLE_NAME="tokens"
DB_NAME="userInformation.db"

app = Flask(__name__)
CORS(app, support_credentials=True)

conn = sqlite3.connect(DB_NAME,check_same_thread=False)

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def selectAll(tableName:str):
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM %s" % str(tableName))
    rows = cur.fetchall()
    for row in rows:
        print("EACH ROW IN THE TABLE: ",tableName,row)
    cur.close()
    conn.commit()
    return

def updateIsValid(isValid,token):
    try:
        
        print("BEFORE IS_VALID UPDATION :",isValid,token)
        updateQuery='''UPDATE tokens SET IS_VALID = ?  WHERE TOKEN= ?'''
        conn.execute(updateQuery,(isValid,token))
        selectAll("tokens")
        conn.commit()
        return True
    except Exception as e:
        print("Update is isValid Vaild error code :",str(e))
        return False

def updateIsLogin(isLogin,userName,password):
    try:
        
        selectAll(USER_TABLE_NAME)
        print("BEFORE UPDATEISLOGIN")
        updateQuery="""UPDATE userAuth SET IS_LOGIN=? WHERE USERNAME=? AND PASSWORD=?"""
        conn.execute(updateQuery,(isLogin,userName,password))
        selectAll(USER_TABLE_NAME)
        conn.commit()
        return True
    except Exception as e:
        print("Update is isLogin Valid error code :",str(e))
        return False

def updateToken(userName,password,token):
    try:
        selectAll(USER_TABLE_NAME)
        print("BEFORE UPDATEISLOGIN")
        updateQuery="""UPDATE userAuth SET IS_LOGIN=? , TOKEN_ID=? WHERE USERNAME=? AND PASSWORD=?"""
        conn.execute(updateQuery,(1,token,userName,password))
        selectAll(USER_TABLE_NAME)
        conn.commit()
        return True
    except Exception as e:
        print("Update is isLogin Valid error code :",str(e))
        return False

def isUserValid(tableName:str,userName:str,password:str):
    try:
       
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM userAuth WHERE USERNAME=? AND PASSWORD=? AND IS_LOGIN=0 AND TOKEN_ID IS NULL", (userName,password))
        rows = cur.fetchall()
        count=0
        if rows is None or len(rows)<=0:
            return False
        for row in rows:
            print("is user login: ",row)
            if int(list(row)[0])==0:
                return False
            count+=1
            if count>=1:
                break
        
        if count >=1:
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False  

def isValidToken(tableName:str,token:str):
    try:
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM tokens WHERE TOKEN=? AND IS_VALID=?", (token,1))
        rows = cur.fetchall()
        count=0
        if rows is None or len(rows)<=0:
            return False
        for row in rows:
            print("isValidToken: ",row)
            print("==>",list(row)[2])
            if int(list(row)[2])==0:
                return False
        return True
    except Exception as e:
        return False
    

def insertToken(tableName:str, token:str):
    
    is_valid=1
    token_id=str(uuid.uuid4())
    print(tableName,token_id,token,is_valid)
    insertTokenQuery="""INSERT INTO tokens (ID,TOKEN,IS_VALID) VALUES (?,?,?);"""
    print(insertTokenQuery)
    conn.execute(insertTokenQuery,(token_id,token,is_valid))
    print("TOKEN INSERTED SUCCESSFULLY!!!")
    selectAll(tableName)

    return True

def createUserHelper(userInfo:dict):
    
    user_id=str(uuid.uuid4())
    userName=userInfo["username"]
    password=userInfo["password"]
    tableName="userAuth"
    # INSERT THE USER
    conn.execute("INSERT INTO userAuth (ID,USERNAME,PASSWORD,IS_LOGIN, TOKEN_ID) VALUES (?,?,?,?,?)",(user_id,userName,password,0,None))
    conn.commit()
    print("USER SUCCESSFULLY CREATED!!!")
    return True


			
def dropTable(tableName:str):
   
    query="DROP table IF EXISTS {};".format(tableName)
    conn.execute(query)
    print("DELETED THE TABLE SUCCESSFULLY!!! :",str(tableName))
    return True

def createTable(tableName:str):
    
    if tableName=="userAuth":
        dropTable(tableName)

        createQuery=""" CREATE TABLE IF NOT EXISTS {} (
            ID VARCHAR(255) NOT NULL,
            USERNAME VARCHAR(255) NOT NULL,
            PASSWORD CHAR(25) NOT NULL,
            IS_LOGIN INT NOT NULL,
            TOKEN_ID VARCHAR(255)
        ); """.format(tableName)
        conn.execute(createQuery)
        
        
       

    elif tableName=="tokens":
        dropTable(tableName)
        createQuery=""" CREATE TABLE IF NOT EXISTS {} (
            ID VARCHAR(255) NOT NULL,
            TOKEN VARCHAR(255) NOT NULL,
            IS_VALID INT NOT NULL
        ); """.format(tableName)
        conn.execute(createQuery)
    conn.commit()
    
    print("Table successfully created...")
    return

def getRandomToken():
    randomToken=str(uuid.uuid4())
    # insert it to the db
    tokenInjectionStatus=insertToken(tableName=TOKEN_TABLE_NAME, token=randomToken)
    print("GET RANDOM TOKEN==>",randomToken)
    return tokenInjectionStatus,randomToken


@app.route('/createUser',methods=["POST"])
def createUser():
    data = request.json
    userName=data["username"]
    password=data["password"]
    createUserHelper({"username":userName,"password":password})
    print("USER CREATED SUCCESSFULLY!!!")
    return jsonify(statusCode=200,msg="User Successfully created..."),200




@app.route('/login',methods=["POST", "GET"])
def login():
		if request.method=="GET":
			token=request.args.get('token')
			currentServerIp=get_ip()
			return render_template('login-page.html', token=token, ip=currentServerIp)
		else:
			selectAll(USER_TABLE_NAME)
			data = request.json
			userName=data["username"]
			password=data["password"]
			token=data["token"]
			
			#check the database for token if it's exist and not already used we can use it
			if not isValidToken(TOKEN_TABLE_NAME,token):
					print("isValidToken block")
					return jsonify(statusCode=400,msg="NOT A VALID TOKEN / TOKEN EXPIRED..."),400
			else:
					print("Else Block")
					if not updateIsValid(0,token):
							print("FAILED TO UPDATE THE TOKEN VALIDITY IN TABLE...")
							return jsonify(statusCode=400,msg="FAILED TO UPDATE THE TOKEN VALIDITY IN TABLE..."),400

					selectAll(USER_TABLE_NAME)
					isUserValidStatus=isUserValid(USER_TABLE_NAME,userName,password)

					if not isUserValidStatus:
							print(selectAll(USER_TABLE_NAME))
							print("USER/PASSWORD IS WRONG!!! / ALREADY LOGGED USER...")
							# re-set the token
							#updateIsValid(1,token)
							return jsonify(statusCode=400,msg="USER/PASSWORD IS WRONG!!! / ALREADY LOGGED USER..."),400
					else:
							if not updateIsLogin(1,userName,password):
									print("FAILED TO UPDATE THE LOGIN STATUS")
									return jsonify(statusCode=400,msg="FAILED TO UDPATE THE IS_LOGIN STATUS!!!"),400

					updateToken(userName,password,token)
					return jsonify(statusCode=200,msg="success"),200

		
			return jsonify(statusCode=200,msg="success"),200


@app.route('/getQR',methods=["get"])
def getQR():
    tokenStatus,token=getRandomToken()
    if not tokenStatus and token is not None:
        #failed
        return jsonify({"status_code":400,"msg":"TOKEN CREATION FAILED"}),400
    
    # embeded the url & randomeToken
    print("get Ip :")
    currentServerIp=get_ip()
    input_data = "http://"+str(currentServerIp)+":5000/login?token="+token
    print("INPUT URL>",input_data)
    #Creating an instance of qrcode
    qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    print("Image we got :",img)
   

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = str(base64.b64encode(buffered.getvalue()))
    print("img str :",img_str)
    return jsonify(image=img_str,token=token)
    

     # create file-object in memory
    # file_object = io.BytesIO()

    # # write PNG in file-object
    # img.save(file_object, 'PNG')

    # # move to beginning of file so `send_file()` it will read from start    
    # file_object.seek(0)

    # return send_file(file_object, mimetype='image/PNG')

def queryStatus(token):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM userAuth WHERE IS_LOGIN=1 AND TOKEN_ID=?", (token,))
        rows = cur.fetchall()
        print("the query status :",rows)
        if rows is None or len(rows)<=0:
            return False
        for row in rows:
            print("Query Rows: ",row)
            print("==>",list(row)[0])
            if int(list(row)[0])==0:
                return False
        return True
    except Exception as e:
        print("query Status :",str(e))
        return False
# > endpoint
@app.route('/pollLoginStatus',methods=["get"])
def pollLoginStatus():
    try:
        token=request.args.get('token')
        print('Token we got :',token)
        status= queryStatus(token)
        if status==False:
            raise ValueError("failed")
        return jsonify(statusCode=200,status=status),200
    except Exception as e:
        return jsonify(statusCode=400,status="failed"),400


if __name__ == '__main__':
    createTable("userAuth")
    createTable("tokens")
    createUserHelper(userInfo={"username":DEFAULT_USER_NAME,"password":DEFAULT_USER_PASSWORD})
    app.run(debug=True, host='0.0.0.0', port=5000)
