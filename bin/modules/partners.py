from flask import request
import bin.helpers.responses.error as error_response
import bin.helpers.responses.data as data_response
import json

class PartnerHandler:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all_partner(self):
        try:
            query = 'SELECT * FROM partners'
            partners = self.mysql.query(query)
            if(len(partners) < 1) :
                return error_response.not_found('partners not found')

            return data_response.data(partners, 'Get Partners Success')
        except Exception as e:
            return error_response.internal_server(str(e))