# -*- coding: utf-8 -*-

# Classe VirtualLocation definisce un path virtuale che non esiste necessariamente
# Classe Location DEVE AVERE UN PATH VALIDO
# Modifica per git

import os
import datetime


class VirtualLocation(object):
    def __init__(self, locPath):  # costruttore
        '''' Classe VirtualLocation definisce un'interfaccia per le sorgenti e destinazioni
			 da cui copiare e su cui scrivere, controllando l'accessibilità, il mount eccetera

			 Location(Path) deve ricevere un path valido per UNA DIRECTORY
			 getPath ritorna path assoluto!
			 getLastSync ritorna l'ultima volta che l'oggetto è stato utilizzato
			 touchDate(dt = now) riceve un datetime e lo salva come time di ultimo accesso (default now())
		'''
        self.path = os.path.abspath(locPath)
        # nella location Virtuale NON CONTROLLO che esista già il path (HDD scollegato per esempio)
        # => ACCETTA ANCHE PATH CHE NON ESISTONO!

        self.read_ok = os.access(self.path, os.R_OK)  # verifica i privilegi lettura e scrittura
        self.write_ok = os.access(self.path, os.W_OK)

        self.last_sync = None

    def checkRead(self):
        return self.read_ok

    def checkWrite(self):
        return self.write_ok

    def checkAll(self):
        return self.read_ok and self.write_ok

    def getPath(self):
        return self.path

    def getLastSync(self):
        return self.last_sync

    def touchDate(self, dt=datetime.datetime.now()):  # record that the obj was updated now
        self.last_sync = dt

    def isPath(self, path):
        return self.path == os.path.abspath(path)

class Location(VirtualLocation):

    def __init__(self, locPath):

        VirtualLocation.__init__(self,locPath)

        if not os.path.isdir(self.path):
            raise OSError # in questo caso il path DEVE ESSERE VALIDO ESISTENTE E MONTATO

        self.read_ok = os.access(self.path, os.R_OK)  # verifica i privilegi lettura e scrittura
        self.write_ok = os.access(self.path, os.W_OK)

