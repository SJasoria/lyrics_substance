from bs4 import BeautifulSoup
import requests

data = [chr(a) for a in range(ord('a'),ord('z')+1)]
data = ['1'] + data

output = open('artist.csv', 'a')

for alphabet in data:
	count = 1
	while True:
		link='http://www.metrolyrics.com/artists-%s-%d.html'%(alphabet,count)

		try:
			response = requests.get(link)
		except:
			print 'crashed at %s %d'%(alphabet, data)
			output.close()

		if response.status_code != 200:
			break

		soup =  BeautifulSoup(response.text, 'html.parser')

		for tr in soup.find_all('tr'):
			new_soup = BeautifulSoup(str(tr), 'html.parser')
			tds = new_soup.find_all('td')

			if not tds:
				continue
			else:
				artist_soup = BeautifulSoup(str(tds[0]), 'html.parser')
				genre_soup = BeautifulSoup(str(tds[1]), 'html.parser')

				artist_name = ''.join(artist_soup.a.contents)
				artist_link = artist_soup.a['href']
				genre = ' '.join(genre_soup.td.contents)
				output.write('%s\t%s\t%s\n'%(artist_name,genre, artist_link))

		count+=1

output.close()