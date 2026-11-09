# Custom infomapnode tags, introduced after upgrading to gn 4.4.x
from django import template

# Import the original library function from the mapstore client
from geonode_mapstore_client.templatetags.get_menu_json import get_base_right_topbar_menu as original_right_menu

# Import function to differentiate subsite related paths from others
from subsites.utils import extract_subsite_slug_from_request

register = template.Library()

@register.simple_tag(takes_context=True)
def check_subsite(context):
    request = context.get('request')

    if not request:
        return False

    # Extract subsite slug from request.path
    subsite_slug = extract_subsite_slug_from_request(request)

    return bool(subsite_slug)

@register.simple_tag(takes_context=True)
def get_base_right_topbar_menu(context):

    """
    Executes core menu resolution logic, dynamically injecting a Home element 
    if the context processor detects its absence inside the right panel stack.
    """
    menu_items = original_right_menu(context)
    
    # Check if a 'Home' item exists anywhere in the menu list
    has_home = any(item.get('label') == 'Home' for item in menu_items)
    
    if not has_home:
        home_link = {
            "type": "link",
            "href": "/",
            "label": "Home",
            "icon": "home",
            "order": -1 # Ensures it remains on the far left of the right cluster
        }
        menu_items.insert(0, home_link)
        
    return menu_items

