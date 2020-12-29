from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

if __name__ == "__main__":
    response = requests.get("http://www.rainer-maria-rilke.de/")
    homepage_soup = BeautifulSoup(response.content, "html.parser")
    gedichte = homepage_soup.find_all("a",href=True)
    dataframe = pd.DataFrame(columns=["ID", "Title", "Content", "Time", "Place"])
    for gedicht in gedichte:
        if re.match(r"\d+",gedicht["href"]) is not None:

            poem_url = gedicht["href"]
            print(poem_url)
            ID = re.findall(r"\d+\w*\d+",poem_url)[0]
            print(ID)
            poem_response = requests.get("http://www.rainer-maria-rilke.de/"+poem_url)
            poem_soup = BeautifulSoup(poem_response.content, "html.parser")
            try:
                headline = poem_soup.find("h1").get_text()
                print("poet headline: ",headline)
            except:
                continue
            poem_content = poem_soup.find_all("p")[1].get_text()
            poet_time_place =poem_soup.find_all("p")[-1].get_text().strip()
            #print(poet_time_place)
            time = poet_time_place.split(",")[1].strip()
            print("time: ", time)
            place = poet_time_place.split(",")[-1].strip()
            print("place: ",place)
            dataframe = dataframe.append(
                {"ID": ID,
                 "Title": headline,
                 "Content": poem_content,
                 "Time": time,
                 "Place":place},
                ignore_index=True
            )

dataframe[1:].to_csv("all_poem.csv")
