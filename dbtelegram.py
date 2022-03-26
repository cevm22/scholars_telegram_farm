from pymongo import MongoClient
from colorama import Fore, Style
import io
import datetime
import time
#======================================================================
#parametros de base de datos
#======================================================================
MONGO_URI='mongodb://localhost' #en donde se encuentra la base datos
client = MongoClient(MONGO_URI) #inicializacion de la base datos

#==========================================================================
#==========================================================================
#==========================================================================
def tel_update1(vector):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    timestamp=(int(time.time()))
    collection.replace_one({"chatID":vector[0]},
    {
        "chatID": vector[0],
        "input_slp": vector[1],
        "timestamp":timestamp       
        
    },upsert=True) # Comando crea uno nuevo en dado caso de que no exista el documento
    tel_dailyconfirm([vector[0],False])
    return True

def tel_update2(vector):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    timestamp=(int(time.time()))
    collection.update_one({"chatID":vector[0]},
    {
        "$set":{"confirm_slp": vector[1],"timestamp":timestamp }
    })

    return True

def tel_update3(vector):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection    
    collection.update_one({"chatID":vector[0]},
    {
        "$set":{"input_mmr": vector[1]}
    })
    return True

def tel_update4(vector):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection    
    collection.update_one({"chatID":vector[0]},
    {
        "$set":{"confirm_mmr": vector[1]}
    })
    return True

def tel_validation1 (chatID):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    lastinput=collection.find({"chatID":chatID}, #buscar el documento con valor ronin
    {"input_slp":1} # solo devuelve el valor
    )    
    return (lastinput[0]['input_slp'])

def tel_validation2 (chatID):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    lastconfirm=collection.find({"chatID":chatID}, #buscar el documento con valor ronin
    {"confirm_slp":1} # solo devuelve el valor
    )

    return (lastconfirm[0]['confirm_slp'])

def tel_validation3 (chatID):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    lastinput=collection.find({"chatID":chatID}, #buscar el documento con valor ronin
    {"input_mmr":1} # solo devuelve el valor
    )    
    return (lastinput[0]['input_mmr'])

def tel_validation4 (chatID):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    lastinput=collection.find({"chatID":chatID}, #buscar el documento con valor ronin
    {"confirm_mmr":1} # solo devuelve el valor
    )    
    return (lastinput[0]['confirm_mmr'])

def tel_dailyconfirm(complete):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection    
    collection.update_one({"chatID":complete[0]},
    {
        "$set":{"daily_complete": complete[1] }
    },upsert=True)
    return True

def tel_imgpermision(chatID):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    # Document
    timestamp=(int(time.time()))
    collection.update_one({"chatID":chatID},
    {
        "$set":{"validation": True, "timestamp":timestamp }
    })

    return True



