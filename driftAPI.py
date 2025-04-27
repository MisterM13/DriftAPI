################################################################
#                                                              #
#         driftAPI by MisterM (and a bit from chatGPT)         #
#                                                              #
#         Python script to receive data logs from the          #
#         Sturmkind Drift APP via the comunity api interface   #
#         and log the data into a Mysql Database.              #
#                                                              #
#         !!! Important:  !!!                                  #
#         To set up and run, please read the readme.md         #
#                                                              #
################################################################


#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi import Request
import pymysql
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
import os

load_dotenv()


#from chatGPT ---- making a class to query the database more easy
@dataclass
class Race:
	game_id: str = None
	user_name: str = None
	event: str = None
	time: str = None
	target_code: int = None
	false_start: bool = None
	lap: int = None
	driven_distance: int = None
	driven_time: int = None
	lap_time: str = None
	score: int = None
	orientations: list = None
	total_score: int = None
	total_driven_distance: int = None
	total_driven_time: int = None
	
	def to_db_tuple(self):
		return (
			self.game_id,
			self.user_name,
			self.event,
			self.time,
			self.target_code,
			self.false_start,
			self.lap,
			self.driven_distance,
			self.driven_time,
			self.lap_time,
			self.score,
			self.orientations,
			self.total_score,
			self.total_driven_distance,
			self.total_driven_time
			
		)
#----------

#Query to insert the data
sql = "INSERT INTO race (game_id, user_name, event, time, target_code, false_start, lap, driven_distance, driven_time, lap_time, score,orientations, total_score, total_driven_distance, total_driven_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


# TODO: exception handling of database
conn = pymysql.connect(
	host=os.getenv("DB_HOST"),
	user=os.getenv("DB_USER"),
	password=os.getenv("DB_PASSWORD"),
	database=os.getenv("DB_NAME")
)
cursor = conn.cursor()

#games = [] #TODO: implement handling of multiple games
users = []
users_n = []
user_times = [] # ';flag/lap/time' flag: s= start, r=round, f=finish
cars = []
total_laps = 7
first_round = []
lap_counts = []
false_starts=[]
scores = []
game_id = "Test1"

spacer=70*"-"

#TODO: handling the case, a car gets disconnected and directly hits target without start, or makes the same race again

def getTime(formatted_lap):
	time =  formatted_lap.split("/")[2].split(" ")[1]
	h = int(time.split(":")[0])
	m = int(time.split(":")[1])
	s = float(time.split(":")[2])
	return (h,m,s)
	

def calculateLapTime(user_index):
	laps = user_times[user_index].split(";")
	if len(laps)<2:
		print("Error: No rounds finished yet.")
	else:
		(h1,m1,s1) = getTime(laps[-1])
		(h2,m2,s2) = getTime(laps[-2])
		h3 = h1-h2
		m3 = m1-m2
		s3 = s1-s2
		if s3 < 0:
			m3-=1
			s3 = 60+s3
		if m3 < 0:
			h3-=1
			m3 = 60+m3
		if len(str(h3))<2:
			h3 = "0"+str(h3)
		if len(str(m3))<2:
			m3 = "0"+str(m3)
		return str(h3)+":"+str(m3)+":"+str(s3)
	

def printStats():
	print("User","Car","false_start","laps","/","total_laps","score")
	for i in range(len(users_n)):
		print(users_n[i],cars[i],false_starts[i],lap_counts[i],"/",total_laps,scores[i])

#converting the time format to match the datetime(3) format of the db
def extractTime(time):
	database_time = time.split("T")[0]+" "+time.split("T")[1].split("Z")[0]
	return database_time
	

app = FastAPI()

def check(game_id):
	return game_id=="Test1"

@app.get("/")
def read_root():
	return {"message": "Hello, HTTPS world!"}

# Connection through ping
@app.get("/game/{game_id}/ping")
def getping(game_id):
	#check(game_id)
	return {"status":'true',"start_time":'null',"start_delay": 'null',"lap_count": total_laps,"track_condition": 'null',"track_bundle": 'null',"wheels": 'null',"setup_mode": 'null'} #TODO: get infos from stats method/file

#Enter the race
@app.post("/game/{game_id}/enter")
async def getEnter(game_id,request: Request):
	#check(game_id)
	data = await request.json()
	game_id = data.get("game_id")
	user_id = data.get("user_id")
	user_name = data.get("user_name")
	car_name = data.get("data").get("car_name")
	if user_id and user_name is not None:
		users.append(user_id)
		users_n.append(user_name)
		user_times.append("")
		if car_name is not None:
			cars.append(car_name)
		else:
			cars.append("unknown car")
		lap_counts.append(0)
		scores.append(0)
		first_round.append(True)
		false_starts.append(False)
		print(spacer,"Added new User:",user_name)
		return "OK"

#Start the race		
@app.post("/game/{game_id}/start")
async def getStart(game_id,request: Request):
	#check(game_id)
	data = await request.json()
	user_name = data.get("user_name")
	time = data.get("data").get("signal_time")
	u = users_n.index(user_name)
	user_times[u]+="s/0/"+extractTime(time)
	print(spacer,user_name,"started the race")
	race = Race(game_id=game_id, user_name=user_name, event="start",time=extractTime(time))
	cursor.execute(sql, race.to_db_tuple())
	conn.commit()
	printStats() 
	return "OK"

#Cross a target
@app.post("/game/{game_id}/target")
async def getTarget(game_id,request: Request):
	#check(game_id)
	data = await request.json()
	user_name = data.get("user_name")
	time = data.get("data").get("crossing_time")
	u = users_n.index(user_name)
	code = data.get("data").get("target_code")
	false_start=data.get("data").get("false_start")
	dd = data.get("data").get("driven_distance")
	dt = data.get("data").get("driven_time")
	orientations =data.get("data").get("orientations") #TODO: have to sort out some orientations format Problem.
	false_starts[u]=false_start
	scores[u] += data.get("data").get("score")
	#print(scores[i])
	if not first_round[u]:
		lap_counts[u]+=1
		user_times[u]+=";t/"+str(lap_counts[u])+"/"+extractTime(time)
		#print(40*"#",user_times[u])
		race = Race(game_id=game_id, user_name=user_name, 	event="target",target_code=code,false_start=false_start, time=extractTime(time),driven_distance=dd,driven_time=dt,lap=lap_counts[u],lap_time=calculateLapTime(u))
		cursor.execute(sql, race.to_db_tuple())
		conn.commit()
		printStats() 
		print(spacer,user_name,"finished a round. Round Time:",time,calculateLapTime(u))
	else:
		first_round[u]=False
		print(spacer,user_name,"went over start the first Time.")
	return "OK"


#Finished the race
@app.post("/game/{game_id}/end")
async def getEnd(game_id,request: Request):
	#check(game_id)
	data = await request.json()
	user_name = data.get("user_name")
	time = data.get("data").get("finished_time")
	u = users_n.index(user_name)
	user_times[u]+=";e/"+str(lap_counts[u])+"/"+extractTime(time)
	tot_score = data.get("data").get("total_score")
	tot_dd = data.get("data").get("total_driven_distance")
	tot_dt = data.get("data").get("total_driven_time")
	race = Race(game_id=game_id, user_name=user_name, event="end",time=extractTime(time),total_score=tot_score,total_driven_distance=tot_dd,total_driven_time=tot_dt)
	cursor.execute(sql, race.to_db_tuple())
	conn.commit()
	print(spacer,user_name,"finished the race")
	if scores[u]!=tot_score:
		#print(scores[i])
		print(spacer,"total score of",user_name,"did not equal added up score")
		scores[u]=tot_score
	printStats() 
	return "OK"