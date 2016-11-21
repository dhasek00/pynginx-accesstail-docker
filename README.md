# pynginx-accesstail-docker
Dockerized version of the pynginx-accesstail

This will build and run containers to do the following:

1. Run NGINX with PHP-FPM
2. Run python instance of tail.py
3. Run python instance of gentraffic.py

Gentraffic will send requests to the Nginx server 100 times at random intervals.
This is used to test the tail.py script.

Output can be viewed at /var/log/stats.log

## USAGE
### docker-compose is required

From pynginx-accesstail-docker directory

> docker-compose up -d

