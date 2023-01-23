##Parsing basic twitter account information without api (Requests)

For cases when the twitter api limit is not enough, you can use this code. It sends requests through the **Requests** library.

The result of the work is displayed using the **Fast API** - you can use it for your web application or use it directly via *http://127.0.0.1:8000/docs* (Automatic Documentation)

Installation:

> Download the code in any way
> pip install -r twitter_parser\requirements.txt
> Configure the proxy in the .env file, if required

Implemented 4 endpoints details for each are on the page http://127.0.0.1:8000/docs