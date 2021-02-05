# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import csv
import pandas
import pymongo
from pprint import pprint

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    inputFileDataFrame = pandas.read_csv('works_metadata.csv', header=0)
    #print(inputFileDataFrame.describe(include='all'))
    inputFileDataFrame = inputFileDataFrame.drop('id', axis=1)
    inputFileDataDict = inputFileDataFrame.to_dict('records')

    dbClient = pymongo.MongoClient("mongodb://127.0.0.1:27017/?compressors=zlib")
    #pprint(dbClient.admin.command("serverStatus"))
    worksSingleViewDB = dbClient['WorksSingleViewDB']
    pprint(worksSingleViewDB.list_collection_names())
    worksSingleViewDB['WorksSingleViewCollection'].insert_many(inputFileDataDict, ordered=False)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
