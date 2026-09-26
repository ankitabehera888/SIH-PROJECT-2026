import type { Audience, BodyType, Gender } from './symptomCheckerTriage';
import { audienceForAge, modelGender } from './symptomCheckerTriage';

/* Symptom catalogue. The labels and groupings mirror the topic lists the
   hospital symptom checker serves from its GetTopics service
   (bodyregion=<area>&age=adult|peds). Wording of the home-care and
   "when to worry" lines is community-health simplified. */

export interface SymptomCondition {
  name: string;
  icd10: string;
  weight: number;
  specialist: string;
}

export interface Symptom {
  id: string;
  label: string;
  region: string;
  audience: Audience;
  gender?: Gender;
  keywords: string[];
  common?: boolean;
  flags: string[];
  firstAid: string[];
  baseTier: 'self' | 'office' | 'h24';
  homeCare: string[];
  conditions: SymptomCondition[];
}

const P = 'General Physician';
const PAED = 'Paediatrics';
const ENT = 'ENT';
const DERM = 'Dermatology';
const ORTHO = 'Orthopaedics';
const GI = 'Gastroenterology';
const NEURO = 'Neurology';
const OPHTH = 'Ophthalmology';
const OBS = 'Obstetrics & Gynaecology';
const CARDIO = 'Cardiology';
const PULMO = 'Pulmonology';
const URO = 'Urology';
const PSY = 'Psychiatry';

export const SYMPTOMS: Symptom[] = [
  /* ------------------------------ HEAD ------------------------------ */
  { id: 'headache', label: 'Headache', region: 'head', audience: 'both', common: true,
    keywords: ['head pain', 'migraine', 'throbbing head'],
    flags: ['rf.stroke', 'rf.fever-stiff-neck', 'rf.head-injury-vomit', 'rf.pain-severe'], firstAid: ['fa.fever'], baseTier: 'self',
    homeCare: ['Rest in a dark, quiet room and try to sleep.', 'Drink water — dehydration is a common trigger.', 'Cold cloth on the forehead; warm pack on the neck for tension headache.', 'Paracetamol if needed and not allergic — never give aspirin to children.'],
    conditions: [
      { name: 'Tension-type headache', icd10: 'G44.2', weight: 3, specialist: P },
      { name: 'Migraine', icd10: 'G43.9', weight: 3, specialist: NEURO },
      { name: 'Sinusitis', icd10: 'J01.9', weight: 1, specialist: ENT },
    ] },
  { id: 'sore-throat', label: 'Sore throat', region: 'head', audience: 'both', common: true,
    keywords: ['throat pain', 'swallowing pain', 'tonsils'],
    flags: ['rf.sore-throat-severe', 'rf.fever-3-days'], firstAid: ['fa.fever', 'fa.cough-care'], baseTier: 'self',
    homeCare: ['Warm salt-water gargles 3–4 times a day (½ teaspoon salt in a glass of warm water).', 'Drink warm fluids and eat soft food.', 'Steam inhalation eases the throat and nose.', 'Paracetamol for pain if not allergic.'],
    conditions: [
      { name: 'Viral pharyngitis', icd10: 'J02.9', weight: 3, specialist: P },
      { name: 'Streptococcal pharyngitis', icd10: 'J03.90', weight: 2, specialist: P },
      { name: 'Tonsillitis', icd10: 'J03.90', weight: 2, specialist: ENT },
    ] },
  { id: 'earache', label: 'Ear pain', region: 'head', audience: 'both', common: true,
    keywords: ['ear pain', 'earache', 'ear infection'],
    flags: ['rf.ear-pain-severe', 'rf.fever-3-days'], firstAid: ['fa.fever'], baseTier: 'office',
    homeCare: ['Warm compress against the ear for 15 minutes.', 'Keep the ear dry — no oil, water or cotton buds inside.', 'Paracetamol for pain, by weight in children.', 'Sleep with the sore ear facing up.'],
    conditions: [
      { name: 'Acute otitis media', icd10: 'H66.90', weight: 3, specialist: ENT },
      { name: 'Otitis externa (swimmer’s ear)', icd10: 'H60.90', weight: 2, specialist: ENT },
      { name: 'Eustachian tube congestion', icd10: 'H68.90', weight: 1, specialist: ENT },
    ] },
  { id: 'ear-discharge', label: 'Ear discharge or blocked ear', region: 'head', audience: 'both',
    keywords: ['ear discharge', 'pus from ear', 'blocked ear', 'wax'],
    flags: ['rf.ear-pain-severe', 'rf.confusion-new'], firstAid: [], baseTier: 'office',
    homeCare: ['Do not put water, oil or drops in the ear unless prescribed.', 'Wipe the outer ear only, with a clean cloth.', 'Keep the ear covered while bathing.', 'Do not use cotton buds — they push wax deeper.'],
    conditions: [
      { name: 'Otitis externa', icd10: 'H60.90', weight: 3, specialist: ENT },
      { name: 'Chronic suppurative otitis media', icd10: 'H66.3', weight: 2, specialist: ENT },
      { name: 'Impacted cerumen', icd10: 'H61.20', weight: 2, specialist: ENT },
    ] },
  { id: 'red-eye', label: 'Red or itchy eye', region: 'head', audience: 'both',
    keywords: ['red eye', 'eye infection', 'itchy eye', 'conjunctivitis'],
    flags: ['rf.eye-pain-light', 'rf.eye-chemical'], firstAid: ['fa.eye-chemical'], baseTier: 'office',
    homeCare: ['Clean the eye from the inner corner outward using boiled, cooled water and clean cotton.', 'Do not share towels or pillow covers.', 'Wash hands often — it spreads easily.', 'Cool compresses ease itching; stop any eye drop that stings.'],
    conditions: [
      { name: 'Viral conjunctivitis', icd10: 'H10.9', weight: 3, specialist: OPHTH },
      { name: 'Allergic conjunctivitis', icd10: 'H10.45', weight: 2, specialist: OPHTH },
      { name: 'Bacterial conjunctivitis', icd10: 'H10.9', weight: 2, specialist: OPHTH },
    ] },
  { id: 'eye-blurred', label: 'Blurred vision or eye pain', region: 'head', audience: 'both',
    keywords: ['blurred vision', 'vision loss', 'eye pain', 'floaters'],
    flags: ['rf.eye-pain-light', 'rf.eye-chemical', 'rf.stroke'], firstAid: ['fa.eye-chemical'], baseTier: 'h24',
    homeCare: ['Rest the eyes and avoid screens while symptoms last.', 'Do not rub the eye or use leftover eye drops.', 'Note when it started and whether one or both eyes are affected — tell the doctor.', 'Sudden vision loss or flashes of light need same-day care.'],
    conditions: [
      { name: 'Refractive error', icd10: 'H52.4', weight: 2, specialist: OPHTH },
      { name: 'Acute glaucoma', icd10: 'H40.9', weight: 2, specialist: OPHTH },
      { name: 'Diabetic retinopathy', icd10: 'E11.9', weight: 1, specialist: OPHTH },
    ] },
  { id: 'nosebleed', label: 'Nosebleed', region: 'head', audience: 'both',
    keywords: ['nose bleed', 'epistaxis'],
    flags: ['rf.bleeding-severe', 'rf.major-trauma'], firstAid: ['fa.nosebleed'], baseTier: 'self',
    homeCare: ['Sit upright, lean forward, and pinch the soft part of the nose for 10 minutes without releasing.', 'Do not blow or pick the nose for 24 hours.', 'Keep the head above heart level; avoid hot drinks and hot baths.', 'Use saline drops if the inside of the nose feels dry.'],
    conditions: [
      { name: 'Dry nasal mucosa', icd10: 'R04.0', weight: 3, specialist: ENT },
      { name: 'Hypertension-related epistaxis', icd10: 'R04.0', weight: 2, specialist: P },
      { name: 'Nasal trauma or polyp', icd10: 'J33.9', weight: 1, specialist: ENT },
    ] },
  { id: 'toothache', label: 'Toothache or mouth ulcer', region: 'head', audience: 'both',
    keywords: ['tooth pain', 'dental', 'mouth ulcer'],
    flags: ['rf.fever-3-days', 'rf.pain-severe'], firstAid: [], baseTier: 'office',
    homeCare: ['Rinse with warm salt water 3–4 times a day.', 'Paracetamol for pain; avoid very hot, cold or sweet food.', 'Brush twice daily and avoid tobacco, gutka or supari.', 'See a dentist — painkillers alone do not cure an infected tooth.'],
    conditions: [
      { name: 'Dental caries', icd10: 'K02.9', weight: 3, specialist: 'Dentistry' },
      { name: 'Dental abscess', icd10: 'K04.7', weight: 2, specialist: 'Dentistry' },
    ] },
  { id: 'sinus-pain', label: 'Sinus pain or blocked nose', region: 'head', audience: 'both', common: true,
    keywords: ['sinus', 'blocked nose', 'runny nose'],
    flags: ['rf.fever-3-days', 'rf.breathing-mild'], firstAid: ['fa.cough-care'], baseTier: 'self',
    homeCare: ['Steam inhalation twice a day.', 'Saline (salt water) nose drops 3–4 times a day.', 'Drink warm fluids and sleep with the head slightly raised.', 'Avoid dust, smoke and cold drinks while symptoms last.'],
    conditions: [
      { name: 'Acute sinusitis', icd10: 'J01.90', weight: 3, specialist: ENT },
      { name: 'Allergic rhinitis', icd10: 'J30.9', weight: 3, specialist: ENT },
    ] },
  { id: 'dizziness', label: 'Dizziness or fainting', region: 'head', audience: 'both',
    keywords: ['dizzy', 'giddiness', 'fainting', 'vertigo'],
    flags: ['rf.stroke', 'rf.confusion-new', 'rf.sugar-abnormal'], firstAid: ['fa.recovery-position', 'fa.hypoglycemia'], baseTier: 'office',
    homeCare: ['Sit or lie down at once when it starts; do not walk alone.', 'Stand up slowly, in stages, from lying to sitting to standing.', 'Drink water and eat something if you have skipped meals.', 'Avoid driving or climbing while symptoms last.'],
    conditions: [
      { name: 'Orthostatic hypotension', icd10: 'I95.1', weight: 2, specialist: P },
      { name: 'Anaemia', icd10: 'D64.9', weight: 2, specialist: P },
    ] },
  { id: 'crying-baby', label: 'Baby crying a lot or not settling', region: 'head', audience: 'peds',
    keywords: ['crying baby', 'colic', 'unsettled', 'inconsolable'],
    flags: ['rf.newborn-ill', 'rf.breathing-severe'], firstAid: ['fa.newborn'], baseTier: 'h24',
    homeCare: ['Check the basics first: hunger, wet nappy, too hot or cold, or a tight cloth.', 'Hold the baby skin-to-skin and try gentle rocking or a walk.', 'Burp after feeds — trapped wind is a common cause.', 'Never shake a baby. If the cry is high-pitched, weak or the baby is floppy, get care today.'],
    conditions: [
      { name: 'Infant colic', icd10: 'R10.4', weight: 3, specialist: PAED },
      { name: 'Feeding difficulty', icd10: 'P92.9', weight: 2, specialist: PAED },
    ] },
  { id: 'teething', label: 'Teething or drooling', region: 'head', audience: 'peds',
    keywords: ['teething', 'drooling', 'gum pain'],
    flags: ['rf.fever-newborn', 'rf.dehydration-mild'], firstAid: ['fa.fever'], baseTier: 'self',
    homeCare: ['Give a clean, cold spoon or teething ring to chew on — never a frozen one.', 'Wipe the drool to prevent a rash around the mouth.', 'Paracetamol by weight if the baby is very irritable.', 'Fever over 38°C in a baby under 3 months is never “just teething” — get care.'],
    conditions: [
      { name: 'Teething syndrome', icd10: 'K00.7', weight: 3, specialist: PAED },
      { name: 'Viral upper respiratory infection', icd10: 'J06.9', weight: 1, specialist: PAED },
    ] },
  { id: 'ear-pulling', label: 'Child pulling at the ear', region: 'head', audience: 'peds',
    keywords: ['ear pulling', 'ear infection child', 'ear discharge baby'],
    flags: ['rf.ear-pain-severe', 'rf.fever-newborn'], firstAid: ['fa.fever'], baseTier: 'office',
    homeCare: ['Keep the ear dry and clean on the outside only.', 'Give paracetamol by weight for pain.', 'Feed and hydrate in small, frequent amounts.', 'See a doctor if there is discharge, fever, or the baby is not feeding.'],
    conditions: [
      { name: 'Acute otitis media', icd10: 'H66.90', weight: 3, specialist: PAED },
      { name: 'Otitis media with effusion', icd10: 'H65.90', weight: 2, specialist: ENT },
    ] },
  /* ------------------------------ CHEST ----------------------------- */
  { id: 'cough', label: 'Cough', region: 'chest', audience: 'both', common: true,
    keywords: ['cough', 'phlegm', 'dry cough'],
    flags: ['rf.breathing-severe', 'rf.cough-2-weeks', 'rf.cough-fever-child'], firstAid: ['fa.cough-care', 'fa.breathing'], baseTier: 'self',
    homeCare: ['Warm fluids through the day; honey with warm water for children over 1 year.', 'Steam inhalation twice a day.', 'Avoid smoke, dust and cold drinks.', 'Antibiotics are not needed for ordinary coughs — see a doctor if it lasts over 2 weeks.'],
    conditions: [
      { name: 'Acute bronchitis', icd10: 'J20.9', weight: 3, specialist: P },
      { name: 'Common cold', icd10: 'J00', weight: 2, specialist: P },
      { name: 'Pneumonia', icd10: 'J18.9', weight: 2, specialist: PULMO },
    ] },
  { id: 'common-cold', label: 'Cold, sneezing or runny nose', region: 'chest', audience: 'both', common: true,
    keywords: ['cold', 'sneezing', 'runny nose', 'blocked nose'],
    flags: ['rf.breathing-mild', 'rf.fever-3-days'], firstAid: ['fa.cough-care'], baseTier: 'self',
    homeCare: ['Rest, warm fluids and light food.', 'Saline nose drops for a blocked nose at any age.', 'Paracetamol if there is fever or body ache.', 'Coughs and colds settle in 5–7 days without antibiotics.'],
    conditions: [
      { name: 'Common cold', icd10: 'J00', weight: 3, specialist: P },
      { name: 'Influenza', icd10: 'J11.1', weight: 2, specialist: P },
    ] },
  { id: 'breathing-trouble', label: 'Breathing difficulty', region: 'chest', audience: 'both',
    keywords: ['breathless', 'shortness of breath', 'wheezing', 'asthma'],
    flags: ['rf.breathing-severe', 'rf.asthma-attack', 'rf.breathing-mild'], firstAid: ['fa.breathing', 'fa.asthma'], baseTier: 'h24',
    homeCare: ['Sit upright and stay calm; do not lie flat.', 'Use the prescribed inhaler with a spacer — 2 puffs, repeat after 4 minutes if needed.', 'Keep the room dust-free and avoid smoke or burning waste.', 'Count breaths per minute and note any blue lips, chest pulling in, or drowsiness.'],
    conditions: [
      { name: 'Acute asthma exacerbation', icd10: 'J45.901', weight: 3, specialist: PULMO },
      { name: 'Lower respiratory tract infection', icd10: 'J22', weight: 2, specialist: PULMO },
      { name: 'Heart failure', icd10: 'I50.9', weight: 1, specialist: CARDIO },
    ] },
  { id: 'chest-pain', label: 'Chest pain', region: 'chest', audience: 'both',
    keywords: ['chest pain', 'chest tightness', 'heart pain'],
    flags: ['rf.chest-cardiac', 'rf.breathing-mild', 'rf.pain-severe'], firstAid: ['fa.heart-attack'], baseTier: 'h24',
    homeCare: ['Stop all activity and sit resting while the pain is there.', 'Do not drive yourself anywhere — arrange transport.', 'Note the exact time the pain started and what made it worse.', 'Any chest pain with sweating, vomiting or pain in the arm or jaw is an emergency.'],
    conditions: [
      { name: 'Acute coronary syndrome', icd10: 'I24.9', weight: 3, specialist: CARDIO },
      { name: 'Costochondritis / muscular pain', icd10: 'M94.0', weight: 2, specialist: P },
      { name: 'Gastro-oesophageal reflux', icd10: 'K21.9', weight: 2, specialist: GI },
    ] },
  { id: 'palpitations', label: 'Heart racing or palpitations', region: 'chest', audience: 'both',
    keywords: ['palpitations', 'racing heart', 'irregular heartbeat'],
    flags: ['rf.chest-cardiac', 'rf.breathing-mild', 'rf.pain-severe'], firstAid: ['fa.heart-attack'], baseTier: 'h24',
    homeCare: ['Sit down, breathe slowly and avoid caffeine, tobacco and alcohol.', 'Note how long the racing lasts and whether it starts suddenly.', 'Do not drive or climb while it is happening.', 'Racing with chest pain, sweating or fainting is an emergency.'],
    conditions: [
      { name: 'Atrial fibrillation / arrhythmia', icd10: 'I49.9', weight: 3, specialist: CARDIO },
      { name: 'Anxiety-related palpitations', icd10: 'F41.9', weight: 2, specialist: PSY },
      { name: 'Anaemia', icd10: 'D64.9', weight: 2, specialist: P },
    ] },
  { id: 'asthma-attack', label: 'Asthma attack', region: 'chest', audience: 'both',
    keywords: ['asthma', 'inhaler', 'wheeze attack'],
    flags: ['rf.asthma-attack', 'rf.breathing-severe'], firstAid: ['fa.asthma', 'fa.breathing'], baseTier: 'h24',
    homeCare: ['Sit upright and give 2 puffs of the reliever inhaler (salbutamol) with a spacer.', 'Repeat 1 puff every 30–60 seconds up to 10 puffs if needed.', 'Move away from the trigger — smoke, dust, cold air or strong smells.', 'If there is no relief in 15 minutes, get emergency care.'],
    conditions: [
      { name: 'Acute asthma exacerbation', icd10: 'J45.901', weight: 3, specialist: PULMO },
      { name: 'Respiratory tract infection', icd10: 'J22', weight: 2, specialist: PULMO },
    ] },
  { id: 'wheezing-child', label: 'Child wheezing or fast breathing', region: 'chest', audience: 'peds',
    keywords: ['wheeze child', 'fast breathing', 'grunting'],
    flags: ['rf.breathing-severe', 'rf.cough-fever-child', 'rf.fever-newborn'], firstAid: ['fa.breathing'], baseTier: 'h24',
    homeCare: ['Keep the child upright on your lap and calm.', 'Continue breastfeeding or fluids in small amounts.', 'Count breaths in a full minute — over 50 in a baby or 40 in a child needs care.', 'Any chest pulling in, grunting, or blue lips means go to hospital now.'],
    conditions: [
      { name: 'Bronchiolitis', icd10: 'J21.0', weight: 3, specialist: PAED },
      { name: 'Asthma (childhood)', icd10: 'J45.909', weight: 2, specialist: PAED },
      { name: 'Pneumonia', icd10: 'J18.9', weight: 2, specialist: PAED },
    ] },
  { id: 'croup', label: 'Barking cough or hoarse voice (child)', region: 'chest', audience: 'peds',
    keywords: ['croup', 'barking cough', 'hoarse child', 'stridor'],
    flags: ['rf.breathing-severe', 'rf.breathing-mild'], firstAid: ['fa.breathing'], baseTier: 'h24',
    homeCare: ['Keep the child calm — crying makes the barking worse.', 'Sit them upright and give warm fluids.', 'Steam from a hot shower or cool night air can ease the cough.', 'A whistling sound at rest, drooling or a struggle to breathe needs hospital now.'],
    conditions: [
      { name: 'Croup (laryngotracheobronchitis)', icd10: 'J05.0', weight: 3, specialist: PAED },
      { name: 'Epiglottitis', icd10: 'J05.1', weight: 1, specialist: PAED },
    ] },
  { id: 'breast-lump', label: 'Breast lump, pain or discharge', region: 'chest', audience: 'adult', gender: 'F',
    keywords: ['breast lump', 'breast pain', 'nipple discharge'],
    flags: ['rf.lump-new', 'rf.fever-3-days', 'rf.weight-loss'], firstAid: [], baseTier: 'office',
    homeCare: ['Wear a well-fitting, supportive bra, including at night if painful.', 'Warm compress before feeding if breastfeeding; cold pack after.', 'Do not squeeze or massage the lump.', 'Any hard, painless lump or blood-stained discharge needs a doctor and mammography.'],
    conditions: [
      { name: 'Fibrocystic breast change', icd10: 'N60.1', weight: 2, specialist: P },
      { name: 'Breast abscess / mastitis', icd10: 'N61', weight: 2, specialist: 'Surgery' },
      { name: 'Breast carcinoma', icd10: 'C50.9', weight: 1, specialist: 'Surgery' },
    ] },
  /* ----------------------------- ABDOMEN ---------------------------- */
  { id: 'stomach-pain', label: 'Stomach pain or cramps', region: 'abdomen', audience: 'both', common: true,
    keywords: ['stomach pain', 'belly pain', 'cramps', 'gastric'],
    flags: ['rf.abdomen-rigid', 'rf.vomit-blood', 'rf.pain-severe'], firstAid: ['fa.abdominal'], baseTier: 'office',
    homeCare: ['Sip warm water or ORS; avoid oily, spicy food and milk for a day.', 'Rest with knees bent and a warm cloth on the belly.', 'Note the exact site of pain and whether it moves — tell the doctor.', 'Do not take painkillers or antacids before being seen.'],
    conditions: [
      { name: 'Gastritis / dyspepsia', icd10: 'K29.70', weight: 3, specialist: GI },
      { name: 'Acute gastroenteritis', icd10: 'A09', weight: 3, specialist: GI },
      { name: 'Appendicitis', icd10: 'K35.80', weight: 2, specialist: 'Surgery' },
    ] },
  { id: 'vomiting', label: 'Vomiting or nausea', region: 'abdomen', audience: 'both', common: true,
    keywords: ['vomiting', 'throwing up', 'nausea', 'green vomit'],
    flags: ['rf.vomit-blood', 'rf.vomit-persistent', 'rf.dehydration-severe'], firstAid: ['fa.vomit-care', 'fa.dehydration'], baseTier: 'self',
    homeCare: ['Stop food for 1 hour, then give 1 teaspoon of ORS or water every 5 minutes.', 'Increase slowly if it stays down; breastfeed babies normally.', 'Start with rice, curd, banana or toast the next day.', 'Green or bloody vomit, or a hard belly, needs hospital now.'],
    conditions: [
      { name: 'Acute gastroenteritis', icd10: 'A09', weight: 3, specialist: GI },
      { name: 'Food poisoning', icd10: 'A05.9', weight: 2, specialist: GI },
      { name: 'Intestinal obstruction', icd10: 'K56.60', weight: 1, specialist: 'Surgery' },
    ] },
  { id: 'diarrhea', label: 'Loose motions or diarrhoea', region: 'abdomen', audience: 'both', common: true,
    keywords: ['diarrhoea', 'loose motion', 'watery stool'],
    flags: ['rf.diarrhea-blood', 'rf.diarrhea-many', 'rf.dehydration-severe'], firstAid: ['fa.diarrhea-care', 'fa.dehydration'], baseTier: 'self',
    homeCare: ['Start ORS after every loose stool — ½ cup for a child, 1 cup for an adult.', 'Give zinc for 14 days for children under 5, as advised.', 'Continue normal food; avoid sugary drinks and very oily food.', 'Blood in stool, no urine for 8 hours, or drowsiness means hospital now.'],
    conditions: [
      { name: 'Acute gastroenteritis', icd10: 'A09', weight: 3, specialist: GI },
      { name: 'Cholera', icd10: 'A00.9', weight: 1, specialist: GI },
      { name: 'Amoebic dysentery', icd10: 'A06.0', weight: 1, specialist: GI },
    ] },
  { id: 'constipation', label: 'Constipation', region: 'abdomen', audience: 'both',
    keywords: ['constipation', 'hard stool', 'not passing stool'],
    flags: ['rf.abdomen-rigid', 'rf.black-stool', 'rf.vomit-persistent'], firstAid: [], baseTier: 'self',
    homeCare: ['Drink 2–3 litres of water and eat fruit, vegetables and whole grains.', 'Walk 20–30 minutes daily and go to the toilet at the same time each day.', 'Do not strain or hold the breath; use a footstool to raise the knees.', 'No stool for 4 days with vomiting or belly swelling needs care the same day.'],
    conditions: [
      { name: 'Functional constipation', icd10: 'K59.00', weight: 3, specialist: GI },
      { name: 'Irritable bowel syndrome', icd10: 'K58.9', weight: 2, specialist: GI },
      { name: 'Intestinal obstruction', icd10: 'K56.60', weight: 1, specialist: 'Surgery' },
    ] },
  { id: 'heartburn', label: 'Heartburn or acid reflux', region: 'abdomen', audience: 'both',
    keywords: ['heartburn', 'acid reflux', 'sour burps', 'gastric'],
    flags: ['rf.chest-cardiac', 'rf.vomit-blood', 'rf.lasting-pain'], firstAid: [], baseTier: 'self',
    homeCare: ['Eat smaller, more frequent meals and avoid lying down for 2 hours after eating.', 'Cut down on tea, coffee, chillies, fried food and alcohol.', 'Raise the head of the bed by 10–15 cm.', 'Chest pain with sweating is treated as a heart problem, not acidity.'],
    conditions: [
      { name: 'Gastro-oesophageal reflux disease', icd10: 'K21.9', weight: 3, specialist: GI },
      { name: 'Peptic ulcer disease', icd10: 'K27.9', weight: 2, specialist: GI },
    ] },
  { id: 'worms', label: 'Worms in stool or itching around the bottom (child)', region: 'abdomen', audience: 'peds',
    keywords: ['worms', 'pinworms', 'threadworms', 'itching bottom'],
    flags: ['rf.dehydration-mild', 'rf.lasting-pain'], firstAid: [], baseTier: 'office',
    homeCare: ['Wash hands with soap before eating and after using the toilet.', 'Keep nails short; do not let the child scratch and then put fingers in the mouth.', 'Wash and sun-dry bedding, towels and underclothes daily.', 'Deworming is given as a single tablet repeated after 2 weeks — ask your health worker.'],
    conditions: [
      { name: 'Enterobiasis (threadworm)', icd10: 'B80', weight: 3, specialist: PAED },
      { name: 'Ascariasis', icd10: 'B77.9', weight: 2, specialist: PAED },
    ] },
  { id: 'spitting-up', label: 'Baby spitting up or reflux', region: 'abdomen', audience: 'peds',
    keywords: ['spitting up', 'possetting', 'reflux baby'],
    flags: ['rf.newborn-ill', 'rf.vomit-persistent', 'rf.dehydration-severe'], firstAid: ['fa.newborn', 'fa.dehydration'], baseTier: 'office',
    homeCare: ['Burp the baby well and keep them upright for 20–30 minutes after feeds.', 'Feed smaller amounts more often.', 'Do not overfeed or bounce the baby right after feeding.', 'Green or forceful vomiting, or poor weight gain, needs a paediatric review.'],
    conditions: [
      { name: 'Physiological reflux', icd10: 'P92.1', weight: 3, specialist: PAED },
      { name: 'Pyloric stenosis', icd10: 'Q40.0', weight: 1, specialist: PAED },
    ] },
  /* ------------------------------- BACK ----------------------------- */
  { id: 'back-pain', label: 'Back pain', region: 'back', audience: 'both', common: true,
    keywords: ['back pain', 'backache', 'spine pain', 'sciatica'],
    flags: ['rf.back-pain-weeks', 'rf.pain-severe', 'rf.confusion-new'], firstAid: ['fa.back'], baseTier: 'self',
    homeCare: ['Keep moving — short walks beat complete bed rest.', 'Cold pack for the first 2 days, then warm pack, wrapped in cloth.', 'Avoid lifting, bending and long sitting; sleep with a pillow under the knees.', 'Numbness in the groin or legs, or loss of bladder control, is an emergency.'],
    conditions: [
      { name: 'Mechanical low back pain', icd10: 'M54.5', weight: 3, specialist: ORTHO },
      { name: 'Lumbar disc prolapse', icd10: 'M51.26', weight: 2, specialist: ORTHO },
      { name: 'Urinary infection with flank pain', icd10: 'N10', weight: 1, specialist: URO },
    ] },
  { id: 'neck-pain', label: 'Neck pain or stiffness', region: 'back', audience: 'both',
    keywords: ['neck pain', 'stiff neck', 'cervical'],
    flags: ['rf.fever-stiff-neck', 'rf.stroke', 'rf.back-pain-weeks'], firstAid: ['fa.back'], baseTier: 'office',
    homeCare: ['Use a firm pillow that keeps the neck in line with the spine.', 'Avoid long hours looking down at a phone; take breaks every 30 minutes.', 'Warm pack for 15 minutes, then gentle neck stretches.', 'Stiff neck with fever, vomiting or severe headache needs care today.'],
    conditions: [
      { name: 'Cervical muscle strain', icd10: 'M62.838', weight: 3, specialist: ORTHO },
      { name: 'Cervical spondylosis', icd10: 'M47.812', weight: 2, specialist: ORTHO },
      { name: 'Meningitis', icd10: 'G03.9', weight: 1, specialist: P },
    ] },
  { id: 'shoulder-pain', label: 'Shoulder or upper back pain', region: 'back', audience: 'both',
    keywords: ['shoulder pain', 'upper back', 'frozen shoulder'],
    flags: ['rf.fracture', 'rf.major-trauma', 'rf.chest-cardiac'], firstAid: ['fa.fracture', 'fa.sprain'], baseTier: 'office',
    homeCare: ['Rest the shoulder from heavy lifting; keep gentle movement going.', 'Cold pack for the first 2 days, then warm pack for 15 minutes.', 'Sleep on the other side, or with a pillow supporting the arm.', 'Pain with chest tightness or sweating is treated as a heart problem.'],
    conditions: [
      { name: 'Rotator cuff strain', icd10: 'M75.100', weight: 3, specialist: ORTHO },
      { name: 'Frozen shoulder', icd10: 'M75.00', weight: 2, specialist: ORTHO },
      { name: 'Referred cardiac pain', icd10: 'I24.9', weight: 1, specialist: CARDIO },
    ] },
  { id: 'muscle-strain', label: 'Sprain, strain or swelling in a limb', region: 'back', audience: 'both',
    keywords: ['sprain', 'strain', 'swelling', 'muscle pull'],
    flags: ['rf.fracture', 'rf.bite-deep', 'rf.wound-infection'], firstAid: ['fa.sprain', 'fa.fracture'], baseTier: 'self',
    homeCare: ['Rest the area and avoid weight-bearing for 24–48 hours.', 'Cold pack wrapped in cloth for 15 minutes every 2–3 hours.', 'Wrap with a crepe bandage firmly but not tightly, and keep the limb raised.', 'A limb that cannot take weight, or looks bent, needs an X-ray today.'],
    conditions: [
      { name: 'Ligament sprain', icd10: 'S93.601', weight: 3, specialist: ORTHO },
      { name: 'Muscle strain', icd10: 'M62.838', weight: 3, specialist: ORTHO },
      { name: 'Cellulitis', icd10: 'L03.90', weight: 1, specialist: P },
    ] },
  /* ------------------------------ PELVIS ---------------------------- */
  { id: 'urine-burning', label: 'Burning when passing urine', region: 'pelvis', audience: 'both', common: true,
    keywords: ['burning urine', 'uti', 'urination pain', 'cystitis'],
    flags: ['rf.urine-burning-persistent', 'rf.urine-none', 'rf.fever-3-days'], firstAid: ['fa.urine-care'], baseTier: 'office',
    homeCare: ['Drink 2–3 litres of water a day.', 'Pass urine every 2–3 hours and after intercourse; do not hold it in.', 'Keep the area clean and dry, wiping front to back.', 'Fever, back pain or blood in urine means a kidney infection — see a doctor today.'],
    conditions: [
      { name: 'Urinary tract infection', icd10: 'N39.0', weight: 3, specialist: URO },
      { name: 'Pyelonephritis', icd10: 'N10', weight: 1, specialist: URO },
      { name: 'Sexually transmitted infection', icd10: 'A64', weight: 1, specialist: P },
    ] },
  { id: 'urine-frequent', label: 'Passing urine often, or weak stream', region: 'pelvis', audience: 'both',
    keywords: ['frequent urine', 'nocturia', 'weak stream', 'prostate'],
    flags: ['rf.urine-none', 'rf.sugar-abnormal', 'rf.urine-burning-persistent'], firstAid: ['fa.urine-care'], baseTier: 'office',
    homeCare: ['Reduce tea, coffee and alcohol, especially in the evening.', 'Empty the bladder fully, and again just before sleeping.', 'Keep a record of how many times you pass urine in 24 hours.', 'Not passing urine at all is an emergency — go to hospital now.'],
    conditions: [
      { name: 'Urinary tract infection', icd10: 'N39.0', weight: 2, specialist: URO },
      { name: 'Benign prostatic hyperplasia', icd10: 'N40.0', weight: 3, specialist: URO },
      { name: 'Uncontrolled diabetes', icd10: 'E11.9', weight: 2, specialist: P },
    ] },
  { id: 'genital-itch', label: 'Genital itching, sores or discharge', region: 'pelvis', audience: 'both',
    keywords: ['genital itch', 'discharge', 'sores', 'sti'],
    flags: ['rf.lump-new', 'rf.fever-3-days', 'rf.pain-severe'], firstAid: [], baseTier: 'office',
    homeCare: ['Keep the area clean and dry; wear loose cotton underclothes.', 'Do not use scented soaps, powders or home remedies.', 'Avoid sex until a doctor has checked you — a partner may need treatment too.', 'Use condoms and get tested for HIV and syphilis at the nearest ICTC.'],
    conditions: [
      { name: 'Candidiasis', icd10: 'B37.3', weight: 3, specialist: P },
      { name: 'Bacterial vaginosis', icd10: 'N76.0', weight: 2, specialist: OBS },
      { name: 'Sexually transmitted infection', icd10: 'A64', weight: 2, specialist: P },
    ] },
  { id: 'testicle-pain', label: 'Testicle pain or swelling', region: 'pelvis', audience: 'both', gender: 'M',
    keywords: ['testicle pain', 'scrotal swelling', 'groin lump'],
    flags: ['rf.testicle-pain', 'rf.pain-severe', 'rf.fever-3-days'], firstAid: ['fa.testicular'], baseTier: 'h24',
    homeCare: ['Support the scrotum with a folded cloth and rest.', 'Do not apply heat, massage, or try to push anything back.', 'Note whether the pain came on suddenly — that changes the urgency.', 'Sudden severe pain needs hospital within hours, not days.'],
    conditions: [
      { name: 'Testicular torsion', icd10: 'N44.00', weight: 3, specialist: URO },
      { name: 'Epididymo-orchitis', icd10: 'N45.9', weight: 3, specialist: URO },
      { name: 'Inguinal hernia', icd10: 'K40.90', weight: 2, specialist: 'Surgery' },
    ] },
  { id: 'period-pain', label: 'Period pain or heavy bleeding', region: 'pelvis', audience: 'adult', gender: 'F',
    keywords: ['period pain', 'menstrual cramps', 'heavy periods'],
    flags: ['rf.pain-severe', 'rf.pregnancy-emergency', 'rf.period-missed'], firstAid: ['fa.menstrual', 'fa.pregnancy'], baseTier: 'office',
    homeCare: ['Warm water bottle on the lower belly, with plenty of rest.', 'Paracetamol or mefenamic acid after food, if not allergic.', 'Change pads every 4–6 hours and record bleeding days in a diary.', 'Soaking a pad every hour, or pain that stops normal work, needs a doctor.'],
    conditions: [
      { name: 'Primary dysmenorrhoea', icd10: 'N94.6', weight: 3, specialist: OBS },
      { name: 'Endometriosis', icd10: 'N80.9', weight: 1, specialist: OBS },
      { name: 'Pelvic inflammatory disease', icd10: 'N73.9', weight: 1, specialist: OBS },
    ] },
  { id: 'period-missed', label: 'Missed or irregular periods', region: 'pelvis', audience: 'adult', gender: 'F',
    keywords: ['missed period', 'irregular periods', 'late period'],
    flags: ['rf.pregnancy-emergency', 'rf.period-missed', 'rf.weight-loss'], firstAid: ['fa.pregnancy'], baseTier: 'office',
    homeCare: ['Note the first day of the last period and any spotting in between.', 'Do a pregnancy test if there is any chance of pregnancy.', 'Keep weight, sleep and iron-rich food steady — dieting and stress delay periods.', 'If pregnant, register for antenatal care and take folic acid and iron tablets.'],
    conditions: [
      { name: 'Pregnancy', icd10: 'Z33.1', weight: 3, specialist: OBS },
      { name: 'Polycystic ovary syndrome', icd10: 'E28.2', weight: 2, specialist: OBS },
      { name: 'Thyroid disorder', icd10: 'E07.9', weight: 1, specialist: P },
    ] },
  { id: 'pregnancy-warning', label: 'Pregnancy warning signs', region: 'pelvis', audience: 'adult', gender: 'F',
    keywords: ['pregnancy bleeding', 'baby not moving', 'labour pain'],
    flags: ['rf.pregnancy-emergency', 'rf.pregnancy-pain', 'rf.bleeding-severe'], firstAid: ['fa.pregnancy'], baseTier: 'h24',
    homeCare: ['Lie on the left side and count baby movements for one hour after a meal.', 'Drink water and eat something small if you feel faint.', 'Carry your MCP card and keep the hospital number saved.', 'Bleeding, severe pain, fits, blurred vision or reduced movement means hospital now.'],
    conditions: [
      { name: 'Threatened preterm labour', icd10: 'O60.00', weight: 3, specialist: OBS },
      { name: 'Reduced fetal movements', icd10: 'O36.89', weight: 3, specialist: OBS },
      { name: 'Pre-eclampsia', icd10: 'O14.90', weight: 2, specialist: OBS },
    ] },
  /* ------------------------------ BOTTOM ---------------------------- */
  { id: 'piles', label: 'Piles or pain when passing stool', region: 'bottom', audience: 'both',
    keywords: ['piles', 'haemorrhoids', 'anal pain', 'fissure'],
    flags: ['rf.black-stool', 'rf.bleeding-severe', 'rf.diarrhea-blood'], firstAid: ['fa.abdominal'], baseTier: 'office',
    homeCare: ['Drink 2–3 litres of water and eat fibre — fruit, vegetables, whole grains.', 'Do not strain or sit long on the toilet; keep visits short.', 'Warm sitz bath for 10 minutes twice a day soothes the pain.', 'Any bleeding from the bottom must be examined by a doctor.'],
    conditions: [
      { name: 'Haemorrhoids', icd10: 'K64.9', weight: 3, specialist: 'Surgery' },
      { name: 'Anal fissure', icd10: 'K60.2', weight: 3, specialist: 'Surgery' },
      { name: 'Colorectal carcinoma', icd10: 'C18.9', weight: 1, specialist: 'Surgery' },
    ] },
  { id: 'rectal-bleeding', label: 'Blood in stool or rectal bleeding', region: 'bottom', audience: 'both',
    keywords: ['blood in stool', 'rectal bleeding', 'black stool'],
    flags: ['rf.black-stool', 'rf.bleeding-severe', 'rf.weight-loss'], firstAid: ['fa.abdominal'], baseTier: 'h24',
    homeCare: ['Note the colour and amount of blood, and whether it mixed with stool.', 'Drink fluids and eat iron-rich food — liver, greens, jaggery.', 'Avoid painkillers like ibuprofen and aspirin until reviewed.', 'Blood in stool always needs a doctor’s examination, even if painless.'],
    conditions: [
      { name: 'Haemorrhoids', icd10: 'K64.9', weight: 3, specialist: 'Surgery' },
      { name: 'Peptic ulcer bleeding', icd10: 'K27.4', weight: 2, specialist: GI },
      { name: 'Colorectal carcinoma', icd10: 'C18.9', weight: 1, specialist: 'Surgery' },
    ] },
  /* ------------------------------- ARMS ----------------------------- */
  { id: 'arm-pain', label: 'Arm or elbow pain', region: 'arms', audience: 'both',
    keywords: ['arm pain', 'elbow pain', 'arm injury', 'tennis elbow'],
    flags: ['rf.fracture', 'rf.major-trauma', 'rf.pain-severe'], firstAid: ['fa.fracture', 'fa.sprain'], baseTier: 'office',
    homeCare: ['Rest the arm from lifting and repetitive work.', 'Cold pack wrapped in cloth for 15 minutes, up to 4 times a day.', 'Use a sling to keep the arm supported and raised.', 'A bent limb, or one that cannot move at all, needs an X-ray today.'],
    conditions: [
      { name: 'Muscle or tendon strain', icd10: 'M62.838', weight: 3, specialist: ORTHO },
      { name: 'Fracture of upper limb', icd10: 'S42.90', weight: 2, specialist: ORTHO },
      { name: 'Arthritis of elbow', icd10: 'M19.90', weight: 1, specialist: ORTHO },
    ] },
  { id: 'hand-pain', label: 'Hand, wrist or finger pain', region: 'arms', audience: 'both',
    keywords: ['hand pain', 'wrist pain', 'finger pain', 'carpal tunnel'],
    flags: ['rf.fracture', 'rf.bite-deep', 'rf.wound-infection'], firstAid: ['fa.fracture', 'fa.wound'], baseTier: 'office',
    homeCare: ['Rest the hand and remove any rings before swelling increases.', 'Cold pack for 15 minutes every few hours.', 'Keep the hand raised on a pillow when sitting.', 'Numbness of the fingers at night (carpal tunnel) should be reviewed.'],
    conditions: [
      { name: 'Wrist sprain', icd10: 'S63.501', weight: 3, specialist: ORTHO },
      { name: 'Fracture of hand or finger', icd10: 'S62.90', weight: 2, specialist: ORTHO },
      { name: 'Carpal tunnel syndrome', icd10: 'G56.00', weight: 2, specialist: ORTHO },
    ] },
  { id: 'finger-injury', label: 'Finger injury or nail problem', region: 'arms', audience: 'both',
    keywords: ['finger injury', 'nail injury', 'crushed finger', 'ingrown nail'],
    flags: ['rf.fracture', 'rf.bite-deep', 'rf.bleeding-severe'], firstAid: ['fa.wound', 'fa.fracture'], baseTier: 'office',
    homeCare: ['Wash gently with clean water and cover with a sterile dressing.', 'Keep the finger raised and apply a cold pack for 15 minutes.', 'Do not remove an embedded object — support it while travelling.', 'A badly torn nail, or blood collecting under it, needs a doctor.'],
    conditions: [
      { name: 'Finger contusion', icd10: 'S60.20', weight: 3, specialist: ORTHO },
      { name: 'Distal phalanx fracture', icd10: 'S62.60', weight: 2, specialist: ORTHO },
      { name: 'Paronychia', icd10: 'L03.019', weight: 2, specialist: P },
    ] },
  /* ------------------------------- LEGS ----------------------------- */
  { id: 'knee-pain', label: 'Knee pain or swelling', region: 'legs', audience: 'both', common: true,
    keywords: ['knee pain', 'knee swelling', 'knee injury'],
    flags: ['rf.fracture', 'rf.pain-severe', 'rf.major-trauma'], firstAid: ['fa.fracture', 'fa.sprain'], baseTier: 'office',
    homeCare: ['Rest the knee and avoid climbing stairs or squatting.', 'Cold pack for 15 minutes every 2–3 hours for the first 2 days.', 'Wrap with a crepe bandage and keep the leg raised on a pillow.', 'A knee that locks, gives way, or cannot take weight needs an X-ray.'],
    conditions: [
      { name: 'Knee sprain / meniscal injury', icd10: 'S83.90', weight: 3, specialist: ORTHO },
      { name: 'Osteoarthritis of knee', icd10: 'M17.9', weight: 3, specialist: ORTHO },
      { name: 'Septic arthritis', icd10: 'M00.90', weight: 1, specialist: ORTHO },
    ] },
  { id: 'ankle-sprain', label: 'Ankle or foot pain and swelling', region: 'legs', audience: 'both', common: true,
    keywords: ['ankle sprain', 'foot pain', 'twisted ankle'],
    flags: ['rf.fracture', 'rf.bite-deep', 'rf.wound-infection'], firstAid: ['fa.sprain', 'fa.fracture'], baseTier: 'self',
    homeCare: ['Rest, cold pack for 15 minutes, compression bandage and elevation.', 'Do not walk on it for the first 24 hours if very painful.', 'Keep the bandage firm but not tight — toes should stay pink and warm.', 'Cannot take four steps, or the ankle looks deformed, needs an X-ray today.'],
    conditions: [
      { name: 'Ankle sprain', icd10: 'S93.401', weight: 3, specialist: ORTHO },
      { name: 'Ankle fracture', icd10: 'S82.90', weight: 2, specialist: ORTHO },
      { name: 'Plantar fasciitis', icd10: 'M72.2', weight: 1, specialist: ORTHO },
    ] },
  { id: 'leg-swelling', label: 'Leg swelling or calf pain', region: 'legs', audience: 'both',
    keywords: ['leg swelling', 'calf pain', 'oedema', 'clot'],
    flags: ['rf.breathing-mild', 'rf.pain-severe', 'rf.chest-cardiac'], firstAid: ['fa.breathing'], baseTier: 'h24',
    homeCare: ['Raise the leg above heart level when sitting or lying.', 'Walk gently — long immobility increases clot risk.', 'Reduce salt; keep a record of daily weight if you have heart or kidney disease.', 'Swelling in one leg with calf pain or breathlessness needs care today.'],
    conditions: [
      { name: 'Deep vein thrombosis', icd10: 'I80.209', weight: 3, specialist: 'Surgery' },
      { name: 'Venous insufficiency', icd10: 'I87.209', weight: 2, specialist: 'Surgery' },
      { name: 'Heart failure', icd10: 'I50.9', weight: 1, specialist: CARDIO },
    ] },
  { id: 'toe-pain', label: 'Toe pain or ingrown toenail', region: 'legs', audience: 'both',
    keywords: ['toe pain', 'ingrown toenail', 'gout', 'toe injury'],
    flags: ['rf.fracture', 'rf.wound-infection', 'rf.pain-severe'], firstAid: ['fa.wound', 'fa.sprain'], baseTier: 'office',
    homeCare: ['Soak the foot in warm salt water for 10 minutes twice a day.', 'Wear open, well-fitting footwear; cut nails straight across.', 'Keep the toe raised and avoid tight shoes or long walking.', 'Spreading redness, fever, or a toe wound with diabetes needs care today.'],
    conditions: [
      { name: 'Ingrown toenail with infection', icd10: 'L60.0', weight: 3, specialist: 'Surgery' },
      { name: 'Gout', icd10: 'M10.9', weight: 2, specialist: P },
      { name: 'Toe fracture', icd10: 'S92.90', weight: 2, specialist: ORTHO },
    ] },
  /* ------------------------------- SKIN ----------------------------- */
  { id: 'rash-local', label: 'Rash in one area', region: 'skin', audience: 'both', common: true,
    keywords: ['rash', 'redness', 'ringworm', 'eczema'],
    flags: ['rf.rash-spreading', 'rf.fever-rash', 'rf.wound-infection'], firstAid: ['fa.skin-care'], baseTier: 'self',
    homeCare: ['Wash with plain water and mild soap; pat dry, do not rub.', 'Apply coconut oil or the prescribed cream thinly.', 'Keep nails short and avoid scratching; a cool cloth eases itching.', 'A rash with fever, or blistering and spreading fast, needs care today.'],
    conditions: [
      { name: 'Contact dermatitis', icd10: 'L23.9', weight: 3, specialist: DERM },
      { name: 'Fungal infection (tinea)', icd10: 'B35.9', weight: 3, specialist: DERM },
      { name: 'Eczema', icd10: 'L30.9', weight: 2, specialist: DERM },
    ] },
  { id: 'rash-widespread', label: 'Widespread rash or fever with rash', region: 'skin', audience: 'both',
    keywords: ['widespread rash', 'fever rash', 'measles', 'viral rash'],
    flags: ['rf.fever-rash', 'rf.rash-spreading', 'rf.breathing-mild'], firstAid: ['fa.fever', 'fa.skin-care'], baseTier: 'h24',
    homeCare: ['Keep the person cool and hydrated; give paracetamol for fever.', 'Do not apply oils, turmeric or toothpaste to the rash.', 'Keep them away from pregnant women and unvaccinated children.', 'Rash with fever, drowsiness or breathing difficulty needs urgent care.'],
    conditions: [
      { name: 'Viral exanthem', icd10: 'B09', weight: 3, specialist: P },
      { name: 'Measles', icd10: 'B05.9', weight: 2, specialist: P },
      { name: 'Dengue fever', icd10: 'A90', weight: 2, specialist: P },
    ] },
  { id: 'itchy-skin', label: 'Itching all over', region: 'skin', audience: 'both',
    keywords: ['itching', 'pruritus', 'scabies', 'hives'],
    flags: ['rf.rash-spreading', 'rf.fever-rash', 'rf.lasting-pain'], firstAid: ['fa.skin-care'], baseTier: 'office',
    homeCare: ['Bathe in cool water, pat dry and apply a soothing moisturiser.', 'Avoid hot water, woollen clothes and strong soaps.', 'Scabies needs treatment for every family member at the same time, and washing clothes in hot water.', 'Itching with yellow eyes, weight loss or pregnancy needs a doctor.'],
    conditions: [
      { name: 'Scabies', icd10: 'B86', weight: 3, specialist: DERM },
      { name: 'Urticaria (hives)', icd10: 'L50.9', weight: 3, specialist: DERM },
      { name: 'Dry skin / xerosis', icd10: 'L85.3', weight: 2, specialist: DERM },
    ] },
  { id: 'boil', label: 'Boil, abscess or infected sore', region: 'skin', audience: 'both',
    keywords: ['boil', 'abscess', 'pus', 'cellulitis'],
    flags: ['rf.wound-infection', 'rf.fever-3-days', 'rf.sugar-abnormal'], firstAid: ['fa.wound', 'fa.skin-care'], baseTier: 'office',
    homeCare: ['Apply warm compresses for 15 minutes, 3–4 times a day.', 'Keep it clean and covered; do not squeeze or cut it yourself.', 'Wash hands after touching it and use a separate towel.', 'Spreading redness, red streaks, fever or diabetes needs a doctor today.'],
    conditions: [
      { name: 'Cutaneous abscess', icd10: 'L02.91', weight: 3, specialist: 'Surgery' },
      { name: 'Cellulitis', icd10: 'L03.90', weight: 3, specialist: P },
      { name: 'Folliculitis', icd10: 'L73.9', weight: 2, specialist: DERM },
    ] },
  { id: 'wound', label: 'Cut, scrape or open wound', region: 'skin', audience: 'both', common: true,
    keywords: ['cut', 'wound', 'scrape', 'bleeding'],
    flags: ['rf.bleeding-severe', 'rf.bite-deep', 'rf.wound-infection'], firstAid: ['fa.wound', 'fa.bleeding'], baseTier: 'self',
    homeCare: ['Wash the wound under clean running water for 5 minutes.', 'Cover with a clean dressing; change it daily or when wet.', 'Get a tetanus injection if the wound is dirty or from a bite.', 'Spreading redness, pus, foul smell or fever means see a doctor within 24 hours.'],
    conditions: [
      { name: 'Superficial laceration', icd10: 'S01.91', weight: 3, specialist: P },
      { name: 'Infected wound', icd10: 'T79.3', weight: 2, specialist: 'Surgery' },
      { name: 'Tetanus-prone wound', icd10: 'Z23', weight: 1, specialist: P },
    ] },
  { id: 'burn', label: 'Burn or scald', region: 'skin', audience: 'both',
    keywords: ['burn', 'scald', 'hot water burn', 'fire'],
    flags: ['rf.burn-large', 'rf.major-trauma', 'rf.dehydration-mild'], firstAid: ['fa.burn', 'fa.dehydration'], baseTier: 'h24',
    homeCare: ['Cool the burn with cool running water for 20 minutes — no ice, butter or toothpaste.', 'Cover loosely with a clean, non-fluffy cloth; do not burst blisters.', 'Give ORS or water to drink for the first 24 hours.', 'Burns bigger than the palm, or on the face, hands, feet or genitals, need hospital.'],
    conditions: [
      { name: 'Superficial partial-thickness burn', icd10: 'T23.201', weight: 3, specialist: 'Surgery' },
      { name: 'Deep burn / full-thickness burn', icd10: 'T24.201', weight: 2, specialist: 'Surgery' },
      { name: 'Wound infection', icd10: 'T79.3', weight: 2, specialist: 'Surgery' },
    ] },
  { id: 'insect-bite', label: 'Insect, snake or animal bite', region: 'skin', audience: 'both',
    keywords: ['insect bite', 'bee sting', 'snake bite', 'dog bite'],
    flags: ['rf.anaphylaxis', 'rf.snake-bite', 'rf.bite-deep'], firstAid: ['fa.anaphylaxis', 'fa.snake-bite', 'fa.wound'], baseTier: 'office',
    homeCare: ['Remove the sting by scraping sideways; wash with soap and water.', 'Apply a cold pack wrapped in cloth for 10 minutes to reduce swelling.', 'Do not cut, suck or tie a bandage around a snake bite.', 'Any breathing difficulty, swelling of the face or throat is an emergency.'],
    conditions: [
      { name: 'Local insect bite reaction', icd10: 'T14.1', weight: 3, specialist: P },
      { name: 'Snake envenomation', icd10: 'T63.0', weight: 1, specialist: 'Surgery' },
      { name: 'Animal bite, rabies exposure', icd10: 'W54.0', weight: 2, specialist: 'Surgery' },
    ] },
  { id: 'jaundice-newborn', label: 'Yellow skin or eyes (newborn)', region: 'skin', audience: 'peds',
    keywords: ['jaundice baby', 'yellow eyes newborn'],
    flags: ['rf.newborn-ill', 'rf.dehydration-severe', 'rf.fever-newborn'], firstAid: ['fa.newborn'], baseTier: 'h24',
    homeCare: ['Breastfeed often — 8–12 feeds in 24 hours helps clear bilirubin.', 'Put the baby in the sun in the early morning for short spells, undressed, with eyes covered.', 'Do not stop breastfeeding or give sugar water.', 'Yellow palms and soles, drowsiness or poor feeding needs hospital today.'],
    conditions: [
      { name: 'Neonatal hyperbilirubinaemia', icd10: 'P59.9', weight: 3, specialist: PAED },
      { name: 'Breastfeeding jaundice', icd10: 'P59.3', weight: 2, specialist: PAED },
    ] },
  { id: 'diaper-rash', label: 'Nappy rash or skin folds rash', region: 'skin', audience: 'peds',
    keywords: ['nappy rash', 'diaper rash', 'skin fold rash'],
    flags: ['rf.rash-spreading', 'rf.fever-rash', 'rf.wound-infection'], firstAid: ['fa.skin-care'], baseTier: 'self',
    homeCare: ['Change the nappy as soon as it is wet or soiled.', 'Clean with plain water, pat dry, and leave the baby without a nappy when possible.', 'Apply a thin barrier cream of zinc oxide or coconut oil.', 'Blisters, pus or a rash spreading beyond the nappy area needs a doctor.'],
    conditions: [
      { name: 'Irritant contact dermatitis', icd10: 'L22', weight: 3, specialist: PAED },
      { name: 'Candidal nappy rash', icd10: 'B37.2', weight: 2, specialist: PAED },
    ] },
  /* ------------------------------ GENERAL --------------------------- */
  { id: 'fever', label: 'Fever', region: 'general', audience: 'both', common: true,
    keywords: ['fever', 'temperature', 'hot body'],
    flags: ['rf.fever-newborn', 'rf.fever-stiff-neck', 'rf.fever-rash', 'rf.fever-3-days'], firstAid: ['fa.fever', 'fa.dehydration'], baseTier: 'self',
    homeCare: ['Give fluids often — water, ORS, soup, breast milk for babies.', 'Sponge with lukewarm water; keep clothing light.', 'Paracetamol by weight, up to 4 doses in 24 hours; never aspirin for children.', 'Fever over 3 days, or with rash, stiff neck or drowsiness, needs a doctor.'],
    conditions: [
      { name: 'Viral fever', icd10: 'R50.9', weight: 3, specialist: P },
      { name: 'Malaria', icd10: 'B54', weight: 2, specialist: P },
      { name: 'Typhoid fever', icd10: 'A01.00', weight: 1, specialist: P },
    ] },
  { id: 'fever-child', label: 'Fever in a child', region: 'general', audience: 'peds', common: true,
    keywords: ['child fever', 'baby temperature', 'high fever child'],
    flags: ['rf.fever-newborn', 'rf.fever-rash', 'rf.dehydration-mild', 'rf.breathing-severe'], firstAid: ['fa.fever', 'fa.newborn', 'fa.dehydration'], baseTier: 'office',
    homeCare: ['Continue breastfeeding; give ORS and water in small amounts.', 'Sponge with lukewarm water; do not use cold water or ice.', 'Paracetamol by weight only — never aspirin.', 'Any fever in a baby under 3 months, or a drowsy child, needs care now.'],
    conditions: [
      { name: 'Viral fever', icd10: 'R50.9', weight: 3, specialist: PAED },
      { name: 'Pneumonia', icd10: 'J18.9', weight: 2, specialist: PAED },
      { name: 'Dengue fever', icd10: 'A90', weight: 2, specialist: PAED },
    ] },
  { id: 'tiredness', label: 'Tiredness, weakness or body ache', region: 'general', audience: 'both',
    keywords: ['tired', 'weakness', 'fatigue', 'body ache'],
    flags: ['rf.pain-severe', 'rf.weight-loss', 'rf.confusion-new'], firstAid: ['fa.fever'], baseTier: 'office',
    homeCare: ['Rest and sleep 7–8 hours; take short naps if needed.', 'Eat iron-rich food — green leafy vegetables, jaggery, liver, eggs.', 'Drink 2–3 litres of water a day.', 'Weakness with weight loss, night sweats or bleeding must be investigated.'],
    conditions: [
      { name: 'Anaemia', icd10: 'D64.9', weight: 3, specialist: P },
      { name: 'Hypothyroidism', icd10: 'E03.9', weight: 2, specialist: P },
      { name: 'Tuberculosis', icd10: 'A15.9', weight: 1, specialist: PULMO },
    ] },
  { id: 'sunstroke', label: 'Heat exhaustion or sunstroke', region: 'general', audience: 'both',
    keywords: ['heat stroke', 'sunstroke', 'heat exhaustion'],
    flags: ['rf.heat-stroke', 'rf.dehydration-severe', 'rf.confusion-new'], firstAid: ['fa.heat', 'fa.dehydration'], baseTier: 'h24',
    homeCare: ['Move to shade, loosen clothes and cool with wet cloths and a fan.', 'Give ORS or lemon-salt water if fully awake — never force fluids into an unconscious person.', 'Avoid going out between 12 and 3 pm; cover the head.', 'Hot dry skin with confusion or fainting is an emergency — call 108 / 112.'],
    conditions: [
      { name: 'Heat exhaustion', icd10: 'T67.3', weight: 3, specialist: P },
      { name: 'Heat stroke', icd10: 'T67.0', weight: 2, specialist: P },
      { name: 'Dehydration', icd10: 'E86.0', weight: 3, specialist: P },
    ] },
  { id: 'sleep-problems', label: 'Cannot sleep, or anxiety', region: 'general', audience: 'both',
    keywords: ['insomnia', 'anxiety', 'panic', 'stress', 'sleep'],
    flags: ['rf.mood-weeks', 'rf.suicidal', 'rf.confusion-new'], firstAid: ['fa.mood-care', 'fa.mental-health'], baseTier: 'office',
    homeCare: ['Keep a fixed sleep and wake time, and no screens in bed.', 'Avoid tea, coffee and alcohol after the evening.', 'Try slow breathing: in for 4 counts, out for 6, for 5 minutes.', 'If low mood lasts 2 weeks, or there are thoughts of self-harm, get help now — call 14416.'],
    conditions: [
      { name: 'Insomnia', icd10: 'G47.00', weight: 3, specialist: PSY },
      { name: 'Anxiety disorder', icd10: 'F41.9', weight: 3, specialist: PSY },
      { name: 'Depression', icd10: 'F32.9', weight: 2, specialist: PSY },
    ] },
  { id: 'low-mood', label: 'Low mood, crying or no interest', region: 'general', audience: 'both',
    keywords: ['depression', 'sadness', 'hopeless', 'no interest'],
    flags: ['rf.suicidal', 'rf.mood-weeks', 'rf.weight-loss'], firstAid: ['fa.mental-health', 'fa.mood-care'], baseTier: 'office',
    homeCare: ['Talk to one trusted person today — do not keep it inside.', 'Keep meals, sleep and a short daily walk going, even without interest.', 'Avoid alcohol, tobacco and gutka; they worsen mood.', 'Thoughts of self-harm need immediate help — Tele-MANAS 14416, free, 24×7.'],
    conditions: [
      { name: 'Depressive episode', icd10: 'F32.9', weight: 3, specialist: PSY },
      { name: 'Postpartum depression', icd10: 'F53.0', weight: 2, specialist: PSY },
      { name: 'Anxiety disorder', icd10: 'F41.9', weight: 2, specialist: PSY },
    ] },
  { id: 'weight-loss', label: 'Weight loss or no appetite', region: 'general', audience: 'both',
    keywords: ['weight loss', 'appetite loss', 'losing weight'],
    flags: ['rf.weight-loss', 'rf.cough-2-weeks', 'rf.lump-new'], firstAid: [], baseTier: 'office',
    homeCare: ['Eat small, frequent, energy-dense meals — add ghee, groundnut, banana.', 'Weigh yourself weekly and write it down.', 'Do not use weight-loss or appetite powders without advice.', 'Weight loss with a cough over 2 weeks needs a TB test at the nearest health centre.'],
    conditions: [
      { name: 'Tuberculosis', icd10: 'A15.9', weight: 3, specialist: PULMO },
      { name: 'Uncontrolled diabetes', icd10: 'E11.9', weight: 2, specialist: P },
      { name: 'Malignancy', icd10: 'C80.1', weight: 1, specialist: 'Oncology' },
    ] },
  { id: 'immunization-reaction', label: 'Reaction after vaccination', region: 'general', audience: 'peds',
    keywords: ['vaccine reaction', 'immunisation', 'injection swelling'],
    flags: ['rf.anaphylaxis', 'rf.fever-3-days', 'rf.fever-newborn'], firstAid: ['fa.fever', 'fa.anaphylaxis'], baseTier: 'self',
    homeCare: ['Mild fever, a sore arm and sleepiness for 1–2 days is expected.', 'Apply a clean cold pack wrapped in cloth to the injection site.', 'Give paracetamol by weight only if there is fever or pain.', 'Breathing difficulty, generalised hives, or a limp child is an emergency.'],
    conditions: [
      { name: 'Expected vaccine reaction', icd10: 'T88.1', weight: 3, specialist: PAED },
      { name: 'Anaphylaxis', icd10: 'T78.2', weight: 1, specialist: PAED },
    ] },
];

/* --------------------------- lookup helpers --------------------------- */
export const symptomById = (id: string): Symptom | undefined => SYMPTOMS.find((s) => s.id === id);

/* Audience = entered age; gender = selected Man/Woman card. */
export function symptomsForRegion(regionId: string, model: BodyType, ageMonths = 999): Symptom[] {
  const audience = audienceForAge(ageMonths);
  const gender = modelGender(model);
  return SYMPTOMS.filter((s) => {
    if (s.region !== regionId) return false;
    const ageOk = s.audience === 'both' || s.audience === audience;
    const genderOk = !s.gender || s.gender === gender || s.gender === 'B';
    return ageOk && genderOk;
  });
}

export function searchSymptoms(
  query: string,
  model: BodyType,
  ageMonths = 999,
  limit = 40,
  labelOf?: (s: Symptom) => string,
): Symptom[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const audience = audienceForAge(ageMonths);
  const gender = modelGender(model);
  return SYMPTOMS
    .filter((s) => (s.audience === 'both' || s.audience === audience) && (!s.gender || s.gender === gender || s.gender === 'B'))
    .filter((s) => (labelOf?.(s) ?? s.label).toLowerCase().includes(q) || s.keywords.some((k) => k.includes(q)))
    .slice(0, limit);
}

export const commonSymptoms = (model: BodyType, ageMonths = 999): Symptom[] => {
  const audience = audienceForAge(ageMonths);
  const gender = modelGender(model);
  return SYMPTOMS.filter((s) =>
    s.common
    && (s.audience === 'both' || s.audience === audience)
    && (!s.gender || s.gender === gender || s.gender === 'B'),
  );
};
