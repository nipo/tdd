from datetime import date, time, datetime, timedelta
import re

__doc__ = """

2D-Doc data definitions from
"Specifications-techniques-des-codes-a-barres_2D-Doc_v3.1.3.pdf" from
ANTS website.  This only defines perimeter ID 1.

"""

class Format:
    def __init__(self, size_min, size_max):
        self.size_min = size_min
        self.size_max = size_max

    def parse(self, text):
        return text

    def serialize(self, text):
        if self.size_min is not None and len(text) < self.size_min:
            raise ValueError("Too small")
        if self.size_max is not None and len(text) > self.size_max:
            raise ValueError("Too long")
        return text

class String(Format):
    allowed_format = re.compile(r'.*')
    pad_post = None
    pad_pre = None

    def parse(self, text):
        if self.pad_pre is not None:
            return text.lstrip(self.pad_pre)
        if self.pad_post is not None:
            return text.rstrip(self.pad_post)
        return text

    def serialize(self, text):
        if self.size_min == self.size_max and len(text) != self.size_min:
            if self.pad_pre:
                text = text.rjust(self.size_min, self.pad_pre)
            elif self.pad_post:
                text = text.ljust(self.size_min, self.pad_post)
        if self.size_min is not None and len(text) < self.size_min:
            raise ValueError("Too small")
        if self.size_max is not None and len(text) > self.size_max:
            raise ValueError("Too long")
        return text

class StringAZ(String):
    allowed_format = re.compile(r'[A-Z]*')

class StringAZ09(String):
    allowed_format = re.compile(r'[A-Z0-9]*')

class StringAZSp(String):
    allowed_format = re.compile(r'[A-Z ]*')

class StringAZ09Sp(String):
    allowed_format = re.compile(r'[A-Z0-9 ]*')

class StringAZ09SpSl(String):
    allowed_format = re.compile(r'[A-Z0-9 /]*')

class StringAZSpSl(String):
    allowed_format = re.compile(r'[A-Z /]*')

class StringAZ09Dash(String):
    allowed_format = re.compile(r'[A-Z0-9-]*')

class Numeric(String):
    allowed_format = re.compile(r'[0-9]*')

class Numeric0(String):
    allowed_format = re.compile(r'[0-9]*')
    pad_pre = '0'

QualName = StringAZ09SpSl
Iso3166_2 = String

class Decimal(String):
    allowed_format = re.compile(r'[0-9.-]*')
    pad_pre = '0'

class PhoneNumber(String):
    allowed_format = re.compile(r'[0-9 ]*')
    pad_pre = ' '
    
class Date4(Format):
    EPOCH = date(2000, 1, 1)

    def parse(self, text):
        v = int(text, 16)
        return self.EPOCH + timedelta(days = v)

    def serialize(self, d):
        return f'{(d - self.EPOCH).days:04X}'
    
class Boolean(Format):
    def parse(self, text):
        return text == "1"

    def serialize(self, v):
        return "1" if v else "0"

class JJMMAAAA(Format):
    def parse(self, text):
        j = int(text[:2], 10)
        m = int(text[2:4], 10)
        a = int(text[4:8], 10)
        return date(a, m, j)

    def serialize(self, d):
        return f'{d.day:02d}{d.month:02d}{d.year:04d}'

class JJMMAAAAHHMM(Format):
    def parse(self, text):
        j = int(text[:2], 10)
        m = int(text[2:4], 10)
        a = int(text[4:8], 10)
        h = int(text[8:10], 10)
        mi = int(text[10:12], 10)
        return datetime(a, m, j, h, mi)

    def serialize(self, d):
        return f'{d.day:02d}{d.month:02d}{d.year:04d}{d.hour:02d}{d.minute:02d}'

class HexInt(Format):
    def parse(self, text):
        v = int(text, 16)
        return v

    def serialize(self, v):
        if self.size_min == self.size_max:
            fmt = "%%0%dX" % self.size_min
        else:
            fmt = "%X"
        return fmt % v

class Time6(Format):
    def parse(self, text):
        h = int(text[:2], 10)
        m = int(text[2:4], 10)
        s = int(text[4:6], 10)
        return time(h, m, s)

    def serialize(self, d):
        return f'{d.hour:02d}{d.minute:02d}{d.second:02d}'

class HHMM(Format):
    def parse(self, text):
        h = int(text[:2], 10)
        m = int(text[2:4], 10)
        return time(h, m)

    def serialize(self, d):
        return f'{d.hour:02d}{d.minute:02d}'

class StringBase32(Format):
    def parse(self, text):
        from base64 import b32decode
        text = text + '='*((-len(text))%8)
        return b32decode(text)

    def serialize(self, text):
        from base64 import b32encode
        return b32encode(text)

class Base36(Format):
    def parse(self, text):
        return int(text, 36)

    def serialize(self, text):
        raise NotImplementedError()

class Definition:
    def __init__(self, id, name, size_min, size_max, encoding, description = ""):
        self.id = id
        self.name = name
        self.fixed = size_min if size_min == size_max else None
        self.encoding = encoding(size_min, size_max)
        self.description = description

class Group:
    def __init__(self, name, *definitions):
        self.name = name
        self.definitions = list(definitions)

class Doctype:
    def __init__(self, id, user_type, emitter_type):
        self.id = id
        self.user_type = user_type
        self.emitter_type = emitter_type

class Perimeter:
    def __init__(self, id, *items):
        self.id = id
        self.groups = []
        self.datatypes = {}
        self.doctypes = {}
        for i in items:
            if isinstance(i, Group):
                self.groups.append(i)
                for d in i.definitions:
                    self.datatypes[d.id] = i, d
            elif isinstance(i, Doctype):
                self.doctypes[i.id] = i

    def datatype_get(self, id):
        group, definition = self.datatypes[id]
        return group, definition

    def doctype_get(self, id):
        return self.doctypes[id]

class Definitions:
    def __init__(self, *perimeters):
        self.perimeters = {}
        for p in perimeters:
            self.perimeters[p.id] = p

    def datatype_get(self, perimeter, id):
        try:
            p = self.perimeters[perimeter]
            return p.datatype_get(id)
        except KeyError:
            return Group("Unknown group"), Definition(id, "Unknown "+id, 0, None, String)

    def doctype_get(self, perimeter, id):
        try:
            p = self.perimeters[perimeter]
            return p.doctype_get(id)
        except KeyError:
            return Doctype(id, "Unknown "+id, "Unknown")

c40 = Definitions(
    Perimeter(1,
              Doctype("00", "Justificatif de domicile", "Sp??cifique"),
              Doctype("01", "Justificatif de domicile", "Facture"),
              Doctype("02", "Justificatif de domicile", "Avis TH"),
              Doctype("03", "Justificatif de domiciliation bancaire", "RIB"),
              Doctype("05", "Justificatif de domiciliation bancaire", "SEPAmail"),
              Doctype("04", "Justificatif de ressources", "Avis IR"),
              Doctype("06", "Justificatif de ressources", "Bulletin de salaire"),
              Doctype("11", "Justificatif de ressources", "Relev?? de compte"),
              Doctype("11", "Justificatif de ressources", "Relev?? de compte"),
              Doctype("11", "Justificatif de ressources", "Relev?? de compte"),
              Doctype("07",  "Justificatif d'identit??", "Titre d???identit??"),
              Doctype("08",  "Justificatif d'identit??", "MRZ"),
              Doctype("13", "Justificatif d'identit??", "Document ??tranger"),
              Doctype("09", "Justificatif fiscal", "Facture ??tendue"),
              Doctype("10", "Justificatif d'emploi", "Contrat de travail"),
              Doctype("15", "Justificatif d'emploi", "Attestation de d??cision favorable d'une demande d'autorisation de travail"),
              Doctype("A0", "Justificatif de v??hicule", "Certificat de qualit?? de l'air"),
              Doctype("A7", "Justificatif de v??hicule", "Certificat de qualit?? de l'air (V2)"),
              Doctype("14", "Justificatif de v??hicule", "Attestation DICEM"),
              Doctype("A1", "Justificatif permis de conduire", "Courrier Permis ?? points"),
              Doctype("A2", "Justificatif de sant??", "Carte Mobilit?? Inclusion"),
              Doctype("A3", "Justificatif d'activit??", "Macaron VTC"),
              Doctype("A5", "Justificatif d'activit??", "Carte T3P"),
              Doctype("A6", "Justificatif d'activit??", "Carte Professionnelle Sapeur-Pompier"),
              Doctype("A9", "Justificatif d'activit??", "Permis de chasser"),
              Doctype("A4", "Justificatif m??dical", "Certificat de d??c??s"),
              Doctype("B0", "Justificatif acad??mique", "Dipl??me"),
              Doctype("B1", "Justificatif acad??mique", "Attestation de Versement de la Contribution ?? la Vie Etudiante"),
              Doctype("12", "Justificatif juridique/judiciaire", "Acte d'huissier"),
              Doctype("A8", "Certificat d???immatriculation", "Certificat de session ??lectronique"),
              Doctype("C1", "Autorisations douani??re", "Renseignement Tarifaire Contraignant"),
              Doctype("C2", "Autorisations douani??re", "Accord Pr??alable pour le transfert d???armes"),
              Doctype("C3", "Autorisations douani??re", "Permis de transfert d???armes ?? feu et de munitions"),
              Doctype("C4", "Autorisations douani??re", "Autorisation d???importation de mat??riels de guerre"),
              Doctype("C5", "Autorisations douani??re", "Licence d???exportation d???armes ?? feu"),
              Doctype("C6", "Autorisations douani??re", "Agr??ment de transfert d???armes ?? feu et de munitions"),
              Doctype("B2", "R??sultats des tests virologiques", "Test COVID"),
              Doctype("L1", "Attestation Vaccinale", "Attestation Vaccinale"),

              Group("Identifiants de donn??es compl??mentaires du code 2D-DOC",
                    Definition("01", "Identifiant unique du document", 0, None, String),
                    Definition("02", "Cat??gorie de document", 0, None, String),
                    Definition("03", "Sous-cat??gorie de document", 0, None, String),
                    Definition("04", "Application de composition", 0, None, String),
                    Definition("05", "Version de l???application de composition", 0, None, String),
                    Definition("06", "Date de l???association entre le document et le code 2D-Doc", 4, 4, Date4),
                    Definition("07", "Heure de l???association entre le document et le code 2D-Doc", 6, 6, Time6),
                    Definition("08", "Date d???expiration du document", 4, 4, Date4),
                    Definition("09", "Nombre de pages du document", 4, 4, Numeric0),
                    Definition("0A", "Editeur du 2D-Doc", 9, 9, Numeric0),
                    Definition("0B", "Int??grateur du 2D-Doc", 9, 9, Numeric0),
                    Definition("0C", "URL du document", 0, None, StringBase32),
              ),

              Group("Identifiants de donn??es propres aux factures",
                    Definition("10", "Ligne 1 de la norme adresse postale du b??n??ficiaire de la prestation", 0, 38, QualName),
                    Definition("11", "Qualit?? et/ou titre de la personne b??n??ficiaire de la prestation", 0, 38, StringAZSp),
                    Definition("12", "Pr??nom de la personne b??n??ficiaire de la prestation", 0, 38, StringAZSp),
                    Definition("13", "Nom de la personne b??n??ficiaire de la prestation", 0, 38, StringAZSp),
                    Definition("14", "Ligne 1 de la norme adresse postale du destinataire de la facture", 0, 38, QualName),
                    Definition("15", "Qualit?? et/ou titre de la personne destinataire de la facture", 0, 38, StringAZSp),
                    Definition("16", "Pr??nom de la personne destinataire de la facture", 0, 38, StringAZSp),
                    Definition("17", "Nom de la personne destinataire de la facture", 0, 38, StringAZSp),
                    Definition("18", "Num??ro de la facture", 0, None, StringAZSp),
                    Definition("19", "Num??ro de client", 0, None, StringAZSp),
                    Definition("1A", "Num??ro du contrat", 0, None, StringAZSp),
                    Definition("1B", "Identifiant du souscripteur du contrat", 0, None, StringAZSp),
                    Definition("1C", "Date d???effet du contrat", 8, 8, JJMMAAAA),
                    Definition("1D", "Montant TTC de la facture", 0, 16, Decimal),
                    Definition("1E", "Num??ro de t??l??phone du b??n??ficiaire de la prestation", 0, 30, PhoneNumber),
                    Definition("1F", "Num??ro de t??l??phone du destinataire de la facture", 0, 30, PhoneNumber),
                    Definition("1G", "Pr??sence d???un co-b??n??ficiaire de la prestation non mentionn?? dans le code", 1, 1, Boolean),
                    Definition("1H", "Pr??sence d???un co-destinataire de la facture non mentionn?? dans le code", 1, 1, Boolean),
                    Definition("1I", "Ligne 1 de la norme adresse postale du co-b??n??ficiaire de la prestation", 0, 38, QualName),
                    Definition("1J", "Qualit?? et/ou titre du co-b??n??ficiaire de la prestation", 0, 38, StringAZSp),
                    Definition("1K", "Pr??nom du co-b??n??ficiaire de la prestation", 0, 38, StringAZSp),
                    Definition("1L", "Nom du co-b??n??ficiaire de la prestation", 0, 38, StringAZSp),
                    Definition("1M", "Ligne 1 de la norme adresse postale du co-destinataire de la facture", 0, 38, QualName),
                    Definition("1N", "Qualit?? et/ou titre du co-destinataire de la facture", 0, 38, StringAZSp),
                    Definition("1O", "Pr??nom du co-destinataire de la facture", 0, 38, StringAZSp),
                    Definition("1P", "Nom du co-destinataire de la facture", 0, 38, StringAZSp),
                    Definition("20", "Ligne 2 de la norme adresse postale du point de service des prestations", 0, 38, StringAZ09Sp),
                    Definition("21", "Ligne 3 de la norme adresse postale du point de service des prestations", 0, 38, StringAZ09Sp),
                    Definition("22", "Ligne 4 de la norme adresse postale du point de service des prestations", 0, 38, StringAZ09Sp),
                    Definition("23", "Ligne 5 de la norme adresse postale du point de service des prestations", 0, 38, StringAZ09Sp),
                    Definition("24", "Code postal ou code cedex du point de service des prestations", 5, 5, Numeric0),
                    Definition("25", "Localit?? de destination ou libell?? cedex du point de service des prestations", 0, 32, StringAZSp),
                    Definition("26", "Pays de service des prestations", 2, 2, Iso3166_2),
                    Definition("27", "Ligne 2 de la norme adresse postale du destinataire de la facture", 0, 38, StringAZ09Sp),
                    Definition("28", "Ligne 3 de la norme adresse postale du destinataire de la facture", 0, 38, StringAZ09Sp),
                    Definition("29", "Ligne 4 de la norme adresse postale du destinataire de la facture", 0, 38, StringAZ09Sp),
                    Definition("2A", "Ligne 5 de la norme adresse postale du destinataire de la facture", 0, 38, StringAZ09Sp),
                    Definition("2B", "Code postal ou code cedex du destinataire de la facture", 5, 5, Numeric0),
                    Definition("2C", "Localit?? de destination ou libell?? cedex du destinataire de la facture", 0, 32, StringAZSp),
                    Definition("2D", "Pays du destinataire de la facture", 2, 2, Iso3166_2),
              ),

              Group("Identifiants de donn??es bancaires",
                    Definition("30", "Qualit?? Nom et Pr??nom", 0, 140, QualName),
                    Definition("31", "Code IBAN", 14, 38, StringAZ09),
                    Definition("32", "Code BIC/SWIFT", 8, 11, StringAZ09),
                    Definition("33", "Code BBAN", 0, 30, StringAZ09),
                    Definition("34", "Pays de localisation du compte", 2, 2, Iso3166_2),
                    Definition("35", "Identifiant SEPAmail (QXBAN)", 14, 34, StringAZ09),
                    Definition("36", "Date de d??but de p??riode", 4, 4, Date4),
                    Definition("37", "Date de fin de p??riode", 4, 4, Date4),
                    Definition("38", "Solde compte d??but de p??riode", 0, 11, Decimal),
                    Definition("39", "Solde compte fin de p??riode", 0, 11, Decimal),
              ),

              Group("Identifiants de donn??es fiscales",
                    Definition("40", "Num??ro fiscal", 13, 13, Numeric0),
                    Definition("41", "Revenu fiscal de r??f??rence", 0, None, Numeric),
                    Definition("42", "Situation du foyer", 0, None, StringAZ),
                    Definition("43", "Nombre de parts", 0, None, Numeric),
                    Definition("44", "R??f??rence d???avis d???imp??t", 13, 13, Numeric0),
              ),

              Group("Identifiants de donn??es relatives ?? l???activit?? professionnelle",
                    Definition("50", "SIRET de l???employeur", 14, 14, Numeric0),
                    Definition("51", "Nombre d???heures travaill??es", 6, 6, Decimal),
                    Definition("52", "Cumul du nombre d???heures travaill??es", 7, 7, Decimal),
                    Definition("53", "D??but de p??riode", 4, 4, Date4),
                    Definition("54", "Fin de p??riode", 4, 4, Date4),
                    Definition("55", "Date de d??but de contrat", 8, 8, JJMMAAAA),
                    Definition("56", "Date de fin de contrat", 8, 8, JJMMAAAA),
                    Definition("57", "Date de signature du contrat", 8, 8, JJMMAAAA),
                    Definition("58", "Salaire net imposable", 0, 11, Decimal),
                    Definition("59", "Cumul du salaire net imposable", 0, 12, Decimal),
                    Definition("5A", "Salaire brut du mois", 0, 11, Decimal),
                    Definition("5B", "Cumul du salaire brut", 0, 12, Decimal),
                    Definition("5C", "Salaire net", 0, 11, Decimal),
                    Definition("5D", "Ligne 2 de la norme adresse postale de l???employeur", 0, 38, StringAZ09Sp),
                    Definition("5E", "Ligne 3 de la norme adresse postale de l???employeur", 0, 38, StringAZ09Sp),
                    Definition("5F", "Ligne 4 de la norme adresse postale de l???employeur", 0, 38, StringAZ09Sp),
                    Definition("5G", "Ligne 5 de la norme adresse postale de l???employeur", 0, 38, StringAZ09Sp),
                    Definition("5H", "Code postal ou code cedex de l???employeur", 5, 5, Numeric0),
                    Definition("5I", "Localit?? de destination ou libell?? cedex de l???employeur", 0, 32, StringAZSp),
                    Definition("5J", "Pays de l???employeur", 2, 2, Iso3166_2),
                    Definition("5K", "Identifiant Cotisant Prestations Sociales", 0, 50, StringAZ09Sp),
                    Definition("5L", "Num??ro de SIRET ou RNA", 9, 14, StringAZ09),
                    Definition("5M", "D??nomination sociale", 0, 38, StringAZ09Sp),
                    Definition("5N", "Num??ro de dossier d'autorisation de travail", 21, 21, Numeric0),
                    Definition("5O", "Nom de l'employeur", 0, 38, StringAZSp),
                    Definition("5P", "Pr??nom de l'employeur", 0, 38, StringAZSp),
                    Definition("5Q", "Nom du d??clarant", 0, 38, StringAZSp),
                    Definition("5R", "Pr??nom du d??clarant", 0, 38, StringAZSp),
                    Definition("5S", "Fonction du d??clarant", 0, 40, StringAZSp),
                    Definition("5T", "Type de contrat de travail", 1, 1, StringAZ),
                    Definition("5U", "Dur??e du contrat", 0, 12, StringAZ09Sp),
              ),

              Group("Identifiants de donn??es relatives aux titres d???identit??",
                    Definition("60", "Liste des pr??noms", 0, 60, StringAZSpSl),
                    Definition("61", "Pr??nom", 0, 20, StringAZSp),
                    Definition("62", "Nom patronymique", 0, 38, StringAZSp),
                    Definition("63", "Nom d???usage", 0, 38, StringAZSp),
                    Definition("64", "Nom d?????pouse/??poux", 0, 38, StringAZSp),
                    Definition("65", "Type de pi??ce d???identit??", 2, 2, StringAZSp),
                    Definition("66", "Num??ro de la pi??ce d???identit??", 0, 20, StringAZ09),
                    Definition("67", "Nationalit??", 2, 2, Iso3166_2),
                    Definition("68", "Genre", 1, 1, StringAZ),
                    Definition("69", "Date de naissance", 8, 8, JJMMAAAA),
                    Definition("6A", "Lieu de naissance", 0, 32, StringAZSp),
                    Definition("6B", "D??partement du bureau ??metteur", 3, 3, StringAZ09),
                    Definition("6C", "Pays de naissance", 2, 2, Iso3166_2),
                    Definition("6D", "Nom et pr??nom du p??re", 0, 60, StringAZ09SpSl),
                    Definition("6E", "Nom et pr??nom de la m??re", 0, 60, StringAZ09SpSl),
                    Definition("6F", "Machine Readable Zone (Zone de Lecture Automatique, ZLA)", 0, 90, StringAZ09Sp),
                    Definition("6G", "Nom", 1, 38, StringAZSp),
                    Definition("6H", "Civilit??", 1, 10, StringAZSp),
                    Definition("6I", "Pays ??metteur", 2, 2, Iso3166_2),
                    Definition("6J", "Type de document ??tranger", 1, 1, Numeric0),
                    Definition("6K", "Num??ro de la demande de document ??tranger", 19, 19, Numeric0),
                    Definition("6L", "Date de d??p??t de la demande", 8, 8, JJMMAAAA),
                    Definition("6M", "Cat??gorie du titre", 0, 40, StringAZSp),
                    Definition("6N", "Date de d??but de validit??", 8, 8, JJMMAAAA),
                    Definition("6O", "Date de fin de validit??", 8, 8, JJMMAAAA),
                    Definition("6P", "Autorisation", 0, 40, StringAZSp),
                    Definition("6Q", "Num??ro d?????tranger", 0, 10, StringAZ09),
                    Definition("6R", "Num??ro de visa", 12, 12, StringAZ09),
                    Definition("6S", "Ligne 2 de l???adresse postale du domicile", 0, 38, StringAZ09Sp),
                    Definition("6T", "Ligne 3 de l???adresse postale du domicile", 0, 38, StringAZ09Sp),
                    Definition("6U", "Ligne 4 de l???adresse postale du domicile", 0, 38, StringAZ09Sp),
                    Definition("6V", "Ligne 5 de l???adresse postale du domicile", 0, 38, StringAZ09Sp),
                    Definition("6W", "Code postal ou code cedex de l???adresse postale du domicile", 5, 5, Numeric0),
                    Definition("6X", "Commune de l???adresse postale du domicile", 0, 32, StringAZSp),
                    Definition("6Y", "Code pays de l???adresse postale du domicile", 2, 2, Iso3166_2),
                    Definition("6Z", "Num??ro d'??tranger de l'autorisation de travail", 9, 11, StringAZ09),
              ),

              Group("Identifiants de donn??es relatives aux donn??es de sant??",
                    Definition("70", "Date et heure du d??c??s", 12, 12, JJMMAAAAHHMM),
                    Definition("71", "Date et heure du constat de d??c??s", 12, 12, JJMMAAAAHHMM),
                    Definition("72", "Nom du d??funt", 1, 38, StringAZSp),
                    Definition("73", "Pr??noms du d??funt", 0, 60, StringAZSpSl),
                    Definition("74", "Nom de jeune fille du d??funt", 0, 38, StringAZSp),
                    Definition("75", "Date de naissance du d??funt", 8, 8, JJMMAAAA),
                    Definition("76", "Genre du d??funt", 1, 1, StringAZ),
                    Definition("77", "Commune de d??c??s", 0, 45, StringAZSp),
                    Definition("78", "Code postal de la commune de d??c??s", 5, 5, Numeric0),
                    Definition("79", "Adresse du domicile du d??funt", 0, 114, StringAZ09Sp),
                    Definition("7A", "Code postal du domicile du d??funt", 5, 5, Numeric0),
                    Definition("7B", "Commune du domicile du d??funt", 0, 45, StringAZSp),
                    Definition("7C", "Obstacle m??dico-l??gal", 1, 1, Boolean),
                    Definition("7D", "Mise en bi??re", 1, 1, StringAZ),
                    Definition("7E", "Obstacle aux soins de conservation", 1, 1, Boolean),
                    Definition("7F", "Obstacle aux dons du corps", 1, 1, Boolean),
                    Definition("7G", "Recherche de la cause du d??c??s", 1, 1, Boolean),
                    Definition("7H", "D??lai de transport du corps", 2, 2, HexInt),
                    Definition("7I", "Proth??se avec pile", 1, 1, Boolean),
                    Definition("7J", "Retrait de la pile de proth??se", 1, 1, Boolean),
                    Definition("7K", "Code NNC", 13, 13, StringAZ09),
                    Definition("7L", "Code Finess de l???organisme agr????", 9, 9, StringAZ09),
                    Definition("7M", "Identification du m??decin", 0, 64, StringAZ09Sp),
                    Definition("7N", "Lieu de validation du certificat de d??c??s", 0, 128, StringAZ09Sp),
                    Definition("7O", "Certificat de d??c??s suppl??mentaire", 1, 1, Boolean),
              ),

              Group("Identifiants relatifs aux activit??s professionnelles",
                    Definition("80", "Nom", 0, 38, StringAZSp),
                    Definition("81", "Pr??noms", 0, 60, StringAZSpSl),
                    Definition("82", "Num??ro de carte", 0, 20, StringAZ09Sp),
                    Definition("83", "Organisme de tutelle", 0, 40, StringAZ09Sp),
                    Definition("84", "Profession", 0, 40, StringAZ09Sp),
                    Definition("85", "Num??ro de permis de chasser", 17, 17, StringAZ09Dash),
              ),

              Group("Identifiants relatifs aux donn??es juridiques/judiciaires",
                    Definition("90", "Identit?? de l???huissier de justice", 0, 38, StringAZSpSl),
                    Definition("91", "Identit?? ou raison sociale du demandeur", 0, 38, StringAZSpSl),
                    Definition("92", "Identit?? ou raison sociale du destinataire", 0, 38, StringAZSpSl),
                    Definition("93", "Identit?? ou raison sociale de tiers concern??", 0, 38, StringAZSpSl),
                    Definition("94", "Intitul?? de l???acte", 0, 38, StringAZ09Sp),
                    Definition("95", "Num??ro de l???acte", 0, 18, StringAZ09),
                    Definition("96", "Date de signature de l???acte", 8, 8, JJMMAAAA),
              ),

              Group("Identifiants de donn??es relatives aux v??hicules",
                    Definition("A0", "Pays ayant ??mis l???immatriculation du v??hicule", 2, 2, Iso3166_2),
                    Definition("A1", "Immatriculation du v??hicule", 0, 17, StringAZ09Dash),
                    Definition("A2", "Marque du v??hicule", 0, 17, StringAZ09Sp),
                    Definition("A3", "Nom commercial du v??hicule", 0, 17, StringAZ09Sp),
                    Definition("A4", "Num??ro de s??rie du v??hicule (VIN)", 17, 17, StringAZ09Sp),
                    Definition("A5", "Cat??gorie du v??hicule", 3, 3, StringAZ09Sp),
                    Definition("A6", "Carburant", 2, 2, StringAZ09),
                    Definition("A7", "Taux d?????mission de CO2 du v??hicule (en g/km)", 3, 3, HexInt),
                    Definition("A8", "Indication de la classe environnementale de r??ception CE", 0, 12, StringAZ09SpSl),
                    Definition("A9", "Classe d?????mission polluante", 3, 3, String),
                    Definition("AA", "Date de premi??re immatriculation du v??hicule", 8, 8, JJMMAAAA),
                    Definition("AB", "Type de lettre", 0, 8, StringAZ09),
                    Definition("AC", "N?? Dossier", 0, 19, StringAZ09),
                    Definition("AD", "Date Infraction", 4, 4, Date4),
                    Definition("AD", "Date Infraction", 4, 4, Date4),
                    Definition("AE", "Heure de l???infraction", 4, 4, HHMM),
                    Definition("AF", "Nombre de points retir??s lors de l???infraction", 1, 1, Base36),
                    Definition("AG", "Solde de points", 1, 1, Base36),
                    Definition("AH", "Num??ro de la carte", 0, 30, StringAZ09),
                    Definition("AI", "Date d???expiration initiale", 8, 8, JJMMAAAA),
                    Definition("AJ", "Num??ro EVTC", 13, 13, StringAZ09),
                    Definition("AK", "Num??ro de macaron", 7, 7, Numeric0),
                    Definition("AL", "Num??ro de la carte", 11, 11, StringAZ09),
                    Definition("AM", "Motif de sur-classement", 0, 5, StringAZ09Sp),
                    Definition("AN", "Kilom??trage", 8, 8, Numeric0),
                    Definition("AO", "Num??ro d???identification", 6, 6, Numeric0),
                    Definition("AP", "Type d???engin", 0, 60, StringAZSp),
                    Definition("AQ", "Num??ro de s??rie", 0, 25, StringAZ09),
                    Definition("AR", "Mod??le", 0, 35, StringAZ09Sp),
                    Definition("AS", "Couleur dominante", 0, 10, StringAZ),
                    Definition("AT", "Type de propri??taire", 1, 1, Numeric),
                    Definition("AU", "Ligne 2 de l'adresse postale du propri??taire", 0, 38, StringAZ09Sp),
                    Definition("AV", "Ligne 3 de l'adresse postale du propri??taire", 0, 38, StringAZ09Sp),
                    Definition("AW", "Ligne 4 de l'adresse postale du propri??taire", 0, 38, StringAZ09Sp),
                    Definition("AX", "Ligne 5 de l'adresse postale du propri??taire", 0, 38, StringAZ09Sp),
                    Definition("AY", "Code postal ou code cedex de l'adresse postale du propri??taire", 5, 5, Numeric0),
                    Definition("AZ", "Commune de l'adresse postale du propri??taire", 0, 32, StringAZSp),
              ),

              Group("Identifiants de donn??es pour les justificatifs acad??miques",
                    Definition("B0", "Liste des pr??noms", 0, 60, StringAZSpSl),
                    Definition("B1", "Pr??nom", 0, 20, StringAZSp),
                    Definition("B2", "Nom patronymique", 0, 38, StringAZSp),
                    Definition("B3", "Nom d???usage", 0, 38, StringAZSp),
                    Definition("B4", "Nom d?????pouse/??poux", 0, 38, StringAZSp),
                    Definition("B5", "Nationalit??", 2, 2, Iso3166_2),
                    Definition("B6", "Genre", 1, 1, StringAZ),
                    Definition("B7", "Date de naissance", 8, 8, JJMMAAAA),
                    Definition("B8", "Lieu de naissance", 0, 32, StringAZ09Sp),
                    Definition("B9", "Pays de naissance", 2, 2, Iso3166_2),
                    Definition("BA", "Mention obtenue", 1, 1, Numeric),
                    Definition("BB", "Num??ro ou code d???identification de l?????tudiant", 0, 50, StringAZ09Sp),
                    Definition("BC", "Num??ro du dipl??me", 0, 20, StringAZ09Sp),
                    Definition("BD", "Niveau du dipl??me selon la classification CEC", 1, 1, Numeric),
                    Definition("BE", "Cr??dits ECTS obtenus", 3, 3, Numeric0),
                    Definition("BF", "Ann??e universitaire", 3, 3, HexInt),
                    Definition("BG", "Type de dipl??me", 2, 2, StringAZ),
                    Definition("BH", "Domaine", 0, 30, StringAZ09Sp),
                    Definition("BI", "Mention", 0, 30, StringAZ09Sp),
                    Definition("BJ", "Sp??cialit??", 0, 30, StringAZ09Sp),
                    Definition("BK", "Num??ro de l???Attestation de versement de la CVE", 14, 14, StringAZ09Dash),
              ),

              Group("Identifiants de donn??es relatives au certificat de cession ??lectronique",
                    Definition("C0", "Genre du vendeur", 1, 1, StringAZ),
                    Definition("C1", "Nom patronymique du vendeur", 0, 38, StringAZSp),
                    Definition("C2", "Pr??nom du vendeur", 0, 20, StringAZSp),
                    Definition("C3", "Date et heure de la cession", 12, 12, JJMMAAAAHHMM),
                    Definition("C4", "Date de la signature du vendeur", 8, 8, JJMMAAAA),
                    Definition("C5", "Genre de l???acheteur", 1, 1, StringAZ),
                    Definition("C6", "Nom patronymique de l???acheteur", 0, 38, StringAZSp),
                    Definition("C7", "Pr??nom de l???acheteur", 0, 20, StringAZSp),
                    Definition("C8", "Ligne 4 de la norme adresse postale du domicile de l???acheteur", 0, 38, StringAZ09Sp),
                    Definition("C9", "Code postal ou code cedex du domicile de l???acheteur", 5, 5, Numeric0),
                    Definition("CA", "Commune du domicile de l???acheteur", 0, 45, StringAZSp),
                    Definition("CB", "N?? d???enregistrement", 10, 10, Numeric0),
                    Definition("CC", "Date et heure d???enregistrement dans le SIV", 12, 12, JJMMAAAAHHMM),
              ),

              Group("Identifiants de donn??es relatives aux autorisations douani??res",
                    Definition("D0", "R??f??rence RTC", 17, 17, String),
                    Definition("D1", "Nom du titulaire", 0, 50, String),
                    Definition("D2", "EORI", 0, 20, StringAZ09),
                    Definition("D3", "Date de d??but de validit??", 8, 8, JJMMAAAA),
                    Definition("D4", "Date de fin de validit??", 8, 8, JJMMAAAA),
                    Definition("D5", "Code marchandise", 8, 10, String),
                    Definition("D6", "Num??ro de d??cision", 8, 8, Numeric0),
                    Definition("D7", "Date de d??cision", 8, 8, JJMMAAAA),
                    Definition("D8", "Dur??e de validit??", 2, 2, Numeric0),
                    Definition("D9", "Date de fin de validit?? de la licence", 8, 8, JJMMAAAA),
                    Definition("DA", "Num??ro de licence", 8, 8, Numeric0),
                    Definition("DB", "Nom de l???exp??diteur", 0, 50, StringAZSp),
                    Definition("DC", "Pr??nom de l???exp??diteur", 0, 50, StringAZSp),
                    Definition("DD", "Date de naissance de l???exp??diteur", 8, 8, JJMMAAAA),
                    Definition("DE", "Raison sociale de l???exp??diteur", 0, 50, StringAZ09Sp),
                    Definition("DF", "SIREN de l???exp??diteur", 9, 9, Numeric0),
                    Definition("DG", "SIRET de l???exp??diteur", 14, 14, Numeric0),
                    Definition("DH", "EORI de l???exp??diteur", 0, 20, StringAZ09),
                    Definition("DI", "TIN de l???exp??diteur", 4, 30, StringAZ09),
                    Definition("DJ", "Nom de l???exportateur", 0, 50, StringAZSp),
                    Definition("DK", "Pr??nom de l???exportateur", 0, 50, StringAZSp),
                    Definition("DL", "Date de naissance de l???exportateur", 8, 8, JJMMAAAA),
                    Definition("DM", "Raison sociale de l???exportateur", 0, 50, StringAZ09Sp),
                    Definition("DN", "SIREN de l???exportateur", 9, 9, Numeric0),
                    Definition("DO", "SIRET de l???exportateur", 14, 14, Numeric0),
                    Definition("DP", "EORI de l???exportateur", 0, 20, StringAZ09),
                    Definition("DQ", "Nom du destinataire", 0, 50, StringAZSp),
                    Definition("DR", "Pr??nom du destinataire", 0, 50, StringAZSp),
                    Definition("DS", "Date de naissance du destinataire", 8, 8, JJMMAAAA),
                    Definition("DT", "Raison sociale du destinataire", 0, 50, StringAZ09Sp),
                    Definition("DU", "SIREN du destinataire", 9, 9, Numeric0),
                    Definition("DV", "SIRET du destinataire", 14, 14, Numeric0),
                    Definition("DW", "EORI du destinataire", 0, 50, StringAZ09),
                    Definition("DX", "TIN du destinataire", 4, 30, StringAZ09),
                    Definition("DY", "Nombre de lignes articles", 3, 3, Numeric0),
              ),

              Group("Identifiants de donn??es relatives aux r??sultats des tests virologiques",
                    Definition("F0", "Liste des pr??noms", 0, 38, String),
                    Definition("F1", "Nom patronymique", 0, 60, String),
                    Definition("F2", "Date de naissance", 8, 8, JJMMAAAA),
                    Definition("F3", "Genre", 1, 1, StringAZ),
                    Definition("F4", "Code analyse", 3, 7, StringAZ09),
                    Definition("F5", "R??sultat de l???analyse", 1, 1, StringAZ),
                    Definition("F6", "Date et heure du pr??l??vement", 12, 12, JJMMAAAAHHMM),
              ),

              Group("Identifiants de donn??es relatives ?? une attestation vaccinale",
                    Definition("L0", "Nom Patronymique du patient", 0, 80, String),
                    Definition("L1", "Liste des pr??noms du patient", 0, 80, String),
                    Definition("L2", "Date de naissance du patient", 8, 8, JJMMAAAA),
                    Definition("L3", "Nom de la maladie couverte", 0, 30, String),
                    Definition("L4", "Agent prophylactique", 5, 15, String),
                    Definition("L5", "Nom du vaccin", 5, 30, String),
                    Definition("L6", "Fabricant du vaccin", 5, 30, String),
                    Definition("L7", "Rang du dernier ??tat de vaccination effectu??", 1, 1, Numeric0),
                    Definition("L8", "Nombre de doses attendues pour un cycle complet", 1, 1, Numeric0),
                    Definition("L9", "Date du dernier ??tat du cycle de vaccination", 8, 8, JJMMAAAA),
                    Definition("LA", "Etat du cycle de vaccination", 2, 2, StringAZ),
              ),
    ),
)
