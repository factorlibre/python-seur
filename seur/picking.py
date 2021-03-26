#This file is part of seur. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from seur.api import API

from xml.dom.minidom import parseString
import os
import datetime
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class Picking(API):
    """
    Picking API
    """
    __slots__ = ()

    def create(self, data):
        """
        Create a picking using the given data

        :param data: Dictionary of values
        :return: reference (str), label (pdf), error (str)
        """
        reference = None
        label = None
        error = None

        if self.context.get('pdf'):
            tmpl = loader.load('picking_send_pdf.xml')
        else:
            tmpl = loader.load('picking_send.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'vat': self.vat,
            'franchise': self.franchise,
            'seurid': self.seurid,
            'ci': self.ci,
            'ccc': self.ccc,
            'servicio': data.get('servicio', '1'),
            'product': data.get('product', '2'),
            'total_bultos': data.get('total_bultos', 1),
            'total_kilos': data.get('total_kilos', '1'),
            'peso_bulto': data.get('peso_bulto', '1'),
            'observaciones': data.get('observaciones', ''),
            'referencia_expedicion': data.get('referencia_expedicion', ''),
            'ref_bulto': data.get('ref_bulto', ''),
            'clave_portes': data.get('clave_portes', 'F'), # F: Facturacion
            'clave_reembolso': data.get('clave_reembolso', 'F'), # F: Facturacion
            'valor_reembolso': data.get('valor_reembolso', ''),
            'es_cambio': data.get('es_cambio', 'N'),
            'cliente_nombre': data.get('cliente_nombre', ''),
            'cliente_direccion': data.get('cliente_direccion', ''),
            'cliente_tipovia': data.get('cliente_tipovia', 'CL'),
            'cliente_tnumvia': data.get('cliente_tnumvia', 'N'),
            'cliente_numvia': data.get('cliente_numvia', '.'),
            'cliente_escalera': data.get('cliente_escalera', '.'),
            'cliente_piso': data.get('cliente_piso', '.'),
            'cliente_puerta': data.get('cliente_puerta', ''),
            'cliente_poblacion': data.get('cliente_poblacion', ''),
            'cliente_cpostal': data.get('cliente_cpostal', ''),
            'cliente_pais': data.get('cliente_pais', ''),
            'cliente_email': data.get('cliente_email', ''),
            'cliente_telefono': data.get('cliente_telefono', ''),
            'cliente_movil': data.get('cliente_movil', ''),
            'cliente_atencion': data.get('cliente_atencion', ''),
            'aviso_preaviso': data.get('aviso_preaviso', 'N'),
            'aviso_reparto': data.get('aviso_reparto', 'N'),
            'aviso_email': data.get('aviso_email', 'N'),
            'aviso_sms': data.get('aviso_sms', 'N'),
            'id_mercancia': data.get('id_mercancia', ''),
            'entrega_sabado': data.get('entrega_sabado', 'N'),
            'id_entrega_sabado': data.get('id_entrega_sabado', 'N'),
            'cod_centro': data.get('cod_centro', '')
        }

        if not self.context.get('pdf'):
            vals['printer'] = self.context.get('printer', 'ZEBRA')
            vals['printer_model'] = self.context.get('printer_model', 'LP2844-Z')
            vals['ecb_code'] = self.context.get('ecb_code', '2C')

        url = 'https://cit.seur.com/CIT-war/services/ImprimirECBWebService'
        if self.is_test_config:
            url = 'https://citpre.seur.com/CIT-war/services/'\
                'ImprimirECBWebService'
        xml = tmpl.generate(**vals).render()

        result = self.connect(url, xml)
        dom = parseString(result)

        #Get message error from XML
        mensaje = dom.getElementsByTagName('mensaje')
        if mensaje:
            if mensaje[0].firstChild.data != 'OK':
                error = mensaje[0].firstChild.data
                return reference, label, error

        #Get reference from XML
        ecb = dom.getElementsByTagName('ECB')
        if ecb:
            reference = ecb[0].childNodes[0].firstChild.data

        if self.context.get('pdf'):
            #Get PDF file from XML
            pdf = dom.getElementsByTagName('PDF')
            if pdf:
                label = pdf[0].firstChild.data
        else:
            #Get TXT file from XML
            traza = dom.getElementsByTagName('traza')
            if traza:
                label = traza[0].firstChild.data

        return reference, label, error

    def pickup_service(self, data):
        tmpl = loader.load('pickup_service.xml')

        if not self.ws_username or not self.ws_password:
            raise Exception(
                'You have not set the username and password for ws.seur.com '
                'and are necessary for a pickup service.')

        vals = {
            'username': self.ws_username,
            'password': self.ws_password,
            'nombre_empresa': data.get('nombre_empresa', ''),
            'razon_social': data.get('razon_social', ''),

            'ccc_ordenante': data.get('ccc_ordenante'),
            'pais_nif_ordenante': data.get('pais_nif_ordenante'),
            'nif_ordenante': data.get('nif_ordenante'),
            'nombre_ordenante': data.get('nombre_ordenante'),
            'apellidos_ordenante': data.get('apellidos_ordenante', '.'),
            'cp_ordenante': data.get('cp_ordenante'),
            'tipo_via_ordenante': data.get('tipo_via_ordenante', 'CL'),
            'calle_ordenante': data.get('calle_ordenante'),
            'tipo_num_ordenante': data.get('tipo_num_ordenante', 'IN'),
            'num_ordenante': data.get('num_ordenante', ''),
            'escalera_ordenante': data.get('escalera_ordenante', '.'),
            'piso_ordenante': data.get('piso_ordenante', '.'),
            'puerta_ordenante': data.get('puerta_ordenante', '.'),
            'poblacion_ordenante': data.get('poblacion_ordenante'),
            'provincia_ordenante': data.get('provincia_ordenante'),
            'pais_ordenante': data.get('pais_ordenante'),
            'idioma_ordenante': data.get('idioma_ordenante'),
            'pref_fax_ordenante': data.get('pref_fax_ordenante', ''),
            'fax_ordenante': data.get('fax_ordenante', ''),
            'mail_ordenante': data.get('mail_ordenante'),
            'pref_tel_ordenante': data.get('pref_tel_ordenante'),
            'tel_ordenante': data.get('tel_ordenante'),

            'razon_social_origen': data.get('razon_social_origen', ''),
            'nif_origen': data.get('nif_origen'),
            'nombre_origen': data.get('nombre_origen'),
            'apellidos_origen': data.get('apellidos_origen', '.'),
            'cp_origen': data.get('cp_origen'),
            'tipo_via_origen': data.get('tipo_via_origen', 'CL'),
            'calle_origen': data.get('calle_origen'),
            'tipo_num_origen': data.get('tipo_num_origen', 'IN'),
            'num_origen': data.get('num_origen', ''),
            'escalera_origen': data.get('escalera_origen', '.'),
            'piso_origen': data.get('piso_origen', '.'),
            'puerta_origen': data.get('puerta_origen', '.'),
            'poblacion_origen': data.get('poblacion_origen'),
            'provincia_origen': data.get('provincia_origen'),
            'pais_origen': data.get('pais_origen'),
            'pais_nif_origen': data.get('pais_nif_origen'),
            'pref_tel_origen': data.get('pref_tel_origen'),
            'tel_recogida_origen': data.get('tel_recogida_origen'),

            'razon_social_destino': data.get('razon_social_destino', ''),
            'nombre_destino': data.get('nombre_destino'),
            'apellidos_destino': data.get('', '.'),
            'cp_destino': data.get('cp_destino'),
            'tipo_via_destino': data.get('tipo_via_destino', 'CL'),
            'calle_destino': data.get('calle_destino'),
            'tipo_num_destino': data.get('tipo_num_destino', 'IN'),
            'num_destino': data.get('num_destino', ''),
            'escalera_destino': data.get('escalera_destino', '.'),
            'piso_destino': data.get('piso_destino', '.'),
            'puerta_destino': data.get('puerta_destino', '.'),
            'poblacion_destino': data.get('poblacion_destino'),
            'provincia_destino': data.get('provincia_destino'),
            'pais_destino': data.get('pais_destino'),
            'pref_tel_destino': data.get('pref_tel_destino'),
            'tel_destino': data.get('tel_destino'),

            'mercancia': data.get('mercancia', '2'),
            'num_bultos': data.get('num_bultos', '1'),
            'lista_bultos': data.get('lista_bultos', '1;1;1;1;1'),
            'tipo_porte': data.get('tipo_porte', 'P'),
            'producto': data.get('producto', '2'),
            'servicio': data.get('servicio', '1'),

            'dia_recogida': data.get('dia_recogida'),
            'mes_recogida': data.get('mes_recogida'),
            'anyo_recogida': data.get('anyo_recogida'),
            'hora_manana_de': data.get('hora_manana_de'),
            'hora_manana_a': data.get('hora_manana_a'),
            'hora_tarde_de': data.get('hora_tarde_de'),
            'hora_tarde_a': data.get('hora_tarde_a'),

            'ultima_recogida_dia': data.get('ultima_recogida_dia', ''),
            'tipo_recogida': data.get('tipo_recogida', 'R'),
            'tipo_envio': data.get('tipo_envio', 'N'),
            'aviso': data.get('aviso', 'N'),
            'tipo_aviso': data.get('tipo_aviso', ''),
            'entrega_nave': data.get('entrega_nave', 'N'),
            'entrega_sabado': data.get('entrega_sabado', 'N'),
            'num_referencia': data.get('num_referencia'),
            'notas': data.get('notas', ''),
            'valor_declarado': data.get('valor_declarado', '0')
        }
        url = 'https://ws.seur.com/webseur/services/WSCrearRecogida'
        if self.is_test_config:
            url = 'https://wspre.seur.com/webseur/services/WSCrearRecogida'
        xml = tmpl.generate(**vals).render()

        result = self.connect(url, xml)
        dom = parseString(result)
        try:
            info = parseString(
                dom.getElementsByTagName('out')[0].childNodes[0].data.
                encode('utf-8'))
        except:
            info = parseString(
                dom.getElementsByTagName('ns1:out')[0].childNodes[0].data.
                encode('utf-8'))
        pickup_ref = False
        pickup_num = False
        amount = False
        error_code = False
        error_description = False
        pick = info.getElementsByTagName('RECOGIDA')
        error = info.getElementsByTagName('ERROR')
        if pick:
            pickup_ref = info.getElementsByTagName('LOCALIZADOR').pop()\
                .childNodes[0].data
            pickup_num = info.getElementsByTagName('NUM_RECOGIDA').pop()\
                .childNodes[0].data
            amount = info.getElementsByTagName('TASACION').pop()\
                .childNodes[0].data
        if error:
            error_code = info.getElementsByTagName('CODIGO').pop()\
                .childNodes[0].data
            error_description = info.getElementsByTagName('DESCRIPCION')\
                .pop().childNodes[0].data
        return pickup_ref, pickup_num, amount, error_code, error_description

    def cancel_pickup(self, pickup_num, pickup_ref):
        tmpl = loader.load('pickup_service_cancel.xml')

        if not self.ws_username or not self.ws_password:
            raise Exception(
                'You have not set the username and password for ws.seur.com '
                'and are necessary for a pickup service.')

        url = 'https://ws.seur.com/webseur/services/WSCrearRecogida'
        if self.is_test_config:
            url = 'https://wspre.seur.com/webseur/services/WSCrearRecogida'
        vals = {
            'username': self.ws_username,
            'password': self.ws_password,
            'pickup_ref': pickup_ref,
            'pickup_num': pickup_num
        }
        xml = tmpl.generate(**vals).render()
        result = self.connect(url, xml)
        dom = parseString(result)
        info = dom.getElementsByTagName('ns1:out')[0].childNodes[0].data
        error = info
        # The label for success and error is the same, so we have to search
        # the word 'exito' but actually we search just 'xito' because the 'e'
        # comes with accent mark.
        if info.find('xito'):
            error = False
        return info, error

    def info(self, data):
        """
        Picking info using the given data

        :param data: Dictionary of values
        :return: info dict
        """
        tmpl = loader.load('picking_info.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'expedicion': data.get('expedicion', 'S'),
            'reference': data.get('reference'),
            'service': data.get('service', '0'),
            'public': data.get('public', 'N'),
            }

        url = 'https://ws.seur.com/webseur/services/WSConsultaExpediciones'
        xml = tmpl.generate(**vals).render()
        result = self.connect(url, xml)
        dom = parseString(result)

        #Get info
        info = dom.getElementsByTagName('ns1:out')
        return info[0].firstChild.data

    def list(self, data):
        """
        Picking list using the given data

        :param data: Dictionary of values
        :return: list dict
        """
        tmpl = loader.load('picking_list.xml')

        t = datetime.datetime.now()
        today = '%s-%s-%s' % (t.day, t.month, t.year)

        vals = {
            'username': self.username,
            'password': self.password,
            'ccc': self.ccc,
            'expedicion': data.get('expedicion', 'S'),
            'date_from': data.get('from', today),
            'date_to': data.get('to', today),
            'service': data.get('service', '0'),
            'public': data.get('public', 'N'),
            }

        url = 'https://ws.seur.com/webseur/services/WSConsultaExpediciones'
        xml = tmpl.generate(**vals).render()
        result = self.connect(url, xml)
        dom = parseString(result)

        #Get list
        info = dom.getElementsByTagName('ns1:out')
        return info[0].firstChild.data

    def label(self, data):
        """
        Get label picking using reference

        :param data: Dictionary of values
        :return: string
        """
        if self.context.get('pdf'):
            tmpl = loader.load('picking_label_pdf.xml')
        else:
            tmpl = loader.load('picking_label.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'vat': self.vat,
            'franchise': self.franchise,
            'seurid': self.seurid,
            'ci': self.ci,
            'ccc': self.ccc,
            'servicio': data.get('servicio', '1'),
            'product': data.get('product', '2'),
            'total_bultos': data.get('total_bultos', 1),
            'total_kilos': data.get('total_kilos', '1'),
            'peso_bulto': data.get('peso_bulto', '1'),
            'observaciones': data.get('observaciones', ''),
            'referencia_expedicion': data.get('referencia_expedicion', ''),
            'ref_bulto': data.get('ref_bulto', ''),
            'clave_portes': data.get('clave_portes', 'F'), # F: Facturacion
            'clave_reembolso': data.get('clave_reembolso', 'F'), # F: Facturacion
            'valor_reembolso': data.get('valor_reembolso', ''),
            'cliente_nombre': data.get('cliente_nombre', ''),
            'cliente_direccion': data.get('cliente_direccion', ''),
            'cliente_tipovia': data.get('cliente_tipovia', 'CL'),
            'cliente_tnumvia': data.get('cliente_tnumvia', 'N'),
            'cliente_numvia': data.get('cliente_numvia', '.'),
            'cliente_escalera': data.get('cliente_escalera', '.'),
            'cliente_piso': data.get('cliente_piso', '.'),
            'cliente_puerta': data.get('cliente_puerta', ''),
            'cliente_poblacion': data.get('cliente_poblacion', ''),
            'cliente_cpostal': data.get('cliente_cpostal', ''),
            'cliente_pais': data.get('cliente_pais', ''),
            'cliente_email': data.get('cliente_email', ''),
            'cliente_telefono': data.get('cliente_telefono', ''),
            'cliente_atencion': data.get('cliente_atencion', ''),
            }

        if not self.context.get('pdf'):
            vals['printer'] = self.context.get('printer', 'ZEBRA')
            vals['printer_model'] = self.context.get('printer_model', 'LP2844-Z')
            vals['ecb_code'] = self.context.get('ecb_code', '2C')

        url = 'https://cit.seur.com/CIT-war/services/ImprimirECBWebService'
        if self.is_test_config:
            url = 'https://citpre.seur.com/CIT-war/services/'\
                'ImprimirECBWebService'
        xml = tmpl.generate(**vals).render()

        result = self.connect(url, xml)
        dom = parseString(result)

        if self.context.get('pdf'):
            pdf = dom.getElementsByTagName('PDF')
            if pdf:
                return pdf[0].firstChild.data
        else:
            traza = dom.getElementsByTagName('traza')
            if traza:
                return traza[0].firstChild.data

        return None

    def manifiesto(self, data):
        """
        Get Manifiesto

        :param data: Dictionary of values
        :return: string
        """
        tmpl = loader.load('manifiesto.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'vat': self.vat,
            'franchise': self.franchise,
            'seurid': self.seurid,
            'ci': self.ci,
            'ccc': self.ccc,
        }
        if data.get('date'):
            vals['date'] = data.get('date')
        else:
            d = datetime.datetime.now()
            vals['date'] = '%s-%s-%s' % (d.year, d.strftime('%m'), d.strftime('%d'))

        url = 'https://cit.seur.com/CIT-war/services/DetalleBultoPDFWebService'
        if self.is_test_config:
            url = 'https://citpre.seur.com/CIT-war/services/'\
                'DetalleBultoPDFWebService'
        xml = tmpl.generate(**vals).render()

        result = self.connect(url, xml)
        dom = parseString(result)

        pdf = dom.getElementsByTagName('ns1:out')
        if pdf:
            return pdf[0].firstChild.data
        return

    def city(self, city):
        """
        Get Seur values from city

        :param city: string
        :return: dict
        """
        tmpl = loader.load('city.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'city': city.upper(),
            }

        url = 'https://ws.seur.com/WSEcatalogoPublicos/servlet/XFireServlet/WSServiciosWebPublicos'
        xml = tmpl.generate(**vals).render()
        result = self.connect(url, xml)

        dom = parseString(result)
        info = dom.getElementsByTagName('ns1:out')
        data = info[0].firstChild.data
        dom2 = parseString(data.encode('utf-8'))
        registros = dom2.getElementsByTagName('REGISTROS')

        total = registros[0].childNodes.length

        values = []
        for i in range(1, total+1):
            reg_name = 'REG%s' % i
            reg = registros[0].getElementsByTagName(reg_name)[0]
            vals = {}
            for r in reg.childNodes:
                vals[r.nodeName] = r.firstChild.data
            values.append(vals)

        return values

    def zip(self, zip):
        """
        Get Seur values from zip

        :param zip: string
        :return: list dict
        """
        tmpl = loader.load('zip.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'zip': zip,
            }

        url = 'https://ws.seur.com/WSEcatalogoPublicos/servlet/XFireServlet/WSServiciosWebPublicos'
        xml = tmpl.generate(**vals).render()
        result = self.connect(url, xml)

        dom = parseString(result)
        info = dom.getElementsByTagName('ns1:out')
        data = info[0].firstChild.data

        dom2 = parseString(data.encode('utf-8'))
        registros = dom2.getElementsByTagName('REGISTROS')

        total = registros[0].childNodes.length

        values = []
        for i in range(1, total+1):
            reg_name = 'REG%s' % i
            reg = registros[0].getElementsByTagName(reg_name)[0]
            vals = {}
            for r in reg.childNodes:
                vals[r.nodeName] = r.firstChild.data
            values.append(vals)

        return values
