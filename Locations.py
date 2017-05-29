## Classe Location definisce dove prendere e dove salvare i files

import os 

class Location:
	'Classe Location definisce dove prendere e dove salvare i files'

	def __init__(self, locPath): # costruttore
		try:                                        # verifica che il path sia valido, se non lo è chi lo chiama deve gestire 
			self.path = os.path.abspath(locPath)    # ed eliminare l'oggetto non valido
		except e:
			raise e
