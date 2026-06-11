
from django import template
from geonode_mapstore_client.templatetags.get_menu_json import get_user_menu as _get_user_menu
from geonode_mapstore_client.templatetags.get_menu_json import _get_request_user

register = template.Library()

@register.simple_tag(takes_context=True)
def get_user_menu_extended(context):
    menu = _get_user_menu(context)
    
    user = _get_request_user(context)
    if user and user.is_authenticated and user.is_superuser:
        menu_items = []
        if len(menu):
            items = menu[0]['items']
            for item in items:
                menu_items.append(item)
                if item['type'] == 'link' and item['href'] == '/admin/':
                    menu_items.append({
                        'type': 'link',
                        'href': '/catalogue/',
                        'label': 'Catalogue'
                    })
            menu[0]['items'] = menu_items
    
    return menu
