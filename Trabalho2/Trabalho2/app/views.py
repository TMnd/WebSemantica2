"""
Definition of views.
"""
import sys
from rdflib import Graph
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.somename import somename
from pathlib import Path
import sqlite3
import os
import os.path
from rdflib.graph import ConjunctiveGraph, Namespace
from collections import OrderedDict
from app.forms import checkclub

m = somename()

#load ficheiro para memoria
fich = Path("triplos.nt")
if fich.is_file():
    print("A dar load ao ficheiro...")
    m.lerFicheiro("triplos.nt")
else: 
    print("O ficheiro nao foi encontrado")

#criar a base de dados
m.sqlLite()

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def database(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)

    lista =[]
    lista = m.teste()

    return render(
        request,
        'app/database.html',
        {
            'title':'List of triples in the database',
            'listar':lista
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def convert(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    if 'convert' in request.POST :
        gen = []

        tipo = request.POST['tipoConversao']
        print(tipo)
        m.converter(tipo)

        gen = m.lerFicheiro_2("qq."+tipo)

        return render(
            request,
            'app/convert.html',
            {
                'title':'Convertion',
                'message':'Choose the format you wish:',
                'lista': gen,
            }
        )
    else:
         return render(
            request,
            'app/convert.html',
            {
                'title':'Convertion',
                'message':'Choose the format you wish:',
            }
        )

def sparql(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    lista={}
    output=[]

    form = checkclub()

    clubsList = m.sparql_listTeams()
    
    if 'sparql' in request.POST :
        team =  request.POST['teams']
        print(team)

        FB = Namespace("http://example.com/partida/")
        FB2 = Namespace("http://example.com/equipa/")
        FB3 = Namespace("http://example.com/data/")

        g = ConjunctiveGraph()

        g.parse("triplos.n3", format="n3")
        results = g.query("""
                SELECT ?HomeTeam ?AwayTeam ?homeGols ?awayGols ?result ?gameDate
                WHERE{
                    {
                        ?clubHomeId ns1:team '"""+team+"""'.
                        ?gameId ns2:HomeTeam ?clubHomeId.
                        ?gameId ns2:AwayTeam ?ClubAwayId.
                        ?ClubAwayId ns1:team ?AwayTeam.
                        ?gameId ns2:Date ?dateId.
                        ?dateId ns3:date ?gameDate.
                        ?gameId ns2:FTHG ?homeGols.
                        ?gameId ns2:FTAG ?awayGols.
                        ?gameId ns2:FTR ?result.
                    }
                    UNION
                    {
                        ?clubAwayId ns1:team '"""+team+"""'.
                        ?gameId ns2:AwayTeam ?clubAwayId.
                        ?gameId ns2:HomeTeam ?ClubHomeId.
                        ?ClubHomeId ns1:team ?HomeTeam.
                        ?gameId ns2:Date ?dateId.
                        ?dateId ns3:date ?gameDate.
                        ?gameId ns2:FTHG ?homeGols.
                        ?gameId ns2:FTAG ?awayGols.
                        ?gameId ns2:FTR ?result.
                    }
                }""", \
        initNs={'ns1': FB2,'ns2': FB, 'ns3':FB3})

        for i in results:
            if i[0] is None:
                if str(i[4]) == 'H':
                    aux = "Win"
                elif str(i[4]) == 'D':
                    aux = "Draw"
                elif str(i[4]) == 'A':
                    aux = "Defeat"
                valores = team + " - " + str(i[2]) + " : " + str(i[3]) + " - " + str(i[1]) + " - " + aux
            elif i[1] is None:
                if str(i[4]) == 'H':
                    aux = "Defeat"
                elif str(i[4]) == 'D':
                    aux = "Draw"
                elif str(i[4]) == 'A':
                    aux = "Win"
                valores = str(i[0]) + " - " + str(i[2]) + " : " + str(i[3]) + " - " + team + " - " + aux
            dataString = str(i[5]).split("/")
            dataDone = dataString[0]+"-"+dataString[1]+"-"+"20"+dataString[2]
            ter = datetime.strptime(dataDone, '%d-%m-%Y')
            lista[ter] = valores

        new_d = OrderedDict(sorted(lista.items()))

        for u in new_d:
            key = str(u).split(" ")
            output.append(key[0]+ " - " + lista[u])
        
        return render(
            request,
            'app/sparql.html',
            {
                'title':'Queries',
                'clubsList':clubsList,
                'clubeSelecionado':output,
                'teamChoose':team,
            }
        )
    elif 'sparqlASK' in request.POST:
        insert =  request.POST['name_field']

        insert = insert.title()

        FB2 = Namespace("http://example.com/equipa/")

        g = ConjunctiveGraph()

        g.parse("triplos.n3", format="n3")
        results = g.query("""
                ASK {
                     ?film ns1:team '"""+insert+"""'.
                }""", \
        initNs={'ns1': FB2})

        for i in results:
            result = i

        return render(
            request,
            'app/sparql.html',
            {
                'title':'Queries',
                'clubsList':clubsList,
                'clubeSelecionado':'',
                'teamChoose': 'None',
                'form': form,
                'result':result,
                'insert':insert,
            }
        )
    elif 'sparqlBets' in request.POST:

        list = {}
        finalList = {}

        FB = Namespace("http://example.com/partida/")
        FB2 = Namespace("http://example.com/equipa/")
        FB3 = Namespace("http://example.com/data/")

        g = ConjunctiveGraph()

        g.parse("triplos.n3", format="n3")
        results = g.query("""
                SELECT ?partida ?team_name_a ?team_name_h ?B365H ?B365D ?B365A ?BWH ?BWD ?BWA
                WHERE{
                    ?ateam ns1:team ?team_name_a.
                    ?hteam ns1:team ?team_name_h.
                    ?partida ns2:HomeTeam ?hteam.
                    ?partida ns2:AwayTeam ?ateam.
                    ?partida ns2:B365A ?B365A.
                    ?partida ns2:B365D ?B365D.
                    ?partida ns2:B365H ?B365H.
                    ?partida ns2:BWA ?BWA.
                    ?partida ns2:BWD ?BWD.
                    ?partida ns2:BWH ?BWH.
                }""", \
        initNs={'ns1': FB2,'ns2': FB})

        for i in results:
            values = []
            partida = str(i[0]).split("/",4)
            bet = m.biggest(i[3],i[4],i[5])
            bw = m.biggest(i[6],i[7],i[8])
            if bet == i[3]:
                winner = "Home Team"
            elif bet == i[4]:
                winner = "Draw"
            elif bet == i[5]:
                winner = "Away team"
            if bw == i[6]:
                winner2 = "Home Team"
            elif bw == i[7]:
                winner2 = "Draw"
            elif bw == i[8]:
                winner2 = "Away team"
            for j in i[1:]:
                values.append(j)
            values.append(winner)
            values.append(winner2)
            list[partida[4]]= values
        
        newList = m.natural_sort(list)

        for qq in newList:
            finalList[qq] = list[qq]

        #for o in finalList:
        #    print(o + " => " + str(finalList[o]))

        return render(
            request,
            'app/sparql.html',
            {
                'title':'Queries',
                'clubsList':clubsList,
                'clubeSelecionado':'',
                'result':'',
                'teamChoose': 'None',
                'form': form,
                'bets':finalList,
            }
        )
    else:
        return render(
            request,
            'app/sparql.html',
            {
                'title':'Queries',
                'clubsList':clubsList,
                'clubeSelecionado':'',
                'result':'',
                'bets':'',
                'teamChoose': 'None',
                'form': form,
            }
        )