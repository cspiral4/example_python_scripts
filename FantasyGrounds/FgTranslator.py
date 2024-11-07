#!python
import xml.etree.ElementTree as ET
import argparse

fg_parser = argparse.ArgumentParser(description='parse FG xml file to text')
fg_parser.add_argument('xml_filename', help='xml file to translate')
fg_args = fg_parser.parse_args()

# find character abilities
# find character age, alignment, appearance, background, bg_bonds
tree = ET.parse(fg_args.xml_filename)
root = tree.getroot()
character = root.find('character')

# top level details
deity = character.findtext('deity')
exp = character.findtext('exp')
exp_needed = character.findtext('expneeded')
flaws = character.findtext('flaws')
gender = character.findtext('gender')
height = character.findtext('height')
ideals = character.findtext('ideals')
level = character.findtext('level')
chr_name = character.findtext('name')
chr_notes = character.findtext('notes')
percep = character.findtext('perception')
percep_mod = character.findtext('perceptionmodifier')
personality = character.findtext('personalitytraits')
prof_bonus = character.findtext('prof_bonus')
race = character.findtext('race')
size = character.findtext('size')
weight = character.findtext('weight')
age = character.findtext('age')
alignment = character.findtext('alignment')
appearance = character.findtext('appearance')
background = character.findtext('background')
bonds = character.findtext('bonds')

print('NAME:       %s'%chr_name)
print('LEVEL:      %s'%level)
print('EXP:        %s'%exp)
print('EXP NEEDED: %s'%exp_needed)
print('AGE:        %s'%age)
print('DEITY:      %s'%deity)
print('ALIGNMENT:  %s'%alignment)
print('RACE:       %s'%race)
print('PROF BONUS: %s'%prof_bonus)
print('PERCEPTION: %s'%percep)
print('PERCEP MOD: %s'%percep_mod)
print('GENDER:     %s'%gender)
print('SIZE:       %s'%size)
print('HEIGHT:     %s'%height)
print('WEIGHT:     %s'%weight)
print('BACKGROUND: %s'%background)
print('APPEARANCE: %s'%appearance)
print('TRAITS:     %s'%personality)
print('IDEALS:     %s'%ideals)
print('FLAWS:      %s'%flaws)
print('BONDS:      %s'%bonds)

# Abilities
abilities = character.find('abilities')
ability_names = ['charisma', 'constitution', 'dexterity',
                 'intelligence', 'strength', 'wisdom']
for ability in ability_names:
    tmp_ability = abilities.find(ability)
    bonus = tmp_ability.findtext('bonus')
    save = tmp_ability.findtext('save')
    svmod = tmp_ability.findtext('savemodifier')
    svprof = tmp_ability.findtext('saveprof')
    score = tmp_ability.findtext('score')

    print('\n%s'%ability)
    print('\tscore:            %s'%score)
    print('\tbonus:            %s'%bonus)
    print('\tsave proficiency: %s'%svprof)
    print('\tsave:             %s'%save)
    print('\tsave modifier:    %s'%svmod)

# find classes and get class stats
classes = character.find('classes')
for class_id in classes:
    name = class_id.findtext('name')
    level = class_id.findtext('level')
    hit_die = class_id.findtext('hddie')
    print('\nCLASS: %s\nLEVEL: %s\nHIT DIE: %s'%(name, level, hit_die))

# for hp, get total and wounds
hitpoints = character.find('hp')
hp = hitpoints.findtext('total')
print('\nHIT POINTS: %s'%hp)

# get initiative/total value
initiative = character.find('initiative')
init_bonus = initiative.findtext('total')
print('INITIATIVE BONUS: %s'%init_bonus)

# find defenses/ac
defenses = character.find('defenses')
for ac in defenses:
    armor = ac.findtext('armor')
    misc = ac.findtext('misc')
    proficiency = ac.findtext('prof')
    shield = ac.findtext('shield')
    stat2 = ac.findtext('stat2')
    temp_ac = ac.findtext('temporary')
    total_ac = ac.findtext('total')

    print('ARMOR CLASS: %s'%total_ac)
    print('\tARMOR: %s'%armor)
    print('\tMISC BONUS: %s'%misc)
    print('\tPROFICIENCY: %s'%proficiency)
    print('\tSHIELD: %s'%shield)
    print('\tSTAT2: %s'%stat2)
    print('\tTEMP BONUS: %s'%temp_ac)

# get featlist id elements
feats = character.find('featlist')
for feat_id in feats:
    name = feat_id.findtext('name')
    print('\nFEAT: %s'%name)

# get featurelist
features = character.find('featurelist')
for feature in features:
    name = feature.findtext('name')
    source = feature.findtext('feature')
    print('FEATURE: %s, SOURCE: %s'%(name, source))

# get speed stats
speed = character.find('speed')
spd_armor = speed.findtext('armor')
spd_base = speed.findtext('base')
spd_misc = speed.findtext('misc')
spd_temp = speed.findtext('temporary')
spd_total = speed.findtext('total')

print('\nSPEED: BASE: %s'%spd_base)
print('\tARMOR: %s'%spd_armor)
print('\tMISC: %s'%spd_misc)
print('\tTEMPORARY: %s'%spd_temp)
print('\tTOTAL: %s'%spd_total)

# languages
languages = character.find('languagelist')
print('\nLANGUAGES')
for language in languages:
    print('\t%s'%language.findtext('name'))

# skilllist
skills = character.find('skilllist')
print('\nSKILLS')
for skill in skills:
    name = skill.findtext('name')
    prof = skill.findtext('prof')
    stat = skill.findtext('stat')
    total = skill.findtext('total')

    print('\tNAME: %s'%name)
    print('\tPROFICIENCY: %s'%prof)
    print('\tSTAT: %s'%stat)
    print('\tTOTAL: %s\n'%total)

# proficiencies
profbonus = character.findtext('profbonus')
print('\nPROFICIENCY BONUS: %s'%profbonus)
print('PROFICIENCIES:')
proflist = character.find('proficiencylist')
for proficiency in proflist:
    print('\t%s'%proficiency.findtext('name'))

# Weapons
weapons = character.find('weaponlist')
print('\nWEAPONS')
for weapon in weapons:
    print('NAME: %s'%weapon.findtext('name'))
    print('PROF: %s'%weapon.findtext('prof'))
    print('AMMO: %s'%weapon.findtext('ammo'))
    print('MAX AMMO: %s'%weapon.findtext('maxammo'))
    print('ATTACK BONUS: %s'%weapon.findtext('attackbonus'))
    dmglist = weapon.find('damagelist')
    for dmg in dmglist:
        print('DAMMAGE BONUS: %s'%dmg.findtext('bonus'))
        print('DAMMAGE DICE: %s'%dmg.findtext('dice'))
        print('DAMMAGE TYPE: %s'%dmg.findtext('type'))
    print('PROPERTIES: %s\n'%weapon.findtext('properties'))

# get coins information
coins = character.find('coins')
print('\nMONEY')
for slot in coins:
    name = slot.findtext('name')
    amt = slot.findtext('amount')
    if amt == '0':
        continue
    print('%s: %s'%(name, amt))
    
# inventorylist
print('\nINVENTORY')
inv_list = character.find('inventorylist')
for inv_id in inv_list:
    name = inv_id.findtext('name')
    count = inv_id.findtext('count')
    type_inv = inv_id.findtext('type')
    weight = inv_id.findtext('weight')
    isidentified = inv_id.findtext('isidentified')
    location = inv_id.findtext('location')
    cost = inv_id.findtext('cost')

    print('ITEM: %s, COUNT: %s'%(name, count))
    print('\tIS IDENTIFIED: %s'%isidentified)
    print('\tLOCATION: %s'%location)
    print('\tTYPE: %s'%type_inv)
    print('\tWEIGHT: %s'%weight)
    print('\tCOST: %s\n'%cost)

# get encumbrance data
encumbrance = character.find('encumbrance')
encumbered = encumbrance.findtext('encumbered')
encumbheavy = encumbrance.findtext('encumberedheavy')
liftpushdrag = encumbrance.findtext('liftpushdrag')
load = encumbrance.findtext('load')
max_load = encumbrance.findtext('max')

print('\nENCUMBERED:      %s'%encumbered)
print('ENCUMBEREDHEAVY: %s'%encumbheavy)
print('LIFT/PUSH/DRAG:  %s'%liftpushdrag)
print('LOAD:            %s'%load)
print('MAX:             %s\n'%max_load)

# powergroup
powergroup = character.find('powergroup')
print('\nPOWERGROUP')
for power_id in powergroup:
    name = power_id.findtext('name')
    atkprof = power_id.findtext('atkprof')
    ctype = power_id.findtext('castertype')
    prepped = power_id.findtext('prepared')
    saveprof = power_id.findtext('saveprof')
    stat = power_id.findtext('stat')

    print('\nNAME: %s'%name)
    print('\tATTACK PROFICIENCY: %s'%atkprof)
    print('\tCASTER TYPE: %s'%ctype)
    print('\tPREPARED: %s'%prepped)
    print('\tSAVE PROFICIENCY: %s'%saveprof)
    print('\tSTAT: %s'%stat)

# powers
powermeta = character.find('powermeta')
print('\nSPELL SLOTS')
for slot in powermeta:
    max_spells = slot.findtext('max')
    if max_spells == '0':
        continue
    # slot id or 'spellslot1' through 'spellslot9'
    # indicate spell level in the id string.
    # so, spellslot1 is the number of first level spells that can be cast.
    print('SLOT: %s'%slot.tag)
    print('MAX SLOTS: %s\n'%max_spells)

