import html
import requests
import shutil
import argparse
import os
import sys
import csv
import getpass
import time
from lxml import html
from threading import Thread
from PyQt5.QtWidgets import QApplication, QLabel, QDesktopWidget
from pathlib import Path

Direct_Path = os.path.dirname(os.path.realpath(__file__))
USER_NAME = getpass.getuser()
Wait = 1

def Site_Exists(url):
	request = requests.get(url)
	if request.status_code == 200:
		return 1
	else:	
		return 0

def Make_GUI(Text):
	app = QApplication(sys.argv)
	label = QLabel(Text)
	screen = QDesktopWidget().screenGeometry()
	label.setGeometry(screen.width()-200, screen.height()-200,200,50)
	label.show()
	app.exec_()

def Show_Notification(Text):
	thread = Thread(target = Make_GUI, args = (Text, ))
	thread.start()

def Check_for_MangaUpdate(Url, Old_Release_Text):
	try:
		response = requests.get(Url, stream=True)
		if response.status_code == 200:
			tree = html.fromstring(response.content)
			Title = tree.xpath('/html/body/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[1]/span[1]')[0].text
			Release = tree.xpath('//*[@id="main_content"]/div[2]/div[1]/div[3]/div[12]')
			Release_Text = Release[0].text_content().split(' by')[0]
		else:
			return 0, response.status_code, "" 	

		if Release_Text == Old_Release_Text:
			return 0, "", ""
		else:	
			return 1, Release_Text, Title
	except Exception as e:
		print(e + " Could not check " + Url + " for Updates ...")

def Check_List_for_Updates():
	try:
		with open('Mangalist.csv', newline='') as f:
			reader = csv.reader(f)
			Mangalist = list(reader)

		for i in range(len(Mangalist)):
			Results = 0, "", ""
			try:
				Results = Check_for_MangaUpdate('https://www.mangaupdates.com/series.html?id='+Mangalist[i][1],Mangalist[i][2])
			except:
				pass		
			if Results[0]:
				Show_Notification("New Release of "+Results[2]+'\n'+Results[1])
				Mangalist[i][0] = Results[2]
				Mangalist[i][2] = Results[1]
				with open("Update.txt", "a") as file:
					file.write(str(Results))

		with open("Mangalist.csv", "w", newline="") as f:
			writer = csv.writer(f)
			writer.writerows(Mangalist)		
	except Exception as e:
		print(e + " Could not check for Updates ...")

def Add_to_startup(Timer):
	if sys.platform == "win32":
	    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
	    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
	        bat_file.write('cd /'+Direct_Path[0].lower()+' '+Direct_Path+'\n')
	        bat_file.write(r'start "" %s' % 'Update.py'+" -E -T "+Timer)

	else:
		print("Coming Soon...")        

def Init_List():
	Mangalist = []
	with open("Mangalist.csv", "w", newline="") as f:
		writer = csv.writer(f)
		writer.writerows(Mangalist)

def Add_to_list(Name, ID, Chapter):
	with open('Mangalist.csv','a') as fd:
		fd.write(Name+','+ID+','+Chapter+"\n")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Mangaupdate Checker')
	parser.add_argument('-S','--Startup', action='store_false')
	parser.add_argument('-I','--Init', action='store_false')
	parser.add_argument('-A','--Add', action='store_false')
	parser.add_argument('-E','--End', action='store_false') # Endless mode
	parser.add_argument('-D', '--ID',
	action="store", dest="ID",
	help="Manga ID", default="")
	parser.add_argument('-N', '--Name',
	action="store", dest="Name",
	help="Manga Name", default="")
	parser.add_argument('-T', '--Time',
	action="store", dest="Time",
	help="Time for Update", default="")
	args = parser.parse_args()

	if not args.Init:
		Init_List()
	else:
		if ~args.Add | ~args.Startup:
			if not args.Startup:
				Add_to_startup(args.Time)
			else:
				if not args.Add:
					Add_to_list(args.Name, args.ID,Check_for_MangaUpdate('https://www.mangaupdates.com/series.html?id='+args.ID,"")[1])
				else:
					if not args.End:
						while True:
							try:
								response = requests.get('https://www.mangaupdates.com', stream=True, timeout=1)
								Check_List_for_Updates()
								time.sleep(int(args.Time))
							except:
								time.sleep(Wait)
								print("Failed to Update")
								pass	
					Check_List_for_Updates()
		else:
			print("use -S or -A ...")	
