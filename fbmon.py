##
##
## In the source of your facebook profile is a string which has a list of users
## These users are listed in order of who has liked or shared your posts, chatted with you, or viewed your timeline the most
## The listed users are not neccesarily friends with you
## It can be used to see who has been viewing your profile
## This script gets it and looks up the names, from the UID that they are listed as
## Happy hunting ;-)
##
##

import subprocess, json, csv, re, getpass, shlex, os, sys, time
from bs4 import BeautifulSoup
from os import path

#Tests if selenium module is installed
try:
	from selenium import webdriver
except:
	print "Module \"selenium\" must be isntalled"
	exit()

#Clears the LUI
subprocess.Popen(["clear"])

#For some reason it clears the login prompt if this isn't there
time.sleep(0.1)

#Non-expiring app access token
#If this is taken down or stops working, you can use your own app ID and secret in this format as an access token: "APP_ID|APP_SECRET"
oauth_access_token = "173094776370970|qhEYPEHxCgXqAJsutXhYSTiajwk"

#URL that selenium sends login details to
baseurl = "https://facebook.com/login"

#Login details not stored anywhere, only sent via SSL to facebook
print "Welcome to fbmon."
print "Please log in to Facebook."
print "Login details are not saved or logged anywhere."
print "They are only sent to facebook via SSL."
print "If you are in doubt, please examine the code thoroughly."
print ""
username = raw_input("Email: ")

print ""
print "(characters hidden)"
password = getpass.getpass()

#The xpaths of the email field, password field, and submit buttons on facebook.com/login
xpaths = {'usernameTxtBox' : "//*[@id='email']", 'passwordTxtBox' : "//*[@id='pass']", 'submitButton' : "//*[@id='u_0_2']"}

#Finds the path of phantomjs regardless of fbmon folder location
jspath = sys.path[0] + "/phantomjs"

#Tells selenium to use PhantomJS browser, and save the log to nowhere
#Headless browser (has no GUI) that selenium can control
#PhantomJS binary is compiled on Kali 2.0
#Binary might not work on different distros due to a bug in their source
try:
	mydriver = webdriver.PhantomJS(executable_path=jspath, service_log_path=os.path.devnull)
	#If PhantomJS throws errors, try replacing preceeding line with this:
	#mydriver = webdriver.Firefox()
	#Using firefox gives the same end result, but opens the browser window while selenium is using it
except:
	print "Selenium cant load PhantomJS. The binary might not work on your distro because of a known bug in their code, or it might not have permission to run as executable."
	print "Compile PhantomJS yourself, or look in the code to see how to use firefox instead."
	exit()

#Using selenium to access your facebook profile
mydriver.get(baseurl)
mydriver.maximize_window()

#Clears email box and writes user email
mydriver.find_element_by_xpath(xpaths['usernameTxtBox']).clear()
mydriver.find_element_by_xpath(xpaths['usernameTxtBox']).send_keys(username)

#Clears password box and writes user password
mydriver.find_element_by_xpath(xpaths['passwordTxtBox']).clear()
mydriver.find_element_by_xpath(xpaths['passwordTxtBox']).send_keys(password)

#Submits login details
mydriver.find_element_by_xpath(xpaths['submitButton']).click()

#Gets HTML source of your profile
HTML = mydriver.page_source

#Done with selenium
mydriver.quit()

#Parsing the HTML source of your pofile to find the InitialFriendsChatList
soup = BeautifulSoup(HTML)

#The JSON string we want is embedded in the last <script> tag, this finds it
data = soup.find_all("script")[-1].text

#Finds the exact JSON string that we want inside the last <script> tag
#If it doesnt exist, selenium got the source of the login page instead of your profile, because of wrong login details
try:
	inputwq = re.search(r'\{"list":\[(.*)\],"groups"', data).group(1)
except:
	print ""
	print "Malformed or nonexistent InitialFriendsChatList. Wrong login details?"
	exit()

#Converts the JSON string into Comma Separated Values that the csv module can handle
input = shlex.split(inputwq)

#Gets csv to find the UIDs inside the JSON string
parser = csv.reader(input)

#Clears the LUI
subprocess.Popen(["clear"])

#Opens retrievednames.txt and truncates to 0 bytes
#If you want to keep an old version, just rename it
def clearandstamp():
	date = subprocess.Popen(["date"], stdout=subprocess.PIPE).communicate()[0]
	file = open('retrievednames.txt', 'w+')
	file.write(date + 'Names retrieved with facebook graph API\n\n')

#Looks up every UID from your profile and writes it to file
def parseandwrite():
	clearandstamp()
	print "Retrieving names and writing to retrievednames.txt \n"
	for fields in parser:
		for i,f in enumerate(fields):
			
			#Facebook adds an irrelevant "-X" to every UID, where X is a number between 0 and 3
			#This removes the last two digits from every value before it looks them up
			f = f[:-2]
			
			#Uses graph API to look up a name based on UID
			#The API returns JSON
			curl_lookup = subprocess.Popen(["curl", "https://graph.facebook.com/" + f + "?access_token=" + oauth_access_token], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

			#Loads the returned JSON into the json module
			parsed_json = json.loads(curl_lookup)

			#Finds the value 'name' in the returned JSON
			try:
				#Writes the UID in question, the corresponding name, and a link to their profile to retrievednames.txt
				name_only = (parsed_json['name']).encode('utf-8')			
				file = open('retrievednames.txt', 'a')	
				file.write(f + '\t' + '|' + name_only + '\t' + '\t' + '\t' + '\n' + 'https://facebook.com/' + f + '\n' + '\n')
				print (f + '\t' + '|' + name_only + '\t' + '\t' + '\t' + '\n' + 'https://facebook.com/' + f + '\n')
			
			#If the value 'name' does not exist, the UID lookup was denied or failed
			except KeyError:
				print('BAD UID (USER DELETED?) SKPPING...\n')			
parseandwrite()
print "Program completed succesfully!"
print "You'll find your stalkers in \"retrievednames.txt\""
print "Thank you for using fbmon"
print "Exiting..."
