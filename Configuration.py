# -*- coding: utf-8 -*-

#  Classe Configuration definisce una configurazione di funzionamento dei backup
# Sorgenti e Destinazioni dei backup, frequenza, logica additiva o archivio

import datetime
from Locations import Location, VirtualLocation


class Conf:

    def __init__(self, Name, Freq=datetime.timedelta(days=3)):
        '''
        Classe configurazione:
        NomeConf
        Sorgenti
        Destinazioni
        Frequenza
        Varie
        '''
        if type(Name) is not str:
            raise ValueError
        self.Name = Name

        self.Sources = []
        self.Dest = []
        self.Map = {}

        if not isinstance(Freq, datetime.timedelta):
            print 'Conf Error: freq is not a timedelta'
            raise ValueError
        self.Freq = Freq

        # due marker per tenere traccia se tutte le destinazioni sono scrivibili e le sorgenti leggibili

        self.allSourcesReadable = True
        self.allDestWritable = True

    def setName(self, nome):
        if type(nome) is not str:
            raise ValueError

        self.Name = nome

    def sourceAlExists(self, path):

        return path in [p.getPath() for p in self.Sources]

    def destAlExists(self, path):

        return path in [p.getPath() for p in self.Dest]

    def addSource(self, pathS, pathD):
        ''' Aggiunge man mano le sorgenti. Se la sorgente esiste già è ValueError, se no la aggiunge! Se
        la destinazione non esiste ancora la crea, quindi linka nella mappa interna source e dest'''

        if self.sourceAlExists(pathS): # se esisteva già è un errore
            raise ValueError

        newS = VirtualLocation(pathS) # altrimenti va aggiunto
        self.Sources.append(newS)
        self.allSourcesReadable = self.allSourcesReadable and newS.checkRead() # controlla se tutto si può leggere

        if not self.destAlExists(pathD): # se non esisteva la dest va aggiunta
            self.addDest(pathD)


        self.Map[pathS] = pathD # mappa la sorgente alla destinazione!

    def addDest(self, path):

         new = VirtualLocation(path)
         self.Dest.append(new)
         self.allDestWritable = self.allDestWritable and new.checkWrite() # controlla se tutto è scrivibile

    def rebind(self, pathS, pathD):
        '''
        Modifica Map per cambiare l'associazione di una source ad una dest (può dover eliminare una dest)
        '''
        if not self.sourceAlExists(pathS): # se source non esiste è un errore
            raise ValueError

        if not self.destAlExists(pathD): # se dest non esiste va aggiunta
            self.addDest(pathD)

        currDest = self.Map[pathS] # salva la attuale destinazione
        self.Map[pathS] = pathD

        # E' necessario verificare se la destinazione rimossa sia ancora necessaria o se si possa eliminarla
        self.cleanDests(currDest)

    def cleanDests(self, path):
        ''' Controlla se, dopo aver rimosso una destinazione, questa sia ancora mappata da qualche sorgente o se
        invece si possa rimuoverla '''
        if path not in self.Map:
            self.removeDest(path)

    def removeDest(self, path):
        '''Bisogna rimuovere sulla base del path, ma non basta fare remove path perchè non è una lista di oggetti
        path bensì di VirtualLocations'''
        for f in self.Dest:
            if f.getPath() is path:
                self.Dest.remove(f)

    def removeSource(self, path):
        '''Bisogna rimuovere sulla base del path, ma non basta fare remove path perchè non è una lista di oggetti
           path bensì di VirtualLocations'''
        for f in self.Sources:
            if f.getPath() is path:
                self.Sources.remove(f)

    def checkAllReadable(self):

        if not self.Sources: # empty lists are false
            return True
        for s in self.Sources:
            if not s.checkRead():
                return False
        return True

    def checkAllWritable(self):

        if not self.Dest: # empty lists are false
            return True
        for d in self.Dest:
            if not d.checkWrite():
                return False
        return True

    def setFreq(self, freq):
        if not isinstance(freq, datetime.timedelta):
            print 'Conf Error: freq is not a timedelta'
            raise ValueError
        self.Freq = freq


    def printConf(self):

        print 'Configuration ', self.Name
        print 'Sources: ', self.Sources
        print 'Destinations: ', self.Dest
        print 'Frequenza Sync: ', self.Freq
        print 'All Sources Readable' if self.allSourcesReadable else 'SOME SOURCES UNREADABLE'
        print 'All Dests Writable' if self.allDestWritable else 'SOME DESTS NOT WRITABLE'

    def getWorkingSources(self):
        '''
        Scorre la lista delle sorgenti e ritorna solo quelle utilizzabili in pratica adesso(esistenti e leggibili),
        più una lista di sorgenti inutilizzabili
        '''

        workSources = []
        badSources = []
        for s in self.Sources:
            try:
                new = Location(s.getPath()) # prova a generare una location vera a partire dalla virtuale
                if not new.checkRead():
                    raise OSError
                workSources.append(new)
            except OSError:
                badSources.append(s)
        return [workSources, badSources]

    def getWorkingDests(self):
        '''
        Scorre la lista delle destinazioni e ritorna solo quelle utilizzabili in pratica adesso, più una lista di
        destinazioni inutilizzabili
        '''

        workDest = []
        badDest = []
        for d in self.Dest:
            try:
                new = Location(d.getPath()) # prova a generare una location vera a partire dalla virtuale
                if not new.checkWrite():
                    raise OSError
                workDest.append(new)
            except OSError:
                badDest.append(d)
        return [workDest, badDest]

    def genWorkingConf(self):
        '''
        Genera una nuova configurazione, limitata alle sorgenti e destinazioni esistenti ed accessibili ora.
        QUINDI deve eliminare le dest inagibili e le sorgenti inagibili o associate a destinazioni inagibili
        E restringere la Mappa di conseguenza. Qui ci starebbe un po' di algoritmo!
        '''
        workingConf = Conf(self.Name.join('-ReducedToWorking') , self.Freq)

        wD = self.getWorkingDests()
        wS = self.getWorkingSources()

        for s in wS[0]: # scorre le sorgenti buone
            dest = self.Map[s.getPath()]
            if VirtualLocation(dest) not in wD[1]: # se la destinazione della sorgente buona non è cattiva
                                                   # sorgente buona, destinazione buona
                workingConf.addSource(s.getPath(), dest) # aggiungi la nuova sorgente, la dest potrebbe essere
                                                              # duplicata ma se la vede da sè

        return workingConf