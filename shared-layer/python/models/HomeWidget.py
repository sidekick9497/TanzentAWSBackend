import json


class HomeWidget:
    def __init__(self):
        self.id = -1
        self._user_id = ''
        self.external_id = ''
        self._composite_id = ''
        self._widget_id = ''
        self.group_id = ''
        self.is_widget_private = False
        self.shared_to_circles = []
        self.widget_type = '-1'
        self.widget_data = '{}'

    @property
    def widget_id(self):
        return self._widget_id

    @widget_id.setter
    def widget_id(self, value):
        self._widget_id = value

    @property
    def composite_id(self):
        return self._composite_id

    @composite_id.setter
    def composite_id(self, value):
        self._composite_id = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value
    @staticmethod
    def from_json(json_string):
        try:
            data = json.loads(json_string)
            home_widget = HomeWidget()
            home_widget.id = data.get('id', -1)
            home_widget._user_id = data.get('userId', '')
            home_widget.external_id = data.get('externalId', '')
            home_widget._composite_id = data.get('compositeId', '')
            home_widget._widget_id = data.get('widgetId', '')
            home_widget.group_id = data.get('groupId', '')
            home_widget.is_widget_private = data.get('isWidgetPrivate', False)
            home_widget.shared_to_circles = data.get('sharedToCircles', [])
            home_widget.widget_type = data.get('widgetType', '-1')
            home_widget.widget_data = data.get('widgetData', '{}')
            return home_widget
        except json.JSONDecodeError:
            return None