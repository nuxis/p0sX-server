import requests

class GeekEventsImporter:
    def __init__(self, token, object_id):
        self.base_url = "https://www.geekevents.org/pickupstation/api"
        self.token = token
        self.object_id = object_id

    def get_unfetched_items(self):
        url = f"{self.base_url}/unfetched/?object={self.object_id}"
        result = requests.get(
            url,
            headers={
                "Authorization": "Token {}".format(self.token)
            }
        )

        if not result.ok:
            raise Exception("Failed to get items for GeekEvents", result.status_code, result.text)

        items_json = result.json()
        items = []

        for item_json in items_json:
            order_id = int(item_json["order"]["pk"])
            item_id = int(item_json["id"])
            amount = round(float(item_json["order"]["sum"]))
            badge = item_json["user"]["usercard"]
            first_name = item_json["user"]["first_name"]
            last_name = item_json["user"]["last_name"]

            items.append(GeekEventsItem(order_id, item_id, badge, first_name, last_name, amount))

        return items

    def mark_as_fetched(self, id):
        url = f"{self.base_url}/{id}/fetch/?object={self.object_id}"
        result = requests.post(
            url,
            headers={
                "Authorization": "Token {}".format(self.token)
            }
        )

        return result.ok

class GeekEventsItem:
    def __init__(self, order_id, item_id, badge, first_name, last_name, amount):
        self.order_id = order_id
        self.item_id = item_id
        self.badge = badge
        self.first_name = first_name
        self.last_name = last_name
        self.amount = amount