import requests
import random
import time

PAGES = ["/", "/about.php", "/redirect.php", "/error.php", "/error2.php", "/noexist.html"]

def main():
    # Wait for services to come up
    time.sleep(10)
    for x in range(0,100):
        timer = random.random()
        page_int = random.randint(0,5)
        page = PAGES[page_int]
        r = requests.get("http://nginx"+page, headers={'Connection':'close'})
        print(r)
        time.sleep(timer)

if __name__ == '__main__':
    main()
