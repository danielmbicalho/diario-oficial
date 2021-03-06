# -*- coding: utf-8 -*-
from dateparser import parse
import datetime as dt
import json
import scrapy

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class SpFrancaSpider(BaseGazetteSpider):
    TERRITORY_ID = '3516200'
    name = 'sp_franca'
    allowed_domains = ['franca.sp.gov.br']
    start_urls = ['http://www.franca.sp.gov.br/pmf-diario/rest/diario/init']
    document_date_url = 'http://www.franca.sp.gov.br/pmf-diario/rest/diario/buscaPorArquivo/{}'
    documents_url = 'http://www.franca.sp.gov.br/arquivos/diario-oficial/documentos/{}'

    def parse(self, response):
        """
        @url http://www.franca.sp.gov.br/pmf-diario/rest/diario/init
        @returns requests 10
        """
        dates = set(json.loads(response.body_as_unicode()))

        start_date = dt.date(2015, 1, 1)
        delta = dt.timedelta(days=1)
        while start_date <= dt.date.today():
            if '{d.month}-{d.day}-{d.year}'.format(d=start_date) in dates:
                url = self.document_date_url.format(start_date.strftime('%d-%m-%Y'))
                yield scrapy.Request(url, self.parse_document)

            start_date += delta

    def parse_document(self, response):
        """
        @url http://www.franca.sp.gov.br/pmf-diario/rest/diario/buscaPorArquivo/03-01-2018
        @returns items 1
        @scrapes date file_urls is_extra_edition territory_id power scraped_at
        """
        items = []

        document = json.loads(response.body_as_unicode())[0]
        date = dt.date.fromtimestamp(document['data'] / 1000)
        url = self.documents_url.format(document['nome'])

        items.append(
            Gazette(
                date=date,
                file_urls=[url],
                is_extra_edition=False,
                territory_id=self.TERRITORY_ID,
                scraped_at=dt.datetime.utcnow(),
                power='executive'
            )
        )

        return items
