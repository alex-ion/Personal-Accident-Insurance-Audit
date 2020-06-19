import xlsxwriter, time, os.path, shutil, smtplib, csv, sys
import sqlite3

lista_fisiere_folder_pai = []
fisiere_importate=[]
lista_fisiere_folder_contracte = []
lista_contracte_importate = []
lista_pai_importate = []
lista_locatii = []
lista_serii_pai = []
contracte_cu_pai_nevandut= []
contracte_cu_mai_multe_paiuri_vandute= []
contracte_inexistente_pe_care_e_vandut_pai=[]
polite_vandute_de_mai_multe_ori=[]
incarcare_efectuata=False
    
class SeriiPai():
    total_SeriiPai=0
    def __init__(self, serie_pai, cod_locatie, inventar):
        global lista_serii_pai
        self.index=SeriiPai.total_SeriiPai
        self.serie_pai = serie_pai
        self.cod_locatie = cod_locatie
        self.inventar=inventar
        lista_serii_pai.append(self)
        SeriiPai.total_SeriiPai+=1


class Locatii():
    def __init__(self, nume_locatie, cod_locatie):
        global lista_locatii
        self.nume_locatie = nume_locatie
        self.cod_locatie = cod_locatie
        lista_locatii.append(self)


class ContracteImportate():
    total_ContracteImportate=0
    def __init__(self, contract, LOR, licenseNo, out_date, outlocT, pai, pai_amt, grp_ctr, grp_crg, tarif1_out, agent_out):
        global lista_contracte_importate
        self.index=ContracteImportate.total_ContracteImportate
        self.contract = contract.upper().strip(" ")
        self.LOR = LOR
        self.cancelled=False
        if LOR=="0":
            self.cancelled=True
        self.licenseNo = licenseNo.upper()
        self.out_date = out_date
        self.outlocT = outlocT
        self.pai = pai
        self.pai_amt = pai_amt
        self.grp_ctr = grp_ctr
        self.grp_crg = grp_crg
        self.tarif1_out = tarif1_out
        self.agent_out = agent_out
        lista_contracte_importate.append(self)
        ContracteImportate.total_ContracteImportate+=1


class PaiuriVandute():
    total_PaiuriVandute=0
    def __init__(self, NR_CRT, contract, Nr_polita, data_polita, licenseNo, LOR, pai_day, pai_amt, observatii, raportat):
        global lista_pai_importate
        self.index=PaiuriVandute.total_PaiuriVandute
        self.NR_CRT = NR_CRT
        self.contract = contract.upper().strip(" ")
        self.Nr_polita = Nr_polita.upper().strip(" ")
        self.data_polita = data_polita
        self.licenseNo = licenseNo.upper()
        if LOR=="":
            LOR=0
        if pai_day=="":
            pai_day=0
        if pai_amt=="":
            pai_amt=0          
        self.LOR = LOR
        self.pai_day = pai_day
        self.pai_amt = pai_amt
        self.observatii = observatii
        self.raportat = raportat.strip(".csv")
        lista_pai_importate.append(self)
        PaiuriVandute.total_PaiuriVandute+=1


def incarcare_fisiere_contracte():
    # Constituire lista fisiere cu contractele disponibile in folder
    global cale1, lista_contracte_importate, lista_fisiere_folder_contracte, fisiere_importate
    temp=0
    cale1 = "Contracte din platforma"
    lista_fisiere_folder_contracte=os.listdir(cale1)
    for fisier1 in lista_fisiere_folder_contracte:
        temp+=1
        fisiere_importate.append(fisier1)
        incarcare_fisiere_contracte1(fisier1)
        
    if temp>0:
        print "Am importat " + str(len(fisiere_importate))+" fisiere cu contracte si "+ str(len(lista_contracte_importate))+" contracte.\n"


def incarcare_fisiere_contracte1(f):
    # Importare fisier care contine PAI-urile dintr-o anumita luna pentru verificarea corectitudinii raportarii
    global cale1
    total_temp = 0
    try:
        fisier = open(os.path.join(cale1, f), "rb")
        print "Procesez fisierul: " + str(f) + ".",
        reader = csv.reader(fisier, delimiter=",", quotechar='"', quoting=True)
        lista_import = list(reader)
        lista_import.remove(lista_import[0])
        fisier.close()
        for linie in lista_import:
            obiect = len(globals())
            total_temp += 1
            if linie[46] == "1" or linie[91] == "6FI":
               globals()[obiect] = ContracteImportate(linie[0], linie[5], linie[10], linie[26], linie[32], linie[46], linie[49], linie[67], linie[68], linie[91], linie[96])
        print "Totalul pentru fisierul " + str(f) + " este " + str(total_temp)
    except Exception, err:
        print "Am primit eroarea: '" + str(err) + "' la deschiderea fisierului: " + str(f)


def incarcare_fisiere_pai():
    """Consituire lista fisiere cu PAI-uri pe luni disponibile in folder"""
    global cale2, lista_pai_importate, lista_fisiere_folder_pai, fisiere_importate
    cale2 = "Luni raportate"
    lista_fisiere_folder_pai=os.listdir(cale2)
    for fisier2 in lista_fisiere_folder_pai:
        incarcare_fisiere_pai1(fisier2)
    print "\nAm importat " + str(len(lista_fisiere_folder_pai))+" fisiere cu PAI-uri si "+ str(len(lista_pai_importate))+" PAI-uri vandute/anulate.\n"
        
def incarcare_fisiere_pai1(f):
    """Importare fisier care contine PAI-urile dintr-o anumita luna pentru verificarea corectitudinii raportarii"""
    global cale2
    total_temp = 0
    try:
        fisier2 = open(os.path.join(cale2, f), "rb")
        print "Procesez fisierul: " + str(f) + ".",
        reader = csv.reader(fisier2, delimiter=",", quotechar='"', quoting=True)
        lista_import = list(reader)
        lista_import.remove(lista_import[0])
        fisier2.close()
        for linie in lista_import:
            obiect = len(globals())
            total_temp += 1
            globals()[obiect] = PaiuriVandute(linie[0], linie[1], linie[2], linie[3], linie[4], linie[5], linie[6], linie[7], linie[8], str(f))
        print "Totalul pentru fisierul " + str(f) + " este " + str(total_temp)
    except(Exception), err:
        print "Am primit eroarea: '" + str(err) + "' la deschiderea fisierului: " + str(f)

def incarcare_locatii():
    global lista_locatii
    try:
        fisier = open("LOCATII.csv", "rb")
        reader = csv.reader(fisier, delimiter=",", quotechar='"', quoting=True)
        lista_import = list(reader)
        lista_import.remove(lista_import[0])
        fisier.close()
        for linie in lista_import:
            obiect = len(globals())
            print "Am importat locatia", linie[1]
            globals()[obiect] = Locatii(linie[0], linie[1])
        print "\nAm importat " + str(len(lista_locatii)) + " locatii"                
    except(Exception), err:
        print "Am primit eroarea: '" + str(err) + "' la deschiderea fisierului cu locatiile"

def incarcare_serii_pai():
    global lista_serii_pai
    try:
        fisier = open("SERII PAI.csv", "rb")
        reader = csv.reader(fisier, delimiter=",", quotechar='"', quoting=True)
        lista_import = list(reader)
        lista_import.remove(lista_import[0])
        fisier.close()
        for linie in lista_import:
            obiect = len(globals())
            globals()[obiect] = SeriiPai(linie[0], linie[1], linie[2])
        print "\nAm importat " + str(len(lista_serii_pai)) + " serii PAI\n"
    except(Exception), err:
        print "Am primit eroarea: '" + str(err) + "' la deschiderea fisierului cu seriile PAI"



def scriere_log(mesaj):
    LogFile=open("raport.txt", "a+")
    LogFile.write(mesaj)
    print mesaj,
    LogFile.close()

    
def impartire_pe_categorii():
    """Impartire pe categorii"""
    global  contracte_cu_pai_nevandut, contracte_cu_mai_multe_paiuri_vandute, contracte_inexistente_pe_care_e_vandut_pai
    lista_temp=[]
    for element in lista_contracte_importate:
            lista_temp=[i for i in xrange(len(lista_pai_importate)) if lista_pai_importate[i].contract==element.contract]
            if len(lista_temp)>1:
                contracte_cu_mai_multe_paiuri_vandute.append({element:lista_temp})
            elif len(lista_temp)==0 and element.cancelled==False:
                contracte_cu_pai_nevandut.append(element)
                
    for element in lista_pai_importate:
        if element.contract.isdigit():
            lista_temp=[i for i in xrange(len(lista_contracte_importate)) if lista_contracte_importate[i].contract==element.contract]
            if len(lista_temp)==0:
                contracte_inexistente_pe_care_e_vandut_pai.append(element)

def raport1():
    """Contracte pe care apar mai multe PAI-uri vandute"""
    scriere_log(raport1.__doc__.upper()+"\n\n")
    for element1 in contracte_cu_mai_multe_paiuri_vandute:
        scriere_log("Pe contractul "+element1.keys()[0].contract+" s-au vandut mai multe polite: ")
        for element2 in element1.values()[0]:
            scriere_log(lista_pai_importate[element2].Nr_polita+" - "+lista_pai_importate[element2].raportat+", ")
        scriere_log("\n")
    scriere_log("\n")


def raport2():
    """Contracte pe care s-a vandut PAI dar nu s-a completat polita"""
    incasare_brand2=0
    cedare_insurer=0
    rata_6F=0
    scriere_log(raport2.__doc__.upper()+" ("+str(len(contracte_cu_pai_nevandut))+" contracte)\n\n")
    for element1 in contracte_cu_pai_nevandut:
        scriere_log("Pe contractul "+element1.contract+" deschis pe "+element1.outlocT+" in "+element1.out_date+" s-a vandut PAI, dar nu s-a completat polita\n")
        if element1.tarif1_out=="6FI":
            rata_6F=rata_6F+1
        if element1.grp_crg=="L":
            incasare_brand2=float(incasare_brand2)+float(element1.pai_amt)
            cedare_insurer=float(cedare_insurer)+float(3.4)*float(element1.LOR)
        else:
            incasare_brand2=float(incasare_brand2)+float(element1.pai_amt)
            cedare_insurer=float(cedare_insurer)+float(2)*float(element1.LOR)
    print "\nNoi am incasat "+str(incasare_brand2)+" EUR si ar fi trebuit sa cedam catre insurer "+str(cedare_insurer)+" EUR. Au fost "+str(rata_6F)+" contracte pe rata 6F in care PAI-ul este inclus in tarif si nu se taxeaza suplimentar."
    
    scriere_log("\n")

def raport3():
    """Polite PAI care s-au emis pe contracte inexistente sau pe contracte pe care nu s-a incasat PAI"""
    scriere_log(raport3.__doc__.upper()+"\n\n")
    for element1 in contracte_inexistente_pe_care_e_vandut_pai:
        scriere_log("Pe contractul "+element1.contract+" s-a emis polita de PAI, insa contractul nu exista sau nu s-a incasat PAI pe el\n")
    scriere_log("\n")

def raport4():
    """Polite PAI raportate ca vandute, care nu figureaza in lista de serii PAI primite de la insurer"""
    lista_temp=[]
    scriere_log(raport4.__doc__.upper()+"\n\n")
    for element in lista_serii_pai:
        lista_temp.append(element.serie_pai)
    for element in lista_pai_importate:
        if element.Nr_polita.lstrip("0") not in lista_temp and element.raportat!="Corectii":
            scriere_log("Polita '"+str(element.Nr_polita)+"' raportata pe contractul '"+str(element.contract)+"' in '"+str(element.raportat)+"' nu exista in lista de serii pai.\n")
    scriere_log("\n")
    
def raport5():
    """Polite care apar vandute de mai multe ori"""
    polite_vandute_de_mai_multe_ori=[]
    scriere_log(raport5.__doc__.upper()+"\n\n")
    for element in lista_pai_importate:
        lista_temp=[i for i in xrange(len(lista_pai_importate)) if lista_pai_importate[i].Nr_polita==element.Nr_polita and element.Nr_polita.isdigit()]
        if len(lista_temp)>1:
            polite_vandute_de_mai_multe_ori.append({element:lista_temp})
    for element1 in polite_vandute_de_mai_multe_ori:
        scriere_log("Polita "+element1.keys()[0].Nr_polita+" este vanduta pe mai multe contracte: ")
        for element2 in element1.values()[0]:
            scriere_log(lista_pai_importate[element2].contract+" - "+lista_pai_importate[element2].raportat+", ")
        scriere_log("\n")
    scriere_log("\n")
        

##def raport6():
##    """raport gol, poate fi folosit"""


def raport11():
    """Verificare sume raportate pe grupe auto"""
    global lista_pai_importate, lista_contracte_importate
    scriere_log(raport11.__doc__.upper()+"\n\n")
    diferenta_suma=0
    temp=0
    for element1 in lista_pai_importate:
        if round(float(element1.pai_day)*float(element1.LOR),2)!=round(float(element1.pai_amt),2):
            scriere_log("Pe polita PAI cu numarul "+element1.Nr_polita+", pozitia "+element1.NR_CRT+" raportata in "+element1.raportat+" sunt diferente de plati. Trebuia raportat "+str(round(float(element1.pai_day),2)*round(float(element1.LOR),2))+" EUR dar s-a raportat "+str(round(float(element1.pai_amt),2))+" EUR\n")
            temp=round(float(element1.pai_amt),2)-round(float(element1.pai_day),2)*round(float(element1.LOR),2)
            diferenta_suma=diferenta_suma+temp
        for element2 in lista_contracte_importate:
            if element1.contract==element2.contract and element1.raportat!="Corectii":
                if element2.grp_ctr=="L" and element1.pai_day!="3.4":
                    scriere_log("Pe contractul "+str(element1.contract)+" (raportat in "+str(element1.raportat)+") grupa "+str(element2.grp_ctr)+" s-a raportat cu "+str(element1.pai_day)+" EUR/zi in loc de 3.4 EUR/zi.")
                    temp=float(3.4)*float(element1.LOR)-float(element1.pai_day)*float(element1.LOR)

                    if temp>=0:
                        scriere_log(" Am raportat cu "+str(temp)+" EUR mai putin decat trebuia.\n")
                    else:
                        scriere_log(" Am raportat cu "+str(temp).strip("-")+" EUR mai mult decat trebuia.\n")
                    diferenta_suma=diferenta_suma+temp*(-1)
                elif element2.grp_ctr!="L" and element1.pai_day!="2":
                    scriere_log("Pe contractul "+str(element1.contract)+" (raportat in "+str(element1.raportat)+") grupa "+str(element2.grp_ctr)+" s-a raportat cu "+str(element1.pai_day)+" EUR/zi in loc de 2 EUR/zi.")
                    temp=float(2)*float(element1.LOR)-float(element1.pai_day)*float(element1.LOR)
                    if temp>=0:
                        scriere_log(" Am raportat cu "+str(temp)+" EUR mai putin decat trebuia.\n")
                    else:
                        scriere_log(" Am raportat cu "+str(temp).strip("-")+" EUR mai mult decat trebuia.\n")
                    diferenta_suma=diferenta_suma+temp*(-1)
                        
                if element1.LOR!=element2.LOR:
                    scriere_log("Pe contractul "+str(element1.contract)+" (raportat in "+str(element1.raportat)+") sunt "+str(element2.LOR)+" zile vandute pe contract si "+str(element1.LOR)+" zile raportate.")
                    diferenta_zile=int(element1.LOR)-int(element2.LOR)
                    if diferenta_zile>0:
                        if element2.grp_ctr=="L":
                            temp=diferenta_zile*3.4
                            scriere_log(" Am raportat cu "+str(round(float(temp),2))+" EUR mai mult decat trebuia.\n")                        
                        else:
                            temp=diferenta_zile*2
                            scriere_log(" Am raportat cu "+str(round(float(temp),2))+" EUR mai mult decat trebuia.\n")
                        diferenta_suma=diferenta_suma+temp
                    else:
                        if element2.grp_ctr=="L":
                            temp=diferenta_zile*3.4
                            scriere_log(" Am raportat cu "+str(round(float(temp),2)).strip("-")+" EUR mai putin decat trebuia.\n")                       
                        else:
                            temp=diferenta_zile*2
                            scriere_log(" Am raportat cu "+str(round(float(temp),2)).strip("-")+" EUR mai putin decat trebuia.\n")
                        diferenta_suma=diferenta_suma+temp
    if diferenta_suma>0:
        scriere_log("\nPentru diferentele de sume de mai sus, avem de luat de la insurer "+str(diferenta_suma).strip("-")+ " EUR\n")
    elif diferenta_suma<0:
        scriere_log("\nPentru diferentele de sume de mai sus, avem de dat catre insurer "+str(diferenta_suma).strip("-")+ " EUR\n")
    scriere_log("\n")

def raport7():
    """Verificare toate seriile PAI on hand"""
    global lista_serii_pai, lista_locatii, lista_pai_importate
    for element1 in lista_locatii:
        for element2 in lista_serii_pai:
            temp=False
            if element1.cod_locatie==element2.cod_locatie and element1.cod_locatie!="B7H":
                for element3 in lista_pai_importate:
                    if element2.serie_pai==element3.Nr_polita:
                        temp=True
                if temp==False:
                    print ("Polita "+element2.serie_pai+" este on hand pe statia "+element2.cod_locatie)
                    
def raport8():
    """Verificare serii PAI on hand pe un anumit punct"""
    global lista_serii_pai, lista_locatii, lista_pai_importate
    statie=raw_input("Introdu codul statiei pentru care verifici seriile PAI on hand:\t\t").upper()
    for element2 in lista_serii_pai:
        temp=False
        if element2.cod_locatie==statie:
            for element3 in lista_pai_importate:
                if element2.serie_pai==element3.Nr_polita:
                    temp=True
            if temp==False:
                print ("Polita "+element2.serie_pai+" este on hand pe statia "+element2.cod_locatie)
    
def raport9():
    """Verificare serii PAI lipsa pe un anumit punct dupa ce s-a efectuat inventarul"""
    global lista_serii_pai, lista_locatii, lista_pai_importate
    statie=raw_input("Introdu codul statiei pentru care verifici seriile PAI on hand:\t\t").upper()
    for element2 in lista_serii_pai:
        temp=False
        if element2.cod_locatie==statie and element2.inventar!="ok":
            for element3 in lista_pai_importate:
                if element2.serie_pai==element3.Nr_polita:
                    temp=True
            if temp==False:
                print ("Polita "+element2.serie_pai+" este lipsa pe statia "+element2.cod_locatie)

def raport10():
    """Verificare serii PAI lipsa pe toate punctele dupa ce s-a efectuat inventarul"""
    global lista_serii_pai, lista_locatii, lista_pai_importate
    scriere_log(raport10.__doc__.upper()+"\n\n")
    for element1 in lista_locatii:
        for element2 in lista_serii_pai:
            temp=False
            if element1.cod_locatie==element2.cod_locatie and element2.inventar!="ok" and element1.cod_locatie!="B7H":
                for element3 in lista_pai_importate:
                    if element2.serie_pai==element3.Nr_polita:
                        temp=True
                if temp==False:
                    scriere_log("Polita "+element2.serie_pai+" este lipsa pe statia "+element2.cod_locatie+"\n")
    scriere_log("\n")
    
    
def raport12():
    """Verificare polite intocmite pentru masini de alta grupa decat cea pe care s-a taxat"""
    global lista_pai_importate, lista_contracte_importate
    scriere_log(raport12.__doc__.upper()+"\n\n")     
    for element1 in lista_pai_importate:
        for element2 in lista_contracte_importate:
            if element1.contract==element2.contract and element1.raportat!="Corectii":
                if element2.grp_ctr=="L" and element2.grp_crg!="L":
                    scriere_log("Pe contractul "+str(element1.contract)+"(raportat in "+str(element1.raportat)+") s-a inchiriat grupa "+str(element2.grp_ctr)+" la pret de "+str(element2.grp_crg)+"\n")
                if element2.grp_ctr!="L" and element2.grp_crg=="L":
                    scriere_log("Pe contractul "+str(element1.contract)+"(raportat in "+str(element1.raportat)+") s-a inchiriat grupa "+str(element2.grp_ctr)+" la pret de "+str(element2.grp_crg)+"\n")
    scriere_log("\n")

def raport13():
    """Vizualizare toate PAI-urile care au ceva scris la Observatii"""
    global lista_pai_importate
    print "Nr. CRT".center(10),"RA".center(10),"NR Polita".center(10),"Data Polita".center(10),"Nr. Auto inchiriat".center(15),"Nr Zile".center(10),"Suma / zi".center(10),"Suma Totala/EUR".center(10),"Raportat".center(20),"Observatii".center(10)
    for element in lista_pai_importate:
        if element.observatii.strip(" ")!="":
            print element.NR_CRT.center(10),element.contract.center(10),element.Nr_polita.center(10),element.data_polita.center(10),element.licenseNo.center(15),str(element.LOR).center(15),str(element.pai_day).center(15),str(element.pai_amt).center(10),element.raportat.center(20),element.observatii.center(10)

def raport14():
    """Contracte pe care s-a vandut PAI de pe un anumit punct, dar nu s-a completat polita"""
    global contracte_cu_pai_nevandut
    statie=raw_input("Introdu codul statiei pentru care verifici contractele pe care nu s-a completat polita:\t\t").upper()
    for element in contracte_cu_pai_nevandut:
        if element.outlocT==statie:
            print "Pe contractul "+element.contract+" s-a vandut PAI, dar nu s-a completat polita"
                    
def cautare_contract():
    """Cautare contract"""
    global lista_contracte_importate
    optiune=raw_input("Introdu numarul de contract cautat: ")
    lista_temp=[i for i in xrange(len(lista_contracte_importate)) if lista_contracte_importate[i].contract==optiune]
    if len(lista_temp)>0:
        print "Contract".center(10),"LOR".center(10),"licenseNo".center(10),"out_date".center(20),"outlocT".center(10),"pai".center(10),"pai_amt".center(10),"grp_ctr".center(10),"grp_crg".center(10),"tarif1_out".center(10),"agent_out".center(10)
        e=lista_contracte_importate[lista_temp[0]]
        print e.contract.center(10),e.LOR.center(10),e.licenseNo.center(10),e.out_date.center(20),e.outlocT.center(10),e.pai.center(10),e.pai_amt.center(10),e.grp_ctr.center(10),e.grp_crg.center(10),e.tarif1_out.center(10),e.agent_out.center(10)
    else:
        print "Contractul "+optiune+" nu a fost gasit"
        

def cautare_pai():
    """Cautare PAI"""
    global lista_pai_importate
    optiune=raw_input("Introdu numarul de PAI cautat: ")
    lista_temp=[i for i in xrange(len(lista_pai_importate)) if lista_pai_importate[i].Nr_polita==optiune]
    if len(lista_temp)>0:
        print "Nr. CRT".center(10),"RA".center(10),"NR Polita".center(10),"Data Polita".center(10),"Nr. Auto inchiriat".center(15),"Nr Zile".center(10),"Suma / zi".center(10),"Suma Totala/EUR".center(10),"Raportat".center(20),"Observatii".center(10)
        for e in lista_temp:
            element=lista_pai_importate[e]
            print element.NR_CRT.center(10),element.contract.center(10),element.Nr_polita.center(10),element.data_polita.center(10),element.licenseNo.center(15),str(element.LOR).center(15),str(element.pai_day).center(15),str(element.pai_amt).center(10),element.raportat.center(20),element.observatii.center(10)
    else:
        print "PAI-ul "+optiune+" nu a fost gasit"


def cautare_pai_dupa_numar_contract():
    """Cautare PAI dupa numarul de contract"""
    global lista_pai_importate
    optiune=raw_input("Introdu numarul de contract pentru care vrei sa cauti polita PAI: ")
    lista_temp=[i for i in xrange(len(lista_pai_importate)) if lista_pai_importate[i].contract==optiune]
    if len(lista_temp)>0:
        print "Nr. CRT".center(10),"RA".center(10),"NR Polita".center(10),"Data Polita".center(10),"Nr. Auto inchiriat".center(15),"Nr Zile".center(10),"Suma / zi".center(10),"Suma Totala/EUR".center(10),"Raportat".center(20),"Observatii".center(10)
        for e in lista_temp:
            element=lista_pai_importate[e]
            print element.NR_CRT.center(10),element.contract.center(10),element.Nr_polita.center(10),element.data_polita.center(10),element.licenseNo.center(15),str(element.LOR).center(15),str(element.pai_day).center(15),str(element.pai_amt).center(10),element.raportat.center(20),element.observatii.center(10)
    else:
        print "Contractul "+optiune+" nu a fost gasit"


def main():
    global incarcare_efectuata
    while True:
        print "_________________________________________________________________________________________________________"
        print "\n\n\t\t\tMENIU\n"
        if incarcare_efectuata==False:
            print "1. Incarcare Contracte, PAI-uri, Locatii si Serii PAI"
        elif incarcare_efectuata==True:
            print "Sunt incarcate "+str(len(lista_contracte_importate))+" contracte, "+str(len(lista_pai_importate))+" PAI-uri vandute/anulate, "+str(len(lista_locatii))+" locatii si "+str(len(lista_serii_pai))+" serii PAI \n"
            print "1. "+cautare_contract.__doc__
            print "2. "+cautare_pai.__doc__
            print "3. "+cautare_pai_dupa_numar_contract.__doc__
            print "4. "+raport1.__doc__
            print "5. "+raport2.__doc__         
            print "6. "+raport14.__doc__              
            print "7. "+raport3.__doc__
            print "8. "+raport4.__doc__
            print "9. "+raport5.__doc__
            #print "10. "+raport6.__doc__
            print "11. "+raport11.__doc__               
            print "12. "+raport7.__doc__
            print "13. "+raport8.__doc__
            print "14. "+raport9.__doc__
            print "15. "+raport10.__doc__
            print "16. "+raport12.__doc__
            print "17. "+raport13.__doc__
            print "20. Toate rapoartele"
            print "Q. Exit\n"
        optiune=raw_input("Alege o varianta: ")
        print "\n"
        if optiune == "1" and incarcare_efectuata==False:
            incarcare_fisiere_contracte()
            incarcare_fisiere_pai()
            incarcare_locatii()
            incarcare_serii_pai()
            print "Te rog sa astepti procesarea fisierelor.."
            impartire_pe_categorii()
            incarcare_efectuata=True
        elif optiune == "1" and incarcare_efectuata==True:
            cautare_contract()
        elif optiune == "2" and incarcare_efectuata==True:
            cautare_pai()
        elif optiune == "3" and incarcare_efectuata==True:
            cautare_pai_dupa_numar_contract()            
        elif optiune == "4" and incarcare_efectuata==True:
            raport1()
        elif optiune == "5" and incarcare_efectuata==True:
            raport2()
        elif optiune == "6" and incarcare_efectuata==True:
            raport14()              
        elif optiune == "7" and incarcare_efectuata==True:
            raport3()
        elif optiune == "8" and incarcare_efectuata==True:
            raport4()
        elif optiune == "9" and incarcare_efectuata==True:
            raport5()
##        elif optiune == "10" and incarcare_efectuata==True:
##            raport6()
        elif optiune == "11" and incarcare_efectuata==True:
            raport11()            
        elif optiune == "12" and incarcare_efectuata==True:
            raport7()
        elif optiune == "13" and incarcare_efectuata==True:
            raport8()
        elif optiune == "14" and incarcare_efectuata==True:
            raport9()
        elif optiune == "15" and incarcare_efectuata==True:
            raport10()
        elif optiune == "16" and incarcare_efectuata==True:
            raport12()
        elif optiune == "17" and incarcare_efectuata==True:
            raport13()             
        elif optiune == "20" and incarcare_efectuata==True:
            primul_timp=time.time()
            raport1()
            raport2()
            raport3()
            raport4()
            raport5()
            #raport6()
            raport10()
            raport11()
            raport12()
            timp_doi=time.time()
            diferenta_timp=timp_doi-primul_timp
            print "Rularea a durat "+str(diferenta_timp)+" secunde"
        elif optiune.upper() == "Q":
            break
        else:
            print "Optiunea aleasa nu este valida"
        
main()
