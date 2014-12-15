import json
import httplib
import re
"""
based on
    https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&format=json
"""
def getTitle(url):

    # Find video id
    matches = re.findall("v=[a-zA-Z0-9\-_]+", url)

    # More than one is a hack
    if len(matches) != 1:
        return None

    video_id = matches[0]

    c = httplib.HTTPSConnection("www.youtube.com")
    c.request("GET", "/oembed?url=https://www.youtube.com/watch?%s&format=json" % (video_id))
    response = c.getresponse()
    if response.status == 200:
        data = response.read()
        test = json.loads(data)
        return test[u'title']
    return None

if __name__ == "__main__":
    print getTitle('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


