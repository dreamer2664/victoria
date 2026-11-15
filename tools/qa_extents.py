import bpy
for n in ("Hull_Shell","DeckHouse_SaloonDeck","DeckHouse_Promenade","BoatDeck",
          "Bridge","Decks_SaloonProm","Boats_Davits","Funnels","Masts",
          "Interior_Rooms","Promenade_Rails","Hull_Seams"):
    ob=bpy.data.objects.get(n)
    if not ob: print("%-22s MISSING"%n); continue
    xs=[v.co.x for v in ob.data.vertices]; ys=[v.co.y for v in ob.data.vertices]
    zs=[v.co.z for v in ob.data.vertices]
    print("%-22s x %7.1f..%6.1f  y %5.2f..%5.2f  z %5.2f..%5.2f" %
          (n,min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
