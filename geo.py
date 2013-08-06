import math

def distance(pt0, pt1, miles=True):
    """Return the distance between two points, specified (lon, lat), in miles (or kilometers)"""
    LON, LAT = 0, 1
    pt0 = math.radians(pt0[LON]), math.radians(pt0[LAT])
    pt1 = math.radians(pt1[LON]), math.radians(pt1[LAT])
    lon_delta = pt1[LON] - pt0[LON]
    lat_delta = pt1[LAT] - pt0[LAT]
    a = math.sin(lat_delta / 2)**2 + math.cos(pt0[LAT]) * math.cos(pt1[LAT]) * math.sin(lon_delta / 2)**2    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = 6371 * c # radius of Earth in km
    if miles:
        d *= 0.621371192
    return d

def project(pt):
    """ Project a (lon, lat) point to x,y space using the Mercator projection
        http://wiki.openstreetmap.org/wiki/Mercator#Python_Implementation        
    """    
    def merc_x(lon):
        r_major = 6378137.000
        return r_major * math.radians(lon)
    def merc_y(lat):
        if lat > 89.5:
            lat = 89.5
        if lat < -89.5:
            lat = -89.5
        r_major = 6378137.000
        r_minor = 6356752.3142
        temp = r_minor / r_major
        eccent = math.sqrt(1 - temp**2)
        phi = math.radians(lat)
        sinphi = math.sin(phi)
        con = eccent * sinphi
        com = eccent / 2
        con = ((1.0 - con) / (1.0 + con))**com
        ts = math.tan((math.pi / 2 - phi) / 2) / con
        y = (0 - r_major) * math.log(ts)
        return y 
    return merc_x(pt[0]), merc_y(pt[1])   

def geohash_encode(pt):
    """Geohash a point (lon, lat)"""
    import geohash
    return geohash.encode(pt[1], pt[0])
    
def geohash_decode(string):
    """Decode a geohash into a point (lon, lat)"""
    import geohash
    return geohash.decode(string)

def heading(pt0, pt1):
    """Returns the angle between two points, in degrees"""
    degrees = math.degrees(math.atan2(float(pt1[0] - pt0[0]), float(pt1[1] - pt0[1])))
    if degrees < 0:
        degrees += 360
    return degrees

def angular_difference(deg0, deg1):
    """Return the difference between two angles in positive degrees"""
    result = abs(deg0 - deg1)
    if result > 180:
        result = abs(360 - result)
    return result    
