


> Written with [StackEdit](https://stackedit.io/) 

# driftAPI Script

### About:
This script was build to easily receive the data from the Dr!ft App over the Drift Comunity API and log them into an MySQL database.

### Setup:

1. Create a [MySQL](https://www.mysql.com) Database.
2. Create following table with an sql query:
```sql
create  Table  race (log_id INT AUTO_INCREMENT PRIMARY KEY, game_id varchar(50) not null, user_name varchar(50) not null, `event`  varchar(50),`time` datetime(3), target_code int, false_start bool,lap int, driven_distance int, driven_time int, lap_time time(3), score int, orientations json, total_score int, total_driven_distance int, total_driven_time int );
```
3. Create an .env File inside the Project Folder with the access data to the Database:
```
DB_HOST=<hostadress>
DB_USER=<database username>
DB_PASSWORD=<password>
DB_NAME=<database name>
 ```
4. Open a Terminal from the Project Folder and install the Python requirements with:
`pip install -r requirements.txt`
5. Open a Terminal from the Project Folder and run: `ngrok http 8001`
6. Open a Terminal from the Project Folder and run: `uvicorn driftAPI:app --host 0.0.0.0 --port 8001`
On success it displays some infos and: `Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)`
7. Now open the Dr!ft App -> Play ->Race -> Community API on:
```
Username: <your name>
URL: <https://...ngrok-free.app/game>
Game ID: <Test1>
```
If there's a green tick in the App, your're all good.

#### With self signed Certificates without ngrok
You can also try to run the Script with self signed Certificates. However I couldn't manage to run it, because the App probably don't accept self signed certificates. However if you want to try:
1. Open a Terminal from the Project Folder and Generate the Keys with:
`openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`
2. Run the script with:
`uvicorn driftAPI:app --host 0.0.0.0 --port 8001 --ssl-keyfile=key.pem --ssl-certfile=cert.pem`

### Limitations:

- [ ] no settings for the cars/races yet
- [ ] handles only one race at the time
- [x]  calculations of the lap durations
- [x] one instance to collect all the data from start, target and end
- [ ] problem with collecting the orientations data
- [x] on time status printouts
- [x] logging the stats into a database   
- [ ] no webui 
- [ ] no app
- [ ] no csv export


### License
This Project is free to use and modify under the [GPL](https://www.gnu.org/licenses/gpl-3.0.html).
 Have fun with your cars ;-)
 
