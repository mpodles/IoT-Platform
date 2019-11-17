import peewee as pw

import mysql.connector


try:
    myDB = mysql.connector.connect(host="192.168.1.12", user="root ",passwd="password",database="IoTPlatform")
    mycursor=myDB.cursor()
except Exception as e:
    print (e)

def select(table,rows="*",condition=""):
    mycursor.execute("SELECT "+rows+" FROM "+table+" "+condition)
    myresult =mycursor.fetchall()
    return myresult

if __name__ == '__main__':
        result=select(table="Users",condition="WHERE Login='abc' AND Password='abc'")
        print(result[0][0])



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
