"""Link module .blend files into one scene (keeps modules separately editable)."""
import os, sys, bpy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def link_modules(modules, out_path=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system='METRIC'
    for m in modules:
        path = os.path.join(ROOT, "models", "module_%s.blend" % m)
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.objects = list(src.objects)
            dst.collections = list(src.collections)
            dst.materials = list(src.materials)
        for ob in dst.objects:
            if ob.name not in bpy.context.scene.collection.all_objects:
                try:
                    bpy.context.scene.collection.objects.link(ob)
                except Exception:
                    pass
        for col in dst.collections:
            try:
                if col.name not in bpy.context.scene.collection.children:
                    bpy.context.scene.collection.children.link(col)
            except Exception:
                pass
    if out_path:
        bpy.ops.wm.save_as_mainfile(filepath=out_path)
if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    mods = argv[0].split(",") if argv else ["hull","superstructure"]
    out = argv[1] if len(argv)>1 else os.path.join(ROOT,"models","ship_assembly.blend")
    link_modules(mods, out)
    print("assembled", mods, "->", out)
