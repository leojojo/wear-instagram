""" This program scrapes from wear.jp """
# -*- coding: utf-8 -*-

import mechanize, os, urlparse
from BeautifulSoup import BeautifulSoup
from PIL import Image
from resizeimage import resizeimage
from InstagramAPI import InstagramAPI

USERNAME = ''    # your wear username here
INSTA_USERNAME = ''    # your instagram username here
INSTA_PASSWORD = ''   # your instagram password here
URL = 'http://wear.jp'

###### create mechanize browser #####

br = mechanize.Browser()
br.set_handle_robots( False )
br.addheaders = [('User-agent', 'Firefox')]
html = br.open(URL + '/' + USERNAME + '/')
#print html.read()



###### search page for links to coordinates #####

coord_links = {}
for link in br.links(url_regex = USERNAME + "/\d+"):
    coord_links.update({link.url : link})
#print coord_links



###### comapre with links saved in line #####

f = open("wear.txt", "a+")

### read from file
f.seek(0)
lines = f.readlines()
lines = [x.replace('\n', '') for x in lines]
#print lines

### find difference between file and page
found = set(coord_links.keys()) - set(lines)
#print found

### update file & put new links in list
new_links = {}
if found:
    for found_url in found:
        f.seek(2)
        f.write(found_url + "\n")
        new_links.update({found_url : coord_links[found_url]})
else:
    print "no new coordinates!"

#f.seek(0); print f.read()
f.close()



##### move to new link #####

for l in new_links.values():
    coord_page = br.follow_link(l)
    #print br.response().read()
    soup = BeautifulSoup(coord_page)
    img = soup.find("div", {"id":"coordinate_img"}).find("img")["src"]
    #print img



    ##### save images #####

    filename = os.path.basename(urlparse.urlsplit(img)[2])
    #print filename
    br.retrieve(img, "images/" + filename)



##### post to instagram #####

for img in os.listdir('images'):
    with open("images/" + img, 'r+b') as f:
        with Image.open(f) as image:
            cover = resizeimage.resize_cover(image, [500, 631])     #500, 631 OR 1000, 1262
            cover.save(img + '.jpg', image.format)

            i = InstagramAPI(INSTA_USERNAME, INSTA_PASSWORD)
            i.login()
            i.uploadPhoto(img+ ".jpg", "instagram caption. from wear-instagram.")
            i.logout()