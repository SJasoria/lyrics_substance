import os
import requests
from bs4 import BeautifulSoup

UAH = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'}

with open('artist.csv') as artists:
	pwd = os.getcwd()
	for line in artists:
		data = line.split('\t')

		artist = data[0]
		genre = data[1]
		link = data[2]

		print 'trying artist %s' %(artist)

		try:
			os.mkdir(artist)
		except OSError:
			pass

		os.chdir(artist)

		new_pwd=os.getcwd()

		genre_file = open("genre.txt", 'w')
		genre_file.write(genre)
		genre_file.close()

		count=1

		pre_link =	link.strip().replace('lyrics.html', '')
		while True:

			print 'trying page %d' %(count)
			link = pre_link + 'alpage-%d.html' %(count)

			try:
				response = requests.get(link, headers=UAH)
			except:
				print 'crashed at %s' %(link)
				raw_input()


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

					try:
						os.mkdir(year)
					except OSError:
						pass

					os.chdir(year)

					try:
						response = requests.get(song_link, headers=UAH)
					except:
						print 'crashed at %s' %(song_link)
						raw_input()

					lyrics_soup = BeautifulSoup(response.text, 'html.parser')
					song = []
					for verse in lyrics_soup.findAll('p', {'class': 'verse'}):
						data = verse.text
						song.append(data)

					song_file = open(song_name, 'w')
					song_file.write('\n'.join(song))
					song_file.close()
					os.chdir(new_pwd)


			count+=1

		os.chdir(pwd)