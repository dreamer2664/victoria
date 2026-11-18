"""LEONIDAS-II: single metric plan, geometry datums and circulation contract.

Original fictional Aurelian envelope, not a traced historical vessel.
No dependency on any other agent's geometry. +X bow, +Y port, +Z baseline.
The legacy longitudinal control curves are retained as examined design inputs;
sections, counter, topology, accommodation and mechanical placement are new.
"""
from __future__ import annotations
import math, json
from pathlib import Path
import numpy as np
from .hull import HULL as LEGACY_HULL

ROOT=Path(__file__).resolve().parents[1]
LOA, BEAM, DRAFT, M_PER_STUD=166.0,18.4,6.5,0.28
SHAFT_Z, PROP_X, PROP_R, RUDDER_X=3.0,-78.0,2.65,-79.5
CRANK_R, CONROD_L, PISTON_ROD_L=1.80/2,3.00,2.90
ENGINE_XS=(-11.5,-16.0,-21.0)
ENGINE_BORES=(1.40,2.25,3.50)
SHAFT_RPM, PROP_PITCH, ADVANCE_RATIO=72.0,9.40,.88
BOILER_XS=(3.0,15.5,28.0)
BOILER_YS=(-4.4,0.0,4.4)
FUNNELS=(4.5,30.0)
DECKS={'orlop':2.35,'lower':5.2,'main':8.8,'saloon':11.8,'promenade':14.4,'boat':17.2,'bridge':20.0}
DECK_TOPS={'orlop':5.10,'lower':8.68,'main':11.68,'saloon':14.28,'promenade':17.08,'boat':19.88,'bridge':22.5}
DECK_NAMES={'orlop':'Orlop / lower accommodation','lower':'Lower deck','main':'Main accommodation deck','saloon':'Upper / saloon deck','promenade':'Promenade deck','boat':'Boat deck','bridge':'Navigating bridge'}
BULKHEAD_X=(-74,-58,-30,-7,-3,9,22,36,58,72)

# Dedicated vertical casings, not rooms. Engine ventilation rises beside (not
# through) the dining room. Their footprint is also cut from every deck plate.
CASINGS=[{'id':'Uptake_Aft','rect':(2.3,6.7,-2.2,2.2),'z0':6.0,'z1':30.6},
         {'id':'Uptake_Forward','rect':(27.8,32.2,-2.2,2.2),'z0':6.0,'z1':30.6},
         {'id':'EngineVent','rect':(-9.5,-6.4,-2.2,2.2),'z0':1.6,'z1':17.7},
         {'id':'EngineCasing','rect':(-27.8,-9.7,-3.15,3.15),'z0':8.60,'z1':11.72}]

# Fair longitudinal control arrays. Original curves are sampled once rather
# than invoking their spline evaluator for every rivet/furniture test.
_X=np.linspace(-83,83,1331)
_BW=np.asarray(LEGACY_HULL.beam_wl(_X)).reshape(-1)
_BD=np.asarray(LEGACY_HULL.beam_deck(_X)).reshape(-1)
_ZD=np.asarray(LEGACY_HULL.deck_z(_X)).reshape(-1)
_ZK=np.asarray(LEGACY_HULL.keel_z(_X)).reshape(-1)
# New rounded counter overhang: the old pointed aft deck was too pinched to
# contain steering gear. These are design offsets, not measured museum data.
_aftx=np.array([-83,-82.7,-82,-80,-76,-72,-64,-58])
_afty=np.array([0,.70,1.35,2.35,3.35,4.05,5.10,float(np.interp(-58,_X,_BD))])
_BD=np.where(_X<-58,np.interp(_X,_aftx,_afty),_BD)

def deck_z(x):return float(np.interp(x,_X,_ZD))
def keel_z(x):return max(.08,float(np.interp(x,_X,_ZK)))
def beam_deck(x):return max(0.,float(np.interp(x,_X,_BD)))
def hb(x,z):
    """Outer half breadth of new section, metres. Finite outside hull => 0."""
    if not -83<=x<=83:return 0.
    zk=keel_z(x);zd=deck_z(x)
    if z<zk-1e-6 or z>zd+1e-6:return 0.
    bw=max(0.,float(np.interp(x,_X,_BW)));bd=beam_deck(x)
    if zk>=DRAFT-.01 or bw<.015:
        return bd*max(0.,min(1.,(z-zk)/max(.01,zd-zk)))**.80
    r=max(.015,bw*(.51-.27*min(1.,abs(x)/83)**3))
    rv=min(r*.86,(DRAFT-zk)*.90)
    if z<zk+rv:
        f=max(0.,min(1.,(z-zk)/max(rv,.001)))
        return max(0.,bw-r+r*math.sqrt(max(0.,1-(1-f)**2)))
    if z<=DRAFT:return bw
    f=(z-DRAFT)/max(.01,zd-DRAFT)
    return max(0.,bw+(bd-bw)*f**1.30)

def min_hb(x0,x1,z):return min(hb(float(x),z) for x in np.linspace(x0,x1,9))
def overlap(a,b,margin=.0):
    return min(a[1],b[1])-max(a[0],b[0])>margin and min(a[3],b[3])-max(a[2],b[2])>margin

def rect(r):return (r['x0'],r['x1'],r['y0'],r['y1'])

ROOMS=[]
def room(id,name,deck,bounds,kind,style='service',**kw):
    x0,x1,y0,y1=map(float,bounds)
    r=dict(id=id,name=name,deck=deck,z=DECKS[deck],top=DECK_TOPS[deck],x0=x0,x1=x1,y0=y0,y1=y1,kind=kind,style=style,**kw)
    r.setdefault('door_wall','y0' if y0>0 else 'y1')
    r.setdefault('door_u',(x0+x1)/2+(.15 if kind.startswith('cabin') else 0))
    r.setdefault('door_width',.9 if kind.startswith('cabin') else 1.15)
    ROOMS.append(r);return r

# General arrangement / public and working spaces; clear passage strips between.
room('M_Entrance','First-class entrance and grand stair','main',(-5.8,1.8,-7.8,7.8),'stairhall','oak',door_wall='y0',door_u=-2,door_width=1.6)
room('M_ForwardThird','Forward third-class dormitory','main',(44,66,-4.6,4.6),'dorm_third',berths=144,door_wall='x0',door_u=0)
room('M_AfterThird','After family steerage','main',(-69.5,-57,-2.85,2.85),'dorm_third',berths=72,door_wall='x1',door_u=0)
room('M_Forecastle','Forecastle seamen and boatswain','main',(68,75,-2.1,2.1),'dorm_crew',berths=24,door_wall='x0',door_u=0)
room('S_Steering','Steam steering and emergency tiller','saloon',(-80.0,-74.4,-1.5,1.5),'steering',door_wall='x1',door_u=0)

room('S_Dining','First-class dining saloon','saloon',(9.4,27.5,-6.5,6.5),'dining','ivory',target_seats=228,door_wall='x0',door_u=-3.4,door_width=1.4)
room('S_Music','Music and drawing room','saloon',(-23.4,-10.4,-5.7,5.7),'music','ivory',door_wall='x1',door_u=-3.5)
room('S_Stair','Grand staircase upper hall','saloon',(-5.8,1.8,-3.2,3.2),'stairhall','oak',door_wall='x0',door_u=-2.3,door_width=1.3)
room('S_Purser','Purser and secure office','saloon',(-5.8,1.8,3.55,6.1),'office','oak',door_wall='y1')
room('S_Mail','Mail and specie room','saloon',(-5.8,1.8,-6.1,-3.55),'mail','service',door_wall='y0')
room('S_Galley','Galley and coal range','saloon',(-39,-26,-5.25,-.7),'galley',door_wall='y1')
room('S_Pantry','Pantry and plate room','saloon',(-32.5,-26,.7,5.25),'pantry',door_wall='y0')
room('S_Bakery','Bakery and bread room','saloon',(-39,-32.8,.7,5.25),'bakery',door_wall='y0',door_u=-33.7)
room('S_Bath_P','Port baths and lavatory','saloon',(-25.5,-23.8,.7,5.25),'bath','tile',door_width=.8,door_wall='y0')
room('S_Bath_S','Starboard lavatory','saloon',(-25.5,-23.8,-5.25,-.7),'wc','tile',door_width=.8,door_wall='y1')
room('S_SecondDining','Second-class dining saloon','saloon',(-59.2,-43,-4.15,4.15),'dining_second','oak',door_wall='x1',door_u=0)

room('P_Library','Library and writing tables','promenade',(9.4,27.5,-5.5,5.5),'library','oak',door_wall='x0',door_u=3.5,door_width=1.4)
room('P_Smoking','First-class smoking saloon','promenade',(-23.4,-10.4,-5.7,5.7),'smoking','mahogany',door_wall='x1',door_u=3.3)
room('P_Writing','Ladies reading and writing lounge','promenade',(-39,-25,-5.25,5.25),'writing','ivory',door_wall='x1',door_u=-3.2)
room('P_SecondLounge','Second-class lounge and book room','promenade',(-60,-47,-3.95,3.95),'lounge_second','oak',door_wall='x1',door_u=0)
room('P_Barber','Barber and hairdressing room','promenade',(-45.7,-40,.7,3.8),'barber','oak',door_wall='y0')
room('P_Wash','Second-class washroom','promenade',(-45.7,-40,-3.8,-.7),'wc','tile',door_wall='y1')
room('P_Stair','Stair landing under skylight','promenade',(-5.8,1.8,-3.2,3.2),'stairhall','oak',door_wall='x0',door_u=2.3)
room('P_Bar','Steward bar and drinks store','promenade',(-5.8,1.8,3.55,5.6),'bar','mahogany',door_wall='y1')
room('P_Coats','Cloak and deck-chair store','promenade',(-5.8,1.8,-5.6,-3.55),'store',door_wall='y0')
room('P_Hospital','Hospital and surgeon','promenade',(49.8,56,-3.6,3.6),'hospital','ivory',door_wall='x0',door_u=0,berths=2)

room('B_Captain','Captain private cabin','boat',(33,40.4,.8,4.4),'cabin_captain','mahogany',berths=1,door_wall='y0')
room('B_Chief','Chief officer cabin','boat',(33,36.5,-4.4,-.8),'cabin_officer','oak',berths=1,door_wall='y1')
room('B_Navigator','Navigating officer cabin','boat',(36.7,40.4,-4.4,-.8),'cabin_officer','oak',berths=1,door_wall='y1')
room('B_Chart','Chart and signal room — no wireless','boat',(20,26.6,-4.4,4.4),'chart','oak',door_wall='x0',door_u=0)
for i,(a,b,c,d) in enumerate([(11,14.9,.8,4.4),(15.1,19,.8,4.4),(11,14.9,-4.4,-.8),(15.1,19,-4.4,-.8)]):
    room(f'B_Officer_{i+1}',f'Engineer / deck officer cabin {i+1}','boat',(a,b,c,d),'cabin_officer','oak',berths=2)
room('N_Wheelhouse','Wheelhouse and navigating instruments','bridge',(33,41,-4.7,4.7),'wheelhouse','teak',door_wall='x0',door_u=3,door_width=1.1)

# Machinery has its own deckheight and enclosing hull. These are real spaces,
# not furniture presets; the machinery builder populates them componentwise.
for id,name,bounds in [('E_Engine','Triple-expansion engine room',(-28,-9.7,-5.1,5.1)),('E_Boilers_A','After stokehold',(-2.8,9,-6.9,6.9)),('E_Boilers_M','Middle stokehold',(9.4,21.8,-6.9,6.9)),('E_Boilers_F','Forward stokehold',(22.2,35.5,-6.9,6.9)),('E_Dynamos','Dynamos and electrical workshop',(-9.4,-3.4,-5.5,-2.65)),('E_Pumps','Feed and circulating pump flat',(-9.4,-3.4,2.65,5.5)),('E_Alley','Watertight shaft alley',(-70,-28.2,-1.5,1.5))]:
    r=room(id,name,'orlop',bounds,'machinery');r.update(z=1.6,top=8.6 if id!='E_Alley' else 4.7)

# Lower accommodation clear of machinery. Explicit central/side passageways.
room('L_ThirdWomen','Forward women and children steerage','lower',(37.5,49,-5.3,5.3),'dorm_third',berths=90,door_wall='x1',door_u=0)
room('L_ThirdMen','Forward men steerage','lower',(49.4,63,-4.0,4.0),'dorm_third',berths=90,door_wall='x0',door_u=0)
room('L_ThirdWash','Third-class washroom and pantry','lower',(63.4,70,-2.4,2.4),'third_wash',door_wall='x0',door_u=0)
room('L_CrewP','Stokers and trimmers port quarters','lower',(-27.7,-10,5.6,7.8),'dorm_crew',berths=40,door_wall='y1')
room('L_CrewS','Stewards starboard quarters','lower',(-27.7,-10,-7.8,-5.6),'dorm_crew',berths=40,door_wall='y0')
room('L_AfterStore','After linen and provision store','lower',(-70,-60,-2.1,2.1),'store',door_wall='x1',door_u=0)

room('O_ThirdF','Lower forward steerage','orlop',(38,62,-4.1,4.1),'dorm_third',berths=144,door_wall='x1',door_u=0)
room('O_ThirdAP','After baggage and sail store port','orlop',(-66,-55,1.6,3.0),'store',berths=0,door_wall='y1')
room('O_ThirdAS','After baggage and sail store starboard','orlop',(-66,-55,-3.0,-1.6),'store',berths=0,door_wall='y0')
room('O_CrewP','Lower crew mess and berths port','orlop',(-52.0,-31,1.6,5.1),'dorm_crew',berths=40,door_wall='y1')
room('O_CrewS','Lower crew mess and berths starboard','orlop',(-52.0,-31,-5.1,-1.6),'dorm_crew',berths=41,door_wall='y0')
room('O_Hold','Forward parcels hold and chain store','orlop',(63,70,-2.2,2.2),'cargo',door_wall='x0',door_u=0)
room('L_ThirdMess','Third-class mess and baggage','lower',(70.3,74.5,-1.6,1.6),'mess',door_wall='x0',door_u=0)
room('S_ColdStore','Ice room and refrigerated provision store','main',(40.5,43.5,-3.0,3.0),'cold_store',door_wall='x0',door_u=0)

# Cabins are individual compartments, never a single zone called "staterooms".
# All have explicit doorway centres onto the two 1.45 m longitudinal passages.
CABIN_ROWS=[(-7.45,-4.55,'y1'),(-3.10,-.20,'y0'),(.20,3.10,'y1'),(4.55,7.45,'y0')]
def make_cabins(deck,x0,x1,target,kind,style,prefix,berths):
    made=0
    for x in np.arange(x0,x1-2.55,.01 if False else 2.72):
        for j,(y0,y1,dw) in enumerate(CABIN_ROWS):
            if made>=target:return made
            box=(float(x),float(x+2.56),y0,y1)
            z=DECKS[deck]
            if min_hb(box[0],box[1],min(z+1,11.7))<max(abs(y0),abs(y1))+.20:continue
            if deck in ('saloon','promenade') and max(abs(y0),abs(y1))>6.7:continue
            if any(overlap(box,rect(r),.001) for r in ROOMS if r['deck']==deck):continue
            if any(overlap(box,c['rect'],.001) for c in CASINGS if c['z0'] < z+.2 < c['z1']):continue
            # Main forward escape stair, aft circulation cross passage.
            if deck=='main' and (overlap(box,(35.0,40.2,-4.5,4.5)) or overlap(box,(35.1,41.6,5.25,6.95))):continue
            if deck=='main' and overlap(box,(-54.9,-51.8,-4.5,4.5)):continue
            made+=1
            room(f'{prefix}{made:03}',f'{"First" if kind=="cabin_first" else "Second"} class cabin {prefix}{made:03}',deck,box,kind,style,berths=berths,door_wall=dw,door_u=float(x+(1.28 if kind=='cabin_second' else 1.43)),door_width=.84,variant=made%5)
    return made
n=make_cabins('main',-54.5,40.0,114,'cabin_first','oak','A',2)
if n<114:
    n+=make_cabins('saloon',37,55.5,114-n,'cabin_first','ivory','U',2)
if n<114:
    n+=make_cabins('promenade',37,49.4,114-n,'cabin_first','ivory','P',2)
# Extra first-class deck cabins have direct access to the open boat deck.
for x in np.arange(-54.2,-25.4,2.9):
    for a,b in [(.8,3.5),(-3.5,-.8)]:
        if n>=114:break
        n+=1
        room(f'B_First{n:03}',f'First-class deck cabin {n}','boat',(float(x),float(x+2.72),a,b),'cabin_first','oak',berths=2,door_wall='y0' if a>0 else 'y1',variant=n%5)
FIRST_CABINS=n
n2=make_cabins('lower',-58.0,-30.2,33,'cabin_second','service','C',4)
if n2<33:
    n2+=make_cabins('saloon',-70.3,-58.9,33-n2,'cabin_second','oak','D',4)
SECOND_CABINS=n2

# True walking routes and cutouts. Flights alternate transversely in the same
# well, rather than stacking impassable straight flights over a landing.
STAIRS=[]
def stair(id,fr,to,x0,x1,y,width,style='service'):
    STAIRS.append(dict(id=id,fr=fr,to=to,z0=DECKS.get(fr,fr) if isinstance(fr,str) else fr,z1=DECKS.get(to,to) if isinstance(to,str) else to,x0=x0,x1=x1,y=y,width=width,style=style))
stair('Grand_Main','main','saloon',-4.6,.4,-1.8,2.2,'oak')
stair('Grand_Upper','saloon','promenade',.4,-4.6,1.8,2.2,'oak')
stair('Prom_To_Boat','promenade','boat',-4.6,.4,-1.8,2.2,'oak')
stair('Forward_Lower','lower','main',37.2,43.2,6.1,1.3)
stair('Forward_Orlop','orlop','lower',37.0,42.8,6.15,1.0)
stair('After_Lower','lower','main',-52.5,-45.8,4.8,1.1)
stair('After_Orlop','orlop','lower',-56.5,-53.0,4.6,.9)
stair('After_Orlop_Starboard','orlop','lower',-56.5,-53.0,-4.6,.9)
stair('After_Upper','main','saloon',-54.5,-49.1,4.8,1.1)
stair('After_Promenade','saloon','promenade',-54.5,-49.1,4.8,1.1)
stair('Engine_Access',1.6,5.2,-8.8,-2.6,0.0,1.4)
stair('Engine_Main','lower','main',-8.8,-2.6,0.0,1.4)
stair('Bridge_Access','boat','bridge',33.0,38.5,6.1,1.3)

# Native-source attachment points at the load waterline datum. These points
# convert (x,y,z) -> (-y,z-DRAFT,-x) exactly once for the Roblox export.
ATTACHMENTS=[
 dict(id='Boarding_Port',position=(-2.0,8.95,8.8),kind='boarding'),
 dict(id='Boarding_Starboard',position=(-2.0,-8.95,8.8),kind='boarding'),
 dict(id='Helm',position=(38.5,0,20.95),kind='helm'),
 dict(id='Telegraph_Ahead',position=(38.2,-2.1,21.1),kind='telegraph_ahead'),
 dict(id='Telegraph_Astern',position=(38.2,-2.8,21.1),kind='telegraph_astern'),
 dict(id='Regulator',position=(-10.5,-3.2,2.7),kind='regulator'),
 dict(id='Stoke',position=(.7,0,2.4),kind='stoke'),
 dict(id='Generator',position=(-6.0,-4.1,2.8),kind='generator'),
 dict(id='Whistle',position=(38.8,3.7,21.2),kind='whistle'),
 dict(id='CastOff',position=(-1.5,8.5,9.8),kind='mooring'),
 dict(id='Funnel_Aft',position=(3.33,0,30.5),kind='smoke'),
 dict(id='Funnel_Forward',position=(28.83,0,30.5),kind='smoke'),
 dict(id='Wake',position=(-81,0,6.5),kind='wake'),
]
for x in (-68,-34,34,68):
 for side in (-1,1):ATTACHMENTS.append(dict(id=f'Moor_{x}_{side}',position=(x,side*max(1,beam_deck(x)-.35),deck_z(x)+.45),kind='cleat'))

BOAT_MOUNTS=[
 dict(id='Steam_Cutter_Stbd',craft='steam_cutter_1888',position=(37.2,-6.0,17.80),required_swl_kg=3900,fore_sling=2.05,aft_sling=-1.55,cradles=[(1.60,-.506),(-1.60,-.509)]),
 dict(id='Rowing_Cutter_Port',craft='rowing_cutter_25ft',position=(-34,6.0,17.66),required_swl_kg=2100,fore_sling=1.95,aft_sling=-1.60,cradles=[(1.55,-.375),(-1.55,-.376)]),
 dict(id='Whaler_Port',craft='whaler_27ft',position=(-20,6.0,17.73),required_swl_kg=1700,fore_sling=1.85,aft_sling=-1.85,cradles=[(1.60,-.430),(-1.60,-.430)]),
]

def roblox_point(p):x,y,z=p;return (-y,z-DRAFT,-x)
def counts():
    out={'first_class_cabins':FIRST_CABINS,'second_class_cabins':SECOND_CABINS,'physical_compartments':len(ROOMS)}
    for key,kinds in [('first_class_berths',{'cabin_first'}),('second_class_berths',{'cabin_second'}),('third_class_berths',{'dorm_third'}),('crew_berths',{'dorm_crew','cabin_captain','cabin_officer'})]:out[key]=sum(r.get('berths',0) for r in ROOMS if r['kind'] in kinds)
    return out

def hydrostatics():
    xs=np.linspace(-82.99,82.99,1101);zs=np.linspace(.08,DRAFT,161)
    areas=np.array([np.trapz([2*hb(float(x),float(z)) for z in zs],zs) for x in xs])
    volume=float(np.trapz(areas,xs));lcb=float(np.trapz(areas*xs,xs)/volume)
    return {'volume_m3':round(volume,2),'saltwater_displacement_t':round(volume*1.025,2),'lcb_m_forward':round(lcb,3),'cb_lbp':round(volume/(158*18.4*6.5),4),'note':'Numerical sections of new design; no stability, strength or resistance certification.'}

def publish():
    p=ROOT/'interfaces'/'leonidas_ii_ship.json'
    data=dict(schema='victoria.leonidas-ii/2.0',vessel='SS Aurelian',fictional=True,period=1889,dimensions_m={'loa':LOA,'lbp':158.0,'beam':BEAM,'draft':DRAFT},authoring={'units':'metres','forward':'+X','port':'+Y','up':'+Z','origin':'midships / baseline'},export={'units':'metres','forward':'-Z','up':'+Y','origin':'midships / load waterline','formula':'(-y,z-6.5,-x)','studs_per_m':1/M_PER_STUD,'scale_in_studio_once':True},decks=DECKS,deck_tops=DECK_TOPS,rooms=ROOMS,stairs=STAIRS,casings=CASINGS,attachments=ATTACHMENTS,boat_mounts=BOAT_MOUNTS,scheduled_counts_not_built_capacity=counts(),count_basis='The room schedule contains targets. Actual modeled berths/seats are in exports/leonidas_ii/build_data.json and are copied into this contract only after the build.',hydrostatics=hydrostatics(),engineering_status='Fictional reconstruction with unverified gameplay integration; no Studio, performance or naval certification.')
    p.write_text(json.dumps(data,indent=2));return data

if __name__=='__main__':
    print(json.dumps(counts(),indent=2))
    print(json.dumps(publish()['hydrostatics'],indent=2))
