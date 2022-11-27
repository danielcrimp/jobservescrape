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



def main():
    
    out = pd.DataFrame(columns=['jid','title','sal','desc'])
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



    # next, just need to For loop this for all IDs, extract salary and Job desc, and that should give us a
    # dataset from which we can do datasciencey stuff.

    base="https://www.jobserve.com/gb/en/mob/job/"

    for i in idlist:
        r = session.get(base+i)
        mysoup = soup.BeautifulSoup(r.content,'lxml')
        title = mysoup.select_one("#cnt > article > header > h3").text
        sal = mysoup.select_one('#cnt > article > div > div.jobinfo > div:nth-child(4)').text
        desc = mysoup.select_one('#cnt > article > div > div.jobdesc').text

        mydict = {
            'jid':i,
            'title':title,
            'sal':sal,
            'desc':desc
        }

        ddf = pd.DataFrame([mydict])

        out = pd.concat([out, ddf])

    out.to_csv('jobs.csv')



if __name__ == '__main__':
    main()