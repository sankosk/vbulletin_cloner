"""
@Author: Esteban Montes

@Description: A set of classes for scrapping data from differents versions of vbulletin
using the printthread function for extracting data from vbulletin forums (3.x and 4.x)
"""

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from operator import is_not
#import azure_translate_api
import requests, re, urllib, ftplib, random, os


def _upload_attachment_ftp(url, user, passw, urlbase, path, attachmentUrl):
	s = ftplib.FTP(url, user, passw)
	s.cwd(path)
	name = ''.join(random.choice('0123456789ABCDEF') for i in range(16)) + "." + requests.get(attachmentUrl).headers['content-type'].split("/")[1]
	urllib.urlretrieve(attachmentUrl, name)
	f = open(name, 'rb')
	s.storbinary('STOR %s' % name, f)
	s.quit()
	f.close()
	os.remove(name)
	return urlbase + "/" + path + name


class Post(object):
	__metaclass__ = ABCMeta

	def __init__(self, content):
		self.content = requests.get(content).text

	@abstractmethod
	def get_title(self):
		raise NotImplementedError()

	@abstractmethod
	def get_messages(self):
		raise NotImplementedError()

	@abstractmethod
	def get_all_authors(self):
		raise NotImplementedError()



class Message(object):
	__metaclass__ = ABCMeta

	def __init__(self, content):
		self.content = content

	@abstractmethod
	def get_author(self):
		raise NotImplementedError()

	@abstractmethod
	def get_content(self):
		raise NotImplementedError()

	@abstractmethod
	def get_quotes(self):
		raise NotImplementedError()

	@abstractmethod
	def get_urls(self):
		raise NotImplementedError()

	@abstractmethod
	def get_attachments(self):
		raise NotImplementedError()


class Quote(object):
	__metaclass__ = ABCMeta

	def __init__(self, content):
		self.content = content

	@abstractmethod
	def get_author(self):
		raise NotImplementedError()

	@abstractmethod
	def get_content(self):
		raise NotImplementedError()

	@abstractmethod
	def get_bbcode(self):
		raise NotImplementedError()



"""
Class for scrapping vbulletin 3.X forums
Author: Esteban Montes
"""
class VBScrapperV3:

	class Post(Post):

		def __init__(self, url):
			Post.__init__(self, url)

		def get_messages(self):
			html = BeautifulSoup(self.content, "html.parser").find_all('table', class_="tborder")
			return html[1:len(html)-1]

		def get_title(self):
			return self.get_messages()[0].find('strong').getText()#.encode('ascii', 'ignore')

		def get_all_authors(self):
			authors = []
			for msg in self.get_messages():
				authors.append(VBScrapperV3.Message(msg).get_author())

			return authors

					

	class Message(Message):

		def __init__(self, content):
			Message.__init__(self, content)

		def get_author(self):
			return self.content.find('td', style=re.compile(".*")).getText()

		def get_quotes(self):
			return self.content.find_all('div', class_=re.compile("quote_[a-zA-Z0-9]"))

		def get_attachments(self):
			return self.content.find_all('a', id=re.compile("(.*)attachment(.*)"))

		def get_urls(self):
			urls = []
			p = re.compile("(.*)attachment(.*)")
			for url in self.content.find_all('a'):
				if p.search(str(url)) is None:
					urls.append(url)

			return urls



		#url, user, passw, urlbase, path, attachmentUrl
		def get_content(self, info, isFirst=False):
			html = self.content.find_all("div")
			if isFirst and len(self.get_attachments()) == 0:
				html = html[1]

			elif isFirst and len(self.get_attachments()) > 0:
				html[2]

			elif isFirst==False and len(self.get_attachments()) == 0:
				html = html[0]

			elif isFirst==False and len(self.get_attachments()) > 0:
				html = html[1]

			try:
				html = str(html)
			except:
				return "What a nice post!"

			try:
				# replacing quotes
				quotes = self.get_quotes()
				for i in range(len(quotes)-1):
					html = html.replace(str(quotes[i]), VBScrapperV3.Quote(quotes[i]).get_bbcode())


				# replacing attachments
				attachments = self.get_attachments()
				for att in attachments:
					#html = html.replace(str(att), "[\img]%s[/img]" % att['href'])
					nuevaurl = _upload_attachment_ftp(info["url"], info["user"], info["pass"], info["urlbase"], info["attachmentPath"], att['href'])
					html = html.replace(str(att), "[\img]%s[/img]" % nuevaurl)
				"""
				# replacing urls
				urls = self.get_urls()
				for url in urls:
					print url
					html = html.replace(url, "[\url]%s[/url]" % url['href'])
				"""

				return BeautifulSoup(html, "html.parser").getText().replace(";=", "=")

			except:
				return "What a nice post man!"


	class Quote(Quote):
		
		def __init__(self, content):
			Quote.__init__(self, content)

		def get_author(self):
			return self.content.find('div', class_="quoteauthor").getText().split(" ")[1]

		def get_content(self):
			return self.content.find('div', class_="quote").getText()

		def get_bbcode(self):
			return "[\quote=%s]%s[/quote]" % (self.get_author(), self.get_content())


"""
Class for scrapping 4.X vbulletin forums
Author: Esteban Montes
"""
class VBScrapperV4:

	class Post(Post):
		def __init__(self, url):
			Post.__init__(self, url)

		def get_messages(self):
			return BeautifulSoup(self.content, "html.parser").find_all('li', id=re.compile("post_\d+"))

		def get_title(self):
			return self.get_messages()[0].find('div', class_="title").getText()#.encode('ascii', 'ignore')

		def get_all_authors(self):
			authors = []
			for msg in self.get_messages():
				authors.append(VBScrapperV4.Message(msg).get_author())

			return authors

	class Message(Message):
		def __init__(self, content):
			Message.__init__(self, content)

		def get_author(self):
			return self.content.find('span', class_="username").getText()

		def get_quotes(self):
			return self.content.find_all('div', class_="bbcode_quote printable")

		def get_attachments(self):
			return self.content.find_all('a', href=re.compile("(.*)attachment(.*)"))

		def get_urls(self):
			urls = []
			p = re.compile("(.*)attachment(.*)")
			for url in self.content.find_all('a'):
				if p.search(str(url)) is None:
					urls.append(url)

			return urls

		def get_content(self, info):
			html = self.content.find('div', class_="content")

			try:
				html = str(html)
			except: 
				return "What a nice post!"

			# replacing quotes
			for quote in self.get_quotes():
				html = html.replace(str(quote), VBScrapperV4.Quote(quote).get_bbcode())
			

			for att in self.get_attachments():
				#html = html.replace(str(att), "[\img]%s[/img]" % att['href'])
				html = html.replace(str(att), "[\img]%s[/img]" % _upload_attachment_ftp(att['href'], info["user"], info["pass"], info["urlbase"], info["attachmentPath"]))

			return BeautifulSoup(html, "html.parser").getText()



	class Quote(Quote):
		def __init__(self, content):
			Quote.__init__(self, content)

		def get_author(self):
			return self.content.find('strong').getText()

		def get_content(self):
			return self.content.find('div', class_="message").getText().decode('utf-8', 'ignore')

		def get_bbcode(self):
			return "[\quote=%s]%s[/quote]" % (self.get_author(), self.get_content())



"""
post = VBScrapperV3.Post("http://www.forexfactory.com/printthread.php?t=590109&pp=20&page=2")
msgs = post.get_messages()

print VBScrapperV3.Message(msgs[11]).get_urls()
"""