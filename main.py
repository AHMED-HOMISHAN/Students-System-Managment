from errno import EROFS
import face_recognition
import cv2
import numpy as np
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
import mysql.connector as mc
import datetime as dt


path = 'photos'
images=[]
classNames = []
personsList = os.listdir(path)
temp_user = ''
 

for cl in personsList:
    curPersonn = cv2.imread(f'{path}/{cl}')
    images.append(curPersonn)
    classNames.append(os.path.splitext(cl)[0])
    for i in classNames:
        mydb2 = mc.connect(
                    host = "localhost",
                    user = "root",
                    password = "",
                    database = "faceid"
                )
        mycursor2 = mydb2.cursor()
        if(str(i[0:2]) == "T."):
            query = "INSERT INTO `users`( `name`,`Date`, `role`) VALUES ('"+str(os.path.splitext(cl)[0])+"','"+str(dt.datetime.now())+"','"+str(1)+"') on duplicate key update name = '"+str(os.path.splitext(cl)[0])+"' "
        else:
            query = "INSERT INTO `users`( `name`,`Date`, `role`) VALUES ('"+str(os.path.splitext(cl)[0])+"','"+str(dt.datetime.now())+"','"+str(0)+"') on duplicate key update name = '"+str(os.path.splitext(cl)[0])+"' "
        mycursor2.execute(query)
        mydb2.commit()

def findEncodings(image):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)

class Login(QDialog):
    
    def __init__(self, QWidget=None):
        super(Login,self).__init__()
        loadUi("login.ui",self)
        self.btnFaceID.clicked.connect(self.Known)
        self.btnLogin.clicked.connect(self.loginfunction)
        
    
    def Known(self):
        cap = cv2.VideoCapture(0)

        cap.set(3, 740)
        cap.set(4, 580)
                
        while True:
            _,img = cap.read()

            imgS = cv2.resize(img, (0,0) , None , 0.25 , 0.25)

            faceCurrentFrame = face_recognition.face_locations(imgS)
            encodeCurrentFrame = face_recognition.face_encodings(imgS,faceCurrentFrame)

            for encodeface,faceLoc in zip(encodeCurrentFrame,faceCurrentFrame):
                matches = face_recognition.compare_faces(encodeListKnown,encodeface)
                faceDis = face_recognition.face_distance(encodeListKnown,encodeface)

                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    try : 
                        username = name
                        mydb = mc.connect(
                            host = "localhost",
                            user = "root",
                            password = "",
                            database = "faceid"
                            )
                        mycursor = mydb.cursor()
                        query = "SELECT * FROM users WHERE  name='"+username+"' "
                        mycursor.execute(query)
                        result = mycursor.fetchone()
                        if result[1]== "T.Waleed":
                            main = Main(username)
                            widget.addWidget(main)
                            widget.setCurrentIndex(widget.currentIndex() + 1)
                        else:
                            query4 = "Update users set Date='"+str(dt.datetime.now())+"' Where name='"+username+"' "
                            mycursor.execute(query4)
                            main = ERROR(f"Thanks {username}")
                            widget.addWidget(main)
                            widget.setCurrentIndex(widget.currentIndex() + 1)
                        return
                    except mc.Error as e:
                        print ("Error Accure" ,mc.Error)
                else :
                    widget.addWidget(ERROR("Sorry, I could not recognize you"))
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                    return

            cv2.waitKey(1)

    def loginfunction(self):
        try : 
            username = self.txtUserName.text()
            mydb = mc.connect(
                host = "localhost",
                user = "root",
                password = "",
                database = "faceid"
                )
            mycursor = mydb.cursor()
            query = "SELECT * FROM users WHERE  name='"+username+"'"
            mycursor.execute(query)
            result = mycursor.fetchone()
            if result[1][0:2]== "T.":
                main = Main(username)
            else:
                query4 = "Update users set Date='"+str(dt.datetime.now())+"' Where name='"+username+"' "
                mycursor.execute(query4)
                main = ERROR(f"Thanks {username}")
            widget.addWidget(main)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        except mc.Error as e:
            print(e)

class Main(QDialog):
    def __init__(self  , username=None):
        super(Main,self).__init__()
        loadUi("main.ui",self)
        self.txtWelcomUser.setText(username)
        self.table_std
        self.selected_std(username)

    def selected_std(self, username=None):
        try:
            mydb_table = mc.connect(
                host = "localhost",
                user = "root",
                password = "",
                database = "faceid"
                )
            mycursor_table = mydb_table.cursor()
            query_table = "SELECT * FROM users Where name != '"+username+"'"
            mycursor_table.execute(query_table)
            results = mycursor_table.fetchall()
            table_row = 0
            self.table_std.setRowCount(len(results))
            for row in results:
                self.table_std.setItem(table_row,0,QTableWidgetItem(str(row[1])))
                self.table_std.setItem(table_row,1,QTableWidgetItem(str(row[2])))
                table_row+=1
        except mc.Error as e:
            print(e)


class ERROR(QDialog):
    def __init__(self , Msg=None):
        super(ERROR,self).__init__()
        loadUi("ERROR.ui",self)
        self.btnGoBack.clicked.connect(self.GoBACK)
        self.label.setText(Msg)
    def GoBACK(self):
        widget.addWidget(Login())
        widget.setCurrentIndex(widget.currentIndex() + 1)
      

app = QApplication(sys.argv)
mainwindow=Login()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(700)
widget.setFixedHeight(800)
widget.show()
app.exec_()