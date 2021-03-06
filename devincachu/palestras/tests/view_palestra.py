# -*- coding: utf-8 -*-
import unittest

from django.conf import settings
from django.core import management
from django.test import client
from django.views.generic import detail
from lxml import html

from palestras import models, views


class PalestraViewTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        management.call_command("loaddata", "palestrantes", "palestras", verbosity=0)

    @classmethod
    def tearDownClass(cls):
        management.call_command("flush", verbosity=0, interactive=False)

    def setUp(self):
        factory = client.RequestFactory()
        self.request = factory.get("/programacao/hannibal-lecter/vito-corleone/escalando-aplicacoes-django/")

    def test_deve_herdar_de_DetailView(self):
        assert issubclass(views.PalestraView, detail.DetailView)

    def test_model_deve_ser_Palestra(self):
        self.assertEquals(models.Palestra, views.PalestraView.model)

    def test_context_object_name_deve_ser_palestra(self):
        self.assertEquals("palestra", views.PalestraView.context_object_name)

    def test_deve_renderizar_template_palestra_html(self):
        self.assertEquals("palestra.html", views.PalestraView.template_name)

    def test_deve_buscar_palestra_pelo_slug_informado(self):
        palestra = models.Palestra.objects.get(pk=3)
        view = views.PalestraView()
        view.kwargs = {u"slug": palestra.slug, u"palestrantes": "james-bond"}
        self.assertEquals(palestra, view.get_queryset()[0])

    def test_deve_verificar_se_os_palestrantes_passados_realmente_sao_os_palestrantes_da_palestra(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView()
        view.kwargs = {u"slug": palestra.slug, u"palestrantes": "chico-buarque"}
        self.assertEquals([], list(view.get_queryset()))

    def test_deve_retornar_apenas_uma_palestra_quando_tem_dois_palestrantes(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView()
        view.kwargs = {u"slug": palestra.slug, u"palestrantes": "hannibal-lecter/vito-corleone"}
        self.assertEquals(1, view.get_queryset().count())

    def test_deve_definir_canonical_url(self):
        palestra = models.Palestra.objects.get(pk=1)
        esperado = "%s/programacao/hannibal-lecter/vito-corleone/%s/" % (settings.BASE_URL, palestra.slug)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(esperado, dom.xpath('//link[@rel="canonical"]')[0].attrib["href"])

    def test_deve_definir_meta_keywords(self):
        palestra = models.Palestra.objects.get(pk=1)
        esperado = u"dev in cachu 2012, palestra, %s, %s" % (palestra.titulo, palestra.nomes_palestrantes().replace(" e ", ", "))
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(esperado, dom.xpath('//meta[@name="keywords"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_definir_meta_description(self):
        palestra = models.Palestra.objects.get(pk=1)
        esperado = palestra.descricao
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(esperado, dom.xpath('//meta[@name="description"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_definir_og_title_com_titulo_da_palestra(self):
        palestra = models.Palestra.objects.get(pk=1)
        esperado = palestra.titulo
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(esperado, dom.xpath('//meta[@property="og:title"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_definir_og_type_como_activity(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals("activity", dom.xpath('//meta[@property="og:type"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_definir_og_url_com_url_da_palestra(self):
        palestra = models.Palestra.objects.get(pk=1)
        esperado = "%s/programacao/hannibal-lecter/vito-corleone/%s/" % (settings.BASE_URL, palestra.slug)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(esperado, dom.xpath('//meta[@property="og:url"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_usar_foto_do_primeiro_palestrante_como_og_image(self):
        palestra = models.Palestra.objects.get(pk=1)
        palestrante = palestra.palestrantes.all()[:1].get()
        esperado = "%s%s" % (settings.MEDIA_URL, palestrante.foto)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(esperado, dom.xpath('//meta[@property="og:image"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_usar_devincachu_como_og_sitename(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals("Dev in Cachu 2012", dom.xpath('//meta[@property="og:site_name"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_ter_og_description_com_descricao_da_palestra(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals(palestra.descricao, dom.xpath('//meta[@property="og:description"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_ter_og_locale_pt_BR(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals("pt_BR", dom.xpath('//meta[@property="og:locale"]')[0].attrib["content"].encode("iso-8859-1"))

    def test_deve_usar_fb_app_id_apropriado(self):
        palestra = models.Palestra.objects.get(pk=1)
        view = views.PalestraView.as_view()
        response = view(self.request, slug=palestra.slug, palestrantes=u"hannibal-lecter/vito-corleone")
        response.render()
        dom = html.fromstring(response.content)
        self.assertEquals("220413784720358", dom.xpath('//meta[@property="fb:app_id"]')[0].attrib["content"].encode("iso-8859-1"))
