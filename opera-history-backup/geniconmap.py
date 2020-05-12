"""
The script generating the list of html icons of the visisted sites
based on the collected history and opera favicons cache.

Note: Opera browser must be closed during the runtime, unfortunatelly.
"""

from sqlite3 import Connection
import sqlite3
from os.path import expanduser

###############################################################################
FAVICONS_DB = expanduser("~") + "/.config/opera/Favicons"
HISTORY_DB = "history.db"
OUTFILE = "ficonmap.html"
###############################################################################

def load_favicons():
    """ Loads the dict url -> favicon_url from the opera cache. """

    with sqlite3.connect(FAVICONS_DB) as conn:
        cursor = conn.cursor()

        sql = """SELECT icon_mapping.page_url AS site_url, favicons.url AS favicon_url 
                FROM icon_mapping INNER JOIN favicons ON favicons.id = icon_mapping.icon_id"""

        result = cursor.execute(sql)
        conn.commit()

        return dict(map(lambda r: (r[0], r[1]), result))

#favicons = load_favicons()
#print(len(favicons))

def load_sites():
    """ Loads the list {url, server, title} from the collected history file """

    with sqlite3.connect(HISTORY_DB) as conn:
        cursor = conn.cursor()

        sql = """SELECT url, server, title FROM history
                ORDER by date_spec, time"""

        result = cursor.execute(sql)
        conn.commit()

        return list(map(lambda r: {'url': r[0], 'server': r[1], 'title': r[2]}, result))

#sites = load_sites()
#print(len(sites))

def add_favicons_to_sites(favicons, sites):
    """ Adds the favicon url to each site (mutably, no return) """

    for site in sites:
        if site['url'] in favicons.keys():
            site['favicon'] = favicons[site['url']]
        else:
            site['favicon'] = None


#add_favicons_to_sites(favicons, sites)
#print(str(sites))

def render_site(site):
    """ Returns the html content of one site to be shown (the icon) """

    return """
        <a href="{0}" title="{1}" target="_blank">
            <img src="{2}" alt="{3}$>
        </a>
    """.format(site['url'], site['title'], site['favicon'], "&#x2717")

def render_the_html(sites):
    """ Returns the html of the whole html file """

    return '''
<html>
    <head>
        <title>favicons map!</title>
        <style>
            img {{ width: 16px; height: 16px; }}
            a {{ text-decoration: none; }}
        </style>
    </head>
    <body>
        {0}
    </body>
</html>
    '''.format("".join(list(map(lambda s: render_site(s), sites))))

#sites = [{'url': 'http://localhost/any', 'server': 'localhost', 'favicon': 'icon.ico', 'title': 'Local host!'}]
#html = render_the_html(sites)
#print(html)


def render_to_file(sites):
    """ Renders the given sites and saves to output file """

    with open(OUTFILE, 'wt') as handle:
        html = render_the_html(sites)
        handle.write(html)

###############################################################################

def runit():
    """ Runs the load and export. """

    favicons = load_favicons()
    sites = load_sites()

    add_favicons_to_sites(favicons, sites)

    render_to_file(sites)

if __name__ == '__main__':
    runit()
