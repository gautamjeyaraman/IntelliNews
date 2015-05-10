from cyclone.web import URLSpec
from cyclone_server import views
from cyclone_server import api


def munge_route_list(rl):
    new_l = []
    for item in rl:
        if isinstance(item, list):
            new_l.extend(munge_route_list(item))
        else:
            new_l.append(item)
    return new_l


routes = munge_route_list([
    URLSpec(r'/', views.IndexHandler),
    URLSpec(r'/home', views.HomeViewHandler),
    URLSpec(r'/document/([0-9]+)', views.DocumentViewHandler),
    URLSpec(r'/search/(.*)', views.SearchViewHandler),

    URLSpec(r'/api/latest/sample', api.SampleHandler)
])
