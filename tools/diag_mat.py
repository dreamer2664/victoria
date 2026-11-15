import bpy, sys
sys.path.insert(0,"/home/user/victoria")
for n in ("Interior_Floors","Decks_SaloonProm","Library","Music_Room","Galley"):
    ob=bpy.data.objects.get(n)
    if not ob: print(n,"MISSING"); continue
    mats=[m.name if m else None for m in ob.data.materials]
    print("%-20s faces=%5d mats=%s" % (n, len(ob.data.polygons), mats))
    if ob.data.polygons:
        idx=set(p.material_index for p in ob.data.polygons)
        print("   material indices used:", sorted(idx))
