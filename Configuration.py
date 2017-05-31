# -*- coding: utf-8 -*-

#  Classe Configuration definisce una configurazione di funzionamento dei backup
# Sorgenti e Destinazioni dei backup, frequenza, logica additiva o archivio

import datetime
from Locations import Location, VirtualLocation


class Conf:

    def __init__(self, Name='', Freq=datetime.timedelta(days=3)):
        '''
        Classe configurazione:
        NomeConf
        Sorgenti
        Destinazioni
        Frequenza
        Varie
        '''
        if type(Name) is not basestring:
            raise ValueError
        self.Name = Name

        self.Sources = []
        self.Dest = []

        if not isinstance(Freq, datetime.timedelta):
            print 'Conf Error: freq is not a timedelta'
            raise ValueError
        self.Freq = Freq

        # due marker per tenere traccia se tutte le destinazioni sono scrivibili e le sorgenti leggibili

        self.allSourcesReadable = True
        self.allDestWritable = True

    def setName(self, nome):
        if type(nome) is not basestring:
            raise ValueError

        self.Name = nome

    def addSource(self, path):

        new = VirtualLocation(path)

        self.Sources.append(new)
        self.allSourcesReadable = self.allSourcesReadable and new.checkRead() # controlla se tutto si può leggere

    def addDest(self, path):

        new = VirtualLocation(path)

        self.Dest.append(new)
        self.allDestWritable = self.allDestWritable and new.checkWrite() # controlla se tutto è scrivibile

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

        workingConf = Conf(self.Name.join('Working') , self.Freq)

        wS = self.getWorkingSources()[0]
        for s in wS:
            workingConf.addSource(s)

        wD = self.getWorkingDests()[0]
        for d in wD:
            workingConf.addDest(d)

        return workingConf