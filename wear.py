# -*- coding: utf-8 -*-
""" This program scrapes from wear.jp and posts to instagram """

import mechanize, os, sys, urlparse
from BeautifulSoup import BeautifulSoup
from PIL import Image
from resizeimage import resizeimage
from InstagramAPI import InstagramAPI

URL = 'http://wear.jp'
USERNAME = ''

INSTA_USERNAME = ''
PASSWORD = ''
comments = ' '

###### create mechanize browser #####

br = mechanize.Browser()
br.set_handle_robots( False )
br.addheaders = [('User-agent', 'Firefox')]
html = br.open(URL + '/' + USERNAME + '/')
#print html.read()



###### search page for links to coordinates #####

coord_links = {}
for link in br.links(url_regex = USERNAME + '/\d+'):
    coord_links.update({link.url : link})
#print coord_links



###### comapre with links saved in line #####

f = open('wear.txt', 'a+')

### read from file
f.seek(0)
lines = f.readlines()
lines = [x.replace('\n', '') for x in lines]
#print lines

### find difference between file and page
found = set(coord_links.keys()) - set(lines)
#print found

### update file & put new links in list
new_links = []
if found:
    for found_url in found:
        f.seek(2)
        f.write(found_url + '\n')
        new_links.append(coord_links[found_url])
        #print new_links
else:
  f.close()
  print 'no new coordinates!'
  sys.exit()

#f.seek(0); print f.read()
f.close()



##### move to new link #####

print 'collecting new coordinates...'
txt = []
for l in new_links:
    print l.url
    coord_page = br.follow_link(l)
    #print br.response().read()
    soup = BeautifulSoup(coord_page)
    img = soup.find('div', {'id':'coordinate_img'}).find('img')['src']
    content_txt = soup.find('p', {'class':'content_txt'}).text.encode('utf-8')
    print content_txt
    txt.insert(0, content_txt)



    ##### save images #####

    filename = os.path.basename(urlparse.urlsplit(img)[2])
    print filename
    br.retrieve(img, "images/" + filename)



##### post to instagram #####

print 'posting to instagram...'
for idx, img in enumerate(os.listdir('images')):
    with open("images/" + img, 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [500, 631])     #500, 631 OR 1000, 1262
            cover.save("images/" + img, image.format)

            #try:
            i = InstagramAPI(INSTA_USERNAME, PASSWORD)
            i.login()
            i.uploadPhoto("images/" + img, txt[idx] + comments)
            i.logout()
            #except Exception as e:
              #print 'message:' + e.message
            #else:
            print img + ' successfully posted!'
    os.remove('images/' + img)
