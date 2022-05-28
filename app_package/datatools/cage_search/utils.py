# import os
import pandas as pd
# from datetime import date
# from datetime import timedelta
# import datetime
# import requests
# from requests.exceptions import MissingSchema
# from flask import current_app
import numpy as np
from app_package import db
# from app_package.modelsBls import Industrynames,Industryvalues, Commoditynames, Commodityvalues
from app_package.modelsCage import Cagecompanies
#added for BLS API call
# from sqlalchemy import func
from dateutil.relativedelta import relativedelta
import json


    
def makeSearchExactDict(formDict):
    searchStringDict={}
    exactDict={}
    for i,j in formDict.items():
        if i != 'searchCage' and i[-5:] != 'Exact':
            searchStringDict[i]=j
        elif i[-5:] == 'Exact':
            exactDict[i[:-5]]=j
    return (searchStringDict,exactDict)
    
    
def searchQueryCageToDf(formDict):
    searchDict={'companyName':'ADRS_NM_C_TXT1', 'companyNameSub':'ADRS_NM_C_TXT2','cageCode': 'CAGE_code',
        'address': ['ST_ADDRESS1','ST_ADDRESS2'], 'city': 'CITY', 'state': 'ST_US_POSN'}

    searchStringDict, exactDict=makeSearchExactDict(formDict)
    searchQuery = Cagecompanies.query
    for i,j in searchStringDict.items():
        if i == 'address' and exactDict.get(i)=='checked':
            searchQuery=searchQuery.filter(getattr(Cagecompanies, 'ST_ADDRESS1')==j)
        elif i == 'address':
            for n in searchDict[i]:
                searchQuery=searchQuery.filter(getattr(Cagecompanies, n).contains(j))
        elif i != 'searchCage':
            if exactDict.get(i):
                searchQuery=searchQuery.filter(getattr(Cagecompanies, searchDict[i])==j)
            else:
                searchQuery=searchQuery.filter(getattr(Cagecompanies, searchDict[i]).contains(j))
    
    columnNames=['CAGE','Company Name', 'Company Sub Name', 'Address1', 'Address2','PO Box',
        'City', 'State', 'Zip', 'Country', 'Phone']
    searchQueryDf=pd.DataFrame([(i.CAGE_code,i.ADRS_NM_C_TXT1,i.ADRS_NM_C_TXT2,i.ST_ADDRESS1,i.ST_ADDRESS2,
                            i.PO_BOX,i.CITY,i.ST_US_POSN, i.ZIP_CODE,i.COUNTRY,i.TELEPHONE_NUMBER) for i in searchQuery], 
                           columns=columnNames)

    return searchQueryDf
    

def cageExcelObjUtil(filePathAndName,df):
    excelObj=pd.ExcelWriter(filePathAndName,datetime_format='yyyy-mm-dd')
    sheetName='CAGE Search'
    dfHeader = pd.DataFrame([list(df.columns)])
    dfHeader.to_excel(excelObj,sheet_name=sheetName,header=False,index=False)
    df.to_excel(excelObj, sheet_name=sheetName,startrow=len(dfHeader), header=False,index=False)
    #adjust column width
    worksheet=excelObj.sheets[sheetName]
    worksheet.set_column(1,1,20)
    worksheet.set_column(3,3,20)
    worksheet.set_column(6,6,15)
    worksheet.set_column(7,7,5)
    worksheet.set_column(10,10,12)
    workbook=excelObj.book
    worksheet.freeze_panes(1,0)
    return excelObj


# def checkDbForExistingData(seriesIdListClean, table_name):
#     for table in db.Model.__subclasses__():
#         if table.__tablename__ == table_name:
#             database_to_search = table

#     api_search_list =[]
#     for series in seriesIdListClean:
#         max_year = db.session.query(func.max(database_to_search.year)).filter(
#             database_to_search.series_id == seriesIdListClean[0]).first()[0]
#         id_list = db.session.query(database_to_search.id, database_to_search.period).filter(
#             database_to_search.series_id == seriesIdListClean[0],database_to_search.year == max_year).all()

#         x=0
#         for i in id_list:
#             if int(i[1][1:3]) > x:
#                 x = int(i[1][1:3])
#                 id_of_max_period_from_series_id = i[0]#<----id_of_max_period_from_series_id is the
#         #database_to_search.id for the most current entry of theseries_id in the database.
        
#         month_value, year_value = db.session.query(database_to_search).filter(
#             database_to_search.id == id_of_max_period_from_series_id).with_entities(
#             database_to_search.period, database_to_search.year).first()
#         month_value = int(month_value[1:])
#         db_date = datetime.datetime.strptime(f'{year_value}-{month_value}-1','%Y-%m-%d').date()
        
#         # BLS release dates vary between the 9th and 17th of the month. Here i'm assuming
#         #all db is current up to 2 months and 13 days behind the current date. Or 
#         #up to the 14th of the two months following the month in the db.
#         #***idea: put release schedule in a dictionary and update db_date_is_good_until based on schedule.
#         db_date_is_good_until = db_date +relativedelta(months=2)+relativedelta(days=13)
        
#         current_date = datetime.datetime.now().date()
#         if current_date >db_date_is_good_until:
#             api_search_list.append(series)
#     return (db_date_is_good_until, api_search_list)


# def blsApiCall(db_date_is_good_until, api_search_list):
#     headers = {'Content-type': 'application/json'}
#     startYear=datetime.datetime.now().date() + relativedelta(years=-3)
#     startYear=startYear.year
#     endYear=db_date_is_good_until.year
#     data = json.dumps({"seriesid": api_search_list,"startyear":startYear, 
#                        "endyear":endYear,
#                        'registrationkey':current_app.config['REGISTRATION_KEY']
#                       })
#     bls_pull = requests.post(current_app.config['BLS_API_URL'], data=data, headers=headers)
#     print('API Status code:',bls_pull.status_code)
#     if bls_pull.status_code != 200:
#         return print('API call did not go through. Status is something other than 200.')
#     json_data=json.loads(bls_pull.text)
#     return json_data


# def makeDfDictionary(api_search_list, json_data):
#     df_dict={}
#     for series in api_search_list:
#         series_id_list = []
#         year_list =[]
#         period_list =[]
#         value_list =[]
#         footnote_codes_list = []
#         series_count = api_search_list.index(series)
#         print(series)
#         print('makeDfDictionary -- json_data:::',json_data)
#         try:
#             for record in json_data['Results']['series'][series_count]['data']:
#                 series_id_list.append(json_data['Results']['series'][series_count]['seriesID'])
#                 year_list.append(record['year'])
#                 period_list.append(record['period'])
#                 value_list.append(record['value'])
#                 footnote_codes_list.append(record['footnotes'][0].get('code'))
#             df_dict[series]=pd.DataFrame(list(zip(series_id_list,year_list,period_list,value_list,
#                                                  footnote_codes_list)), columns=['series_id','year','period','value','footnote_codes'])
#         except:
#             print(series, 'has current data to update')
            
#     for df in df_dict.values():
#         df['id']=df.index
#         df.set_index('id', inplace = True)
    
#     return df_dict


# def deleteOldRows(table_name, df_dict):
#     import sqlalchemy as sa
#     meta = sa.MetaData()
#     # table_name = 'commodityvalues'
#     for df in df_dict.values():
#         sa_table = sa.Table(table_name, meta, autoload=True, autoload_with=db.engine)
#         cond = df.apply(lambda row: sa.and_(sa_table.c['series_id'] == row['series_id'],
#                                                 sa_table.c['year'] == row['year'],
#                                                 sa_table.c['period'] == row['period']), axis=1)
#         cond = sa.or_(*cond)

#         # Define and execute the DELETE
#         delete = sa_table.delete().where(cond)
#         with db.engine.connect() as conn:
#             conn.execute(delete)
        
#         # Now you can insert the new data
#         df.to_sql(table_name, db.engine, if_exists='append', index=False)


# def updateDbWithApi(seriesIdListClean, table_name):
    
#     db_date_is_good_until, api_search_list = checkDbForExistingData(seriesIdListClean, table_name)
#     print('successfully checked Db for Existing Data. The follwing indicies need updating: ',api_search_list)
#     if len(api_search_list)>0:
#         json_data = blsApiCall(db_date_is_good_until, api_search_list)
#         df_dict = makeDfDictionary(api_search_list, json_data)
#         print('succesfully created df_dict')
#         deleteOldRows(table_name, df_dict)
#         print('Succesfully update! Appeneded ', table_name,' for :',api_search_list)
#     else:
#         print('All requested series_ids already up to date. No BLS API call necessary.')
    
    
    