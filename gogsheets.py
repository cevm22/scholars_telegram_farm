import os.path
import time
import axies_script 
from googleapiclient.discovery import build
from google.oauth2 import service_account
import axies_script
import config

SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID spreadsheet.
spreadsheetID = config.SHEET_ID

service = build('sheets','v4', credentials=creds)

sheet = service.spreadsheets()
#result = sheet.values().get(spreadsheetId=spreadsheetID,range='Database_SLP').execute() #obtener valores de toda la hoja
#values = result.get('values', []) #mostrar los valores de toda la hoja de la funcion anterior

#Insertar en hoja los valores de variable "vector"
#vector =[["0xañsndfñao12123s",123,1111,"13/08/21"],["0x1s2d3fv1e2df3",2323,1200,"13/09/21"],["0x0f9f8djs7env7f6s",150,2222,"15/12/21"]]
#append: es para agregar al final de la lista
#update: es actualizar a partir del rango "range"
#requests=sheet.values().append(spreadsheetId=spreadsheetID,range='Database_SLP!A2', #valueInputOption="USER_ENTERED",body={"values":vector}).execute() 

def update_slp_mmr_daily(vector):
        #vector=[ronin,slp,mmr,day]
        requests=sheet.values().append(spreadsheetId=spreadsheetID,range='Database_SLP!A2', valueInputOption="USER_ENTERED",body={"values":vector}).execute()
        update_slp_mmr_manual(vector) 
        return
def update_slp_mmr_manual(vector):
        #vector=[['0x168674c2fce3494c043435b524d6b08b364f36a8', '111', '5555', '1628923455']]

        index=int(searchronin_backend(vector[0][0]))+30 #OBTENER POSICION EXCEL RONIN

        sheetpos_yesterdayslp=str('backend!R'+str(index))
        actual = sheet.values().get(spreadsheetId=spreadsheetID,range=sheetpos_yesterdayslp).execute() 
        result=actual['values']
        yesterdayvalue=str('backend!U'+str(index))

        yesterdaslp=sheet.values().update(spreadsheetId=spreadsheetID,range=yesterdayvalue, valueInputOption="USER_ENTERED",body={"values":result}).execute()        
        #ACTUALIZAR VALOR MANUAL
        #vector=[ronin,slp,mmr,day]        
        sheetpos=str('backend!Q'+str(index))
        requests=sheet.values().update(spreadsheetId=spreadsheetID,range=sheetpos, valueInputOption="USER_ENTERED",body={"values":vector}).execute()

        
        return 
        
def searchronin_backend(ronin):
        result = sheet.values().get(spreadsheetId=spreadsheetID,range='Scholar_Details!D11:D').execute() 
        for i in range(0,len(result['values'])):
                if ronin==str(result['values'][i][0]):                                               
                        return(i)

def pullronin_backend():
        result= sheet.values().get(spreadsheetId=spreadsheetID,range='Scholar_Details!D11:D').execute() 
        vector= result['values']
        return vector

def update_dailyconfirmfalse(vector):
        #Clear all data from backend sheet #vector=[['Ferag', '1629305815']]
        sheet.values().clear(spreadsheetId=spreadsheetID,range='backend!AH30:AH').execute()
        sheet.values().clear(spreadsheetId=spreadsheetID,range='backend!AI30:AI').execute()
        requests=sheet.values().append(spreadsheetId=spreadsheetID,range='backend!AH30', valueInputOption="USER_ENTERED",body={"values":vector}).execute()
        return

def update_axiesdatabase(vector):
        print("funcion update axies database")        
        deleterows()
        a=[]
        for i in range(0,len(vector)):                                
                
                a.append(axies_script.ronin_wallet_axies(vector[i][0]))                
                print(i)
        req=sheet.values().append(spreadsheetId=spreadsheetID,range='axies_db!B12', valueInputOption="USER_ENTERED",body={"values":vector}).execute()
        req1=sheet.values().append(spreadsheetId=spreadsheetID,range='axies_db!C12', valueInputOption="USER_ENTERED",body={"values":a}).execute()        
        return True
def deleterows():
        sheet.values().clear(spreadsheetId=spreadsheetID,range='axies_db!B12:BB100').execute()
        return

#funcion para exportar las partes de los axies en el googsheets 
def update_axieinfo():
        result= sheet.values().get(spreadsheetId=spreadsheetID,range='axies_db_data!B12:B').execute() 
        vec_totalaxies=sheet.values().get(spreadsheetId=spreadsheetID,range='axies_db_data!B10').execute() 
        total=int(vec_totalaxies["values"][0][0])
        vector= result['values']        
        #print(len(vector))        
        for i in range(0,total):
                axieID=(vector[i][0])
                axieinfo=pull_axieinfo(axieID)
                vectoraxieinfo=add_axieinfo(i,axieinfo)
                
                print(str(i)+ " > "+str(axieID))                
        return

def update_erroraxieinfo():
        result= sheet.values().get(spreadsheetId=spreadsheetID,range='axies_db_data!D12:D').execute() 
        vec_totalaxies=sheet.values().get(spreadsheetId=spreadsheetID,range='axies_db_data!B10').execute() 
        total=int(vec_totalaxies["values"][0][0])
        vector= result['values']       
        for i in range(0,total):                
                axieID=(vector[i][0])
                if axieID=="ERROR":
                        rows=str('axies_db_data!B'+str(int(12+i)))                        
                        getID= sheet.values().get(spreadsheetId=spreadsheetID,range=rows).execute() 
                        newid=(getID['values'][0][0])
                        axieinfo=pull_axieinfo(newid)
                        vectoraxieinfo=add_axieinfo(i,axieinfo)                
                        print(str(i)+ " > "+str(axieID))   
        return
def pull_axieinfo(axie_id):
        vector=[]
        try:
                axie_fam_info=axies_script.axie_family(axie_id)
                #print(axie_fam_info)
                time.sleep(1)        
                axie_gen_info=axies_script.axie_genes(axie_id)

                if axie_gen_info is False:
                        print("axie en huevo")
                        return False
                else:
                        vector.append(axie_fam_info[4])
                        vector.append(axie_fam_info[3][0])#HP
                        vector.append(axie_fam_info[3][2])#speed
                        vector.append(axie_fam_info[3][3])#skill
                        vector.append(axie_fam_info[3][1])#morale

                        vector.append(axie_gen_info[0])#breed count
                        vector.append(axie_gen_info[1][0])#D eyes
                        vector.append(axie_gen_info[1][1])#R1 eyes
                        vector.append(axie_gen_info[1][2])#R2 eyes
                        vector.append(axie_gen_info[2][0])#D ears
                        vector.append(axie_gen_info[2][1])#R1 ears
                        vector.append(axie_gen_info[2][2])#R2 ears
                        vector.append(axie_gen_info[3][0])#D mouth
                        vector.append(axie_gen_info[3][1])#R1 mouth
                        vector.append(axie_gen_info[3][2])#R2 mouth
                        vector.append(axie_gen_info[4][0])#D head
                        vector.append(axie_gen_info[4][1])#R1 head
                        vector.append(axie_gen_info[4][2])#R2 head
                        vector.append(axie_gen_info[5][0])#D back
                        vector.append(axie_gen_info[5][1])#R1 back
                        vector.append(axie_gen_info[5][2])#R2 back
                        vector.append(axie_gen_info[6][0])#D tail
                        vector.append(axie_gen_info[6][1])#R1 tail
                        vector.append(axie_gen_info[6][2])#R2 tail
                        return vector
        except Exception as e:
                print(e)
                return "error"

def add_axieinfo(row,axieinfovec):
        time.sleep(1)
        vector=[]
        range=str('axies_db_data!D'+str(row+12)) #start at row 12
        rangeclear=str(range+':AA'+str(row+12))
        try:
                if axieinfovec is False:
                        sheet.values().clear(spreadsheetId=spreadsheetID,range=rangeclear).execute()
                        newvec=[['huevo',0]]                
                        sheet.values().update(spreadsheetId=spreadsheetID,range=range, valueInputOption="USER_ENTERED",body={"values":newvec}).execute()       
                else:
                        sheet.values().clear(spreadsheetId=spreadsheetID,range=rangeclear).execute()
                        vector.append(axieinfovec)                
                        sheet.values().update(spreadsheetId=spreadsheetID,range=range, valueInputOption="USER_ENTERED",body={"values":vector}).execute()   
                        return            
        except:
                errorvec=[]
                sheet.values().clear(spreadsheetId=spreadsheetID,range=rangeclear).execute()
                errorvec=[['ERROR',0]]                
                sheet.values().update(spreadsheetId=spreadsheetID,range=range, valueInputOption="USER_ENTERED",body={"values":errorvec}).execute() 
                return
                
        
