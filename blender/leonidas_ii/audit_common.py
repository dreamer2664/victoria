"""Shared audit input identity, never a physical-acceptance shortcut."""
import os,hashlib
from pathlib import Path
import bpy
from meshkit import ROOT,GAME_QUALITY


def audit_inputs(candidate=False):
    expected_model=ROOT/('exports/leonidas_ii/build/Aurelian_Game_Source.blend' if GAME_QUALITY else 'models/leonidas_ii/Aurelian_1889.blend')
    expected_data=ROOT/('exports/leonidas_ii/build/build_data.json' if GAME_QUALITY else 'exports/leonidas_ii/build_data.json')
    model=Path(bpy.data.filepath).resolve()
    override=os.getenv('LII_AUDIT_BUILD_DATA')
    assert candidate or not override,'Build-data override is diagnostic/candidate-only.'
    data=ROOT/override if override else expected_data
    assert model.is_file(),('No actual saved mesh input',str(model))
    assert data.is_file(),('Missing matching build data',str(data))
    if not candidate:
        assert model==expected_model.resolve(),('Wrong saved model for requested quality',str(model),str(expected_model))
    return model,data


def current_generator_hashes():
    # Match build.py's explicit provenance set, including newly added
    # auditors. Checking only the OLD build's keys missed unbound new files.
    here=Path(__file__).resolve().parent
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(here.glob('*.py')) if p.name not in ('render.py','render_crew_details.py','audit_structure.py')}


def binding_mismatches(current,saved):
    return sorted(k for k in set(current)|set(saved) if current.get(k)!=saved.get(k))
