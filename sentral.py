import requests
import xlrd
import numpy as np
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup
import json
import re
import csv
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import math
from urllib.parse import quote


class Truancy_period:
    def __init__(self, period, class_name, teacher, details, code):
        self.period = period
        self.class_name = class_name
        self.teacher = teacher
        self.details = details
        self.code = code
        pass
    pass

def xls2npArray(xls):
    array = []
    names = []
    for col in range(0,xls.ncols):
        names.append( xls.cell_value(0, col) )
    for row in range(1,xls.nrows):
        temp_dict = {}
        #print(xls.cell_value(row, col))
        for col in range(0,xls.ncols):
            if xls.cell_value(row, col) == None:
                temp_dict[names[col]] = ''
            else:
                temp_dict[names[col]] = xls.cell_value(row, col)
        array.append( temp_dict )
    return array
    pass


#WILDLY INCONSISTENT
"""
def xls2npArray(xls):
    array = []
    names = []
    for col in range(0,xls.ncols):
        names.append( xls.cell_value(0, col) )
    for row in range(1,xls.nrows):
        temp_dict = {}
        for col in range(0,xls.ncols):
            temp_dict[names[col]] = xls.cell_value(row, col)
        array.append( temp_dict )
    return array
    pass
"""

def csv2dictArray(csv_string):
    return [{k: v for k, v in row.items()}
        for row in csv.DictReader(csv_string.splitlines(), skipinitialspace=True)]
    '''in_val = 0
    print(csv_string)
    for row in csv.DictReader(csv_string.splitlines(), skipinitialspace=True):
        print(in_val)
        in_val+=1'''
    '''data = csv.split('\n')
    array = []
    headings = data[0].split(',')
    for d in range(1,len(data) ):
        temp_dict = {}
        for i in headings:
            temp_dict[headings[i]] = data[d].split(',')
        array.append( temp_dict )
    return array'''
    pass


#Reports

class Reports_Setup:
    def __init__(self):
        pass

    def get_all_banks(self):
        
        r = session.get(server+"reports/setup/commentbanks/manage")
        if True:
            soup = BeautifulSoup(r.content,features="lxml")
            cb = soup.find("div", {"id": "layout-2col-content"} )
            xml_i = cb.find("table",{"class": "table table-striped"}).findAll('a')
            bank_ids = []
            banks = []
            
            for i in xml_i:
                #print()
                if parse_qs(urlparse(i.get('href')).query)['id'][0] not in bank_ids:
                    bank_ids.append( parse_qs(urlparse(i.get('href')).query)['id'][0] )

            for b_id in bank_ids:
                r = session.get(server+"reports/setup/commentbanks/manage?action=exportComments&id="+b_id)
                content = bytes()
                if r.status_code == 200:
                    with open("bank"+b_id+".csv", 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk: # filter out keep-alive new chunks
                                content += chunk
                                f.write(chunk)
                    f.close()
                file = open("bank"+b_id+".csv","r")
                banks.append(content.decode("utf-8"))
                file.close()
                """csv_reader = csv.reader(file, skipinitialspace=True)
                line = 0
                for row in csv_reader:
                    #print(row)
                    if line > 0:
                        print(row[1])
                        comments.append( row[1] )
                        line+=1
                    else:
                        line+=1
                    pass
                break"""
        return banks
        pass
        #get comment banks
        #id layout-2col-content
        #table table table-striped
        #manage
        #for each link

class Reports:
    def __init__(self):
        self.setup = Reports_Setup()
        pass

    def get_all_reporting_periods(self):
        #https://moruya-h.sentral.com.au/reports/change_reporting_period
        pass

    def get_active_reporting_periods(self):
        #rp-change-link > parent > 2 > 1 > 0 > at ul here
        pass

    def get_overall_assessment_raw(self):
        #https://moruya-h.sentral.com.au/reports/export/overall_assessment
        pass

    def get_overall_assessment(self):
        #https://moruya-h.sentral.com.au/reports/export/overall_assessment
        pass
    
    def get_student_outcomes_raw(self):
        #https://moruya-h.sentral.com.au/reports/export/outcomes
        r = session.get(server+"reports/71/export/outcomes")
        content = bytes()
        if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
        return xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        pass

    def get_student_outcomes(self):
        #https://moruya-h.sentral.com.au/reports/export/outcomes
        return xls2npArray(self.get_student_outcomes_raw())
        pass
    
    def get_attitudes_to_learning(self):
        #https://moruya-h.sentral.com.au/reports/export/attitudes
        return xls2npArray(self.get_attitudes_to_learning_raw())
        pass

    def get_attitudes_to_learning_raw(self):
        #https://moruya-h.sentral.com.au/reports/export/attitudes
        r = session.get(server+"reports/export/attitudes")
        content = bytes()
        if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
        return xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        pass

# Attendance

class Attendance_Administration:
    def __init__(self):
        pass

    def export_alaysis_data(self,year="2024",school_years=["7","8","9","10","11","12"],action="exportAttendanceSummary",ga_enabled="1"):
        #/attendance/administration/export_analysis_data
        """
        {
                "year": "2024",
                "school_years[]": [
                        "7",
                        "8",
                        "9",
                        "10",
                        "11",
                        "12"
                ],
                "action": "exportAttendanceSummary",
                "ga_enabled": "1"
        }
        """
        post_data = {
                        "year":year,
                        "school_years[]":school_years,
                        "action":action,
                        "ga_enabled":ga_enabled,
                        }
        #print(post_data)
        response_text = ""
        r = session.post(server+"attendance/administration/export_analysis_data", data= post_data, stream=True)
        for chunk in r.iter_content(chunk_size=8192):
            #print(chunk)
            response_text += chunk.decode("utf-8")
        #returns CSV
        return(response_text)
        pass

class Attendance_Reports:
    def __init__(self):
        pass

    def absencesPercentage(self,time_length="year",year=datetime.now().strftime("%Y"),start_date=datetime.now().strftime("%Y-%m-%d"),
                           end_date=datetime.now().strftime("%Y-%m-%d"),limit='no', limit_sign="moreequal",
                           limit_percent="0",reasons=["8","1","9"],group="years",
                           years=["7","8","9","10","11","12"],action="export"):
        #length=year&year=2021&limit_sign=moreequal&limit_percent=100&reasons%5B%5D=8&reasons%5B%5D=1
        #&reasons%5B%5D=9&group=years&years%5B%5D=7&years%5B%5D=8&years%5B%5D=9&years%5B%5D=10
        #&years%5B%5D=11&years%5B%5D=12&action=generate
        #/attendance/reports/percentage

        # length=period&year=2022&start_date=2022-02-07&end_date=2022-03-18&limit=yes&limit_sign=lessequal&limit_percent=85&reasons%5B%5D=8&reasons%5B%5D=1&reasons%5B%5D=7&reasons%5B%5D=5&reasons%5B%5D=3&reasons%5B%5D=9&group=years&years%5B%5D=7&years%5B%5D=8&years%5B%5D=9&years%5B%5D=10&years%5B%5D=11&years%5B%5D=12&action=export
        
        post_data = {
                        "length":time_length,
                        "year":year,
                        "start_date":start_date,
                        "end_date":end_date,
                        "limit":limit,
                        "limit_sign":limit_sign,
                        "limit_percent":limit_percent,
                        "reasons[]": reasons,
                        "group":group,
                        "years[]": years,
                        "action":action
                        }
        #print(post_data)
        r = session.post(server+"attendance/reports/percentage", 
                    data= post_data
                    )
        #returns CSV
        return(csv2dictArray(r.text))
        pass

    def absencesLists(self,date_from:datetime,date_to:datetime):
        """length=period&
        length=period&
        year=2023&start_date=2023-07-16&end_date=2023-07-27&absence_display=code&absence_types=all&reasons%5B%5D=8&
        reasons%5B%5D=1&show_inactive_students=true&group_absences=date&group=none&action=export
        """
        """
        {'length': 'period',
        'year': '2023',
        'start_date': '2023-07-12',
        'end_date': '2023-07-26',
        'absence_types': 'all',
        'absence_display': 'code', 'reasons': ['8', '1'),
        'show_inactive_students': 'true',
        'group_absences': 'date', 'group': 'none', 'action': 'export'}
        """
        post_data = {
                        "length":"period",
                        "year":"2023",
                        "start_date": date_from.strftime("%Y-%m-%d"),
                        "end_date":date_to.strftime("%Y-%m-%d"),
                        "absence_types":"all",
                        "absence_display":"code",
                        "reasons": [1,8],
                        "show_inactive_students":"true",
                        "group_absences":"date",
                        "group":"none",
                        "action":"export"
                        }
        #print(post_data)
        r = session.post(server+"attendance/reports/absences", stream=True,
                    data=post_data
                    )
        content = bytes()
        if r.status_code == 200:
            with open("temp.xls", 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
                        f.write(chunk)
            f.close()

        #sheet = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        #print(f'{sheet.ncols} x {sheet.nrows}')
        return xls2npArray( xlrd.open_workbook(file_contents=content).sheet_by_index(0) )
        pass

class Attendance:
    def __init__(self):
        self.reports = Attendance_Reports()
        self.administration = Attendance_Administration()
        pass


# Wellbeing Levels

class Wellbeing_Levels:
    def __init__(self):
        pass

    #places students on a level
    def new(self,
                    students=[],level_movement="",effective_date=None,effective_hour="",effective_minute="",
                    effective_ampm="AM",expires="never",expires_days="2", description="",action="addLevelHistory"
                ):
        start_date_string=""
        end_date_string=""
        if effective_date:
            effective_date_string = effective_date.strftime("%Y-%m-%d")
        data={
            "students[]": students,
            "level_movement": level_movement,
            "effective_date": effective_date_string,
            "effective_hour": effective_hour,
            "effective_minute": effective_minute,
            "effective_ampm": effective_ampm,
            "expires": expires,
            "expires_days": expires_days,
            "description": description,
            "action": action
        }
        print(data)
        r = session.post(server+"wellbeing/levels/new",
                data=data
                )
        print(r)
        return r


# Wellbeing Reports

class Wellbeing_Reports:
    def __init__(self):
        pass

    #returns an xls of awards
    def awards(self,
                    report_style="listing",add_filter="",date_range="thisweek",start_date=None,end_date=None,category="",award="",award_roll_class="",
                    award_class="",level="",year="",roll_class="",gender="",house="",letter_type=""
                ):
        start_date_string=""
        end_date_string=""
        if start_date:
            start_date_string = start_date.strftime("%Y-%m-%d")
        if end_date:
            end_date_string = end_date.strftime("%Y-%m-%d")
        r = session.post(server+"wellbeing/reports/awards",
                data={
                    "search-report-style": report_style,
                    "search-add-filter": add_filter,
                    "search-date-range": date_range,
                    "search-start-date": start_date_string,
                    "search-end-date": end_date_string,
                    "search-category": category,
                    "search-award": award,
                    "search-award-roll-class": award_roll_class,
                    "search-award-class": award_class,
                    "search-level": level,
                    "search-year": year,
                    "search-roll-class": roll_class,
                    "search-gender": gender,
                    "search-house": house,
                    "run-search": "Run+Search",
                    "letter_type":letter_type
                    }
                )
        print(r.url+"&export-xls")
        r = session.get(r.url+"&export-xls", stream=True)
        #print(r.text)
        content = bytes()
        if r.status_code == 200:
            #with open("temp.xls", 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
                        #f.write(chunk)
            #f.close()
        #print(content)
        return xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        #https://moruya-h.sentral.com.au/wellbeing/reports/awards
        pass

    def level_ids(self,action,option,check_string):
        
        dp_ids = set()
        xls = self.monitoring_cards(action,option)
        #print('************')
        #print('*'+action+'*'+option+'*')
        for row in range(1,xls.nrows):
            #print(xls.row(row))
            if check_string in xls.cell_value(row, 16) and xls.cell_value(row, 5) == 'Student':
                dp_ids.add(xls.cell_value(row, 0))
        #print('************')
        return dp_ids
    
    #returns an xls of awards
    #search-report-style=Overview
    #&level-restriction=all
    #&search-add-filter=
    #&search-date-range=asof
    #&search-start-date=2022-08-12
    #&search-year=
    #&search-gender=&search-roll-class=&search-level=&run-search=Run+Search&letter_type=level&letter_type=level
    def levels(self,
                    report_style="Overview",level_restriction="all",add_filter="",date_range="today",as_at="",start_date="",
                    level="",year="",roll_class="",gender="",letter_type="level"
                ):
        as_at_string=""
        if as_at:
            as_at_string = as_at.strftime("%Y-%m-%d")
        r = session.post(server+"wellbeing/reports/levels",
                data={
                    "search-report-style": report_style,
                    "level-restriction": level_restriction,
                    "search-add-filter": add_filter,
                    "search-date-range": date_range,
                    "search-start-date": start_date,
                    "search-year": year,
                    "search-gender": gender,
                    "search-roll-class": roll_class,
                    "search-level": level,
                    "run-search": "Run Search",
                    "letter_type": letter_type
                    }
                )
        #print(r.url+"&export-xls")
        r = session.get(r.url+"&export-xls", stream=True)
        #print(r.text)
        content = bytes()
        if r.status_code == 200:
            #with open("temp.xls", 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
                        #f.write(chunk)
            #f.close()
        #print(content)
        return xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        pass

    def incident_ids(self,date_from,date_to,search_category_id=""):
        ids = set()
        xls = self.incident(date_from,date_to,search_category_id=search_category_id)
        for row in range(1,xls.nrows):
            ids.add(xls.cell_value(row, 4))
        return ids

    def incident_named_values(self,date_from,date_to,search_category_id=""):
        return xls2npArray( self.incident(date_from,date_to,search_category_id=search_category_id) )

    def monitoring_card_ids(self,action,option,check_string):
        
        dp_ids = set()
        xls = self.monitoring_cards(action,option)
        #print('************')
        #print('*'+action+'*'+option+'*')
        for row in range(1,xls.nrows):
            #print(xls.row(row))
            if check_string in xls.cell_value(row, 17):
                dp_ids.add(xls.cell_value(row, 0))
        #print('************')
        return dp_ids

    def monitoring_cards(self,action,option):
        r = session.post(server+"wellbeing/reports/incidents",
                data={
                    "search-date-range":"thisyear",
                    "search-action":action,
                    "search-action-option":option,
                    "search-imported":"0",
                    "category":"incident",
                    "run-search":"Run+Search",
                    "include-duplicates":"false",
                    "letter_type":"incident",
                    "victims-witnesses":"All"
                    }
                )
        #print(r.url+"&export-xls&victims-witnesses=All")
        r = session.get(r.url+"&export-xls&victims-witnesses=All", stream=True)

        content = bytes()
        if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
        
        return xlrd.open_workbook(file_contents=content).sheet_by_index(0)

    def suspensions2(self,search_report_style="",search_add_filter="",search_date_range="current",search_category="",
                    search_type="",search_year="",search_roll_class="",search_gender="",search_returned_early="",
                    search_resolution="",run_search="Run+Search"):
        #https://moruya-h.sentral.com.au/s-dOZjOZ/wellbeing/reports/suspensions
        r = session.post(server+"wellbeing/reports/suspensions",
                data={
                    "search-report-style": search_report_style,
                    "search-add-filter": search_add_filter,
                    "search-date-range": search_date_range,
                    "search-category": search_category,
                    "search-type": search_type,
                    "search-year": search_year,
                    "search-roll-class": search_roll_class,
                    "search-gender": search_gender,
                    "search-returned-early": search_returned_early,
                    "search-resolution": search_resolution,
                    "run-search": run_search
                    }
                )
        #print(r.url+"&export-xls&victims-witnesses=All")
        r = session.get(r.url+"&export-xls", stream=True)

        content = bytes()
        if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
        
        xls = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        
        headings = []
        data = []
        for col in range(0,xls.ncols):
            headings.append( xls.cell_value(0, col) )
            
        for row in range(1,xls.nrows):
            temp_row = {}
            for col in range(0,xls.ncols):
                temp_row[ headings[col] ] = xls.cell_value(row, col)
            data.append( temp_row )
        return data
    
    def incident(self,
                 date_from,date_to,search_category_id="",search_type_id="",
                 search_report_style="", refine_tally_results="", total_on="incidents", search_add_filter="",
                 search_date_range="custom", search_start_date="", search_end_date="",
                 search_incident_detail_id="", search_incident_detail_option_id="", search_year="",
                 search_roll_class="", search_gender="", search_incident_followup_status="", search_incident_followup_extended_resolution="",
                 search_incident_naward_resolution_status="", search_imported="0", search_student_type="Student", category="incident",
                 run_search="Run+Search", include_duplicates="false", letter_type="incident", victims_witnesses="All"):
        r = session.post(server+"wellbeing/reports/incidents",
                data={
                    "search-report-style": search_report_style, 
                    "refine-tally-results": refine_tally_results,
                    "total-on": total_on,
                    "search-add-filter": search_add_filter,
                    "search-date-range": search_date_range,
                    "search-start-date": date_from.strftime("%Y-%m-%d"),
                    "search-end-date": date_to.strftime("%Y-%m-%d"),
                    "search-category-id": search_category_id,
                    "search-type-id": search_type_id,
                    "search-incident-detail-id": search_incident_detail_id,
                    "search-incident-detail-option-id": search_incident_detail_option_id,
                    "search-year": search_year,
                    "search-roll-class": search_roll_class,
                    "search-gender": search_gender,
                    "search-incident-followup-status": search_incident_followup_status, 
                    "search-incident-followup-extended-resolution": search_incident_followup_extended_resolution,
                    "search-incident-naward-resolution-status": search_incident_naward_resolution_status,
                    "search-imported": search_imported,
                    "search-student-type": search_student_type,
                    "category": category,
                    "run-search": run_search,
                    "include-duplicates": include_duplicates,
                    "letter_type": letter_type,
                    "victims-witnesses": victims_witnesses
                    }
                )
        print(r.url+"&export-xls&victims-witnesses="+victims_witnesses)
        r = session.get(r.url+"&export-xls&victims-witnesses="+victims_witnesses, stream=True)
        #print(r.text)
        content = bytes()
        if r.status_code == 200:
            #with open("temp.xls", 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
                        #f.write(chunk)
            #f.close()
        return xlrd.open_workbook(file_contents=content).sheet_by_index(0)

    def incidents(self,
                 date_from: datetime.date,date_to: datetime.date,search_category_id="",search_type_id="",
                 search_report_style="", refine_tally_results="", total_on="incidents", search_add_filter="",
                 search_date_range="custom", search_start_date="", search_end_date="",
                 search_incident_detail_id="", search_incident_detail_option_id="", search_year="",
                 search_roll_class="", search_gender="", search_incident_followup_status="", search_incident_followup_extended_resolution="",
                 search_incident_naward_resolution_status="", search_imported="0", search_student_type="Student", category="incident",
                 run_search="Run+Search", include_duplicates="false", letter_type="incident", victims_witnesses="All"):
        r = session.post(server+"wellbeing/reports/incidents",
                data={
                    "search-report-style": search_report_style, 
                    "refine-tally-results": refine_tally_results,
                    "total-on": total_on,
                    "search-add-filter": search_add_filter,
                    "search-date-range": search_date_range,
                    "search-start-date": date_from.strftime("%Y-%m-%d"),
                    "search-end-date": date_to.strftime("%Y-%m-%d"),
                    "search-category-id": search_category_id,
                    "search-type-id": search_type_id,
                    "search-incident-detail-id": search_incident_detail_id,
                    "search-incident-detail-option-id": search_incident_detail_option_id,
                    "search-year": search_year,
                    "search-roll-class": search_roll_class,
                    "search-gender": search_gender,
                    "search-incident-followup-status": search_incident_followup_status, 
                    "search-incident-followup-extended-resolution": search_incident_followup_extended_resolution,
                    "search-incident-naward-resolution-status": search_incident_naward_resolution_status,
                    "search-imported": search_imported,
                    "search-student-type": search_student_type,
                    "category": category,
                    "run-search": run_search,
                    "include-duplicates": include_duplicates,
                    "letter_type": letter_type,
                    "victims-witnesses": victims_witnesses
                    }
                )
        print(r.url+"&export-xls&victims-witnesses="+victims_witnesses)
        r = session.get(r.url+"&export-xls&victims-witnesses="+victims_witnesses, stream=True)
        output=[]
        #print(content)
        xls = xlrd.open_workbook(file_contents=r.content).sheet_by_index(0)
        #print(xls)
        #print('************')
        #print('*'+action+'*'+option+'*')
        #for row in range(1,xls.nrows):
        #    print(xls.row(row))
        #print('************')
        #sh = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        output_data = []
        for rownum in range(xls.nrows):
            #print( xls.row_values(rownum) )
            row_data = []
            for colnum in range(xls.ncols):
                row_data.append( xls.cell_value(rownum,colnum))
            output_data.append(row_data)
            #output.append( sh.row_values(rownum) )
        
        return output_data


    def suspensions(self,report_id=''):
        r = session.post(server+"wellbeing/reports/suspensions?report_id="+str(report_id) )
        print(r.url+"&export-xls")
        r = session.get(r.url+"&export-xls", stream=True)
        #print(r.text)
        content = bytes()
        if r.status_code == 200:
            #with open("temp.xls", 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk
                        #f.write(chunk)
            #f.close()
        xls = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        output_data = []
        for rownum in range(xls.nrows):
            #print( xls.row_values(rownum) )
            row_data = []
            for colnum in range(xls.ncols):
                row_data.append( xls.cell_value(rownum,colnum))
            output_data.append(row_data)
            #output.append( sh.row_values(rownum) )
        
        return output_data

    def suspension_names(self,report_id=""):
        suspensions = []
        xls = self.suspensions(report_id=report_id)
        for row in range(1,len(xls)):
            #print(xls.cell_value(row, 2),xls.cell_value(row, 1),xls.cell_value(row, 6),xls.cell_value(row, 9),xls.cell_value(row, 10))
            if "No" in xls[row][9]:
                if 'Suspension' in xls[row][6]:
                    suspensions.append(xls[row][2]+ ' ' + xls[row][1])
        return suspensions
    
    def suspension_names_old(self,report_id=""):
        suspensions = []
        xls = self.suspensions(report_id=report_id)
        for row in range(1,xls):
            #print(xls.cell_value(row, 2),xls.cell_value(row, 1),xls.cell_value(row, 6),xls.cell_value(row, 9),xls.cell_value(row, 10))
            if "No" in xls.cell_value(row, 9):
                if 'Suspension' in xls.cell_value(row, 6):
                    suspensions.append(xls.cell_value(row, 2)+ ' ' + xls.cell_value(row, 1))
        return suspensions

    def OLD_suspension_names(self,report_id=""):
        suspensions = {'short':[],'long':[]}
        xls = self.suspensions(report_id=report_id)
        for row in range(1,xls.nrows):
            #print(xls.cell_value(row, 2),xls.cell_value(row, 1),xls.cell_value(row, 6),xls.cell_value(row, 9),xls.cell_value(row, 10))
            if "No" in xls.cell_value(row, 9):
                if 'Long Suspension:' in xls.cell_value(row, 6):
                    suspensions['long'].append(xls.cell_value(row, 2)+ ' ' + xls.cell_value(row, 1))
                elif  'Short Suspension:' in xls.cell_value(row, 6):
                    suspensions['short'].append(xls.cell_value(row, 2)+ ' ' + xls.cell_value(row, 1))
        return suspensions
        
        #/reports/incidents?report_id=2981&export-xls
        #run report
        #get id
        #export to excel
        """
        https://web1.moruya-h.schools.nsw.edu.au/wellbeing/reports/incidents?report_id=3201&export-xls&victims-witnesses=All
        """
    
        '''
        search-report-style	
        refine-tally-results	
        total-on	incidents
        search-add-filter	
        search-date-range	custom
        search-start-date	2019-02-04
        search-end-date	2019-02-10
        search-category-id	
        search-type-id	
        search-incident-detail-id	
        search-incident-detail-option-id	
        search-year	
        search-roll-class	
        search-gender	
        search-incident-followup-status	
        search-incident-followup-extended-resolution	
        search-incident-naward-resolution-status	
        search-imported	0
        category	incident
        run-search	Run+Search
        include-duplicates	false
        letter_type	incident
        victims-witnesses	All
        '''
        pass

#class Wellbeing

class Wellbeing:
    def __init__(self):
        self.reports = Wellbeing_Reports()
        self.levels = Wellbeing_Levels()
        pass

    def new_incident(self,itype):
        r = session.get(server+"wellbeing/incidents/edit?type="+itype)
        key = parse_qs(urlparse(r.url).query)['key'][0]
        r = session.get(server+"wellbeing/incidents/edit?key="+key)
        return key
        pass

    def view_incident(self,id):
        r = session.get(server+"wellbeing/incidents/view?id="+str(int(id)) )
        return r
        pass

    def get_incident_edit_key(self,incident_id):
        r = session.get(server+"wellbeing/incidents/edit?id="+str(int(incident_id)) )
        return parse_qs(urlparse(r.url).query)['key'][0]
        pass

    def open_save_incident(self,incident_id,overwrite_values={}):
        key = self.get_incident_edit_key(incident_id)
        r = self.post_incident_edit(key,overwrite_values)
        if "edit?key=" in r.url:
            soup = BeautifulSoup(r.content,features="lxml")
            cb = soup.find("div", {"class": "content-wrap"} )
            xml_i = cb.find("form").findAll('input')
            inputs = {}
            for i in xml_i:
                if i.get('name') and "[]" in i.get('name'):
                    if i.get('name') not in inputs:
                        inputs[i.get('name')] = []
                    inputs[i.get('name')].append( i.get('value') )
                else:
                    inputs[i.get('name')] = i.get('value')
            r = session.post(server+"wellbeing/incidents/edit?key="+key,data=inputs )
        pass

    def award_awards(self,key,sentral_ids):
        student_dict = {}
        for s_id in sentral_ids:
            student_dict["student-records["+s_id+"]"] = "key-1"
            student_dict["student-followups["+s_id+"]"] = "key-1"
        params = {
            "key":key,
            "action":"save",
            "confirm_followups":"true"
        }
        params = {**params, **student_dict}
        #r = session.post(server+"wellbeing/incidents/edit?key="+key,
        #        data = params
        #        )
        #print( params )
        pass

    def make_unifrom_incident(self,date,incident_Students):
        key = self.new_incident("63")
        extra_keys = {}
        students = []
        student_names = []
        formatted_date = date.strftime("%Y-%m-%d")
        for stu in incident_Students:
            if stu['sentral_id'] in students:
                continue
            session.post(server+"wellbeing/incidents/edit",
                    data = {
                        "action":"addIncidentStudent",
                        "id":stu['sentral_id'],
                        "incident":key,
                        "record":"key-1",
                        "followup":"key-1"
                        }
                    )
            students.append( stu['sentral_id'] )
            student_names.append( stu['given_name']+"+"+stu['family_name'] )
            extra_keys["student-types[" + str(stu['sentral_id']) +"]" ] = "Student"
            extra_keys["student-records[" + str(stu['sentral_id']) +"]" ] = "key-1"
            extra_keys["student-followups[" + str(stu['sentral_id']) +"]" ] = "key-1"

        data = {
                "students[]":students,
                "student_names[]":student_names,
                "date":formatted_date,
                "period":"25",
                "teacher":"246",
                "location":"30",
                "subject":"79",
                "share_records":"true",
                "record_details[211]":"211",
                "record_details[212]":"212",
                "record_detail_options[212][643]":"false",
                "record_detail_options[212][644]":"false",
                "record_detail_options[212][645]":"false",
                "record_detail_options[212][646]":"false",
                "record_detail_options[212][660]":"false",
                "record_detail_options[212][647]":"false",
                "record_detail_options[212][648]":"false",
                "record_detail_options[212][649]":"false",
                "record_detail_options[212][650]":"false",
                "record_detail_options[212][651]":"false",
                "record_detail_options[212][652]":"false",
                "record_detail_options[212][653]":"false",
                "record_detail_options[212][654]":"false",
                "record_detail_options[212][655]":"false",
                "record_detail_options[212][656]":"false",
                "record_detail_options[212][657]":"false",
                "record_detail_options[212][658]":"false",
                "record_detail_options[212][659]":"false",
                "record_detail_options[212][665]":"true",
                "record_description":"Out of uniform",
                "record_key":"key-1",
                "share_followups":"true",
                "followup_action_options[53][88]":"false",
                "followup_action_options[53][89]":"false",
                "followup_action_options[53][91]":"false",
                "followup_action_options[53][90]":"false",
                "followup_action_options[53][92]":"false",
                "followup_action_options[53][93]":"false",
                "followup_actions[39]":"",
                "followup_comment":"Out of uniform",
                "status":"Completed",
                "followup_key":"key-1"
                
            }
        params = {**data, **extra_keys}
        params["id"] = "0"
        params["key"] = key
        params["action"] ="save"
        return session.post(server+"wellbeing/incidents/edit?key="+key,
                    data = params)
        pass

    def post_incident_edit(self,key,overwrite_values={}):
        r = session.get( server+"wellbeing/incidents/edit?key="+key )
        #print(r.content)
        soup = BeautifulSoup(r.content,features="lxml")
        cb = soup.find("div", {"class": "content-block"} )
        xml_i = cb.find("form").findAll(['input','textarea','select'])
        inputs = {}
        for i in xml_i:
            if i.name == 'input':
                if "[]" in i.get('name'):
                    if i.get('name') not in inputs:
                        inputs[i.get('name')] = set()
                    inputs[i.get('name')].add( i.get('value') )
                        
                else:
                    inputs[i.get('name')] = i.get('value')
            elif i.name =='textarea':
                if i and i.contents:
                    inputs[i.get('name')] = i.contents[0]
                else:
                    inputs[i.get('name')] = ""
            elif i.name =='select':
                s = i.findAll('option', selected=True)
                if s:
                    inputs[i.get('name')] = s[0].get('value')

        for v in overwrite_values:
            inputs[v] = overwrite_values[v]
        session.headers.update({'Referer': server+"wellbeing/incidents/edit?key="+key})
        return session.post( server+"wellbeing/incidents/edit?key="+key, data=inputs )
        pass
        

    def incident_add_student(self,id, key):
        session.post(server+"wellbeing/incidents/edit",
                data={
                    "action":"addIncidentStudent",
                    "id":id,
                    "incident":key,
                    "record":"key-2",
                    "followup":"key-2"
                    }
                )
        pass

    def post_incident_edit_confirm_followup(self,key):
        r = post_incident_edit(key)
        #get inputs
        #post
        pass

    def incident_edit(id):
        r = session.post(server+"wellbeing/incidents/edit",
                data={
                    "id":id
                    }
                )
        #print(r.headers)
        #print(r.url)
        pass

    def incident_remove_student(id, key):
        session.post(server+"wellbeing/incidents/edit",
                data={
                    "action":"addIncidentStudent",
                    "id":id,
                    "incident":key,
                    "record":"key-2",
                    "followup":"key-2"
                    }
                )
        pass

#class pxp

class Pxp_Administration:
    def __init__(self):
        pass

    def roll_marking_report(self,date):
        f_date = date.strftime('%Y-%m-%d')
        #print(f_date)
        r = session.get(server+f"attendancepxp/period/administration/roll_report?campus_id=&teacher_name=1&class_name=1&unsubmitted_only=1&range=single_day&date={f_date}&start_date={f_date}&end_date={f_date}&export=1")
        #print(r.content)
        
        if r.text.startswith('<'):
            output=[]
        else:
            output = csv2dictArray(r.text)

        return output
        pass

    def roll_marking_report2(self,teacher_name='0',teacher_id='0',class_name='0',room_name='0',unsubmitted_only='0',
                             date_range="date_range",date_date=datetime.now(),start_date=datetime.now(),end_date=datetime.now()):
        r = session.get(f"{server}attendancepxp/period/administration/roll_report",
                params={
                    "campus_id":"",
                    "teacher_name":teacher_name,
                    "teacher_id":teacher_id,
                    "class_name":class_name,
                    "room_name":room_name,
                    "unsubmitted_only":unsubmitted_only,
                    "range":date_range,
                    "date":date_date.strftime('%Y-%m-%d'),
                    "start_date":start_date.strftime('%Y-%m-%d'),
                    "end_date":end_date.strftime('%Y-%m-%d'),
                    "export":"1"
                    }
                )
        if r.text.startswith('<'):
            output=[]
        else:
            output = csv2dictArray(r.text)

        return output
        pass
    
    def truancy_wizard(self,search_filter="",search_class="all",year="all",house="all",search_range="range",
        start_date="",end_date="",action="report"):
        #r = session.post(server+"wellbeing/reports/incidents",
                
        # gender Student	Date	WebAttend		0	R	1	2	R	3	4	L	L	5	6	B
        #https://moruya-h.sentral.com.au/attendancepxp/period/administration/truancy_report?filter=&class=all&year=all&house=all&range=range&start_date=2020-08-24&end_date=2020-08-24&action=report
        #https://moruya-h.sentral.com.au/attendancepxp/period/administration/truancy/unsorted?filter=&class=all&year=all&house=all&range=last+week&start_date=2020-01-01&end_date=2020-12-31&action=report
        #r = session.get(server+"attendancepxp/period/administration/truancy/unsorted?filter=&class=all&year=all&house=all&range=range&start_date=2020-08-20&end_date=2020-08-20&action=report")
        r = session.get(server+"attendancepxp/period/administration/truancy/unsorted",
        data={
                    "filter": search_filter, 
                    "class": search_class,
                    "year": year,
                    "house": house,
                    "range": search_range,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "action": action
                    })
        #print(r.text)
        if True:
            soup = BeautifulSoup(r.content,features="lxml")
            cb = soup.find("div", {"id": "layout-2col-content"} )
            #print(cb)
            xml_i = cb.find("table",{"class": "pxp-roll truancy-wizard"}).findAll('tr')
            dates = {}
            output_data=[]

            
            for row in range(1,len(xml_i)):
                tds = xml_i[row].find_all("td")
                if len(tds) > 0:
                    
                    #print(tds[2].text.strip())
                    #Thu, 20 August, 2020
                    data=[]
                    try:
                        datestring = datetime.strptime(tds[2].text, '%a, %d %B, %Y')
                        data=[tds[1].text.strip().split("\n")[0],datestring,tds[3].text.strip(),Truancy_period(1,"classname","teacher",tds[7].text.strip(),"code"),tds[7].text.strip(),tds[9].text.strip(),tds[10].text.strip(),tds[3].text.strip(),tds[14].text.strip()]
                        print(tds[7].children[0])
                        #Truancy_period()
                        output_data.append(data)
                        #datestring = datetime.strptime(tds[2].text, '%a, %d %B, %Y')
                        #print( datestring.strftime("%Y-%m-%d").strip() )
                    except ValueError:
                        d = None
                #if parse_qs(urlparse(i.get('href')).query)['id'][0] not in bank_ids:
                #    bank_ids.append( parse_qs(urlparse(i.get('href')).query)['id'][0] )

            '''for b_id in bank_ids:
                r = session.get(server+"reports/setup/commentbanks/manage?action=exportComments&id="+b_id)
                content = bytes()
                if r.status_code == 200:
                    with open("bank"+b_id+".csv", 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk: # filter out keep-alive new chunks
                                content += chunk
                                f.write(chunk)
                    f.close()
                file = open("bank"+b_id+".csv","r")
                banks.append(content.decode("utf-8"))
                file.close()
                
                csv_reader = csv.reader(file, skipinitialspace=True)
                line = 0
                for row in csv_reader:
                    #print(row)
                    if line > 0:
                        print(row[1])
                        comments.append( row[1] )
                        line+=1
                    else:
                        line+=1
                    pass
                break
            '''
        return output_data
        pass
    def uniform_report_tally(self,time_filter="today"):
        r = session.post(server+"attendancepxp/period/administration/additional_information_report?tab=tally&time_filter="+time_filter+"&year_filter=all&class_filter=all&order_filter=surname&show_filter=submitter&teacher_filter=all&term_filter=all&action=exportResults",
                stream=True,
                data = {
                        "show_filter":"submitter",
                        "order_filter":"surname",
                        "year_filter":"all",
                        "class_filter":"all",
                        "teacher_filter":"all",
                        "term_filter":"all",
                        "time_filter":time_filter,
                        "action":"exportResults",
                        "tab":"details"
                    }
                )
        #r = session.get(r.url+"&export-xls&victims-witnesses=All", stream=True)
        print(r)
        print('======')
        '''content = bytes()
        if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        content += chunk'''
        #content #
        output=[]
        #print(content)
        xls = xlrd.open_workbook(file_contents=r.content,ignore_workbook_corruption=True).sheet_by_index(0)
        #print(xls)
        #print('************')
        #print('*'+action+'*'+option+'*')
        #for row in range(1,xls.nrows):
        #    print(xls.row(row))
        #print('************')
        #sh = xlrd.open_workbook(file_contents=content).sheet_by_index(0)
        output_data = []
        for rownum in range(xls.nrows):
            #print( xls.row_values(rownum) )
            row_data = []
            for colnum in range(xls.ncols):
                row_data.append( xls.cell_value(rownum,colnum))
            output_data.append(row_data)
            #output.append( sh.row_values(rownum) )
        
        return output_data

    def uniform_report_tally2(self,time_filter="today"):
        r = session.get(server+"attendancepxp/period/administration/additional_information_report?tab=tally&time_filter="+time_filter+"&year_filter=all&class_filter=all&order_filter=surname&show_filter=submitter&teacher_filter=all&term_filter=all",
                stream=True,
                data = {
                        "show_filter":"submitter",
                        "order_filter":"surname",
                        "year_filter":"all",
                        "class_filter":"all",
                        "teacher_filter":"all",
                        "term_filter":"all",
                        "time_filter":time_filter,
                        "action":"exportResults",
                        "tab":"details"
                    }
                )
        soup = BeautifulSoup(r.content,features="lxml")
        #print(soup)
        rows = soup.find("table", {"class": "report stretch"} ).find("tbody").find_all("tr")
        students = {}
        for row in rows:
            tds = row.find_all("td")
            a = tds[1].find("a")
            sid = str( a.get("href")[a.get("href").rfind("/")+1:] )
            if sid in students:
                student = students[sid]
            else:
                student = {'sentral_id':sid}
                student['given_name'] = a.getText()
                student['family_name'] = tds[2].find("a").getText()
                student['period'] = tds[5].getText().split(',')
                students[sid] = student
                
            
            #if date in dates:
            #    if student['sentral_id'] in dates[date]:
            #        dates[date][ student['sentral_id'] ]['incidents'] = dates[date][ student['sentral_id'] ]['incidents']+1
            #    else:
            #        dates[date][ student['sentral_id'] ] = student
            #else:
            #    dates[date] = {}
            #    dates[date][ student['sentral_id'] ] = student
        return students
        pass

    def uniform_report(self,time_filter="today"):
        r = session.get(server+"attendancepxp/period/administration/additional_information_report?tab=details&time_filter="+time_filter+"&year_filter=all&class_filter=all&order_filter=surname&show_filter=submitter&teacher_filter=all&term_filter=all",
                stream=True,
                data = {
                        "show_filter":"submitter",
                        "order_filter":"surname",
                        "year_filter":"all",
                        "class_filter":"all",
                        "teacher_filter":"all",
                        "term_filter":"all",
                        "time_filter":time_filter,
                        "action":"exportResults",
                        "tab":"details"
                    }
                )
        soup = BeautifulSoup(r.content,features="lxml")
        rows = soup.find("table", {"class": "report stretch"} ).find("tbody").find_all("tr")
        dates = {}
        for row in rows:
            student={}
            tds = row.find_all("td")
            a = tds[1].find("a")
            student['sentral_id'] = str( a.get("href")[a.get("href").rfind("/")+1:] )
            student['given_name'] = a.getText()
            student['incidents'] = 1
            student['family_name'] = tds[2].find("a").getText()
            date = datetime.strptime(   tds[3].getText().split(' ')[1], "%d/%m/%Y" )
            if date in dates:
                if student['sentral_id'] in dates[date]:
                    dates[date][ student['sentral_id'] ]['incidents'] = dates[date][ student['sentral_id'] ]['incidents']+1
                else:
                    dates[date][ student['sentral_id'] ] = student
            else:
                dates[date] = {}
                dates[date][ student['sentral_id'] ] = student
        return dates
        pass
    
class Pxp:
    def __init__(self):
        self.administration = Pxp_Administration()
        pass

#class profiles
class Profiles_Setup:
    def __init__(self):
        pass

    def manage_students_flags(self,include_exclude="include",students=[],bulk_note="",flag_id="",action="saveStudents"):
        r = session.post(server+f"profiles/setup/manage_students_flags?flag_id={flag_id}",
                data={
                    "include_exclude" : include_exclude,
                    "students[]" : students,
                    "bulk_note": bulk_note,
                    "flag_id": flag_id,
                    "action": action
                }
            )
        return r
        """
https://moruya-h.sentral.com.au/s-dOZjOZ/profiles/setup/manage_students_flags?flag_id=74
include_exclude	"include"
students[]	[…]
0	"4046"
1	"3881"
2	"3879"
bulk_note	""
flag_id	"74"
action	"saveStudents"
"""
        pass
        

class Profiles:
    def __init__(self):
        self.setup = Profiles_Setup()
        pass

    #https://moruya-h.sentral.com.au/s-dOZjOZ/profiles/main/search?eduproq=&search=advanced&plan_type=plans&selectFlags=on&flag=52

    def search_flag(self, flag_id):
        r = session.get(server+"profiles/main/search?eduproq=&search=advanced&plan_type=plans&selectFlags=on&flag="+str(flag_id) )
        soup = BeautifulSoup(r.content,features="lxml")
        out = []
        table = soup.find("table", {"class": "table table-striped table-condensed table-hover"} )
        if table:
            rows = table.find("tbody").find_all("tr")
           
            for row in rows:
                href=row.find_all("td")[0].find("a").get("href")
                out.append( href[href.find("students/")+9:href.find("/student-summary")] )
            #table table-striped table-condensed table-hover
            #return list of student profile ids
        return out
        pass

    def search_flag_get_names(self, flag_id):
        r = session.get(server+"profiles/main/search?eduproq=&search=advanced&plan_type=plans&selectFlags=on&flag="+flag_id )
        soup = BeautifulSoup(r.content,features="lxml")
        out = []
        table = soup.find("table", {"class": "table table-striped table-condensed table-hover"} )
        if table:
            rows = table.find("tbody").find_all("tr")
           
            for row in rows:
                href=row.find_all("td")[0].text.strip().split(", ")
                out.append( href[1]+" "+ href[0].title() )
            #table table-striped table-condensed table-hover
            #return list of student profile ids
        return out
        pass

    def student_profile(self,student_id):
        r = session.get( server+"profiles/students/"+student_id )
        pass

    def get_student_id(self, doe_id):
        r = session.get( server+'profiles/ajax/searchStudent?query='+doe_id+'&search_inactive=false' )
        if r :
            return json.loads(r.text)['results'][0]['id']
        pass

    
    def get_student_flags(self,student_id):
        r = session.get( server+"profiles/dialogs/student_flags?student_id="+str(student_id) )
        soup = BeautifulSoup(r.content,features="lxml")
        table = soup.find("table", {"id": "student-flags-table"} )
        divs = table.findAll('div', {"class": "btn-group pull-right"})
        out=[]
        for d in divs:
            #print( d.parent )
            #print("-----")
            temp=[]
            temp.append( d.parent.find("input", {"name": "flag_id[]"} ).get('value') )
            temp.append( d.parent.find("input", {"name": "flag_notes[]"} ).get('value') )
            out.append(temp)
        return out
    
    def set_student_flags(self,student_id,flags):
        flag_ids = []
        flag_notes = []
        for a in flags:
            flag_ids.append( a[0] )
            flag_notes.append( a[1] )

        dd = {
                    'flag_id[]':flag_ids,
                    'flag_notes[]':flag_notes,
                    'student_id':student_id ,
                    'action':'saveFlags'
                }

        #print("set student flags")
        #print(dd)
        
        r = session.post( server+'profiles/dialogs/student_flags',
                data = dd)
        return r.content

    def remove_student_flags(self,student_id,flags):
        old_flags = self.get_student_flags(student_id)
        #print(old_flags)
        new_flags = []
        for f in old_flags:
            if f[0] not in flags:
                if f[0] not in [col[0] for col in new_flags]:
                    new_flags.append( f )
        print( student_id, "old: "+str(old_flags), "new: "+str(new_flags) )
        self.set_student_flags(student_id,new_flags)
        pass

    def add_student_flags(self,student_id,flags):
        old_flags = self.get_student_flags(student_id)
        new_flags = []
        for f in old_flags:
            if f[0] not in [row[0] for row in new_flags]:
                new_flags.append( f )
        #print(old_flags)
        for f in flags:
            if f[0] not in [row[0] for row in new_flags]:
                new_flags.append( f )
        #print( old_flags )
        return self.set_student_flags(student_id,new_flags)
        pass

class Interviews:
    def __init__(self):
        pass

    def unavailable(self, teacher_id, date_id, break_start_time:str, break_end_time:str,break_name,interview_session_id):
        r = session.post(server+f"interviews/",
        data={
                    "teacher_id":teacher_id,
                    "interview_date_id":date_id,
                    "break_start_time":break_start_time,
                    "break_end_time":break_end_time,
                    "break_name":break_name,
                    "break_id":"0",
                    "interview_session_id":interview_session_id,
                    "action":"setUnavailability"
            }
        )
        return r.text

class Admin:
    def __init__(self):
        self.settings = Admin_Settings()
        pass

class Admin_Settings:
    def __init__(self):
        pass

    

    def get_term_dates_as_dates(self,year='2024'):
        r = session.get(server+f'admin/settings/school/calendar?action=setUserTermDates&year={year}')
        soup = BeautifulSoup(r.content,features="lxml")
        return_dict = {}
        for i in range(1,5):
            #print(f"term {i}")
            #print(soup.find("input", {"id": f"term_{i}_start_date"} ))
            #print(soup.find("input", {"name": f"term_{i}_start_date"} )['data-value'])
            #print(soup.find("input", {"name": f"term_{i}_end_date"} )['data-value'])
            d_range = {'start':datetime.strptime(soup.find("input", {"name": f"term_{i}_start_date"} )['data-value'], '%Y-%m-%d'),
                       'end': datetime.strptime(soup.find("input", {"name": f"term_{i}_end_date"} )['data-value'], '%Y-%m-%d') }
            return_dict[str(i)]=d_range

        return return_dict
        pass

    def get_term_and_week(self,_date:datetime ):
        term_dates = self.get_term_dates_as_dates(_date.strftime("%Y"))
        print(term_dates)
        for term in term_dates:
            print(f"term {term}")
            if _date <= term_dates[term]['end']+timedelta(days=2) and _date >= term_dates[term]['start']:
                first_sunday = term_dates[term]['start'] - timedelta( term_dates[term]['start'].weekday() )
                return term, math.floor ( (_date-first_sunday).days / 7) + 1
                
            #term_dates[term_dates][]
        pass

    def get_term_dates(self,year='2022'):
        r = session.get(server+f'admin/settings/school/calendar?action=setUserTermDates&year={year}')
        soup = BeautifulSoup(r.content,features="lxml")
        t1_start = soup.find("input", {"name": "term_1_start_date"} )['data-value']
        t1_end = soup.find("input", {"name": "term_1_end_date"} )['data-value']
        t2_start = soup.find("input", {"name": "term_2_start_date"} )['data-value']
        t2_end = soup.find("input", {"name": "term_2_end_date"} )['data-value']
        t3_start = soup.find("input", {"name": "term_3_start_date"} )['data-value']
        t3_end = soup.find("input", {"name": "term_3_end_date"} )['data-value']
        t4_start = soup.find("input", {"name": "term_4_start_date"} )['data-value']
        t4_end = soup.find("input", {"name": "term_4_end_date"} )['data-value']
        #xml_i = cb.find("table",{"class": "table table-striped"}).findAll('a')
        #student_dict = csv2dictArray(r.text)
        #all_doe_ids = []
        #for row in student_dict:
        #    all_doe_ids.append(row['STUDENT_ID'])
        #return all_doe_ids
        return {'1':{'start':t1_start,'end':t1_end},'2':{'start':t2_start,'end':t2_end},'3':{'start':t3_start,'end':t3_end},'4':{'start':t4_start,'end':t4_end}}
        pass

    def get_users(self):
        r = session.get(server+f'admin/authentication/users_manage')
        soup = BeautifulSoup(r.content,features="lxml")
        table = soup.find("table",{"class":"report stretch"})
        rows_tags = table.findAll('tr',{"class":["row_odd","row_even"]})
        users = []
        for row_tag in rows_tags:
            
            user_data = list(row_tag.findAll('td')[1].stripped_strings)
            #print(user_data)
            if len(user_data) <=2:
                continue
            name = user_data[0][max(user_data[0].find(' '),0):].strip() +' '+ user_data[1].strip()
            title=''
            email = ""
            teacher_id=""
            id_data = list(row_tag.findAll('td')[3].stripped_strings)
            if len(id_data) >= 2:
                teacher_id = id_data[1]
            if len(user_data)>= 3:
                email = user_data[2]
            user={"title":title,"name":name,"email":email,"teacher_id":teacher_id}
            #print(user)
            users.append(user)
        return users
        #student_dict = csv2dictArray(r.text)
        #all_doe_ids = []
        #for row in student_dict:
        #    all_doe_ids.append(row['STUDENT_ID'])
        #return all_doe_ids
        pass    

class Enquiry:
    def __init__(self):
        self.reports = Enquiry_Reports()
        self.exports = Enquiry_Exports()
        pass

class Enquiry_Exports:
    def __init__(self):
        pass

    def all_doe_ids(self):
        r = session.get(server+"enquiry/export/view_export?name=student&inputs[class]=&inputs[roll_class]=&inputs[schyear]=&format=csv&headings=1&action=View")
        student_dict = csv2dictArray(r.text)
        all_doe_ids = []
        for row in student_dict:
            all_doe_ids.append(row['STUDENT_ID'])
        return all_doe_ids
        pass

    

    #https://moruya-h.sentral.com.au/enquiry/export/view_export?name=student&inputs[class]=&inputs[roll_class]=&inputs[schyear]=&format=csv&headings=1&action=Download
    def student_information(self):
        r = session.get(server+"enquiry/export/view_export?name=student&inputs[class]=&inputs[roll_class]=&inputs[schyear]=&format=csv&headings=1&action=Download")
        student_dict = csv2dictArray(r.text)
        return student_dict
        pass

    def student_information_dict(self):
        student_dict = self.student_information()
        return_dict = {}
        for row in student_dict:
            return_dict[row['STUDENT_ID'] ] = row
        return return_dict
        pass

    def class_information(self):
        #https://moruya-h.sentral.com.au/enquiry/export/view_export?name=classes&inputs%5Btype%5D=class&format=xls&headings=1&action=Download
        r = session.get(server+"enquiry/export/view_export?name=classes&inputs[type]=class&format=csv&headings=1&action=Download")
        class_dict = csv2dictArray(r.text)
        return class_dict
        pass

    def class_information_dict(self):
        class_dict = self.class_information()
        return_dict = {}
        for row in class_dict:
            return_dict[row['CLASS_NAME'] ] = row
        return return_dict
        pass

    #https://moruya-h.sentral.com.au/enquiry/export/view_export?name=advstudent&inputs[class]=&inputs[roll_class]=&format=csv&headings=1&action=Download
    def adv_student_information(self):
        r = session.get(server+"enquiry/export/view_export?name=advstudent&inputs[class]=&inputs[roll_class]=&format=csv&headings=1&action=Download")
        student_dict = csv2dictArray(r.text)
        return student_dict
        pass

    def adv_student_information_dict(self):
        student_dict = self.adv_student_information()
        return_dict = {}
        for row in student_dict:
            return_dict[row['STUDENT_ID'] ] = row
        return return_dict
        pass

    def adv_student_information_classes_dict(self):
        student_dict = self.adv_student_information()
        return_dict = {}
        #phone numbers in class1 for some reason?
        r = re.compile(r'^(\d+ *)+$')
        for row in student_dict:
            classes = []
            class_keys = row.keys()
            for c in class_keys:
                
                if c.lower().startswith('class') and row[c] and not r.match(row[c]):
                    classes.append( row[c] )
            return_dict[row['STUDENT_ID'] ] = classes
        return return_dict
        pass

class Dashboard:
    def __init__(self):
        pass

    #https://moruya-h.sentral.com.au/dashboard/daily_notices?action=editDaily&id=281860
    #

    def post_daily_notices(self,dates=[],school_years=[],header="",body="",notice_id="",action="saveNotice",_type="DAILY"):
        r = session.post(server+"dashboard/daily_notices",
        stream=True,
        data = {
                "dates[]":dates,
                "school_years[]":school_years,
                "header":header,
                "body":body,
                "notice_id":notice_id,
                "action":action,
                "type":_type
            }
        )

    def get_daily_notices(self,date=None):
        #https://moruya-h.sentral.com.au/dashboard/daily_notices
        r = session.get(server+f"dashboard/daily_notices?date={date.strftime('%Y-%m-%d')}")

    def get_notices(self,action="loadNotices",_type="",limit_start="",oldest_first="0"):
        #https://moruya-h.sentral.com.au/dashboard/daily_notices
        r = session.get(server+f"dashboard/notices?action={action}&type={_type}&limit_start={limit_start}&oldest_first={oldest_first}")
        """
        {
	"GET": {
		"scheme": "https",
		"host": "moruya-h.sentral.com.au",
		"filename": "/dashboard/notices",
		"query": {
			"action": "loadNotices",
			"type": "unread",
			"limit_start": "10",
			"oldest_first": "0"
		},
		"remote": {
			"Address": "20.213.77.171:443"
		}
	}
}
        """

    def post_notices(self,header="",body="",notice_id="",action="saveNotice",_type="BROADCAST"):
        r = session.post(server+"dashboard/notices",
        stream=True,
        data = {
                "header":header,
                "body":body,
                "notice_id":notice_id,
                "action":action,
                "type":_type
            }
        )
        #https://moruya-h.sentral.com.au/dashboard/notices
    """
    {
	"POST": {
		"scheme": "https",
		"host": "moruya-h.sentral.com.au",
		"filename": "/dashboard/notices",
		"remote": {
			"Address": "20.213.77.171:443"
		}
	}
}

{
	"header": "subject test",
	"body": "<p>msg test</p>",
	"action": "saveNotice",
	"type": "BROADCAST"
}

{
	"GET": {
		"scheme": "https",
		"host": "moruya-h.sentral.com.au",
		"filename": "/dashboard/notices",
		"query": {
			"action": "composePost",
			"noticeAction": "edit",
			"noticeId": "281861"
		},
		"remote": {
			"Address": "20.213.77.171:443"
		}
	}
}

{
	"header": "subject test",
	"body": "<p>msg test</p>",
	"notice_id": "281861",
	"action": "saveNotice",
	"type": "BROADCAST"
}




"""

class Enquiry_Reports:
    def __init__(self):
        pass

    def all_doe_ids(self):
        r = session.get(server+"enquiry/reports/report?name=yearlist")
        #print(f"Sentral: {urlparse(r.url).query}")
        rptkey=parse_qs(urlparse(r.url).query)['rptkey'][0]

        r = session.post(server+"enquiry/reports/report.gpx",
                data={
                    "report_name":"yearlist",
                    "rptkey":rptkey,
                    "formsub":"1",
                    "inputs[years][]":[
                        " 7",
                        " 8",
                        " 9",
                        "10",
                        "11",
                        "12"
                    ],
                    "inputs[opt_student_id]":"Y",
                    "inputs[cells_display]":"Y",
                    "inputs[cells_count]":"18",
                    "inputs[cells_size]":"small",
                    "btn_generate":"Generate+Report"
                }
            )
        r = session.get(server+"oasis/reports/view_report?rptkey="+rptkey+"&sub=1")
        #print(r.content)
        soup = BeautifulSoup(r.content,features="lxml")
        xml_i = soup.findAll("div",{"class": "float-container"})

        all_doe_ids = []
        
        for div in xml_i:
            sch_year_table = div.find("table",{"class": "subrpt-header"})
            sch_year = sch_year_table.text.strip().split("Year: Year ")[1]
            #print(sch_year)
            student_table = div.find("table",{"class": "rpt-list"})

            rows = student_table.findAll('tr')
            i=0
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    i+=1
                    all_doe_ids.append(cells[0].text.strip())
            #print(i)

        #print('\n'.join(all_doe_ids))
        return all_doe_ids

            

        #https://moruya-h.sentral.com.au/oasis/reports/report?name=yearlist
        #post https://moruya-h.sentral.com.au/oasis/reports/report.gpx
        '''
        report_name	"yearlist"
        rptkey	"8NOG41elDxzjR739xyNITr4bLVzOSm1PatVJPH1BiAyxE"
        formsub	"1"
        inputs[years][]	[…]
        0	"+7"
        1	"+8"
        2	"+9"
        3	"10"
        4	"11"
        5	"12"
        inputs[opt_student_id]	"Y"
        inputs[cells_display]	"Y"
        inputs[cells_count]	"18"
        inputs[cells_size]	"small"
        btn_generate	"Generate+Report"
        '''
        pass

#class util
class common_lib:
    def __init__(self):
        
        pass

    def students_selector(self,query):
        string = f"{server}_common/lib/students_selector?module=edupro&query={query}&search_inactive=false&show_external_id=false"
        #print(string)
        r = session.get(string)
        return json.loads(r.text)['results']

#class util
class util:
    def __init__(self):
        
        pass

    def send_email(self,recipient, sender, subject, body):
        text_subtype = 'plain'
        if True:
            msg = MIMEText(body)
            msg['Subject']= subject
            msg['From'] = sender
            msg['To'] = recipient
            #email = EmailMessage()
            #email.set_content(body)
            
            #email['Subject'] = subject
            #email['From'] = sender
            #email['To'] = recipient

            # Send the message via our own SMTP server.
            #conn = SMTP(smtp_server)
            print("A")
            
            
            #conn.set_debuglevel(False)
            if smtp_user and smtp_pass:
                print("B")
                conn = smtplib.SMTP(smtp_server)
                print("C")
                print(f"connecting to {smtp_server} u:{smtp_user}; p:{smtp_pass};")
                conn.login(smtp_user, smtp_pass)
                try:
                    conn.sendmail(sender, recipient, msg.as_string())
                    print("email worked")
                finally:
                    conn.quit()
                
            else:
                print("c")
                email = EmailMessage()
                email.set_content(body)
            
                email['Subject'] = subject
                email['From'] = sender
                email['To'] = recipient
                conn = smtplib.SMTP(smtp_server)
                conn.send_message(email)
                print("d")
            
                
            #smtp = smtplib.SMTP(smtp_server)
            #smtp.send_message(email)
            #smtp.quit()
        #except:
        #    print("couldn't send email")
        pass

    def send_html_email(self,recipient, sender, subject, text, html):
        message = MIMEMultipart("alternative", None, [MIMEText(text), MIMEText(html,'html')])
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = recipient
        smtp = smtplib.SMTP(smtp_server)
        smtp.send_message(message)
        smtp.quit()

# Sentral
dashboard = Dashboard()
enquiry = Enquiry()
interviews = Interviews()
reports = Reports()
attendance = Attendance()
wellbeing = Wellbeing()
profiles = Profiles()
pxp = Pxp()
admin = Admin()
common_lib = common_lib()
util = util()
session = requests.session()
server = ''
smtp_server = ''
smtp_user = ''
smtp_pass = ''

def set_server(server_url):
    global server
    server = server_url
    pass

def set_smtp_server(smtp_url):
    global smtp_server
    smtp_server = smtp_url
    pass

def set_smtp_user_pass(username,password):
    global smtp_user
    global smtp_pass
    smtp_user = username
    smtp_pass = password
    pass
    

def loginold(username,password,public=1):
    session.get(server)
    r = session.post(server+"check_login",
                  data={"sentral-username":username,
                        "sentral-password":password,
                        "public-terminal":public
                        }
            )
    if r.content.decode('utf-8') == 'FAIL':
        return False
    return True

def login(username,password,public=1):
    #session.get(server)
    #print(server+"auth/?manual=true")
    r = session.post(server+"auth/",
                  params={"manual":'true'},
                  data={
	"username": quote(username),
	"password": password,
	"action": "login",
	"public-terminal": "1"
                        }
            )
    #print(r.content.decode)
    if r.content.decode('utf-8') == 'FAIL':
        return False
    r = session.get(server+"auth/")
    #print(r.content)
    #print('---------------')
    return True

def student(id):
    r = session.get(server+"wellbeing/ui_search?q="+id+"&filters[]=Incidents&filters[]=Students")
    #print( r )

def search_student(id):
    r = session.get(server+"wellbeing/search/students_classes?query="+id+"&search_inactive=false")
    pass



