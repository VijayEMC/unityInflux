from unity import Unity
import pprint
import json

params = {'unity_hostname' : '10.4.44.50', 'unity_password': 'Password#1', 'unity_username' : 'admin'}
newUnity = Unity(params)
sess = newUnity.startSession()

#print(newUnity._getMsg(newUnity._doGet("/api/types/metric/instances")))
#print (newUnity._getMsg(newUnity._doGet("/api/instances/metric/14595")))

# GET LIST OF METRICS WITH NAMES, PATH, DESCRIPTION, ETC.
response = newUnity._getMsg(newUnity._doGet("/api/types/metric/instances?fields=name,path,isRealtimeAvailable,description,unitDisplayString"))
                    
# EXTRACT METRICS FROM RESPONSE AND PLACE IN ARRAY
entryObj = []
for i in response['entries']:
    newEntry = i['content']
    entryObj.append(newEntry)
    
# PRINT OUT METRICS THEN ASK USER TO SELECT METRIC
print("Available Metrics: ")

for i in entryObj:    
    print(str(i['id']) + ": " + i['name'] + ": " + i['description'] + ": Real Time Avail? " + str(i['isRealtimeAvailable']))

print("\n\n\n")
metricInput = input("Please enter a metric ID: ")

# GET SPECIFIC METRIC PATH
userMetric = newUnity._getMsg(newUnity._doGet("/api/instances/metric/" + metricInput))


# CREATE POST BODY FOR POST REQUEST
paths = []
paths.append(userMetric['content']['path'])
postBody = {}
postBody["paths"] = paths
postBody["interval"] = 5

# SEND POST REQUEST
respMessage = newUnity._getMsg(newUnity.unityPost("https://10.4.44.50/api/types/metricRealTimeQuery/instances", json.dumps(postBody)))
#print(respMessage)

# GET QUERY ID
queryId = respMessage['content']['id']
#print(queryId)

# GET METRIC REPORT
ourMetric = newUnity._getMsg(newUnity._doGet("/api/types/metricQueryResult/instances?filter=queryId eq " + str(queryId)))
print(ourMetric)


