import googlemaps

gmaps = googlemaps.Client(key='AIzaSyD1gxbKg2bwRVCo_7Z-SLnmea8CGcoQCKk')
source = (36.3648284, 43.2003099)
destination = [(36.4101953, 43.1859467), (36.3648284, 43.2003099), (36.3114923, 43.1918611), (36.3631696, 43.1848604)]
result = gmaps.distance_matrix(source, destination)['rows'][0]['elements']
for item in result:
    print(item['distance']['value']/1000, 'km')




