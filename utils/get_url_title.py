import urllib2
import re
"""
Author: koltrast
"""
def get_title(url):
    # Connect and get HTML doc
    response = urllib2.urlopen(url)
    html = response.read()

    # Find title
    matches = re.findall("<title>.+</title>", html)

    # Should be only one title in a HTML doc
    if len(matches) != 1:
        return None

    # Get title string
    title_str = matches[0]

    # Get rid of HTML tag
    title_str = re.sub("</?title>", "", title_str)

    return title_str.decode('utf-8')

if __name__ == "__main__":
    #print get_title('http://www.google.com')
    print get_title('https://www.google.com')
