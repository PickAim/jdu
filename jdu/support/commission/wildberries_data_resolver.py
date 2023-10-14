from jser.JserResolver.information_resolver import JserInformationResolver


class WildberriesDataResolver(JserInformationResolver):
    def __init__(self):
        super().__init__()

    def mapping_warehouse_data(self):
        # TODO Yeah, i didn't want to make jorm dependent on jser
        warehouses_data = self._warehouse_data['result']['resp']['data']
        warehouse_dict: dict[int, any] = {}
        for data in warehouses_data:
            template_dict = {}
            template_dict['name'] = data['warehouse']
            template_dict['address'] = data['address']
            template_dict['isFbs'] = data['isFbs']
            template_dict['isFbw'] = data['isFbw']
            template_dict['rating'] = data['rating']
            warehouse_dict[data['id']] = template_dict
        return warehouse_dict

    def get_data_for_warehouse(self, id: int):
        mapping_warehouse = self.mapping_warehouse_data()
        return {id: mapping_warehouse[id]}
