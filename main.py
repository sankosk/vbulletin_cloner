"""
Console application : Vbulletin posts content cloner
Author: Esteban Montes
"""
import sys, json, re, urllib, azure_translate_api, vbulletinapi
from bs4 import BeautifulSoup
from scrapper import VBScrapperV3, VBScrapperV4 
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



		#preparing the user list
		for post in data["posts"]:
			authorsV3 = []
			authorsV4 = []
			print post["url"]
			if checkVersion(post["url"]) == 3:
				for auth in VBScrapperV3.Post(post["url"]).get_all_authors():
					authorsV3.append(auth)

				for page in post["pages"]:
					for auth in VBScrapperV3.Post(page).get_all_authors():
						authorsV3.append(auth)

				authorsV3 = list(set(authorsV3))
			
				if len(data["users"]) >= len(authorsV3):
					authorsV3 = dict(zip(authorsV3, data["users"]))


				title = VBScrapperV3.Post(post["url"]).get_title()
				if post["lang"] != "":
					title = azure_translate_api.translate(client, title, post["lang"])
					title = clean_translated(title)

				messages = VBScrapperV3.Post(post["url"]).get_messages()

				obj = VBScrapperV3.Message(messages[0])
				author = obj.get_author()
				if data["enableUserList"] == "yes":
					author = authorsV3[author]


				postcontent = obj.get_content(data["myforums"][0]["ftpconfig"], True)
				if post["lang"] != "":
					postcontent = azure_translate_api.translate(client, postcontent, post["lang"])
					postcontent = clean_translated(postcontent)
				postcontent = replace_separated_tags(postcontent)
				if data["enableUserList"] == "yes":
					postcontent = postcontent.replace(obj.get_author(), author)

				# creando tema
				vb = vbulletinapi.Vbulletin(client_options)
				vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
				vb.login(author, data["myforums"][0]["botPassword"])
				threadid = vb.post_new_thread(post["forumid"], title, postcontent)
				vb.logout()


				for i in range(1, len(messages)):
					obj = VBScrapperV3.Message(messages[i])
					author = obj.get_author()
					if data["enableUserList"] == "yes":
						author = authorsV3[author]
					
					postcontent = obj.get_content(data["myforums"][0]["ftpconfig"])
					if post["lang"] != "":
						postcontent = azure_translate_api.translate(client, postcontent, post["lang"])
						postcontent = clean_translated(postcontent)
					postcontent = replace_separated_tags(postcontent)
					if data["enableUserList"] == "yes":
						postcontent = postcontent.replace(obj.get_author(), author)
					#contestar al tema
					vb = vbulletinapi.Vbulletin(client_options)
					vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
					vb.login(author, data["myforums"][0]["botPassword"])
					vb.post_new_answer(threadid, postcontent)
					vb.logout()

				# para cada pagina del tema contestar al tema
				for page in post["pages"]:
					messages = VBScrapperV3.Post(page).get_messages()

					for msg in messages:
						obj = VBScrapperV3.Message(msg)
						author = obj.get_author()
						
						if data["enableUserList"] == "yes":
							author = authorsV3[author]

						postcontent = obj.get_content(data["myforums"][0]["ftpconfig"])
						if post["lang"] != "":
							postcontent = azure_translate_api.translate(client, postcontent, post["lang"])
							postcontent = clean_translated(postcontent)
						postcontent = replace_separated_tags(postcontent)
						if data["enableUserList"] == "yes":
							postcontent = postcontent.replace(obj.get_author(), author)
						#contestar al tema
						vb = vbulletinapi.Vbulletin(client_options)
						vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
						vb.login(author, data["myforums"][0]["botPassword"])
						vb.post_new_answer(threadid, postcontent)
						vb.logout()

			elif checkVersion(post["url"]) == 4:
				for auth in VBScrapperV4.Post(post["url"]).get_all_authors():
					authorsV4.append(auth)

				for page in post["pages"]:
					for auth in VBScrapperV4.Post(page).get_all_authors():
						authorsV4.append(auth)

				authorsV4 = list(set(authorsV4))
			
				if len(data["users"]) >= len(authorsV4):
					authorsV4 = dict(zip(authorsV4, data["users"]))


				title = VBScrapperV4.Post(post["url"]).get_title()
				if post["lang"] != "":
					title = azure_translate_api.translate(client, title, post["lang"])
					title = clean_translated(title)

				messages = VBScrapperV4.Post(post["url"]).get_messages()

				obj = VBScrapperV4.Message(messages[0])
				author = obj.get_author()
				if data["enableUserList"] == "yes":
					author = authorsV4[author]

				postcontent = obj.get_content(data["myforums"][0]["ftpconfig"])
				if post["lang"] != "":
					postcontent = azure_translate_api.translate(client, postcontent, post["lang"])
					postcontent = clean_translated(postcontent)
				postcontent = replace_separated_tags(postcontent)
				if data["enableUserList"] == "yes":
					postcontent = postcontent.replace(obj.get_author(), author)
				# creando tema
				vb = vbulletinapi.Vbulletin(client_options)
				vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
				vb.login(author, data["myforums"][0]["botPassword"])
				threadid = vb.post_new_thread(post["forumid"], title, postcontent)
				vb.logout()


				for i in range(1, len(messages)):
					obj = VBScrapperV4.Message(messages[i])
					author = obj.get_author()
					if data["enableUserList"] == "yes":
						author = authorsV4[author]
					
					postcontent = obj.get_content(data["myforums"][0]["ftpconfig"])
					if post["lang"] != "":
						postcontent = azure_translate_api.translate(client, postcontent, post["lang"])
						postcontent = clean_translated(postcontent)
					postcontent = replace_separated_tags(postcontent)
					if data["enableUserList"] == "yes":
						postcontent = postcontent.replace(obj.get_author(), author)
					#contestar al tema
					vb = vbulletinapi.Vbulletin(client_options)
					vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
					vb.login(author, data["myforums"][0]["botPassword"])
					vb.post_new_answer(threadid, postcontent)
					vb.logout()

				# para cada pagina del tema contestar al tema
				for page in post["pages"]:
					messages = VBScrapperV4.Post(page).get_messages()

					for msg in messages:
						obj = VBScrapperV4.Message(msg)
						author = obj.get_author()
						if data["enableUserList"] == "yes":
							author = authorsV4[author]

						postcontent = obj.get_content(data["myforums"][0]["ftpconfig"])
						if post["lang"] != "":
							postcontent = azure_translate_api.translate(client, postcontent, post["lang"])
							postcontent = clean_translated(postcontent)
						postcontent = replace_separated_tags(postcontent)

						if data["enableUserList"] == "yes":
							postcontent = postcontent.replace(obj.get_author(), author)
						#contestar al tema
						vb = vbulletinapi.Vbulletin(client_options)
						vb.register_new_user(author, data["myforums"][0]["botPassword"], "%s+%d@gmail.com" % (data["myforums"][0]["emailbase"] ,random_with_N_digits(4)))
						vb.login(author, data["myforums"][0]["botPassword"])
						vb.post_new_answer(threadid, postcontent)
						vb.logout()