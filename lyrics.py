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

done_artists_set = set()


UAH = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}

main_d = os.getcwd()
try:
	os.mkdir(join(main_d, 'results'))
except OSError:
	pass

main_d = join(main_d, 'results')

def extractLyrics():
	while True:
		i = q_of_artist.get()
		extractLyricsforArtist(i)
		q_of_artist.task_done()

def extractLyricsforArtist(data):
		global done_artists_set

		artist = data[0]
		genre = data[1]
		link = data[2]

		if artist.strip() in done_artists_set:
			return

		try:
			os.mkdir(join(main_d, slugify(unicode(artist))))
		except OSError:
			pass

		genre_file = open(join(main_d, slugify(unicode(artist)), 'genre.txt'), 'w')
		genre_file.write(genre)
		genre_file.close()

		count=1

		pre_link =	link.strip().replace('lyrics.html', '')
		while True:

			link = pre_link + 'alpage-%d.html' %(count)

			try:
				response = requests.get(link, headers=UAH)
			except:
				print 'crashed at %s' %(link)
				continue


			if response.url != link:
				break

			soup = BeautifulSoup(response.text, 'html.parser')

			for tr in soup.find_all('tr'):


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
						os.mkdir(join(main_d, slugify(unicode(artist)), year))
					except OSError:
						pass

					try:
						response = requests.get(song_link, headers=UAH)
					except:
						print 'crashed at %s' %(song_link)
						continue

					lyrics_soup = BeautifulSoup(response.text, 'html.parser')
					song = []
					for verse in lyrics_soup.findAll('p', {'class': 'verse'}):
						data = verse.text
						song.append(data)

					song_file = open(join(main_d, slugify(unicode(artist)), year, slugify(song_name)), 'w')
					song_file.write('\n'.join(song))
					song_file.close()
			count+=1
		with open('done_artists', 'a') as done_artists:
			done_artists.write(artist)
			done_artists.write('\n')
			done_artists_set.add(artist.strip())


q_of_artist = Queue()
count_artists = 0

with open('done_artists', 'r') as done_artists:
	for artist in done_artists:
		done_artists_set.add(artist.strip())
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

for i in range(100):
	t= Thread(target = extractLyrics)
	t.daemon = True
	t.start()

q_of_artist.join()
