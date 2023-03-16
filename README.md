<center><h2>Hotels Telegram Bot</h2></center>
This is basically my hot take on a skillbox exam that is about creating a bot that would serve as a pocket searcher of hotels on hotels.com. It uses two apis:

- [Hotels.com](https://rapidapi.com/apidojo/api/hotels4/)
- [Forward & Reverse Geocoding](https://rapidapi.com/GeocodeSupport/api/forward-reverse-geocoding)

The first one is obviously for querying the hotels information, and the second one is to help validating user-input city to seek for.

## Deploy

For the deploy you have to do a few things:
1. Obtain an API key for the telegram bot that is going to be used
2. Obtain an API key from the rapidapi to be used in queries to the APIs listed above as well make sure that those APIs are subscribed with account from which you get the API key from
3. GIt clone the project
4. Put both of the keys to according fields in .env file(see .env.example)
5. Run the project with `docker-compose -f docker/docker-compose.yml up`

