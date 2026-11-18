"""Publish the LEONIDAS-II root dimension entry point; legacy spec unchanged."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import *
contract=json.loads((ROOT/'interfaces/leonidas_ii_ship.json').read_text())
built=json.loads((ROOT/'exports/leonidas_ii/build_data.json').read_text())
# Explicitly separate the schedule from counted physical accommodation.
contract['actual_built_counts']=built['counts']
contract['actual_built_counts_source']='exports/leonidas_ii/build_data.json'
contract['actual_dining_seats']={r['id']:r['actual_seats'] for r in built['rooms'] if r.get('kind') in ('dining','dining_second')}
(ROOT/'interfaces/leonidas_ii_ship.json').write_text(json.dumps(contract,indent=2)+'\n')
rows=[]
def add(name,value,unit='m',basis='fictional reconstruction design choice',source='shipdesign/leonidas_ii.py'):
 rows.append(dict(dimension=name,value=value,unit=unit,source=source,basis=basis))
for k,v in contract['dimensions_m'].items():add(k,v,basis='preserved principal envelope; not a measured historical vessel')
add('metres per Roblox stud',M_PER_STUD,'m/stud','shared project scale; apply once after metric GLB import')
for key,z in DECKS.items():add(key+' deck above baseline',z)
add('shaft centre above baseline',SHAFT_Z)
add('propeller plane X',PROP_X);add('rudder stock X',RUDDER_X)
add('propeller diameter',2*PROP_R);add('propeller pitch',PROP_PITCH)
add('nominal signed ahead shaft speed',SHAFT_RPM,'rpm','kinematic gameplay target, not a power or sea-trial result')
add('nominal advance ratio',ADVANCE_RATIO,'-','gameplay approximation, not measured slip')
add('kinematic target speed',round(SHAFT_RPM*PROP_PITCH/60*ADVANCE_RATIO/.514444,3),'kn','rpm × pitch × advance ratio, not a resistance result')
add('HP/IP/LP bores',list(ENGINE_BORES));add('stroke',2*CRANK_R);add('connecting rod pin distance',CONROD_L)
add('engine cylinder X stations',list(ENGINE_XS));add('boiler X rows',list(BOILER_XS));add('boiler Y stations',list(BOILER_YS));add('funnel base X stations',list(FUNNELS))
add('boiler diameter',4.2);add('boiler barrel length',3.35);add('target boiler working pressure',11,'bar','fictional design target; pressure-vessel/steam balance unverified')
for key,value in contract['hydrostatics'].items():
 if key!='note':add('numerical hull '+key,value,{'volume_m3':'m3','saltwater_displacement_t':'t','lcb_m_forward':'m','cb_lbp':'-'}.get(key,'-'),'numerical section integration, no stability/strength/resistance certification')
manifest=dict(schema='victoria.dimension_manifest',version='2.0',generation='LEONIDAS-II',generated='2026-11-16',ship='SS Aurelian',fictional=True,canonical_interface='interfaces/leonidas_ii_ship.json',legacy_manifest='docs/leonidas_ii/inspection/INHERITED_DIMENSION_MANIFEST.json',note='Supersedes the root legacy entry point only. Original interfaces/ship_spec.json and generators are retained unchanged as provenance; do not mix their machinery/deck values with this generation.',dimensions=rows,coordinates=dict(authoring=contract['authoring'],export=contract['export'],roblox_dimensions_studs=dict(loa=LOA/M_PER_STUD,moulded_beam=BEAM/M_PER_STUD,draft=DRAFT/M_PER_STUD)),actual_built_counts=built['counts'],planning_targets_not_achieved=dict(passengers=900,crew=196),boat_mounts=contract['boat_mounts'],acceptance='Roblox Studio import, avatar/multiplayer/performance, stability, safety and bilateral boat/port approval remain unverified. Three sockets are not the full eleven-boat inventory.')
(ROOT/'DIMENSION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Published root dimensions from current LEONIDAS-II contract and built counts.')
