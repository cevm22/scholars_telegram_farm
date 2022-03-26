from pymongo import MongoClient
from colorama import Fore, Style
import io
import datetime
import time
import config
import telebot
import gogsheets

MasterCID=config.MASTERCHATID
addvector=[]
bot = telebot.TeleBot(config.TOKEN, parse_mode=None)

#======================================================================
#parametros de base de datos
#======================================================================
MONGO_URI='mongodb://localhost' #en donde se encuentra la base datos
client = MongoClient(MONGO_URI) #inicializacion de la base datos

#==========================================================================
# Funcion agregar Informacion de scholars
#==========================================================================
def scholars_info(vector):    
    db=client['scholars'] # DB
    collection=db['info'] # Collection
    # Document
    collection.insert_one({
        "ronin": vector[0], #billetera ronin
        "scholar": vector[1], #scholar
        "user": vector[2], #usuario
        "telegram":vector[3] #telegram
    })
    return True

#==========================================================================
#  agregar api info http://api.lunaciarover.com/stats/0x Roninwallet ++++++
#==========================================================================
def trackinfo_wallets(vector):
    db=client['trackinfo'] # DB
    collection=db['wallets'] # Collection
    # Document
    collection.insert_one({
        "ronin": vector[0],
        "updated_on": vector[1],
        "last_claim_timestamp": vector[2],
        "ronin_slp": vector[3],
        "total_": vector[4],
        "in_game_slp":vector[5],
        "rank":vector[6],
        "mmr":vector[7],
        "total":vector[8],
        "win_rate": vector[9],
    })    
    return True

#==========================================================================
# Funcion agregar seguimiento temporal por hora +++++++++++++++++++++++++++
#==========================================================================
def temporal_lastupdate(vector):
    db=client['temporal'] # DB
    collection=db['lastupdate'] # Collection
    # Document
    collection.replace_one({"ronin":vector[0]},
    {
        "ronin": vector[0],
        "updated_on": vector[1],
        "last_claim_timestamp": vector[2],
        "ronin_slp": vector[3],
        "total_": vector[4],
        "in_game_slp":vector[5],
        "rank":vector[6],
        "mmr":vector[7],
        "total":vector[8],
        "win_rate": vector[9],
    },upsert=True) # Comando crea uno nuevo en dado caso de que no exista el documento
    return True

#==========================================================================
# Funcion buscar ultima actualizacion  temporal por hora ++++++++++++++++++
#==========================================================================
def searchwallet_updated (ronin):
    db=client['temporal'] # DB
    collection=db['lastupdate'] # Collection
    lastupdated=collection.find({"ronin":ronin}, #buscar el documento con valor ronin
    {"updated_on":1} # solo devuelve el valor
    )
    #print(lastupdated[0]['updated_on'])
    return (lastupdated[0]['updated_on'])

#==========================================================================
# Funcion buscar wallets y entregarlo como vector++++++++++++++++++++++++++
#==========================================================================
def pullwalletsinfo():
    vectorinfo=[]
    db=client['scholars'] # DB
    collection=db['info'] # Collection
    data=collection.find()
    #print(lastupdated[0]['updated_on'])
    for r in data:
        vectorinfo.append(str(r['ronin']))        
    return vectorinfo 
#==========================================================================
# Funcion pull temporaltelegram info+++++++++++++++++++++++++++++++++++++++
#==========================================================================
def pulltemp_updateinfo():
    vectorinfo=[]
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    data=collection.find()
    #print(lastupdated[0]['updated_on'])
    for r in data:
        vectorinfo.append([str(r['chatID']),str(r['input']),str(r['timestamp'])])       
    return vectorinfo 
#==========================================================================
# Funcion pull temporaldata info to fill googlesheets++++++++++++++++++++++
#==========================================================================
def pulltemp_googlesheets(cid):    
    vectorinfo=[]
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    data=collection.find({'chatID':cid})    
    ronin=searchroninfromchatid(cid)    
    #print(lastupdated[0]['updated_on'])
    vectorinfo=[[ronin,data[0]['input_slp'],data[0]['input_mmr'],time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(data[0]['timestamp']))]]     
    
    return vectorinfo 
#==========================================================================
# Funcion agregar daily farming++++++++++++++++++++++++++++++++++++++++++++
#==========================================================================
def add_daily():  
    pulltempdata=[]  
    db=client['track'] # DB
    collection=db['daily'] # Collection
    pulltempdata=pulltemp_updateinfo()
    for r in range(0,len(pulltempdata)):
        ronin=searchroninfromchatid(int(pulltempdata[r][0])) #buscar ronin por chatid  
        collection.insert_one({
            "ronin": ronin, #billetera ronin
            "daily": pulltempdata[r][1], #daily
            "update": pulltempdata[r][2], #timestamp        
        })
    return True

#==========================================================================
# Funcion buscar RONIN por chatid++++++++++++++++++++++++++++++++++++++++++
#==========================================================================
def searchroninfromchatid(chatid):
    db=client['scholars'] # DB
    collection=db['info'] # Collection    
    data=collection.find({"telegram":chatid},{"ronin":1})  
    return data[0]['ronin']
#==========================================================================
# Funcion buscar USER por chatid++++++++++++++++++++++++++++++++++++++++++
#==========================================================================
def searchuserfromchatid(chatid):
    db=client['scholars'] # DB
    collection=db['info'] # Collection    
    data=collection.find({"telegram":chatid},{"user":1})  
    return data[0]['user']
#==========================================================================
# Funcion buscar Telegram Chat ID++++++++++++++++++++++++++++++++++++++++++
#==========================================================================
def existchatid(chatid):
    db=client['scholars'] # DB
    collection=db['info'] # Collection

    try:
        data=collection.find({"telegram":chatid},{"telegram":chatid})
        check=(data[0])
        return True

    except Exception as e:
        return  False

#==========================================================================
# Funcion verificar si ya ingresó una vez su daily++++++++++++++++++++++++++
#==========================================================================
def secondinputdaily(chatid):
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    
    try:
        data=collection.find({"chatID":chatid},{"daily_complete":1})
        a=data[0]['daily_complete']        
        return a
    except Exception as e:        
        return False
#==========================================================================
# Funcion pull temporaltelegram daily_complete confirmation++++++++++++++++
#==========================================================================
def pulltemp_dailyconfirm():
    vectorinfo=[]
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    data=collection.find()
    #print(lastupdated[0]['updated_on'])
    for r in data:
        vectorinfo.append([str(r['chatID']),str(r['daily_complete'])])       
    return vectorinfo 
#==========================================================================
# Funcion reset daily_confirm a FALSE +++++++++++++++++++++++++++++++++++++
#==========================================================================
def daily_inputreset():
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    collection.update_many({"daily_complete":True},
    {
        "$set":{"daily_complete":False}
    })
    return
#==========================================================================
# Funcion reset daily_confirm a TRUE +++++++++++++++++++++++++++++++++++++
#==========================================================================
def daily_inputresettrue():
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    collection.update_many({"daily_complete":False},
    {
        "$set":{"daily_complete":True}
    })
    return
#==========================================================================
# Funcion mandar msj scholar a ingrsar su daily++++++++++++++++++++++++++++
#==========================================================================
def notificacion_daily():
    vector=pulltemp_dailyconfirm()  
    try:  
        for r in range(len(vector)):
            chatid=vector[r][0]
            confirm=str(vector[r][1])            
            
            if confirm == 'False':                
                bot.send_message(int(chatid),"FAVOR DE INGRESAR TU TOTAL DE SLP EL DÍA DE HOY, ANTES DE QUE SE REINICIE EL SERVIDOR  ")
                
                
    except Exception as e:
        print("error de loop")
        return
#==========================================================================
# Funcion buscar quién no ingresó su daily+++++++++++++++++++++++++++++++++
#==========================================================================
def search_dailyconfirmfalse():
    vectorinfo=[]
    db=client['temporaltelegram'] # DB
    collection=db['temp_update'] # Collection
    data=collection.find()
    #print(lastupdated[0]['updated_on'])
    for r in data:
        try:
            confirmation=r['daily_complete']
            if confirmation==False:                        
                user=searchuserfromchatid(r['chatID'])            
                vectorinfo.append([user,time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(r['timestamp']))])            

        except Exception as e:                  
            pass
        
    return vectorinfo    

#==========================================================================
# Funcion buscar quién no ingresó su daily+++++++++++++++++++++++++++++++++
# Función para automatizar que se ejecute a las 00:00:00 UTC+++++++++++++++
#==========================================================================
def update_dailyconfirmfalse():
    vector=search_dailyconfirmfalse()
    gogsheets.update_dailyconfirmfalse(vector)
    return

