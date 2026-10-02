from vepar import *

# primjer molekule propana CH3-1-CH2-1-CH3
# primjer molekule propena CH2-2-CH-1-CH3
# primjer molekule 2-Metilheksana CH2-1-CH^1^(CH3)-1-CH2-1-CH2-1-CH2-1-CH3
# alternativno                    CH2-1-CHˇ1ˇ(CH3)-1-CH2-1-CH2-1-CH2-1-CH3
#primjer molekula 2,2-metilpentana CH2-1-CHˇ1ˇ(CH3)-1-CH2^1^(CH2)-1-CH2-1-CH3

KorijeniNaziva = ['nista','met','et','prop','but','pent','heks','hept','okt','non','dek']
MultiplikativniPrefiksi=['nista','nista','di','tri','tetra','penta','heksa']
PostfiksiNaziva=['nista','an','en','in']
class T(TipoviTokena):

    IDENTIFICIRAJ = 'identificiraj'
    OPISI = 'opisi'
    IZJEDNACI = 'izjednaci'
    IZRACUNAJ = 'izracunaj'
    NACRTAJ = 'nacrtaj'

    OOTV, OZATV, UOTV, UZATV = '()[]'
    PLUS = '+'
    MINUS = '-'
    
    STRELICA = '->'

    ELEKTRON = 'e'

    VEZASASTRANE= '-'
    VEZAGORE='^'
    VEZADOLJE='ˇ'
    
    class ATOM(Token):
        def ime(t): return str(t.sadržaj)

    class BROJ(Token):
        def vrijednost(t): return int(t.sadržaj)

@lexer
def kemija(lex):
    for znak in lex:
        if znak.isspace():
            lex.zanemari()
            
        elif znak.isdecimal():
            lex.prirodni_broj(znak,nula=False)
            yield lex.token(T.BROJ)
            
        elif znak.isupper():
            lex >= str.islower
            yield lex.token(T.ATOM)
            
        elif znak.islower():
            lex.plus(str.isalpha)
            yield lex.literal(T)
            
        elif znak=='-':
            if(lex >= '>'):
                yield lex.token(T.STRELICA)
            else:
                yield lex.token(T.VEZASASTRANE)
                znak=next(lex)
                if(znak.isdecimal()):
                    lex.prirodni_broj(znak,nula=False)
                    yield lex.token(T.BROJ)
                    lex >> '-'
                    lex.zanemari()
                else:
                    raise lex.greska("Nije napisana valencija veze")
        elif znak=='^':
            yield lex.token(T.VEZAGORE)
            znak=next(lex)
            if(znak.isdecimal()):
                lex.prirodni_broj(znak,nula=False)
                yield lex.token(T.BROJ)
                lex >> '^'
                lex.zanemari()
            else:
                raise lex.greska("Nije napisana valencija veze")
        elif znak=='ˇ':
            yield lex.token(T.VEZADOLJE)
            znak=next(lex)
            if(znak.isdecimal()):
                lex.prirodni_broj(znak,nula=False)
                yield lex.token(T.BROJ)
                lex >> 'ˇ'
                lex.zanemari()
            else:
                raise lex.greska("Nije napisana valencija veze")
            
        else:
            yield lex.literal(T)

#---------------------------------------------------------------------------------------------
#Beskontekstna gramatika
#start -> IDENTIFICIRAJ OOTV jednadzba OZATV | OPISI OOTV jednadzba OZATV | IZJEDNACI OOTV jednadzba STRELICA jednadzba OZATV |
#	  IZRACUNAJ OOTV jednadzba STRELICA OZATV | NACRTAJ OOTV jednadzba OZATV

#jednadzba -> jednadzba PLUS molekula | jednadzba PLUS BROJ molekula | BROJ molekula | molekula

#molekula -> molekula veza skupina | skupina

#veza -> VEZASASTRANE BROJ | VEZAGORE BROJ OOTV grana OZATV VEZASASTRANE BROJ| VEZADOLJE BROJ OOTV grana OZATV VEZASASTRANE BROJ | VEZAGORE BROJ OOTV grana OZATV VEZADOLJE BROJ OOTV grana OZATV VEZASASTRANE BROJ

#grana -> grana VEZASASTRANE BROJ skupina | skupina

#skupina -> skupina atom | atom | zagrade | zagrade BROJ

# atom -> ATOM | ATOM BROJ

#zagrade -> OOTV molekula OZATV| UOTV molekula UZATV
#---------------------------------------------------------------------------------------------
class spoj(Parser):
    def start(p) -> 'Start':
        if p>T.IDENTIFICIRAJ:
            naredba=p>>T.IDENTIFICIRAJ
            p>>T.OOTV
            lijevo=p.jednadzba()
            p>>T.OZATV
            return Start(naredba,lijevo,nenavedeno)
        
        elif p>T.OPISI:
            naredba=p>>T.OPISI
            p>>T.OOTV
            lijevo=p.jednadzba()
            p>>T.ZAOTV
            return Start(naredba,lijevo,nenavedeno)
            
        elif p>T.IZJEDNACI:
            naredba=p>>T.IZJEDNACI
            p>>T.OOTV
            lijevo=p.jednadzba()
            p >> T.STRELICA
            desno=p.jednadzba()
            p>>T.ZAOTV
            return Start(naredba,lijevo,desno)
            
        elif p>T.IZRACUNAJ:
            naredba=p>>T.IZRACUNAJ
            p>>T.OOTV
            lijevo=p.jednadzba()
            p >> T.STRELICA
            p>>T.ZAOTV
            return Start(naredba,lijevo,nenavedeno)

            
        else:
            naredba=p>>T.NACRTAJ
            p>>T.OOTV
            lijevo=p.jednadzba()
            p>>T.ZAOTV
            return Start(naredba,lijevo,nenavedeno)
        
            

    def jednadzba(p) -> 'jednadzba':
        koliko=[]
        if(p > T.BROJ):
            broj= p >> T.BROJ
            koliko.append(broj)
        else:
            koliko.append(nenavedeno)
            
        molekule = [p.molekula()]
        
        while p > T.PLUS:
            p >> T. PLUS
            if(p > T.BROJ):
                broj= p >> T.BROJ
                koliko.append(broj)
            else:
                koliko.append(nenavedeno)
            molekule.append(p.molekula)
            
        return Jednadzba(molekule,koliko)

    def molekula(p) -> 'molekula':
        skupine = [p.skupina()]
        veze = []
        while(p > {T.VEZAGORE, T.VEZADOLJE, T.VEZASASTRANE}):
            if(p > T.VEZAGORE):
                veze.append(p.veza())
                p >> T.OOTV
                skupine.append(p.grana())
                p >> T.OZATV
            if(p > T.VEZADOLJE):
                veze.append(p.veza())
                p >> T.OOTV
                skupine.append(p.grana())
                p >> T.OZATV
            veze.append(p.veza())
            skupine.append(p.skupina())

        return Molekula(skupine,veze)

    def skupina(p) -> 'skupina':
        atomi=[p.atom()]
        while (p > T.ATOM):
            atomi.append(p.atom())
        return Skupina(atomi)

    def veza(p) -> 'veza':
        if(p > T.VEZAGORE):
            tipveze= p >> T.VEZAGORE
            valencija = p >> T.BROJ
            return Veza(tipveze,valencija)
        elif(p > T.VEZADOLJE):
            tipveze= p >> T.VEZADOLJE
            valencija = p >> T.BROJ
            return Veza(tipveze,valencija)
        elif(p > T.VEZASASTRANE):
            tipveze= p >> T.VEZASASTRANE
            valencija = p >> T.BROJ
            return Veza(tipveze,valencija)
        else:
            raise p.greška("Nije napisano koja je veza")
        
    def grana(p) -> 'grana':
        skupine=[p.skupina()]
        veze=[]
        while( p > T.VEZASASTRANE):
            veze.append(p.veza())
            skupine.append(p.skupina())
        return Grana(skupine,veze)
        
    def atom(p) -> 'atom':
        što = p >> T.ATOM
        koliko = p>=T.BROJ
        return Atom(što, koliko)
class Start(AST):
    naredba: 'IDENTIFICIRAJ|OPISI|IZJEDNACI|IZRACUNAJ|NACRTAJ'
    lijevo: 'Jednadzba'
    desno: 'Jednadzba?'

    def izvrsi(spoj):
        if spoj.naredba.sadržaj == 'identificiraj':
            spoj.lijevo.identificiraj()
        else:
            print("Ne prepoznajem naredbu")
    
class Jednadzba(AST):
    molekule: 'Molekule*'
    koliko: 'BROJ?'

    def identificiraj(jednadzba):
        jednadzba.molekule[0].identificiraj()
        
class Molekula(AST):
    skupine: 'Skupina*'
    veze: 'Veza*'

    def identificiraj(molekula):
        BrojUgljikaUGlavnojGrani=1
        NajvecaVezaGlavneGrane=1
        grane=[]
        mjestagrana=[]
        for i in range(0,len(molekula.veze)):
            if(molekula.veze[i].tipveze.sadržaj=='-'):
                if(molekula.veze[i].valencija.vrijednost()>NajvecaVezaGlavneGrane):
                    NajvecaVezaGlavneGrane=molekula.veze[i].valencija.vrijednost()
                BrojUgljikaUGlavnojGrani+=1
            else:
                grane.append(molekula.skupine[i+1].brojUgljikaUGrani())
                mjestagrana.append(BrojUgljikaUGlavnojGrani)
        for i in range(0,len(grane)):
            for j in range(i,len(grane)):
                if(grane[i]<grane[j]):
                    swap(i,j,grane)
                    swap(i,j,mjestagrana)
        if(len(mjestagrana)>=1):
            if(mjestagrana[0]>BrojUgljikaUGlavnojGrani/2):
                flip(BrojUgljikaUGlavnojGrani,mjestagrana)
        for i in range(0,len(grane)):
            for j in range(i,len(grane)):
                if(grane[i]==grane[j] and mjestagrana[i]>mjestagrana[j]):
                    swap(i,j,mjestagrana)
        i=0
        while(i<len(grane)):
            KolikoIdenticnihGrana=1
            if(len(grane)-i>1):
                while(grane[i]==grane[i+1]):
                    print(mjestagrana[i],end=",")
                    KolikoIdenticnihGrana+=1
                    i+=1
                    if(i==len(grane)-1):
                       break
                    
            print(mjestagrana[i],end="-")
            if(KolikoIdenticnihGrana>1):
                print(MultiplikativniPrefiksi[KolikoIdenticnihGrana],end="")
            print(KorijeniNaziva[grane[i]],end="il-")
            i+=1
        print(KorijeniNaziva[BrojUgljikaUGlavnojGrani],end="")
        print(PostfiksiNaziva[NajvecaVezaGlavneGrane])
        
        
                    
            

class Grana(AST):
    skupine: 'Skupina*'
    veze:'Veza*'

    def brojUgljikaUGrani(grana):
        return len(grana.skupine)
    
class Veza(AST):
    tipveze: 'VEZASASTRANE|VEZAGORE|VEZADOLJE'
    valencija: 'BROJ'

    def kojaValencija(veza):
        return veza.valencija
    def kojiTip(veza):
        return veza.tip
    
class Skupina(AST):
    atomi: 'Atom*'
    
class Atom(AST):
    što: 'ATOM'
    koliko: 'BROJ?'

    def vratiŠto(atom):
        return atom.što.ime()
    def vratiKoliko(atom):
        return atom.koliko.vrijednost()

def swap(i,j,lista):
    temp=lista[i]
    lista[i]=lista[j]
    lista[j]=temp

def flip(DuljinaLanca,lista):
    for i in range(0,len(lista)):
        lista[i]=DuljinaLanca-lista[i]+1
#prikaz(spoj('identificiraj(CH4)'))
#kemija('CH3-1-CHˇ1ˇ(CH3)-1-CH3')
#kemija('CH2-1-CHˇ1ˇ(CH2-1-CH3)-1-CH2^1^(CH3)-1-CH2-1-CH3')
spoj('identificiraj(CH3-1-CHˇ1ˇ(CH3)-1-CH3)').izvrsi()
spoj('identificiraj(2 CH3-1-CHˇ1ˇ(CH2-1-CH3)-1-CH2-1-CH2^1^(CH2-1-CH2-1-CH3)-1-CH3)').izvrsi()
spoj('identificiraj(CH3-1-CH^1^(CH3)-1-CH2-1-CH2-1-CHˇ1ˇ(CH2-1-CH3)-1-CH2-1-C^1^(CH3)ˇ1ˇ(CH3)-1-CH3)').izvrsi()
#kemija('opisi(CH3 -2- CH -1- CH3 + Cl -> )')
#kemija('izjednaci(CH4 + Cl -> CH3Cl + H )')
