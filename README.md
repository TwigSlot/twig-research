# twig-research
Experimental crawler prototypes go here. 

## Scraping
To run the `wiki` spider,
```shell
cd twig_scraper
scrapy crawl wiki -O wiki.json
```

## Deploying Autofill Server
To deploy an autofill server,
```shell
# Note: remember to change the version from v1.0 
docker build -t tch1001/autofill_server:v1.0 . \
    -f ./api_server/Dockerfile
docker push tch1001/autofill_server:v1.0 
kubectl apply -f kubernetes/autofill-service.yaml
```