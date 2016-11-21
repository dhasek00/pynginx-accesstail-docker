import requests
import random
import time

PAGES = ["/", "/about.php", "/redirect.php", "/error.php", "/error2.php", "/noexist.html"]

def main():
    for x in range(0,100):
        timer = random.random()
        page_int = random.randint(0,5)
        page = PAGES[page_int]
        r = requests.get("http://nginx"+page, headers={'Connection':'close'})
        print(r)
        time.sleep(timer)

if __name__ == '__main__':
    main()
