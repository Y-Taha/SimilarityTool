from django.contrib import messages
import sys
from django.shortcuts import render
import difflib
import csv, io
from django.http import HttpResponse
import os
from django.conf import settings
import scipy
from scipy.spatial import distance
import textdistance as textdistance
from fuzzywuzzy import fuzz
import xlwt
from xlwt import Workbook

import difflib
import csv
# Create your views here.
from tune.models import Item


def show(request):
    return HttpResponse("LOL")
def have_same_words(sentence1, sentence2):
    return sorted(sentence1.split()) == sorted(sentence2.split())

def upload(request):
    wb=Workbook()
    sheet1=wb.add_sheet('Sheet 1')
    items = []
    description = []
    duplicates = False
    line_count = 0
    duplicatesN = 0
    f = open("duplicates report.txt", "w")
    template="upload.html"
    prompt={
        'order':'Order of the CSV should be ITEM CODE,MNEMONIC,DESCRIPTION'
    }
    if request.method == "GET":
        return render(request,template,prompt)
    csv_file=request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        #print("WRONG TYPE")
        prompt = {
            'Error': 'Wrong file type'
        }
        messages.error(request,'This is not a csv file')
        return render(request,template,prompt)
    else:
        data_set=csv_file.read().decode('UTF-8')
        io_string=io.StringIO(data_set)
        next(io_string)
        for column in csv.reader(io_string,delimiter=','):
            items_code=column[0]
            item_description=column[2]
            """
            _, created=Item.objects.update_or_create(
                item_code=column[0],
                description=column[1]
            )
            """
            items.append(items_code)
            description.append(item_description)
            line_count += 1
        for i in range(line_count):
            for j in range(i+1, line_count):
                print(i)
                if j != i:
                    alphanumeric1 = ""
                    alphanumeric2 = ""
                    for character in description[i]:
                        if character.isalnum():
                            alphanumeric1 += character
                    for character in description[j]:
                        if character.isalnum():
                            alphanumeric2 += character

                    similarity = textdistance.damerau_levenshtein(alphanumeric1, alphanumeric2)
                    similarity1 = fuzz.ratio(alphanumeric1, alphanumeric2)
                    #print(f'{alphanumeric1}:{alphanumeric2}={similarity},{similarity1}\n')
                    if description[i] == description[j]:
                        if items[i] != items[j]:
                            duplicates = True
                            duplicatesN += 1
                            sheet1.write(duplicatesN,0,items[i])
                            sheet1.write(duplicatesN,1,description[i])
                            sheet1.write(duplicatesN,2,items[j])
                            sheet1.write(duplicatesN,3,description[j])
                            f.write(f'{items[i]},{description[i]},{items[j]},{description[j]}\n')
                    # elif items[i] == items[j]:
                    elif similarity == 0:
                        duplicates = True
                        duplicatesN += 1
                        sheet1.write(duplicatesN, 0, items[i])
                        sheet1.write(duplicatesN, 1, description[i])
                        sheet1.write(duplicatesN, 2, items[j])
                        sheet1.write(duplicatesN, 3, description[j])
                        f.write(f'{items[i]},{description[i]},{items[j]},{description[j]}\n')

                    elif similarity <= 2 and similarity >= 1 and similarity1 >= 94:
                        duplicates = True
                        duplicatesN += 1
                        sheet1.write(duplicatesN, 0, items[i])
                        sheet1.write(duplicatesN, 1, description[i])
                        sheet1.write(duplicatesN, 2, items[j])
                        sheet1.write(duplicatesN, 3, description[j])
                        f.write(f'{items[i]},{description[i]},{items[j]},{description[j]}\n')

                    if similarity1 >= 94 and similarity1 <= 97:
                        duplicates = True
                        duplicatesN += 1
                        sheet1.write(duplicatesN, 0, items[i])
                        sheet1.write(duplicatesN, 1, description[i])
                        sheet1.write(duplicatesN, 2, items[j])
                        sheet1.write(duplicatesN, 3, description[j])
                        f.write(f'{items[i]},{description[i]},{items[j]},{description[j]}\n')

                    if similarity1 >= 70 and similarity1 <= 72:
                        if have_same_words(description[i], description[j]):
                            duplicates = True
                            duplicatesN += 1
                            sheet1.write(duplicatesN, 0, items[i])
                            sheet1.write(duplicatesN, 1, description[i])
                            sheet1.write(duplicatesN, 2, items[j])
                            sheet1.write(duplicatesN, 3, description[j])
                            f.write(f'{items[i]},{description[i]},{items[j]},{description[j]}\n')

        if not duplicates:
            f.write("There are no duplicates")
            #print("There are no duplicates")
            #return render(request, 'hello.html')
            return HttpResponse('<head><title>Master Data Tune</title></head>There are no duplicates')
        sheet1.write(0,0,'Item Code')
        sheet1.write(0,1,'Description')
        sheet1.write(0,2,'Item Code')
        sheet1.write(0,3,'Description')
        wb.save('duplicates report.xls')
        #f.write(f'\nThe number of duplicates: {duplicatesN}')
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        f.close()
        f = open("duplicates report.txt", "r")
        # Define text file name
        ##################################
        #filename = 'duplicates report.txt'
        filename='duplicates report.xls'
        ##################################
        # Define the full file path
        #filepath = BASE_DIR + '/' + filename
        # Open the file for reading content
        #path = open(filepath, 'r')
        # Set the mime type
        # mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        #######################################################
        #response = HttpResponse(f, content_type='text/plain')
        response= HttpResponse(f,content_type='text/plain')
        #######################################################
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response
        return HttpResponse('<head><title>Master Data Tune</title></head>There are duplicates a report file ("duplicates report.txt") has been created')
        context={}
        #return render(request,template,context)


def home(request):
    items = []
    description = []
    duplicates = False
    f=open("duplicates report.txt","w")
    #number_of_items = int(input("Please enter the number of items: "))
    with open(os.path.join(settings.BASE_DIR,'master2.csv')) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                f.write(f'Column names are {", ".join(row)}\n')

                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                items.append(row[0])
                description.append(row[1])
                line_count += 1
                #print(f'\t{row[0]},{row[1]}\n')
        for i in range(line_count-1):
            for j in range(i, line_count-1):
                if j != i:
                    alphanumeric1 = ""
                    alphanumeric2 = ""
                    for character in description[i]:
                        if character.isalnum():
                            alphanumeric1 += character
                    for character in description[j]:
                        if character.isalnum():
                            alphanumeric2 += character

                    similarity = difflib.SequenceMatcher(None, alphanumeric1, alphanumeric2).ratio()
                    if description[i] == description[j]:
                        if items[i] != items[j]:
                            duplicates = True
                            f.write(f'\t{items[i]},{description[i]} AND {items[j]},{description[j]} Are '
                                f'duplicates\n')
                            #print(
                             #   f'\t{items[i]},{description[i]} AND {items[j]},{description[j]} Are '
                              #  f'duplicates')
                            #return HttpResponse(f'\t{items[i]},{description[i]} AND {items[j]},{description[j]} Are '
                                                #f'duplicates')
                    elif items[i] == items[j]:
                        if similarity >= 0.92 or similarity < 0.7:
                            duplicates = True
                            f.write(f'\t{items[i]},{description[i]} AND {items[j]},{description[j]} Are '
                                    f'duplicates\n')
                            #print(
                             #   f'\t{items[i]},{description[i]} AND {items[j]},{description[j]} Are '
                              #  f'duplicates')
                           # return HttpResponse(f'\t{items[i]},{description[i]} AND {items[j]},{description[j]} Are '
                                #f'duplicates')

        if not duplicates:
            f.write("There are no duplicates")
            #print("There are no duplicates")
            return render(request, 'hello.html')
            return HttpResponse('<head><title>Master Data Tune</title></head>There are no duplicates')
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        f.close()
        f = open("duplicates report.txt", "r")
        # Define text file name
        filename = 'duplicates report.txt'
        # Define the full file path
        #filepath = BASE_DIR + '/' + filename
        # Open the file for reading content
        #path = open(filepath, 'r')
        # Set the mime type
        # mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(f, content_type='text/plain')
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        # Return the response value
        return response
        return HttpResponse('<head><title>Master Data Tune</title></head>There are duplicates a report file ("duplicates report.txt") has been created')