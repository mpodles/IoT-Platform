
import mysql.connector

myDB =None
mycursor =None

def connectToDatabase(host ,user ,password):
    global myDB
    global mycursor
    try:
        myDB = mysql.connector.connect(host=host, user=user ,passwd=password ,database="iotplatform")
        mycursor =myDB.cursor()
    except Exception as e:
        print (e)

def select(table ,rows="*" ,condition=""):
    mycursor.execute("SELECT  " +rows +" FROM  " +table +" WHERE  " +condition)
    myresult =mycursor.fetchall()
    return myresult


def insert(table, valueNames, values):
    mycursor.execute("INSERT INTO " + table + valueNames + " VALUES " + values)
    myDB.commit()
    # myresult = mycursor.fetchall()


def update(table, query):
    mycursor.execute("UPDATE " + table + " SET " + query)
    myDB.commit()
    # myresult = mycursor.fetchall()


def delete(table, condition):
    mycursor.execute("DELETE FROM " + table + " WHERE " + condition)
    myDB.commit()


def clearTables():
    mycursor.execute("DELETE FROM devices")
    myDB.commit()
    mycursor.execute("DELETE FROM bridges")
    myDB.commit()


def createDatabaseAndTables(host, user, password):
    myDB = mysql.connector.connect(host=host, user=user, passwd=password)
    mycursor = myDB.cursor()
    mycursor.execute("SHOW DATABASES")
    result = mycursor.fetchall()
    if  ('iotplatform',) in result:
        databaseExists = True
    else:
        databaseExists = False
    if databaseExists:
        myDB = mysql.connector.connect(host=host, user=user, passwd=password, database="iotplatform")
        mycursor = myDB.cursor()
        mycursor.execute("SHOW TABLES")
        tables = mycursor.fetchall()
        print(tables)
        if ("bridges",) not in tables:
            mycursor.execute(
                "CREATE TABLE `bridges` (`BridgeID` int(11) NOT NULL,`UserID` int(11) NOT NULL, `Address` varchar(255) NOT NULL, `Name` varchar(255) NOT NULL) ")
        if ("options",) not in tables:
            mycursor.execute(
                "CREATE TABLE `options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        if ("devices",) not in tables:
            mycursor.execute(
                "CREATE TABLE `devices` ( `DeviceID` int(11) NOT NULL,`Address` varchar(255) NOT NULL,`Name` varchar(255) DEFAULT NULL,`Type` varchar(255) DEFAULT NULL,`BridgeID` int(11) NOT NULL)")
        if ("users",) not in tables:
            mycursor.execute(
                "CREATE TABLE `users` (`UserID` int(11) NOT NULL,`Login` varchar(15) NOT NULL,`Password` varchar(30) NOT NULL)")


        try:
            mycursor.execute("ALTER TABLE `bridges` ADD PRIMARY KEY (`BridgeID`), ADD KEY `UserID` (`UserID`)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `bridges` MODIFY `BridgeID` int(11) NOT NULL AUTO_INCREMENT")
        except Exception as e:
            print(e)
        # mycursor.execute("ALTER TABLE `bridges` ADD CONSTRAINT `Bridges_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`)")
        try:
            mycursor.execute("ALTER TABLE `devices` ADD PRIMARY KEY (`DeviceID`), ADD KEY `BridgeID` (`BridgeID`)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `devices` MODIFY `DeviceID` int(11) NOT NULL AUTO_INCREMENT")
        except Exception as e:
            print(e)
        # mycursor.execute("ALTER TABLE `devices` ADD CONSTRAINT `Devices_ibfk_1` FOREIGN KEY (`BridgeID`) REFERENCES `bridges` (`BridgeID`)")
        try:
            mycursor.execute("ALTER TABLE `users` ADD PRIMARY KEY (`UserID`), ADD UNIQUE KEY `Login` (`Login`)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `users` MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT")
        except Exception as e:
            print(e)



    else:
        try:
            mycursor.execute("CREATE DATABASE iotplatform")
        except Exception as e:
            print(e)
        try:
            myDB = mysql.connector.connect(host=host, user=user, passwd=password, database="iotplatform")
        except Exception as e:
            print(e)
        try:
            mycursor = myDB.cursor()
        except Exception as e:
            print(e)
        try:
            mycursor.execute("CREATE TABLE `bridges` (`BridgeID` int(11) NOT NULL,`UserID` int(11) NOT NULL, `Address` varchar(255) NOT NULL, `Name` varchar(255) NOT NULL) ")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("CREATE TABLE `devices` ( `DeviceID` int(11) NOT NULL,`Address` varchar(255) NOT NULL,`Name` varchar(255) DEFAULT NULL,`Type` varchar(255) DEFAULT NULL,`BridgeID` int(11) NOT NULL)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("CREATE TABLE `options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("CREATE TABLE `users` (`UserID` int(11) NOT NULL,`Login` varchar(15) NOT NULL,`Password` varchar(30) NOT NULL)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `bridges` ADD PRIMARY KEY (`BridgeID`), ADD KEY `UserID` (`UserID`)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `bridges` MODIFY `BridgeID` int(11) NOT NULL AUTO_INCREMENT")
        except Exception as e:
            print(e)
        
        #mycursor.execute("ALTER TABLE `bridges` ADD CONSTRAINT `Bridges_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`)")
        try:
            mycursor.execute("CREATE TABLE `options` (`Type` varchar(255) NOT NULL, `DeviceOption` varchar(255) NOT NULL)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `devices` ADD PRIMARY KEY (`DeviceID`), ADD KEY `BridgeID` (`BridgeID`)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `devices` MODIFY `DeviceID` int(11) NOT NULL AUTO_INCREMENT")
        except Exception as e:
            print(e)
        #mycursor.execute("ALTER TABLE `devices` ADD CONSTRAINT `Devices_ibfk_1` FOREIGN KEY (`BridgeID`) REFERENCES `bridges` (`BridgeID`)")
        try:
            mycursor.execute("ALTER TABLE `users` ADD PRIMARY KEY (`UserID`), ADD UNIQUE KEY `Login` (`Login`)")
        except Exception as e:
            print(e)
        try:
            mycursor.execute("ALTER TABLE `users` MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # mycursor.execute('INSERT INTO bridges (UserID,Address,Name) VALUES (1,"eloadres","elonazwa")')
    print("done")


