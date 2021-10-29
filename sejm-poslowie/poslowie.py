import requests
import bs4
import pandas as pd

res_list = []
for _id in range(1, 461):
    url = f"https://www.sejm.gov.pl/sejm9.nsf/posel.xsp?id={_id:03d}&type=A"
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    })

    dom = bs4.BeautifulSoup(response.text)
    data = dom.find("div", {"id": "title_content"})
    name = data.find("h1").text
    single_pos = {"name": name}


    email, email_div = None, dom.find("p", {"id": "PoselEmail"})
    if email_div:
        email = email_div.next_sibling.find("a").get("href").\
            replace(" ","").replace("DOT",".").replace("AT","@")[1:]
    single_pos["email"] = email

    sections = data.find_all("ul", {"class": "data"})
    for section in sections:
        items = section.findAll("li")
        parse_end = False
        for item in items:
            attr = list(item.children)[0].text[:-1]
            val = list(item.children)[1].text.replace("\xa0", " ")
            print(attr, val)
            single_pos[attr] = val

            if "Zawód" in attr:
                parse_end = True
                break
        if parse_end:
            break

    res_list.append(single_pos)
    print(f"#### {_id} #####")

df = pd.DataFrame(res_list)
df.to_csv("poslowie.csv", index=False)
