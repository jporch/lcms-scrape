import urllib.request
from urllib.error import HTTPError
from lxml import html
import os
import time
import json

def get_church(state,church):
    url = f"http://locator.lcms.org/nchurches_frm/{church}"
    
    
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    tree = html.fromstring(resp.read())

    id = church.split("?")[1]
    if "C" in id:
        url2 = f"http://locator.lcms.org/nchurches_frm/c_data1.asp?{id}"
        try:
            urllib.request.urlretrieve(url2,"stats"+os.path.sep+state+os.path.sep+id+".csv")
        except HTTPError as e:
            with open("stats"+os.path.sep+state+os.path.sep+id+".csv","w") as f:
                f.write("ERROR no stats")


    name_raw = tree.xpath('//h2/text()')
    address_raw = tree.xpath('//div[@class="gutter"]//p/text()')
    organized_raw = tree.xpath('//table//td[@align="right"]//span/text()')
    school_raw = tree.xpath('//div[@class="note"]/text()')
    name = name_raw[0] if len(name_raw)>0 else "~~~"
    if "sat_detail" in church:
        address = (address_raw[0]+address_raw[1]).replace("\r","").replace("\n","")
    else:
        address =  address_raw[0] if len(address_raw)>0 else ",~~~,~~~,~~~"
    organized =  organized_raw[0] if len(organized_raw)>0 else "~~~"
    school =  "YES" if len(school_raw) > 0 and "Related School(s):" in school_raw[0] else "NO"
    if len(str.split(address,",")) >=4:
        city = str.split(address,',')[1].strip()
        state = str.split(address,',')[2].strip()
        zip = str.split(address,',')[3].strip()
        return ",".join([id, name, organized, school, city, state, zip, url])
    else:
        return ",".join([id, name, organized, school, address.strip().replace(",","."), "---","---", url])



def get_state(state):
    url = "http://locator.lcms.org/nchurches_frm/c_summary.asp"
    params = {"state":state}
    data = urllib.parse.urlencode(params)
    data = data.encode('utf-8')
       
    req = urllib.request.Request(url,data)
    resp = urllib.request.urlopen(req)
    tree = html.fromstring(resp.read())
    churches_raw = tree.xpath('//a[@title="View record in detail"]')
    churches = []
    for church in churches_raw:
        if church.attrib['href'] not in churches:
            churches.append(church.attrib['href'])
    if len(churches) > 0 and not os.path.exists("stats"+os.path.sep+state):
        os.mkdir("stats"+os.path.sep+state)
    results = []
    for church in churches:
        res = get_church(state,church)
        print(res)
        results.append(res)
    return results

states = ["AL","AK","AB","AZ","AR","BC","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","MB","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NB","NH","NJ","NM","NY","NF","NC","ND","NT","NS","OH","OK","ON","OR","PA","PE","QC","RI","SK","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","YK"]
#states = ["AZ"]
results = {}
for state in states:
    print(state)
    results[state] = get_state(state)

with open("lcms.csv", "w") as f:
    f.write("ID,Name,Organized,School,City,State,ZIP\n")
    for state in results:
        for res in results[state]:
            f.write(res+'\n')




