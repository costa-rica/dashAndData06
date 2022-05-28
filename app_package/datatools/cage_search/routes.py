from flask import Blueprint

from flask import render_template, url_for, redirect, flash, request, abort, session,\
    Response, current_app, send_from_directory
import os
from app_package.datatools.cage_search.utils import makeSearchExactDict, \
    searchQueryCageToDf, cageExcelObjUtil
# from app_package.datatools.cage_search.forms import CageForm
import logging
from app_package.utils import logs_dir
from logging.handlers import RotatingFileHandler
import json


#Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_cage = logging.getLogger(__name__)
logger_cage.setLevel(logging.DEBUG)
logger_terminal = logging.getLogger('terminal logger')
logger_terminal.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(logs_dir,'cage.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

logger_terminal.handlers.clear()
logger_cage.handlers.clear()
logger_cage.addHandler(file_handler)
logger_terminal.addHandler(stream_handler)
#End set up logger

datatools_cage = Blueprint('datatools_cage', __name__)

    
@datatools_cage.route('/cageCodeSearch',methods=['POST','GET'])
def cageCodeSearch():
    logger_terminal.info(f'***Enter cageCodeSearch***')

    siteTitle='CAGE Code Lookup'
    searchDictClean={'companyName':'Company Name', 'companyNameSub':'Company Name (Subsidiary)','cageCode': 'CAGE Code',
        'address': 'Address', 'city': 'City', 'state': 'State'}
    if request.args.get('searchStringDict'):
        ## Add all the variables we passed to local vars
        searchStringDict=json.loads(request.args.get('searchStringDict'))
        exactDict=json.loads(request.args.get('exactDict'))
        searchDictClean=json.loads(request.args.get('searchDictClean'))
        dfResults=request.args.get('dfResults')
        formDict_passed = json.loads(request.args.get('formDict_passed'))

        df=searchQueryCageToDf(formDict_passed)
        columnNames = df.columns
        dfResults = df.to_dict('records')
        resultsCount = len(df)

    if request.method=="POST":
        logger_cage.info(f'CAGE POST request made')
        formDict = request.form.to_dict()

        #re-Key searchStringDict for webpage
        searchDictClean={'companyName':'Company Name', 'companyNameSub':'Company Name (Subsidiary)','cageCode': 'CAGE Code',
            'address': 'Address', 'city': 'City', 'state': 'State'}

        # logger_terminal.debug(f'formDict:::{formDict}')
        if formDict.get('clearButton'):
            return redirect(url_for('datatools_cage.cageCodeSearch'))

        if formDict.get('searchCage')=='search':
            #two types of Dictionaries: one for words containing(searchStringDict) and exact matches (exactDict)
            searchStringDict,exactDict = makeSearchExactDict(formDict)

            #search key words
            searchStringDict={searchDictClean[i]:j for i,j in searchStringDict.items()}
            #dict with value = checked if search string requested to be exact
            exactDict={searchDictClean[i]:j for i,j in exactDict.items()}

            #check for a blank search criteria
            count=0
            for i in searchStringDict.values():
                count=count + len(i)
            if count<2:
                flash(f'Query too broad. Must enter at least two search characters to narrow search.', 'warning')
                return redirect(url_for('datatools_cage.cageCodeSearch'))

            df=searchQueryCageToDf(formDict)
            resultsCount = len(df)
            if resultsCount>10000:
                flash(f'Query beyond 10,000 row limit. Must enter more search criteria to narrow search.', 'warning')
                return redirect(url_for('datatools_cage.cageCodeSearch'))
        
            columnNames = df.columns
            dfResults = df.to_dict('records')
            
            return redirect(url_for('datatools_cage.cageCodeSearch', siteTitle=siteTitle, columnNames=columnNames, dfResults=dfResults,
                len=len, searchStringDict=json.dumps(searchStringDict), exactDict=json.dumps(exactDict), searchDictClean=json.dumps(searchDictClean),
                resultsCount='{:,}'.format(resultsCount), formDict_passed=json.dumps(formDict)))

        if formDict.get('searchCage')=='download':

            if not os.path.exists(os.path.join(current_app.static_folder, 'utility_cage')):
                os.makedirs(os.path.join(current_app.static_folder, 'utility_cage'))
            filePathAndName=os.path.join(current_app.static_folder, 'utility_cage','CAGE_SearchResults.xlsx')
            excelObj=cageExcelObjUtil(filePathAndName,df)
            excelObj.close()
            return send_from_directory(os.path.join(current_app.static_folder, 'utility_cage'),'CAGE_SearchResults.xlsx', as_attachment=True)
    
    if request.args.get('searchStringDict'):
        return render_template('datatools/cageCodeSearch.html', siteTitle=siteTitle, columnNames=columnNames, dfResults=dfResults,
                len=len, searchStringDict=searchStringDict, exactDict=exactDict, searchDictClean=searchDictClean,
                resultsCount='{:,}'.format(resultsCount))
    else:
        return render_template('datatools/cageCodeSearch.html', siteTitle=siteTitle, searchDictClean=searchDictClean, len=len)
