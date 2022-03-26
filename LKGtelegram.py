from os import truncate
from telebot.types import Update
import requests
import config
import telebot
import datetime
import time
import urllib.request
import dbscript
import dbtelegram
import gogsheets
import logging



print("Ejecutando bot .....")
#Global variables
MasterCID=config.MASTERCHATID
addvector=[]
tokenbot=config.TOKEN_T #config.TOKEN
releasetoken=config.TOKEN
bot = telebot.TeleBot(releasetoken, parse_mode=None)

#flujo para agregar nuevos usuarios al bot
@bot.message_handler(commands=['add'])
def funcionprueba(message):    
    cid = message.chat.id    
    globals()['addvector']=[]
    if cid == MasterCID:

        bot.send_message(message.chat.id,
                        'Este es tu ID -> '+str(message.chat.id) + ' Eres Admin')
        next = bot.send_message(cid, 'INGRESA BILLETERA RONIN COMENZANDO CON 0x EN LUGAR DE "RONIN:"')
        bot.register_next_step_handler(next , add_newronin)
        
    else:
        bot.send_message(message.chat.id, 'NO eres Admin, NO puedes utilizar este comando')
        return      

def add_newronin(message):
    cid = message.chat.id
    input= message.text
    addvector.append(str(input))
    next = bot.send_message(cid, 'INGRESA EL NUMERO DE SCHOLAR (SOLO NÚMEROS)')
    bot.register_next_step_handler(next , add_newscholar)

def add_newscholar(message):
    cid = message.chat.id
    input= message.text
    try:    
        addvector.append(int(input))
        next = bot.send_message(cid, 'INGRESA EL USUARIO QUE JUGARÁ LA CUENTA')
        bot.register_next_step_handler(next , add_newuser)
    except Exception as e:
        bot.send_message(cid, 'ERROR: SOLO SE ADMITEN NUMEROS. VUELVE A INICIAR EL PROCESO')
        globals()['addvector']=[]
        return

def add_newuser(message):
    cid = message.chat.id
    input= message.text
    addvector.append(str(input))
    next = bot.send_message(cid, 'INGRESA EL CHATID DE TELEGRAM PARA SEGUIMIENTO')
    bot.register_next_step_handler(next , add_newtelegramid)

def add_newtelegramid(message):
    cid = message.chat.id
    input= message.text
    try:    
        addvector.append(int(input))
        bot.send_message(cid, 'SE HA ALMACENADO EL SIGUIENTE VECTOR: ')
        bot.send_message(cid, str(addvector))
        savevector=dbscript.scholars_info(addvector)                        
        globals()['addvector']=[]
        bot.send_message(int(input), 'BIENVENIDO A LATIN KNIGHTS GUILD, YO SOY AJOLOBOT, FAVOR DE NOTIFICARLE A LA PERSONA QUE HAS QUEDADO REGISTRADO CORRECTAMENTE')        
    except Exception as e:
        print(e)
        filename = str('error_newtelegramid ' + str(time.time()) + '.txt')  
        fileerror = open(filename, 'w')
        fileerror.write('======================================' + '\n')
        fileerror.write('Error funcion add_newtelegramid '+ str(datetime.datetime.now()) + "\n")
        fileerror.write('======================================' + '\n')
        fileerror.write('API response ->>> -%s' % e + '\n')
        fileerror.write('======================================' + '\n')
        bot.send_message(cid, 'ERROR: SOLO SE ADMITEN NUMEROS. VUELVE A INICIAR EL PROCESO'+"\n")
        bot.send_message(cid, e)
        globals()['addvector']=[]
        return
    
#comando para obtener ID
@bot.message_handler(commands=['id'])
def giveID(message):
    print("suministrando Chat ID")
    bot.send_message(message.chat.id,
                'Este es tu ID -> ' + str(message.chat.id) + ' Entrégaselo a tú administrador de Latin Knights Guild')
    pass

#Flujo para el cmando daily
@bot.message_handler(commands=['daily'])
def telegramdaily(message):
    cid = message.chat.id
    search=dbscript.existchatid(cid)
    if search==True:
        confirm_dailyinput=dbscript.secondinputdaily(cid)           
        if confirm_dailyinput ==False:

            slp = bot.send_message(cid, 'INGRESA EL TOTAL DE SLP QUE TIENES AL DIA DE HOY:')
            bot.register_next_step_handler(slp , inputslp)
        else:
            bot.send_message(cid,'YA INGRESASTE PREVIAMENTE TU DAILY, EN DADO CASO DE QUE HAYA SIDO UN ERROR, FAVOR DE CONSULTARLO CON UN ADMIN DE LATIN KNIGHTS GUILD.')
            return
        

    else:
        bot.send_message(cid,'TU USUARIO TELEGRAM NO SE ENCUENTRA REGISTRADO EN NUESTRAS BASES DE DATOS, FAVOR DE CONTACTAR A UN STAFF DE LATIN KNIGHTS GUILD.')
        return

def inputslp(message):
    cid = message.chat.id
    input= message.text
    large=confirmdigit(input,cid)    
    if large is True:
        dbtelegram.tel_update1([cid,input])
        confirm = bot.send_message(cid, 'CONFIRMA EL MONTO DE SLP')
        bot.register_next_step_handler(confirm , confirmar)
    else:
        bot.send_message(cid, 'FAVOR INGRESAR MÁXIMO 4 DÍGITOS. VUELVE A INICIAR EL PROCESO')
        return

def confirmar(message):
    cid = message.chat.id
    confirmation= message.text
    large=confirmdigit(confirmation,cid)
    if large is True:
        dbtelegram.tel_update2([cid,confirmation])    
        bot.send_message(cid, 'VALIDANDO INFORMACION')
        input=dbtelegram.tel_validation1(cid)
        confirm=dbtelegram.tel_validation2(cid)
        try:
            a=int(input)
            b=int(confirm)
            if (a==b and a>0 and b>0): #AGREGAR CONFIRMACIÓN DE NEGATIVOS
                mmr=bot.send_message(cid, 'COINCIDE EL VALOR SLP. \n\n AHORA, POR FAVOR INGRESA LA CANTIDAD DE COPAS EN QUE QUEDASTE!')
                bot.register_next_step_handler(mmr , inputmmr)
            else:
                bot.send_message(cid, '!ERROR! -> FAVOR INGRESAR SOLO NUMEROS Y LOS VALORES SEAN IGUALES. VUELVE INICIAR EL PROCESO.')
                return
                
        except Exception as e:
            bot.send_message(cid, '!ERROR! -> FAVOR INGRESAR SOLO NUMEROS Y LOS VALORES SEAN IGUALES. VUELVE INICIAR EL PROCESO.')
            return
    else:
        bot.send_message(cid, 'FAVOR INGRESAR MÁXIMO 4 DÍGITOS. VUELVE A INICIAR EL PROCESO')
        return

def inputmmr(message):
    cid = message.chat.id
    mmr= message.text
    large=confirmdigit(mmr,cid)
    if large is True:
        dbtelegram.tel_update3([cid,mmr])
        confirm = bot.send_message(cid, 'CONFIRMA LA CANTIDAD DE COPAS')
        bot.register_next_step_handler(confirm , confirma_mmr) 
    else:
        bot.send_message(cid, 'FAVOR INGRESAR MÁXIMO 4 DÍGITOS. VUELVE A INICIAR EL PROCESO')
        return

def confirma_mmr(message):
    cid = message.chat.id
    confirmation= message.text
    large=confirmdigit(confirmation,cid)
    if large is True:
        dbtelegram.tel_update4([cid,confirmation])
        bot.send_message(cid, 'VALIDANDO INFORMACION')
        input=dbtelegram.tel_validation3(cid)
        confirm=dbtelegram.tel_validation4(cid)
        try:
            a=int(input)                
            b=int(confirm)      
            if (a==b and a>0 and b>0):
                #vector=[ronin,slp,mmr,day]
                vec=dbscript.pulltemp_googlesheets(cid)
                gogsheets.update_slp_mmr_daily(vec)
                #gogsheets.update_slp_mmr_manual(vec)
                dbtelegram.tel_dailyconfirm([cid,True])
                bot.send_message(cid, 'COINCIDEN LOS VALORES, MUCHAS GRACIAS POR TU TIEMPO!')   


            else:
                bot.send_message(cid, '!ERROR! DE COMPARACION -> FAVOR INGRESAR SOLO NUMEROS Y LOS VALORES SEAN IGUALES. VUELVE INICIAR EL PROCESO.')
            
        except Exception as e:
            bot.send_message(cid, '!ERROR! -> FAVOR INGRESAR SOLO NUMEROS Y LOS VALORES SEAN IGUALES. VUELVE INICIAR EL PROCESO.')
            bot.send_message(MasterCID,e)
            return
    else:
        bot.send_message(cid, 'FAVOR INGRESAR MÁXIMO 4 DÍGITOS. VUELVE A INICIAR EL PROCESO')
        return

def confirmdigit(dig,cid):
    try:
        value=len(str(dig))
        
        if value <5:
            posval=int(value)
            return True
        else:            
            return False
    except Exception as e:        
        return False

#Comando para cambiar estado daily a FALSE
@bot.message_handler(commands=['FALSE'])
def reset_temporal(message):
    cid = message.chat.id
    if cid == MasterCID:
        dbscript.daily_inputreset()
        bot.send_message(cid,'Se ha reeseteado todos los daily a FALSE, puedes volver a ingresarlos')
        return
#Comando para cambiar estado daily a TRUE
@bot.message_handler(commands=['TRUE'])
def reset_temporal(message):
    cid = message.chat.id
    if cid == MasterCID:
        dbscript.daily_inputresettrue()
        bot.send_message(cid,'Se ha reeseteado todos los daily a TRUE, puedes volver a ingresarlos')
        return

@bot.message_handler(commands=['TESTMSG'])
def testingmsg(message):
    cid = message.chat.id
    confirm = bot.send_message(cid, 'INGRESA EL CHAT ID PARA ENVIAR MENSAJE DE PRUEBA DE BIENVENIDA')
    bot.register_next_step_handler(confirm , sendtest)
    return

def sendtest(message):
    cid = message.chat.id
    input= message.text
    try:
        bot.send_message(int(input), 'BIENVENIDO A LATIN KNIGHTS GUILD, YO SOY AJOLOBOT, FAVOR DE NOTIFICARLE A LA PERSONA QUE HAS QUEDADO REGISTRADO CORRECTAMENTE')
        bot.send_message(cid,'MENSAJE ENVIADO')
    except Exception as e:
        bot.send_message(cid, 'ERROR: EN MENSAJE DE PRUEBA >>>> '+"\n")
        bot.send_message(cid, e)

    return

#comando para actualizar axies en googsheets
#@bot.message_handler(commands=['axies'])
def update_axiesguild(message):
    cid = message.chat.id
    vector=gogsheets.pullronin_backend()
    gogsheets.update_axiesdatabase(vector)
    bot.send_message(cid,'axies actualizados')
    return  

#start the bot to listen
#bot.polling()
#telebot.logger.setLevel(logging.DEBUG)
bot.infinity_polling(logger_level=logging.DEBUG, timeout=10, long_polling_timeout = 5)
