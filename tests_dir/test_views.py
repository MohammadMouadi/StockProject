from django.http import JsonResponse
from django.test import TestCase, Client
from django.urls import reverse
from  myapp.models import Stock
from django.contrib.auth.models import User
import json
class BaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('index')
        self.single_stock_url = reverse('single_stock', args=['AAPL'])
        self.historic_url = reverse('single_stock_historic', args= ['AAPL'])
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user={
            'firstname': 'Alaa',
            'lastname': 'Yahia',
            'email':'alaa.yahia.1995@gmail.com',
            'password':'rails7777',
        }
        return super().setUp()

class TestViews(BaseTest):

    def test_project_home_list_GET(self):
        response = self.client.get(self.home_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    #top_rank #title #data?


    def test_project_single_stock_GET(self):
        response = self.client.get(self.single_stock_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'single_stock.html')
    #title #data


    def test_project_historic_GET(self):
        response = self.client.get(self.historic_url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
    #data


class RegisterTest(BaseTest):
   def test_can_view_page_correctly(self):
       response=self.client.get(self.register_url)
       self.assertEqual(response.status_code,200)
       self.assertTemplateUsed(response,'register.html')

   def test_can_register_user(self):
        response=self.client.post(self.register_url,self.user,format='text/html')
        self.assertEqual(response.status_code,302)

   # we don't have a problem with short passwords,  not good!
   # def test_cant_register_user_withshortpassword(self):
   #      response=self.client.post(self.register_url,self.user_short_password,format='text/html')
   #      self.assertEqual(response.status_code,400)

   #the system allows invalid emails, not good!
   # def test_cant_register_user_with_invalid_email(self):
   #      response=self.client.post(self.register_url,self.user_invalid_email,format='text/html')
   #      self.assertEqual(response.status_code,400)

   # the page doesn't redirect or give a suitable message! need to be fixed.
   # def test_cant_register_user_with_taken_email(self):
   #      self.client.post(self.register_url,self.user,format='text/html')
   #      response=self.client.post(self.register_url,self.user,format='text/html')
   #      self.assertEqual(response.status_code,400)


class LoginTest(BaseTest):
    def test_can_access_page(self):
        response=self.client.get(self.login_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'login.html')

    def test_login_success(self):
        self.client.post(self.register_url,self.user,format='text/html')
        user=User.objects.filter(email=self.user['email']).first()
        user.is_active=True
        user.save()
        response= self.client.post(self.login_url,self.user,format='text/html')
        self.assertEqual(response.status_code,200)

    def test_cantlogin_with_no_username(self):
        response= self.client.post(self.login_url,{'password':'passwpedtest','username':''},format='text/html')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'login.html')

    def test_cantlogin_with_no_password(self):
        response= self.client.post(self.login_url,{'username':'usernametest','password':''},format='text/html')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'login.html')


class LogoutTest(BaseTest):
    def test_can_access_page(self):
        response=self.client.get(self.logout_url)
        self.assertEqual(response.status_code,302) #302: should be redirected.
        # it subbosed to be redirected to homepage,
        # but  No templates used to render the response, should be fixed.
        #self.assertTemplateUsed(response,'index.html')

    def test_logout_success(self):
        self.client.post(self.register_url,self.user,format='text/html')
        user=User.objects.filter(email=self.user['email']).first()
        user.is_active = True
        user.save()
        response= self.client.post(self.logout_url,self.user,format='text/html')
        user.is_active = False
        user.save()
        self.assertEqual(response.status_code,302) #302: should be redirected.