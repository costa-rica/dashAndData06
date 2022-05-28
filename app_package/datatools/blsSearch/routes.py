from flask import Blueprint

from flask import render_template, url_for, redirect, flash, request, session,\
    current_app, send_from_directory
import os
from app_package.datatools.blsSearch.utils import checkStatusUtility, \
    formatSeriesIdListUtil, seriesIdTitleListIndustry, seriesIdTitleListCommodity, \
    priceIndicesToDf,buildMetaDfUtil,makeExcelObj_priceindices,annualizeDf, \
    quarterizeDf,makeSearchExactDict, updateDbWithApi
import logging
from app_package.utils import logs_dir
from logging.handlers import RotatingFileHandler


# #Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_bls = logging.getLogger(__name__)
logger_bls.setLevel(logging.DEBUG)
logger_terminal = logging.getLogger('terminal logger')
logger_terminal.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(logs_dir,'bls.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

logger_terminal.handlers.clear()
logger_bls.addHandler(file_handler)
logger_terminal.addHandler(stream_handler)

# #End set up logger



datatools_bls = Blueprint('datatools_bls', __name__)

    
@datatools_bls.route('/bls_data_menu',methods=['POST','GET'])
def bls_menu():
    # logger_terminal.info(f'****BLS Menu accessed*****')
    return render_template("datatools/blsDataMenu.html")


@datatools_bls.route('/blsIndustry',methods=['POST','GET'])
def blsIndustry():
    # print('current_app.static_folder:::', type(current_app.static_folder), current_app.static_folder)
    #Delete download file if exists
    if os.path.exists(os.path.join(current_app.static_folder, 'utility_bls','blsIndustryPPI.xlsx')):
        os.remove(os.path.join(current_app.static_folder, 'utility_bls','blsIndustryPPI.xlsx'))
    
    siteTitle = "BLS Industry Producer Price Index (PPI)"
    session['textareaEntry'] = request.args.get('textareaEntry_new')
    cs0=request.args.get('cs0')
    cs1=request.args.get('cs1')
    cs2=request.args.get('cs2')
    cs3=request.args.get('cs3')
    cs4=request.args.get('cs4')
    cs5=request.args.get('cs5')
    cs6=request.args.get('cs6')
    cs7=request.args.get('cs7')
    cs8=request.args.get('cs8')
    cs9=request.args.get('cs9')
    cs10=request.args.get('cs10')
    cs11=request.args.get('cs11')
    cs12=request.args.get('cs12')
    cs13=request.args.get('cs13')
    colNames=['series_id','series_title']
    indexSeriesIdTitleList=seriesIdTitleListIndustry()

    if request.method=="POST":
        logger_bls.info(f'BLS Industry POST request made')
        formDict = request.form.to_dict()
        textareaEntry_new=formDict.get('textareaEntry')
        addSeries_id=formDict.get('addSeries_id')
        periodicity = formDict.get('periodicty')
        # print('formDict:::',formDict)
        

        if addSeries_id:
            csUtil = checkStatusUtility(formDict)
            if textareaEntry_new != None and textareaEntry_new != "":
                textareaEntry_new = textareaEntry_new + ',\n' + addSeries_id
            else:
                textareaEntry_new = addSeries_id 
            return redirect(url_for('datatools_bls.blsIndustry', textareaEntry_new=textareaEntry_new, cs0=csUtil[0],
                cs1=csUtil[1],cs2=csUtil[2],cs3=csUtil[3],cs4=csUtil[4],cs5=csUtil[5],cs6=csUtil[6],cs7=csUtil[7],
                cs8=csUtil[8],cs9=csUtil[9],cs10=csUtil[10], cs11=csUtil[11],cs12=csUtil[12],cs13=csUtil[13]))

        elif formDict.get('downloadButton') and textareaEntry_new != '':
            seriesIdList=session['textareaEntry'].replace('\r\n','')
            #make seriesId for db/api check and indexValuesDf
            seriesIdListClean=formatSeriesIdListUtil(seriesIdList)
            print('Series Requested: ',seriesIdListClean)
            
            updateDbWithApi(seriesIdListClean, 'industryvalues')#<---checks db for requested data not current
            #if any requested data is not of a month 2 months and 13 days from the current date then api call
            
            indexValuesDf=priceIndicesToDf(seriesIdListClean,'Industry')

            #make list for meta data
            metaDataItemsList=[i[:-8] for i in formDict.keys() if 'Checkbox' in i]

            #use list to make metadata indexValuesDf
            metaDf = buildMetaDfUtil(seriesIdListClean, metaDataItemsList, 'Industry')

            #create ExcelWriter object with date formatted, col heading formatted and values centered
            bls_folder_path = os.path.join(current_app.static_folder,'utility_bls')
            if not os.path.exists(bls_folder_path):
                os.makedirs(bls_folder_path)

            filePathAndName=os.path.join(bls_folder_path,'blsIndustryPPI.xlsx')
            sheetName='Indices'

            excelObj=makeExcelObj_priceindices(filePathAndName,metaDf,indexValuesDf,seriesIdListClean,
                metaDataItemsList,sheetName, periodicity)
            excelObj.close()
            return send_from_directory(bls_folder_path,'blsIndustryPPI.xlsx', as_attachment=True)

            
        elif formDict.get('clearButton'):
            if os.path.exists(os.path.join(bls_folder_path,'blsIndustryPPI.xlsx')):
              os.remove(os.path.join(bls_folder_path,'blsIndustryPPI.xlsx'))

            return redirect(url_for('datatools_bls.blsIndustry', cs11="checked"))
        else:
            flash(f'No indices requested', 'warning')
            return redirect(url_for('datatools_bls.blsIndustry'))
            
    return render_template('datatools/blsIndustry.html', siteTitle=siteTitle, indexSeriesIdTitleList=indexSeriesIdTitleList,
    colNames=colNames, len=len, str=str, textareaEntry=session['textareaEntry'], cs0=cs0,
                cs1=cs1,cs2=cs2,cs3=cs3,cs4=cs4,cs5=cs5,cs6=cs6,cs7=cs7,cs8=cs8,cs9=cs9,cs10=cs10,cs11=cs11,
                cs12=cs12,cs13=cs13)



@datatools_bls.route('/blsCommodity',methods=['POST','GET'])
def blsCommodity():
    #Delete download file if exists
    if os.path.exists(os.path.join(current_app.static_folder, 'blsCommodity','blsCommodityPPI.xlsx')):
        os.remove(os.path.join(current_app.static_folder, 'blsCommodity','blsCommodityPPI.xlsx'))
    siteTitle='BLS Commodity Producer Price Index (PPI)'
    session['textareaEntry'] = request.args.get('textareaEntry_new')
    cs0=request.args.get('cs0')
    cs1=request.args.get('cs1')
    cs2=request.args.get('cs2')
    cs3=request.args.get('cs3')
    cs4=request.args.get('cs4')
    cs5=request.args.get('cs5')
    cs6=request.args.get('cs6')
    cs7=request.args.get('cs7')
    cs8=request.args.get('cs8')
    cs9=request.args.get('cs9')
    cs10=request.args.get('cs10')
    cs11=request.args.get('cs11')
    cs12=request.args.get('cs12')
    cs13=request.args.get('cs13')
    colNames=['series_id','series_title']
    indexSeriesIdTitleList=seriesIdTitleListCommodity()
    
    if request.method=="POST":
        # logger_bls.info(f'BLS Commodity POST request made')
        formDict = request.form.to_dict()
        textareaEntry_new=formDict.get('textareaEntry')
        addSeries_id=formDict.get('addSeries_id')
        periodicity = formDict.get('periodicty')

        if addSeries_id:
            csUtil = checkStatusUtility(formDict)
            if textareaEntry_new != None and textareaEntry_new != "":
                textareaEntry_new = textareaEntry_new + ',\n' + addSeries_id
            else:
                textareaEntry_new = addSeries_id 
            return redirect(url_for('datatools_bls.blsCommodity', textareaEntry_new=textareaEntry_new, cs0=csUtil[0],
                cs1=csUtil[1],cs2=csUtil[2],cs3=csUtil[3],cs4=csUtil[4],cs5=csUtil[5],cs6=csUtil[6],cs7=csUtil[7],
                cs8=csUtil[8],cs9=csUtil[9],cs10=csUtil[10], cs11=csUtil[11],cs12=csUtil[12],cs13=csUtil[13]))

        elif formDict.get('downloadButton') and textareaEntry_new != '':
            
            #check text file with last update
            #if update is less than 30 days ago no updatre
            #else request new data from bls
            #then make df
            #then make excel
            
            
            seriesIdList=session['textareaEntry'].replace('\r\n','')
            
            #make seriesId for indexValuesDf
            seriesIdListClean=formatSeriesIdListUtil(seriesIdList)
            print('seriesIdListClean::::',seriesIdListClean)
            indexValuesDf=priceIndicesToDf(seriesIdListClean,'Commodity')

            updateDbWithApi(seriesIdListClean, 'commodityvalues')#<---checks db for requested data not current
            #if any requested data is not of a month 2 months and 13 days from the current date then api call
            
            indexValuesDf=priceIndicesToDf(seriesIdListClean,'Commodity')

            #make list for meta data
            metaDataItemsList=[i[:-8] for i in formDict.keys() if 'Checkbox' in i]
            print('metaDataItemsList:::',metaDataItemsList)

            #use list to make metadata indexValuesDf
            metaDf = buildMetaDfUtil(seriesIdListClean, metaDataItemsList, 'Commodity')

            #create ExcelWriter object with date formatted, col heading formatted and values centered
            bls_folder_path = os.path.join(current_app.static_folder,'utility_bls')
            # isExist = os.path.exists(bls_folder_path)
            if not os.path.exists(bls_folder_path):
                os.makedirs(bls_folder_path)


            filePathAndName=os.path.join(os.path.join(bls_folder_path,'blsCommodityPPI.xlsx'))
            sheetName='Indices'
            #if annualize
            excelObj=makeExcelObj_priceindices(filePathAndName,metaDf,indexValuesDf,seriesIdListClean,
                metaDataItemsList,sheetName, periodicity)
            excelObj.close()
            return send_from_directory(bls_folder_path,'blsCommodityPPI.xlsx', as_attachment=True)

            
        elif formDict.get('clearButton'):
            if os.path.exists(os.path.join(bls_folder_path,'blsCommodityPPI.xlsx')):
              os.remove(os.path.join(bls_folder_path,'blsCommodityPPI.xlsx'))

            return redirect(url_for('datatools_bls.blsCommodity', cs11="checked"))
        else:
            flash(f'No indices requested', 'warning')
            return redirect(url_for('datatools_bls.blsCommodity'))
            
            
    return render_template('datatools/blsCommodity.html', siteTitle=siteTitle, indexSeriesIdTitleList=indexSeriesIdTitleList,
        colNames=colNames, len=len, str=str, textareaEntry=session['textareaEntry'], cs0=cs0,
        cs1=cs1,cs2=cs2,cs3=cs3,cs4=cs4,cs5=cs5,cs6=cs6,cs7=cs7,cs8=cs8,cs9=cs9,cs10=cs10,cs11=cs11,
        cs12=cs12,cs13=cs13)


