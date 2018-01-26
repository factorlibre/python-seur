#This file is part of seur. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from xml.dom.minidom import parseString
import urllib.request, urllib.error, urllib.parse
import os
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class API(object):
    """
    Generic API to connect to seur
    """
    __slots__ = (
        'url',
        'username',
        'password',
        'vat',
        'franchise',
        'seurid',
        'ci',
        'ccc',
        'context',
        'ws_username',
        'ws_password',
        'is_test_config',
    )

    def __init__(self, username, password, vat, franchise, seurid, ci, ccc,
                 ws_username=False, ws_password=False, is_test_config=False,
                 context={}):
        """
        This is the Base API class which other APIs have to subclass. By
        default the inherited classes also get the properties of this
        class which will allow the use of the API with the `with` statement

        Example usage ::

            from seur.api import API

            with API(username, password, vat, franchise, seurid, ci, ccc) as seur_api:
                return seur_api.test_connection()

        :param username: API username of the Seur Web Services. Used for
                         cit.seur.com webservice (generate labels)
        :param password: API password of the Seur Web Services. Used for
                         cit.seur.com webservice (generate labels)
        :param vat: company vat
        :param franchise: franchise code
        :param seurid: identification description
        :param ci: franchise code
        :param ccc: identification description
        :param is_test_config: indicates if is a test in order to use the
                               SEUR's pre-production server
        :param ws_username: API username of the Seur Web Services. Used for
                            ws.seur.com webservice (pickup services)
        :param ws_password: API password of the Seur Web Services. Used for
                            ws.seur.com webservice (pickup services)
        """
        self.username = username
        self.password = password
        self.vat = vat
        self.franchise = franchise
        self.seurid = seurid
        self.ci = ci
        self.ccc = ccc
        self.context = context
        self.ws_username = ws_username
        self.ws_password = ws_password
        self.is_test_config = is_test_config

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self

    def set_ws_login(self, ws_username, ws_password):
        """
        Set the API username and password of the Seur Web Services used for
        ws.seur.com webservice (pickup services). Not confuse with the
        username/password for cit.seur.com.

        :param ws_username: username for ws.seur.com
        :param ws_password: password for ws.seur.com
        """
        self.ws_username = ws_username
        self.ws_password = ws_password

    def connect(self, url, xml):
        """
        Connect to the Webservices and return XML data from seur

        :param url: url service.
        :param xml: XML data.
        
        Return XML object
        """
        xml = xml.encode('utf-8')
        headers={}
        request = urllib.request.Request(url, xml, headers)
        response = urllib.request.urlopen(request)
        return response.read()

    def test_connection(self):
        """
        Test connection to Seur webservices
        Send XML to Seur and return error send data
        """
        tmpl = loader.load('test_connection.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'vat': self.vat,
            'franchise': self.franchise,
            'seurid': self.seurid,
            }

        url = 'http://cit.seur.com/CIT-war/services/ImprimirECBWebService'
        if self.is_test_config:
            url = 'http://citpre.seur.com/CIT-war/services/ImprimirECBWebService'
        xml = tmpl.generate(**vals).render()
        result = self.connect(url, xml)
        dom = parseString(result)

        #Get message connection
        #username and password wrong, get error message
        #send a shipment error, connection successfully
        message = dom.getElementsByTagName('mensaje')
        if message:
            msg = message[0].firstChild.data
            if msg == 'ERROR':
                return 'Connection successfully'
            return msg
        return 'Not found message attribute from %s XML' % method
