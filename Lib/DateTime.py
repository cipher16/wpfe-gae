import time
import datetime

class date:
    @staticmethod
    def StrToDateTime( Str, Format = '%Y-%m-%d %H:%M:%S' ):
      """    
          Les directives de formats dans ce cas sont:
          %Y = annee sur 4 chiffres
          %m = mois sur 2 chiffres: 1..12
          %d = jour sur 2 chiffres: 1..31
          %H = heure sur 2 chiffres: 0..23
          %M = minutes sur 2 chiffres: 0..59
          %S = secondes sur 2 chiffres: 0..59
      """
      return datetime.datetime.fromtimestamp(time.mktime(time.strptime( Str, Format ) ) )