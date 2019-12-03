import peewee as pw

import mysql.connector

myDB=None
mycursor=None

def connectToDatabase(host,user,password):
    global myDB
    global mycursor
    try:
        myDB = mysql.connector.connect(host=host, user=user,passwd=password,database="IoTPlatform")
        mycursor=myDB.cursor()
    except Exception as e:
        print (e)

def select(table,rows="*",condition=""):
    mycursor.execute("SELECT "+rows+" FROM "+table+" WHERE "+condition)
    myresult =mycursor.fetchall()
    return myresult

def insert(table,valueNames,values):
    mycursor.execute("INSERT INTO " + table + valueNames + " VALUES " + values)
    myDB.commit()
    #myresult = mycursor.fetchall()

def update(table,query):
    mycursor.execute("UPDATE "+ table + " SET "+ query)
    myDB.commit()
    #myresult = mycursor.fetchall()

def delete(table,condition):
    mycursor.execute("DELETE FROM "+table+" WHERE "+condition)
    myDB.commit()

def clearTables():
    mycursor.execute("DELETE FROM Devices")
    myDB.commit()
    mycursor.execute("DELETE FROM Bridges")
    myDB.commit()



def createDatabaseAndTables(host,user,password):
    myDB = mysql.connector.connect(host=host, user=user, passwd=password)
    mycursor = myDB.cursor()
    mycursor.execute("SHOW DATABASES")
    if ('IoTPlatform',) in mycursor:
        databaseExists=True
    else:
        databaseExists=False
    if databaseExists:
        myDB = mysql.connector.connect(host=host, user=user, passwd=password,database="IoTPlatform")
        mycursor = myDB.cursor()
        mycursor.execute("SHOW TABLES")
        tables= mycursor.fetchall()
        if ("Bridges",) not in tables:
            mycursor.execute("CREATE TABLE `Bridges` (`BridgeID` int(11) NOT NULL,`UserID` int(11) NOT NULL, `Address` varchar(255) NOT NULL, `Name` varchar(255) NOT NULL) ")
        if ("Options",) not in tables:
            mycursor.execute("CREATE TABLE `Options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        if ("Devices",) not in tables:
            mycursor.execute("CREATE TABLE `Devices` ( `DeviceID` int(11) NOT NULL,`Address` varchar(255) NOT NULL,`Name` varchar(255) DEFAULT NULL,`Type` varchar(255) DEFAULT NULL,`BridgeID` int(11) NOT NULL)")
        if ("Users",) not in tables:
            mycursor.execute("CREATE TABLE `Users` (`UserID` int(11) NOT NULL,`Login` varchar(15) NOT NULL,`Password` varchar(30) NOT NULL)")


        if ("Bridges",) not in tables:
            mycursor.execute("ALTER TABLE `Bridges` ADD PRIMARY KEY (`BridgeID`), ADD KEY `UserID` (`UserID`)")
            mycursor.execute("ALTER TABLE `Bridges` MODIFY `BridgeID` int(11) NOT NULL AUTO_INCREMENT")
            mycursor.execute("ALTER TABLE `Bridges` ADD CONSTRAINT `Bridges_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`)")
        if ("Options",) not in tables:
            mycursor.execute(
                "CREATE TABLE `Options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        if ("Devices",) not in tables:
            mycursor.execute("ALTER TABLE `Devices` ADD PRIMARY KEY (`DeviceID`), ADD KEY `BridgeID` (`BridgeID`)")
            mycursor.execute("ALTER TABLE `Devices` MODIFY `DeviceID` int(11) NOT NULL AUTO_INCREMENT")
            mycursor.execute("ALTER TABLE `Devices` ADD CONSTRAINT `Devices_ibfk_1` FOREIGN KEY (`BridgeID`) REFERENCES `Bridges` (`BridgeID`)")
        if ("Users",) not in tables:
            mycursor.execute("ALTER TABLE `Users` ADD PRIMARY KEY (`UserID`), ADD UNIQUE KEY `Login` (`Login`)")
            mycursor.execute( "ALTER TABLE `Users` MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT")



    else:
        mycursor.execute("CREATE DATABASE IoTPlatform")
        myDB = mysql.connector.connect(host=host, user=user, passwd=password, database="IoTPlatform")
        mycursor = myDB.cursor()
        mycursor.execute("CREATE TABLE `Bridges` (`BridgeID` int(11) NOT NULL,`UserID` int(11) NOT NULL, `Address` varchar(255) NOT NULL, `Name` varchar(255) NOT NULL) ")
        mycursor.execute("CREATE TABLE `Devices` ( `DeviceID` int(11) NOT NULL,`Address` varchar(255) NOT NULL,`Name` varchar(255) DEFAULT NULL,`Type` varchar(255) DEFAULT NULL,`BridgeID` int(11) NOT NULL)")
        mycursor.execute("CREATE TABLE `Options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        mycursor.execute("CREATE TABLE `Users` (`UserID` int(11) NOT NULL,`Login` varchar(15) NOT NULL,`Password` varchar(30) NOT NULL)")
        mycursor.execute("ALTER TABLE `Bridges` ADD PRIMARY KEY (`BridgeID`), ADD KEY `UserID` (`UserID`)")
        mycursor.execute("ALTER TABLE `Bridges` MODIFY `BridgeID` int(11) NOT NULL AUTO_INCREMENT")
        mycursor.execute("ALTER TABLE `Bridges` ADD CONSTRAINT `Bridges_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `Users` (`UserID`)")
        mycursor.execute("CREATE TABLE `Options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        mycursor.execute("ALTER TABLE `Devices` ADD PRIMARY KEY (`DeviceID`), ADD KEY `BridgeID` (`BridgeID`)")
        mycursor.execute("ALTER TABLE `Devices` MODIFY `DeviceID` int(11) NOT NULL AUTO_INCREMENT")
        mycursor.execute("ALTER TABLE `Devices` ADD CONSTRAINT `Devices_ibfk_1` FOREIGN KEY (`BridgeID`) REFERENCES `Bridges` (`BridgeID`)")
        mycursor.execute("ALTER TABLE `Users` ADD PRIMARY KEY (`UserID`), ADD UNIQUE KEY `Login` (`Login`)")
        mycursor.execute( "ALTER TABLE `Users` MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT")


if __name__ == '__main__':
    #mycursor.execute('INSERT INTO Bridges (UserID,Address,Name) VALUES (1,"eloadres","elonazwa")')
    print("done")



#myDB = pw.MySQLDatabase("IoTPlatform", host="192.168.1.12", port=3306, user="root", passwd="password")
# class MySQLModel(pw.Model):
#     """A base model that will use our MySQL database"""
#     class Meta:
#         database = myDB
#
# class Users(MySQLModel):
#     UserID = pw.IntegerField(primary_key=True)
#     Login = pw.UUIDField()
#     Password = pw.UUIDField()
#     class Meta:
#         db_table='Users'
#
# class Bridges(MySQLModel):
#     BridgeID = pw.IntegerField(primary_key=True)
#     UserID = pw.IntegerField()
#     Address = pw.UUIDField()
#     Name = pw.UUIDField()
#     class Meta:
#         db_table='Bridges'
#
# class Devices(MySQLModel):
#     DeviceID = pw.IntegerField(primary_key=True)
#     Address = pw.UUIDField()
#     Name = pw.UUIDField()
#     Type = pw.UUIDField()
#     BridgeID = pw.IntegerField()
#     class Meta:
#         db_table='Devices'

# when you're ready to start querying, remember to connect
#myDB.connect()
#try:
#    usersInfo=Users.get(Users.UserID==1)
#    print(usersInfo)
#except Exception as e:
#    print(e)
#print ("elo")
