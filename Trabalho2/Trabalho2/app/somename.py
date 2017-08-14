import re
import os
import os.path
import rdflib
from rdflib import Graph
from pathlib import Path
import xml.dom.minidom
import sqlite3
from rdflib.graph import ConjunctiveGraph, Namespace

_graph = Graph()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class somename:    
    def lerFicheiro(self, file):
        _graph.parse(file,format="nt")
        lista = set(_graph.predicates())
        for i in lista:
            print(i)

    def lerFicheiro_2(self, file):
        lista = []
        if file.endswith("xml"):
            with open(file) as f1:
                lista = f1.readlines()
        elif file.endswith("n3"):
            with open(file) as f2:
                for line in f2:
                    lista.append(line)
        return lista

    def converter(self,escolha):
        fich = Path('triplos.'+escolha)
        if fich.is_file():
            print("ficheiro removido")
            os.remove('triplos.'+escolha)
        else: 
            print("o ficheiro nao existe")
        uploaded_filename = 'triplos.'+escolha
        print("escolha: " + str(uploaded_filename))
        full_filename = os.path.join(BASE_DIR, uploaded_filename)
        of = open(full_filename, "wb")
        of.write(_graph.serialize(format=escolha))
        of.close()

    def sqlLite(self):
        g = Graph('SQLite')
        filename = "triplos.db"
        my_file = Path(filename)
        if my_file.is_file():
            print("A base de dados ja existe")
            pass
        else:
            g.open(filename, create=True)
            for t in _graph.triples((None, None, None)):
                g.add(t)
            g.commit()
            g.close()
            print("A base de dados")

    def teste(self):
        dbFile = BASE_DIR + '\\triplos.db'
        print(dbFile)
        conn = sqlite3.connect(dbFile)
        c = conn.cursor()
        total = []
        c.execute("Select * from kb_bec6803d52_asserted_statements")
        for i in c.fetchall():
            #print(i[0], i[1], i[2])
            total.append((i[0], i[1], i[2]))
    
        c.execute("Select * from kb_bec6803d52_literal_statements")
        for i in c.fetchall():
            #print(i[0], i[1], i[2])
            total.append((i[0], i[1], i[2]))
        conn.commit()
        conn.close()
        print("TOTAL DE TRIPLOS", len(total))
        return total
      
    def sparql_listTeams(self):
        lista=[]
        PREFIX = Namespace("http://example.com/equipa/")

        g = ConjunctiveGraph()

        g.parse("triplos.n3", format="n3")
        results = g.query("""
                SELECT ?clubeNome
                WHERE{
                    ?clube ns1:team ?clubeNome.
                }""", \
        initNs={'ns1': PREFIX})

        for i in results:
            lista.append(i[0])

        return lista

    def sparql(self):
        FB = Namespace("http://example.com/partida/")
        FB2 = Namespace("http://example.com/equipa/")
        FB3 = Namespace("http://example.com/data/")

        g = ConjunctiveGraph()

        query = str(input("insira a equipa a pesquisar:\n"))
        query = query.title() # primeira letra maiúscula e seguintes minúsculas
        print(query)

        g.parse("triplos.n3", format="n3")
        results = g.query("""
                SELECT ?p ?aa ?d ?h ?r ?q
                WHERE{
                    {
                        ?clube ns1:team '"""+query+"""'.
                        ?a ns2:HomeTeam ?clube.
                        ?a ns2:AwayTeam ?b.
                        ?b ns1:team ?p.
                        ?a ns2:Date ?c.
                        ?c ns3:date ?q.
                        ?a ns2:B365A ?aa.
                        ?a ns2:B365D ?d.
                        ?a ns2:B365H ?h.
                        ?a ns2:FTR ?r.
                    }
                }""", \
        initNs={'ns1': FB2,'ns2': FB, 'ns3':FB3})

        for i in results:
            print(query + " - " + i[0] + " - " + i[1] + " - " + i[2] + " - " + i[3] + " - " + i[4] + " - " + i[5])

    #Maior valor em 3
    def biggest(self,a, y, z):
        Max = a
        if y > Max:
            Max = y
        if z > Max:
            Max = z
            if y > z:
                Max = y
        return Max

    #"smart" sorting 
    def natural_sort(self,l):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(l, key = alphanum_key)