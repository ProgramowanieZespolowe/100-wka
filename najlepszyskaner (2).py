import kivy
kivy.require("1.10.1")
import pyzbar.pyzbar as pyzbar
import numpy as np
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import *
from kivy.uix.button import *
from cv2 import *
from PIL import Image
from json import *
import requests
from kivy.network.urlrequest import *
from kivy.lang import Builder
from pyzbar.pyzbar import decode
from functools import partial
from time import *
from datetime import datetime
from kivy.clock import Clock

# string, który wyświetli się na screenie z wynikiem
result_display = ''
# pusta tablica, w której znajdą się odkodowane dane
wynik_data = []
#inicjalizacja kamery
cam = VideoCapture(0)

Builder.load_string("""
<MainScreen>:
	BoxLayout:
		orientation: 'vertical'
		Image:
			id: image
			source: '/home/michal/logo.jpg'
		Label:
			id: welcome
			text: 'Skanowanie'
	
<ResultsScreen>:
    BoxLayout:
		orientation:'vertical'
        Label:
			id: imie
            text: 'wynik'
        Label:
			id: nazwisko
			text: 'wynik'
		Label:
			id: klasa
			text: 'wynik'
		Label:
			id: sniadanie
			text: 'wynik'
		Label:
			id: obiad
			text: 'wynik'
		Label:
			id: kolacja
			text: 'wynik'
        Button:
            text: 'Do skanu'
            on_press: root.manager.current = 'main'
<Manager>:
	MainScreen:
		name: 'main'
	ResultsScreen:
		name: 'results'
""")

#dekodowanie
def decode(im) :
  # Find barcodes and QR codes
  decodedObjects = pyzbar.decode(im)

  # Print results
  for obj in decodedObjects:
	 # print('Type : ', obj.type)
	  #print('Data : ', obj.data.decode('utf-8'),'\n')
	  #dopisanie zeskanowanych danych do listy
	  wynik_data.append(obj.data.decode('utf-8'))
  return decodedObjects


#skanowanie i uruchomienie dekodowania
class idk():
	def json_connect(self):
		global result_display
		main_api = "http://127.0.0.1:6969/api/v1/posilki/?format=json"
		ID_Ucznia = str(result_display)
		print(ID_Ucznia)
		#url = main_api + '&uczen__ID_Ucznia=' + ID_Ucznia  + '&Dzien=2019-06-04T12:00:00'
		url = main_api + '&uczen__ID_Ucznia=' + ID_Ucznia  + '&Dzien=' + datetime.today().strftime('%Y-%m-%d') +'T12:00:00'
		json_data = requests.get(url).json()
		uczen = json_data["objects"][0]["uczen"]
		url = 'http://127.0.0.1:6969' + uczen
		json_data2 = requests.get(url).json()
		print(type(json_data["objects"][0]["Sniadanie"]))
		print(type(json_data2["Klasa"]))
		global imie
		global nazwisko
		global klasa
		global sniadanie
		global obiad
		global kolacja
		imie = json_data2["Imie"]
		print("Imie ", json_data2["Imie"])
		nazwisko = json_data2["Nazwisko"]
		print("Nazwisko ", json_data2["Nazwisko"])
		klasa = json_data2["Klasa"]
		print("Klasa ", json_data2["Klasa"])
		if json_data["objects"][0]["Sniadanie"] == True:
			sniadanie = "Tak"
		else:
			sniadanie = "Nie"
		print("Sniadanie ", json_data["objects"][0]["Sniadanie"])
		if json_data["objects"][0]["Obiad"] == True:
			obiad = "Tak"
		else:
			obiad = "Nie"
		print("Obiad ", json_data["objects"][0]["Obiad"])
		if json_data["objects"][0]["Kolacja"] == True:
			kolacja = "Tak"
		else:
			kolacja = "Nie"
		print("Kolacja ", json_data["objects"][0]["Kolacja"])
	def skan(self):
		while True:
			s, img = cam.read()
			if s: 
				#zapis zdjęcia co 200ms
				waitKey(200)
				imwrite(r"C:\Users\oskar\zdjecie.jpg",img)
			#odkodowanie zapisanego zdjęcia
			data = decode(Image.open(r"C:\Users\oskar\zdjecie.jpg"))
			#print(data)
			# Read image
			im = imread(r"C:\Users\oskar\zdjecie.jpg")

			decodedObjects = decode(im)
		#przypisanie do stringa pierwszego zeskanowanego wyniku z listy	
			#result_display = str(wynik_data[0])
			try:
				global result_display
				result_display = wynik_data[0]
				self.json_connect()
							
			except IndexError as e:
				pass
isdk=idk()
	
#przypisanie metody skan, aby działała w tle	
tlo = threading.Thread(name = 'skan', target = isdk.skan)

#klasa ze ScreenManagerem
class Manager(ScreenManager):
	pass

#główny ekrean otwierany podczas skanowania
class MainScreen(Screen):
	#uruchamianie co 0.5s próby zmiany ekranu
	def on_enter(self):
		Clock.schedule_interval(self.change_screen, 0.5)
	#jeśli lista danych nie będzie pusta 
	#to przełączamy ekran żeby wyświetlić wynik
	def change_screen(self, dt):
		if wynik_data != []:
			self.manager.current = 'results'
			#wyczyszczenie listy, żeby móc wrócić na poprzedni ekran
			#i skanować dalej
			wynik_data.clear()
			
#ekran z wynikiem		
class ResultsScreen(Screen):
	#po otworzeniu ekranu odświeżamy wartość labela
	#nowa zawartość labela to nasz wynik
	#czyli pierwszy element listy
	def on_enter(self):
		Clock.schedule_once(self.change_result)
	def change_result(self, dt):
		self.ids.imie.text="Imie: " + imie
		self.ids.nazwisko.text="Nazwisko: " + nazwisko
		self.ids.klasa.text="Klasa: " + str(klasa)
		self.ids.sniadanie.text="Sniadanie: " + sniadanie
		self.ids.obiad.text="Obiad: " + obiad
		self.ids.kolacja.text="Kolacja: " + kolacja
		
#klasa naszej aplikacji
class QR_Scanner(App):	
	def build(self):
		#uruchomienie skanera działającego w tle
		tlo.start()
		return Manager()
		
#uruchomienie aplikacji
if __name__ == '__main__':
    QR_Scanner().run()
