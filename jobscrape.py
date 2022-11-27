import bs4 as soup
import requests_html as rh
import json
import pandas as pd

with open('spl.json') as file:
    searchpayload  = json.load(file)


def get_data(spl):
    mysession = rh.HTMLSession()
    mysession.get('https://www.jobserve.com/gb/en/mob/Home/EnableCookie')
    r = mysession.post('https://www.jobserve.com/gb/en/mob/jobsearch',data = spl)
    mysoup = soup.BeautifulSoup(r.content,'lxml')
    myshid = mysoup.find('link').attrs['href'][28:]

    return mysession, myshid

def has_numbers(inputString):
    # necessary for a bodge later
    return any(char.isdigit() for char in inputString)

def main():
    
    session, shid = get_data(searchpayload)
    pagenum = 0
    idlist = []

    while True:

        pagenum = pagenum + 1 
        scrollpayload = {
            "page":pagenum,
            "shid":shid
            }

        r = session.post('https://www.jobserve.com/gb/en/mob/joblist/jobs',data = scrollpayload)        

        try:
            myjson = r.json()
            for i in myjson['items']:
                idlist.append(i['jobID'])
        except:
            break
    
    print("Search complete, "+ str(len(idlist))+" Jobs found")

    base="https://www.jobserve.com/gb/en/mob/job/"

    tuplelist = []

    for i in idlist:
        r = session.get(base+i)
        mysoup = soup.BeautifulSoup(r.content,'lxml')
        title = mysoup.select_one("#cnt > article > header > h3").text

        # forgive me for what I am about to do...
        salparent = mysoup.select_one('#cnt > article > div > div.jobinfo')
        sal = ""
        children = salparent.findChildren()
        for child in children:
            # oh god...
            if ("Rate" in child.text) and (has_numbers(child.text)):
                sal = child.text[12:]
            
        #sal = mysoup.select_one('#cnt > article > div > div.jobinfo > div:nth-child(4)').text
        desc = mysoup.select_one('#cnt > article > div > div.jobdesc').text

        mytuple = (i, title.strip(), sal.strip(), desc.strip())
        tuplelist.append(mytuple)

        # yes i'm accumulating a dataframe in a For
        # I'll convert it to a tuple arrangement later
        

    out = pd.DataFrame(data = tuplelist, columns=['jid','title','sal','desc'])

    out = out.set_index('jid')
    out.to_csv('jobs.csv')



if __name__ == '__main__':
    main()