#!/usr/bin/python
# coding=utf-8

from openpyxl import load_workbook
import shutil

order_number = input("Podaj nr umowy:")
order_date = input("Data zawarcia umowy:")
order_complete = input("Data wykonania umowy:")
order_title = input("Tytuł umowy:")
order_amount = float(input("Kwota brutto [PLN]:"))

xlsTpl = "uod_wzor.xlsx"
fn = "uod_" + order_number.replace("/", "_")+".xlsx"
shutil.copyfile(xlsTpl, fn)

workbook = load_workbook(fn)
worksheet = workbook.get_sheet_by_name("x")

worksheet['D8'] = "nr {}".format(order_number)
worksheet['E19'] = order_date
worksheet['E20'] = order_complete
worksheet['F2'] = "Warszawa, {}".format(order_complete)
worksheet['E18'] = 'UoD {} - {}'.format(order_number, order_title)
worksheet['E24'] = order_amount

workbook.save(fn)
