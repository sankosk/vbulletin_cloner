"""
Update an active thread
"""
import sys, json, re, urllib, azure_translate_api, vbulletinapi
from bs4 import BeautifulSoup
from scrapper import VBScrapperV4, VBScrapperV4 
from random import randint

def checkVersion(url):
	content = urllib.urlopen(url).read()
	v = BeautifulSoup(content, "html.parser").find("meta", {'name':'generator'})['content']
	if "4." in v:
		return 4
	elif "3." in v:
		return 3
	else:
		return 0

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def clean_translated(s):
	return BeautifulSoup(s, "html.parser").find("string", xmlns="http://schemas.microsoft.com/2003/10/Serialization/").getText()


def replace_separated_tags(s):
	return s.replace("\\", "")


if "__main__":
	if len(sys.argv) == 2:
		data = json.loads(file(sys.argv[1]).read())
		client = azure_translate_api.get_access_token('runehackx', 'XQLuy2RtLavQUtVsjtN3M5IPrU/IvfJ3Cl3Sy/Vt/rA=')
		client_options = {
		    'apikey': data["myforums"][0]["apikey"],
		    'forumurl': data["myforums"][0]["url"],
		    'clientname': 'someclient',
		    'clientversion': '1',
		    'platformname': '1',
		    'platformversion': '1',
		    'uniqueid': 'someuniqueid'
		}

		authorsV3 = []
		authorsV4 = []
		toupdate = data["toUpdate"]

		#preparing the user list
		if data["enableUserList"] == "yes":
			
			for i in range(len(toupdate)):
				if checkVersion(toupdate[i]["urlorigen"]) == 3:
					post = VBScrapperV4.Post(toupdate[i]["urlorigen"])
					for author in post.get_all_authors():
						authorsV3.append(author)

					authorsV3 = list(set(authorsV3))
					if len(data["users"]) >= len(authorsV3):
						authorsV3 = dict(zip(authorsV3, data["users"]))

				elif checkVersion(toupdate[i]["urlorigen"]) == 4:
					post = VBScrapperV4.Post(toupdate[i]["urlorigen"])
					for author in post.get_all_authors():
						authorsV4.append(author)

					authorsV4 = list(set(authorsV4))
					if len(data["users"]) >= len(authorsV4):
						authorsV4 = dict(zip(authorsV4, data["users"]))


		for i in range(len(toupdate)):
			if checkVersion(toupdate[i]["urlorigen"]) == 4:
				post = VBScrapperV4.Post(toupdate[i]["urlorigen"])
				post2 = VBScrapperV4.Post(toupdate[i]["urldestino"])

				if len(post.get_messages()) > len(post2.get_messages()):
					for j in range(len(post2.get_messages()), len(post.get_messages())):
						msg = VBScrapperV4.Message(post.get_messages()[j])
						content = msg.get_content(data["myforums"][0]["ftpconfig"])
						author = msg.get_author()
						if data["enableUserList"] == "yes":
							print authorsV4
							author = authorsV4[author]

						
						if toupdate[i]["lang"] != "":
							content = azure_translate_api.translate(client, content, post["lang"])
							content = clean_translated(content)
						

						content = replace_separated_tags(content)
						vb = vbulletinapi.Vbulletin(client_options)
						vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
						vb.login(author, data["myforums"][0]["botPassword"])
						vb.post_new_answer(toupdate[i]["id"], content)
						vb.logout()
