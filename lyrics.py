# encoding=utf8
import httplib
import sys
import threading

from Queue import Queue
from threading import Thread

reload(sys)
sys.setdefaultencoding('utf8')


import os
import requests
from bs4 import BeautifulSoup
from slugify import slugify

from os.path import join

UAH = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}

main_d = os.getcwd()
try:
	os.mkdir(join(main_d, 'results'))
except OSError:
	pass
main_d = join(main_d, 'results')

def extractLyrics():
	print 'Using thread: ' + t.name

	while True:
		i = q_of_artist.get()
		extractLyricsforArtist(i)
		q_of_artist.task_done()

def extractLyricsforArtist(data):
		artist = data[0]
		genre = data[1]
		link = data[2]

		print 'Number of active threads' + str(threading.active_count())
		print 'trying artist %s' %(artist)
		print 'Using thread: ' + t.name

		try:
			os.mkdir(join(main_d, artist))
			print "Made a directory called " + artist
		except OSError:
			pass

		genre_file = open(join(main_d, artist, 'genre.txt'), 'w')
		genre_file.write(genre)
		genre_file.close()

		count=1

		pre_link =	link.strip().replace('lyrics.html', '')
		while True:

			print 'Using thread: ' + t.name
			print 'trying page %d' %(count)
			link = pre_link + 'alpage-%d.html' %(count)

			try:
				response = requests.get(link, headers=UAH)
			except:
				print 'crashed at %s' %(link)


			if response.url != link:
				break

			soup = BeautifulSoup(response.text, 'html.parser')

			for tr in soup.find_all('tr'):

				print 'Using thread: ' + t.name

				new_soup = BeautifulSoup(str(tr), 'html.parser')
				tds = new_soup.find_all('td')

				if not tds:
					continue
				else:
					song_soup = BeautifulSoup(str(tds[1]), 'html.parser')
					year_soup = BeautifulSoup(str(tds[2]), 'html.parser')

					song_name = ''.join(song_soup.a.contents).replace(' Lyrics', '').strip()

					song_link = song_soup.a['href']

					year = ''.join(year_soup.td.contents)

					if not year:
						year = 'Not Available'
					elif not year.isdigit():
						continue

					try:
						os.mkdir(join(main_d, artist, year))
					except OSError:
						pass

					try:
						response = requests.get(song_link, headers=UAH)
					except:
						print 'crashed at %s' %(song_link)

					lyrics_soup = BeautifulSoup(response.text, 'html.parser')
					song = []
					for verse in lyrics_soup.findAll('p', {'class': 'verse'}):
						data = verse.text
						song.append(data)

					song_file = open(join(main_d, artist, year, slugify(song_name)), 'w')
					song_file.write('\n'.join(song))
					song_file.close()
			count+=1
		print 'Outside while true of extractLyrics for an artist: ' +artist


q_of_artist = Queue()
count_artists = 0
try:
	with open('artist.csv') as artists:
		pwd = main_d
		for line in artists:
			data = line.split('\t')
			artist = data[0]
			genre = data[1]
			link = data[2]
			info = [artist, genre, link]
			q_of_artist.put(info)
			count_artists += 1

except KeyboardInterrupt:
	sys.exit(1)

for i in range(count_artists):
	t= Thread(target = extractLyrics)
	t.daemon = True
	t.start()

q_of_artist.join()
