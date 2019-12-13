import time

import API as api

devices= [api.Device("deviceadd1","devicename1"),api.Device("deviceadd2","devicename2","ble"),api.Device("deviceadd3","devicename3","ble")]
options=[api.Options("ble",["read","write","subscribe"])]
device =api.Device("deviceadd1","devicename1","ble")
device2 =api.Device("deviceadd3","devicename3","ble")
data=[
  {
    "_id": "5df3afadc291c78da1875bb8",
    "index": 0,
    "guid": "054ccd53-f650-48de-ad65-62438160b7c8",
    "isActive": False,
    "balance": "$2,557.49",
    "picture": "http://placehold.it/32x32",
    "age": 37,
    "eyeColor": "blue",
    "name": "Casey Carney",
    "gender": "male",
    "company": "BISBA",
    "email": "caseycarney@bisba.com",
    "phone": "+1 (871) 553-3851",
    "address": "773 Wolcott Street, Holtville, West Virginia, 8407",
    "about": "Magna incididunt dolor eiusmod sit aute elit laboris cupidatat sit adipisicing do. Consectetur nisi aute adipisicing velit quis nulla nulla excepteur. Lorem aliquip excepteur cupidatat excepteur enim sunt aute. Dolore aute do occaecat dolore nostrud ea. Dolore mollit pariatur Lorem mollit veniam.\r\n",
    "registered": "2017-10-04T08:33:45 -02:00",
    "latitude": -21.16461,
    "longitude": 12.781413,
    "tags": [
      "ex",
      "esse",
      "enim",
      "deserunt",
      "aute",
      "aliquip",
      "consequat"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Terry Nixon"
      },
      {
        "id": 1,
        "name": "Tanner Finley"
      },
      {
        "id": 2,
        "name": "Hester Joyner"
      }
    ],
    "greeting": "Hello, Casey Carney! You have 2 unread messages.",
    "favoriteFruit": "strawberry"
  },
  {
    "_id": "5df3afad1c250e97e6ce91d5",
    "index": 1,
    "guid": "dc7b05b2-88ef-4c89-b825-97031644144d",
    "isActive": False,
    "balance": "$2,427.33",
    "picture": "http://placehold.it/32x32",
    "age": 23,
    "eyeColor": "blue",
    "name": "Golden Francis",
    "gender": "male",
    "company": "ISOLOGIA",
    "email": "goldenfrancis@isologia.com",
    "phone": "+1 (906) 473-2324",
    "address": "428 Arlington Avenue, Lithium, District Of Columbia, 4673",
    "about": "Et nulla anim ex id non qui enim excepteur. Officia sunt cupidatat commodo tempor exercitation duis. Dolore in officia ex fugiat nisi esse elit quis irure esse. Qui sint ipsum et minim minim laborum quis exercitation amet reprehenderit. Eiusmod quis dolor pariatur deserunt sit incididunt cupidatat esse ut nisi occaecat. Aliqua quis est adipisicing consectetur aliqua consequat ex reprehenderit aliqua ea pariatur incididunt.\r\n",
    "registered": "2019-09-12T12:50:37 -02:00",
    "latitude": -40.388629,
    "longitude": -43.552459,
    "tags": [
      "laborum",
      "eiusmod",
      "id",
      "aliquip",
      "do",
      "eu",
      "dolore"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Alejandra Mclaughlin"
      },
      {
        "id": 1,
        "name": "Darla Mullins"
      },
      {
        "id": 2,
        "name": "Bridget Hopkins"
      }
    ],
    "greeting": "Hello, Golden Francis! You have 6 unread messages.",
    "favoriteFruit": "banana"
  },
  {
    "_id": "5df3afadcdffeea91e2fa092",
    "index": 2,
    "guid": "6a5130e9-4a75-4821-8dda-28ca28d3905a",
    "isActive": True,
    "balance": "$2,733.38",
    "picture": "http://placehold.it/32x32",
    "age": 35,
    "eyeColor": "green",
    "name": "Chandler Alvarez",
    "gender": "male",
    "company": "GINKOGENE",
    "email": "chandleralvarez@ginkogene.com",
    "phone": "+1 (899) 533-3469",
    "address": "901 Gold Street, Clara, Northern Mariana Islands, 5463",
    "about": "Et duis amet dolore esse dolor veniam consectetur eu. Aliqua irure cillum adipisicing anim consequat dolor sint ex cupidatat ut duis mollit. Dolore nostrud cillum anim quis laboris Lorem dolore culpa duis velit tempor in do mollit. Non occaecat fugiat anim laboris Lorem nulla cupidatat voluptate aute sint nisi.\r\n",
    "registered": "2014-07-12T08:16:29 -02:00",
    "latitude": 1.187794,
    "longitude": -79.323502,
    "tags": [
      "fugiat",
      "nulla",
      "consequat",
      "dolore",
      "tempor",
      "do",
      "aliquip"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Dionne Yang"
      },
      {
        "id": 1,
        "name": "Eliza Sutton"
      },
      {
        "id": 2,
        "name": "Wise Dennis"
      }
    ],
    "greeting": "Hello, Chandler Alvarez! You have 9 unread messages.",
    "favoriteFruit": "banana"
  },
  {
    "_id": "5df3afad15671ddd3e005732",
    "index": 3,
    "guid": "e8028c7e-c7f6-4476-aa1a-7047d1913c5e",
    "isActive": False,
    "balance": "$2,299.40",
    "picture": "http://placehold.it/32x32",
    "age": 32,
    "eyeColor": "green",
    "name": "Parks Mcgee",
    "gender": "male",
    "company": "QUAREX",
    "email": "parksmcgee@quarex.com",
    "phone": "+1 (862) 472-3703",
    "address": "408 Love Lane, Chilton, Arizona, 4075",
    "about": "Consectetur sit enim elit magna incididunt deserunt non. Ipsum occaecat adipisicing duis fugiat ad incididunt excepteur. Non do incididunt ipsum exercitation eu elit qui dolore. Irure do velit veniam aute culpa sint deserunt aliquip duis. Proident exercitation deserunt ea excepteur ut id. Minim veniam officia proident officia sunt occaecat ipsum duis.\r\n",
    "registered": "2019-06-22T08:01:24 -02:00",
    "latitude": -38.309177,
    "longitude": -169.782314,
    "tags": [
      "nulla",
      "enim",
      "ex",
      "est",
      "aliquip",
      "fugiat",
      "in"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Viola Shaw"
      },
      {
        "id": 1,
        "name": "Garcia Avila"
      },
      {
        "id": 2,
        "name": "Rosalind Madden"
      }
    ],
    "greeting": "Hello, Parks Mcgee! You have 1 unread messages.",
    "favoriteFruit": "apple"
  },
  {
    "_id": "5df3afad8a87f8b078689abf",
    "index": 4,
    "guid": "81fb1bdf-a685-4b58-a685-3d22d770308d",
    "isActive": True,
    "balance": "$3,032.43",
    "picture": "http://placehold.it/32x32",
    "age": 20,
    "eyeColor": "green",
    "name": "Cristina Perry",
    "gender": "female",
    "company": "ACUSAGE",
    "email": "cristinaperry@acusage.com",
    "phone": "+1 (928) 431-3783",
    "address": "924 Emerson Place, Glenville, New Mexico, 1624",
    "about": "Officia laboris nulla qui Lorem commodo eiusmod magna dolore. Commodo ad aliquip elit incididunt id in ex id qui enim duis cillum nostrud. Ullamco eiusmod ipsum consequat ad commodo consequat tempor fugiat sit eu laborum velit tempor dolor.\r\n",
    "registered": "2014-09-08T12:42:51 -02:00",
    "latitude": 56.885942,
    "longitude": 64.424945,
    "tags": [
      "nisi",
      "voluptate",
      "officia",
      "consectetur",
      "duis",
      "excepteur",
      "eu"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Wiley Dominguez"
      },
      {
        "id": 1,
        "name": "Anne Osborn"
      },
      {
        "id": 2,
        "name": "Gordon Clark"
      }
    ],
    "greeting": "Hello, Cristina Perry! You have 5 unread messages.",
    "favoriteFruit": "strawberry"
  },
  {
    "_id": "5df3afad3770436b1165fd95",
    "index": 5,
    "guid": "1426a500-63a8-480d-a9c7-8bb4ccde4b92",
    "isActive": False,
    "balance": "$2,238.57",
    "picture": "http://placehold.it/32x32",
    "age": 27,
    "eyeColor": "blue",
    "name": "Cobb Rogers",
    "gender": "male",
    "company": "IMANT",
    "email": "cobbrogers@imant.com",
    "phone": "+1 (975) 484-2889",
    "address": "812 Hudson Avenue, Cressey, New Jersey, 8402",
    "about": "Sint adipisicing deserunt nisi sit consequat in aliquip deserunt. Magna irure cupidatat consequat tempor culpa qui voluptate amet. Et duis excepteur ad non proident ut aliquip duis excepteur cupidatat.\r\n",
    "registered": "2019-03-09T04:59:53 -01:00",
    "latitude": 70.235226,
    "longitude": -27.504954,
    "tags": [
      "ea",
      "duis",
      "incididunt",
      "adipisicing",
      "occaecat",
      "ullamco",
      "in"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Ware Solomon"
      },
      {
        "id": 1,
        "name": "Larson Hayes"
      },
      {
        "id": 2,
        "name": "Dillard Woodard"
      }
    ],
    "greeting": "Hello, Cobb Rogers! You have 7 unread messages.",
    "favoriteFruit": "apple"
  },
  {
    "_id": "5df3afade67881ce2bc05f3a",
    "index": 6,
    "guid": "550ea956-9c4b-4d88-9b2f-81f67b7c5825",
    "isActive": True,
    "balance": "$1,762.47",
    "picture": "http://placehold.it/32x32",
    "age": 20,
    "eyeColor": "green",
    "name": "Erica Williamson",
    "gender": "female",
    "company": "ENTROPIX",
    "email": "ericawilliamson@entropix.com",
    "phone": "+1 (895) 565-3752",
    "address": "399 Nelson Street, Northridge, Hawaii, 9105",
    "about": "Et minim fugiat sint dolore. Sit velit ea eu minim cupidatat deserunt aliqua sunt deserunt. Duis pariatur duis dolor deserunt mollit excepteur laboris et Lorem aliquip culpa adipisicing do. Enim deserunt dolore pariatur sint cillum voluptate irure cupidatat dolore eu exercitation ullamco.\r\n",
    "registered": "2014-12-28T04:51:47 -01:00",
    "latitude": 66.551553,
    "longitude": -32.868754,
    "tags": [
      "cupidatat",
      "dolore",
      "commodo",
      "tempor",
      "occaecat",
      "elit",
      "est"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Loretta Noel"
      },
      {
        "id": 1,
        "name": "Pearlie Davis"
      },
      {
        "id": 2,
        "name": "Stout Stanley"
      }
    ],
    "greeting": "Hello, Erica Williamson! You have 5 unread messages.",
    "favoriteFruit": "apple"
  },
  {
    "_id": "5df3afae2a0ab9b923cd8c17",
    "index": 7,
    "guid": "c4112200-d7d3-4d17-92c6-8e0fa9451d82",
    "isActive": False,
    "balance": "$3,801.32",
    "picture": "http://placehold.it/32x32",
    "age": 30,
    "eyeColor": "brown",
    "name": "Bridges Pratt",
    "gender": "male",
    "company": "VIXO",
    "email": "bridgespratt@vixo.com",
    "phone": "+1 (992) 580-2976",
    "address": "918 Friel Place, Advance, Alabama, 4956",
    "about": "Officia sit cillum irure nulla officia quis ad et dolore laboris. Sit mollit ea quis veniam irure. Occaecat consectetur exercitation labore nisi Lorem. Occaecat officia nisi labore nulla Lorem veniam minim irure.\r\n",
    "registered": "2015-04-25T01:43:13 -02:00",
    "latitude": 64.773564,
    "longitude": 41.533361,
    "tags": [
      "Lorem",
      "duis",
      "culpa",
      "ex",
      "pariatur",
      "mollit",
      "veniam"
    ],
    "friends": [
      {
        "id": 0,
        "name": "Juliette Schmidt"
      },
      {
        "id": 1,
        "name": "Elvira Malone"
      },
      {
        "id": 2,
        "name": "Hopkins Gilliam"
      }
    ],
    "greeting": "Hello, Bridges Pratt! You have 2 unread messages.",
    "favoriteFruit": "banana"
  }
]

def on_option(option,data):
    print("REACHED BLE ON OPTION ",option," ",data)

def on_data(data):
    print ("REACHED BLE ON DATA ",data)

def on_option2(option,data):
    print("REACHED BLE ON OPTION2 ",option," ",data)

def on_data2(data):
    print ("REACHED BLE ON DATA2 ",data)


api.connectToBridge()
api.registerDevices(devices)
api.registerOptions(options)
api.bind(device=device,on_data=on_data,on_option=on_option)
api.bind(device=device2,on_data=on_data2,on_option=on_option2)
i=0
while True:
    time.sleep(5)
    api.sendDataFromDevice(device,data)
    #api.sendDataFromDevice(device2, data + 2*i)
    i+=15
    if i>2000:
        i=0
#while True:
#    data=msg.getData()
#    print()
