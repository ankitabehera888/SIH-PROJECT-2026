/* Clinical triage content for the SAHAAY symptom checker.
   Structure, vocabulary and urgency ladder are adapted from the openly served
   Schmitt Decision Logic topic model used by hospital symptom checkers
   (dispositions: level 100/95/90/65/20/10 → Call 911 → Go to ER → Seek care
   now → Within 24 hours → Office hours → Self care). The wording here is
   simplified for community health workers and is NOT a medical device:
   every screen that renders it must show the disclaimer below. */

export type BodyType = 'male' | 'female';
export type ViewSide = 'front' | 'back';
export type Audience = 'adult' | 'peds' | 'both';
export type Gender = 'M' | 'F' | 'B';

export const modelGender = (m: BodyType): Gender => (m === 'female' ? 'F' : 'M');
export const modelLabel = (m: BodyType): string => (m === 'male' ? 'Man' : 'Woman');
/* Paediatric audience comes from entered age, not the selected sex card. */
export const audienceForAge = (ageMonths: number): Audience => (ageMonths < 144 ? 'peds' : 'adult');

/* Age bands used for triage raises and first-aid variants. Stored in months. */
export type AgeBand = 'neonate' | 'infant' | 'child' | 'teen' | 'adult' | 'senior';

export const ageBand = (ageMonths: number): AgeBand => {
  if (ageMonths < 1) return 'neonate';
  if (ageMonths < 12) return 'infant';
  if (ageMonths < 144) return 'child';   // under 12 years
  if (ageMonths < 216) return 'teen';    // under 18 years
  if (ageMonths < 780) return 'adult';   // under 65 years
  return 'senior';
};

export const ageBandLabel = (band: AgeBand): string =>
  band === 'neonate' ? 'Newborn'
    : band === 'infant' ? 'Infant'
      : band === 'child' ? 'Child'
        : band === 'teen' ? 'Teenager'
          : band === 'adult' ? 'Adult'
            : 'Older adult';

export const formatAge = (ageMonths: number): string => {
  if (ageMonths < 1) return 'under 1 month';
  if (ageMonths < 12) return `${ageMonths} month${ageMonths === 1 ? '' : 's'}`;
  const years = Math.floor(ageMonths / 12);
  const rem = ageMonths % 12;
  if (years < 2 && rem) return `${years} year${years === 1 ? '' : 's'} ${rem} month${rem === 1 ? '' : 's'}`;
  return `${years} year${years === 1 ? '' : 's'}`;
};

export interface UrgencyTier {
  id: string;
  level: number;
  label: string;
  short: string;
  timeframe: string;
  action: string;
  /* Tailwind classes kept explicit so both themes read correctly. */
  text: string;
  bg: string;
  border: string;
  ring: string;
  bar: string;
  hex: string;
}

export const URGENCY_TIERS: UrgencyTier[] = [
  {
    id: 'call911', level: 100,
    label: 'Emergency — Call 108 / 112 Now',
    short: 'Emergency',
    timeframe: 'Right now',
    action: 'Call an ambulance or get to the nearest emergency room immediately. Do not wait to see if it improves.',
    text: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-300', ring: 'ring-rose-200', bar: 'bg-rose-600', hex: '#e11d48',
  },
  {
    id: 'er', level: 95,
    label: 'Go to the Emergency Room Now',
    short: 'ER now',
    timeframe: 'Within minutes',
    action: 'Go to the nearest hospital emergency department now. Do not eat or drink until seen.',
    text: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-300', ring: 'ring-rose-200', bar: 'bg-rose-500', hex: '#f43f5e',
  },
  {
    id: 'now', level: 90,
    label: 'Call a Doctor or Seek Care Now',
    short: 'Care now',
    timeframe: 'Today, within a few hours',
    action: 'Contact a doctor or visit a PHC/CHC today. If you cannot reach one within 2 hours, go to the nearest hospital.',
    text: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-300', ring: 'ring-amber-200', bar: 'bg-amber-500', hex: '#f59e0b',
  },
  {
    id: 'h24', level: 65,
    label: 'Contact a Doctor Within 24 Hours',
    short: 'Within 24 h',
    timeframe: 'Within 24 hours',
    action: 'Arrange a consultation or PHC visit within the next 24 hours. Watch closely for any red-flag sign in the meantime.',
    text: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-300', ring: 'ring-orange-200', bar: 'bg-orange-500', hex: '#ea580c',
  },
  {
    id: 'office', level: 20,
    label: 'Contact a Doctor During Office Hours',
    short: 'Office hours',
    timeframe: 'In the next few days',
    action: 'Make a routine appointment with your doctor or health worker if it does not settle, or before.',
    text: 'text-sky-700', bg: 'bg-sky-50', border: 'border-sky-300', ring: 'ring-sky-200', bar: 'bg-sky-500', hex: '#0284c7',
  },
  {
    id: 'self', level: 10,
    label: 'Self Care at Home',
    short: 'Self care',
    timeframe: 'Manage at home',
    action: 'Follow the home care steps below. If things get worse, or new symptoms appear, run the check again.',
    text: 'text-sahaay-deep', bg: 'bg-sahaay-surface', border: 'border-sahaay-deep/25', ring: 'ring-sahaay-200', bar: 'bg-sahaay-500', hex: '#17B366',
  },
];

export const tierById = (id: string): UrgencyTier =>
  URGENCY_TIERS.find((t) => t.id === id) ?? URGENCY_TIERS[URGENCY_TIERS.length - 1];

export interface RedFlag {
  id: string;
  text: string;
  tier: string;
  firstAid: string[];
  regions?: string[];
}

export const DISCLAIMER =
  'This health information is for educational purposes only. It is an AI-assisted triage guide, not a diagnosis. You assume full responsibility for how you choose to use it. In an emergency, call 108 / 112.';
/* ---------------------------------------------------------------------------
   RED FLAGS — the questions a triage nurse asks first. Any single checked
   flag raises the whole assessment to that level, whatever else was selected.
   --------------------------------------------------------------------------- */
export const RED_FLAGS: RedFlag[] = [
  // Level 100 — life threatening, call for an ambulance
  { id: 'rf.not-breathing', tier: 'call911', firstAid: ['fa.cpr'], text: 'Not breathing, or only gasping occasionally' },
  { id: 'rf.unconscious', tier: 'call911', firstAid: ['fa.recovery-position'], text: 'Unconscious, unresponsive, or cannot be woken properly' },
  { id: 'rf.seizure', tier: 'call911', firstAid: ['fa.seizure'], text: 'A seizure (convulsion) now, or a first-ever seizure' },
  { id: 'rf.stroke', tier: 'call911', firstAid: ['fa.stroke'], text: 'Stroke signs — face drooping, one-sided weakness, slurred speech' },
  { id: 'rf.bleeding-severe', tier: 'call911', firstAid: ['fa.bleeding'], text: 'Bleeding that will not stop after 10 minutes of firm pressure' },
  { id: 'rf.choking', tier: 'call911', firstAid: ['fa.choking'], text: 'Choking — cannot breathe, speak or cough' },
  { id: 'rf.anaphylaxis', tier: 'call911', firstAid: ['fa.anaphylaxis'], text: 'Tongue or throat swelling, widespread hives with trouble breathing, or collapse after food, sting or medicine' },
  { id: 'rf.chest-cardiac', tier: 'call911', firstAid: ['fa.heart-attack'], text: 'Chest pressure or pain with sweating, nausea, or pain spreading to arm, neck or jaw' },
  { id: 'rf.poisoning', tier: 'call911', firstAid: ['fa.poisoning'], text: 'Swallowed poison, a chemical, kerosene, or too much medicine' },
  { id: 'rf.breathing-severe', tier: 'call911', firstAid: ['fa.breathing'], regions: ['chest', 'head'], text: 'Struggling to breathe — ribs pulling in, grunting, blue lips or unable to speak a full sentence' },
  { id: 'rf.newborn-ill', tier: 'call911', firstAid: ['fa.newborn'], text: 'Baby under 3 months: fever, poor feeding, or unusually sleepy and floppy' },
  { id: 'rf.major-trauma', tier: 'call911', firstAid: ['fa.head-injury'], text: 'Serious accident or fall from height, or a deep wound to the head, chest or belly' },
  { id: 'rf.suicidal', tier: 'call911', firstAid: ['fa.mental-health'], text: 'Thoughts of harming yourself or someone else, or a plan to do so' },

  // Level 95 — go to the emergency room
  { id: 'rf.head-injury-vomit', tier: 'er', firstAid: ['fa.head-injury'], regions: ['head'], text: 'Head injury with vomiting, confusion, memory loss, or clear fluid from nose/ear' },
  { id: 'rf.abdomen-rigid', tier: 'er', firstAid: ['fa.abdominal'], regions: ['abdomen', 'pelvis'], text: 'Severe belly pain with a hard, board-like or very tender tummy' },
  { id: 'rf.vomit-blood', tier: 'er', firstAid: ['fa.abdominal'], regions: ['abdomen'], text: 'Vomiting blood, or vomit that looks like coffee grounds' },
  { id: 'rf.black-stool', tier: 'er', firstAid: ['fa.abdominal'], regions: ['abdomen', 'bottom'], text: 'Black, tarry stools or a large amount of fresh blood in stool' },
  { id: 'rf.dehydration-severe', tier: 'er', firstAid: ['fa.dehydration'], text: 'No urine for 8+ hours, sunken eyes, no tears, or skin that stays pinched' },
  { id: 'rf.burn-large', tier: 'er', firstAid: ['fa.burn'], regions: ['skin', 'arms', 'legs', 'chest'], text: 'Burn bigger than the person’s palm, or any burn on face, hands, feet or genitals' },
  { id: 'rf.fracture', tier: 'er', firstAid: ['fa.fracture'], regions: ['arms', 'legs'], text: 'Obvious broken bone, bent limb, or cannot put any weight on it' },
  { id: 'rf.eye-chemical', tier: 'er', firstAid: ['fa.eye-chemical'], regions: ['head'], text: 'Chemical or hot liquid in the eye, or a sharp object stuck in the eye' },
  { id: 'rf.snake-bite', tier: 'er', firstAid: ['fa.snake-bite'], regions: ['legs', 'arms', 'skin'], text: 'Snake bite, or a bite from a stray or wild animal' },
  { id: 'rf.bite-deep', tier: 'er', firstAid: ['fa.wound'], regions: ['skin', 'arms', 'legs'], text: 'Deep or gaping wound, or a wound that needs stitches' },
  { id: 'rf.pregnancy-emergency', tier: 'er', firstAid: ['fa.pregnancy'], regions: ['pelvis', 'abdomen'], text: 'Pregnant: heavy bleeding, severe belly pain, fit, or baby moving much less' },
  // Level 90 — call a doctor or seek care today
  { id: 'rf.fever-stiff-neck', tier: 'now', firstAid: ['fa.fever'], regions: ['head', 'back'], text: 'Fever with a stiff neck, severe headache, or light hurting the eyes' },
  { id: 'rf.fever-rash', tier: 'now', firstAid: ['fa.fever'], regions: ['skin'], text: 'Fever together with a new rash' },
  { id: 'rf.fever-newborn', tier: 'now', firstAid: ['fa.newborn'], text: 'Fever 38°C (100.4°F) or higher in a baby under 3 months' },
  { id: 'rf.breathing-mild', tier: 'now', firstAid: ['fa.breathing'], regions: ['chest'], text: 'Short of breath at rest, or breathless doing small tasks' },
  { id: 'rf.pain-severe', tier: 'now', firstAid: [], text: 'Pain rated 8 out of 10 or worse that is not settling' },
  { id: 'rf.vomit-persistent', tier: 'now', firstAid: ['fa.dehydration'], regions: ['abdomen'], text: 'Vomiting everything for more than 8 hours, or cannot keep fluids down' },
  { id: 'rf.diarrhea-many', tier: 'now', firstAid: ['fa.dehydration'], regions: ['abdomen', 'bottom'], text: 'Watery diarrhoea 8 or more times a day, or with dizziness on standing' },
  { id: 'rf.urine-none', tier: 'now', firstAid: ['fa.dehydration'], regions: ['pelvis', 'abdomen'], text: 'Cannot pass urine at all, or only a few drops with severe pain' },
  { id: 'rf.sugar-abnormal', tier: 'now', firstAid: ['fa.hypoglycemia'], text: 'Known diabetes: blood sugar below 70 or above 300 mg/dL, or shaking and sweating' },
  { id: 'rf.heat-stroke', tier: 'now', firstAid: ['fa.heat'], regions: ['skin'], text: 'After heat or sun: hot dry skin, confusion, or stopped sweating' },
  { id: 'rf.confusion-new', tier: 'now', firstAid: ['fa.mental-health'], text: 'New confusion, drowsiness, or behaviour that is not normal for the person' },
  { id: 'rf.testicle-pain', tier: 'now', firstAid: ['fa.testicular'], regions: ['pelvis'], text: 'Sudden severe pain or swelling in a testicle' },
  { id: 'rf.asthma-attack', tier: 'now', firstAid: ['fa.breathing', 'fa.asthma'], regions: ['chest'], text: 'Asthma inhaler not helping, or needing it every 2–3 hours' },

  // Level 65 — contact a doctor within 24 hours
  { id: 'rf.fever-3-days', tier: 'h24', firstAid: ['fa.fever'], text: 'Fever lasting more than 3 days, or coming back after settling' },
  { id: 'rf.dehydration-mild', tier: 'h24', firstAid: ['fa.dehydration'], text: 'Drinking much less, dry lips and mouth, or dark strong-smelling urine' },
  { id: 'rf.rash-spreading', tier: 'h24', firstAid: ['fa.wound'], regions: ['skin'], text: 'Rash spreading quickly, blistering, or painful to touch' },
  { id: 'rf.wound-infection', tier: 'h24', firstAid: ['fa.wound'], regions: ['skin', 'arms', 'legs'], text: 'Wound with spreading redness, pus, bad smell, or fever' },
  { id: 'rf.diarrhea-blood', tier: 'h24', firstAid: ['fa.dehydration'], regions: ['abdomen', 'bottom'], text: 'Blood or mucus in the stool, or diarrhoea lasting more than 5 days' },
  { id: 'rf.sore-throat-severe', tier: 'h24', firstAid: [], regions: ['head'], text: 'Severe sore throat with drooling, or trouble swallowing fluids' },
  { id: 'rf.ear-pain-severe', tier: 'h24', firstAid: [], regions: ['head'], text: 'Ear pain with discharge, hearing loss, or pain behind the ear' },
  { id: 'rf.eye-pain-light', tier: 'h24', firstAid: [], regions: ['head'], text: 'Eye pain with light sensitivity, blurred vision, or sudden floaters' },
  { id: 'rf.cough-fever-child', tier: 'h24', firstAid: [], regions: ['chest'], text: 'Child with cough, fast breathing, or chest pulling in when breathing' },
  { id: 'rf.pregnancy-pain', tier: 'h24', firstAid: ['fa.pregnancy'], regions: ['pelvis', 'abdomen'], text: 'Pregnant with pain, burning when passing urine, or reduced baby movement' },
  { id: 'rf.urine-burning-persistent', tier: 'h24', firstAid: [], regions: ['pelvis', 'abdomen'], text: 'Burning when passing urine for more than 2 days, or with fever' },

  // Level 20 — contact a doctor during office hours
  { id: 'rf.cough-2-weeks', tier: 'office', firstAid: [], regions: ['chest'], text: 'Cough lasting more than 2 weeks' },
  { id: 'rf.lump-new', tier: 'office', firstAid: [], regions: ['chest', 'skin', 'pelvis'], text: 'New lump, swelling or sore that has not healed in 2 weeks' },
  { id: 'rf.lasting-pain', tier: 'office', firstAid: [], text: 'Any symptom lasting more than 2 weeks without improving' },
  { id: 'rf.weight-loss', tier: 'office', firstAid: [], text: 'Losing weight without trying, or loss of appetite for weeks' },
  { id: 'rf.period-missed', tier: 'office', firstAid: [], regions: ['pelvis'], text: 'Missed or very irregular periods, or bleeding between periods' },
  { id: 'rf.mood-weeks', tier: 'office', firstAid: ['fa.mental-health'], text: 'Low mood, worry or poor sleep most days for 2 weeks or more' },
  { id: 'rf.back-pain-weeks', tier: 'office', firstAid: ['fa.back'], regions: ['back'], text: 'Back or joint pain lasting weeks, or morning stiffness' },
];

export const redFlagById = (id: string): RedFlag | undefined => RED_FLAGS.find((f) => f.id === id);

export interface FirstAidVariant {
  title?: string;
  steps?: string[];
}

export interface FirstAidGuide {
  id: string;
  title: string;
  steps: string[];
  /* Age-specific rewrites selected from the patient's age band. */
  ageVariants?: Partial<Record<AgeBand, FirstAidVariant>>;
  /* Hide this guide outside this month range (e.g. newborn-only). */
  minAgeMonths?: number;
  maxAgeMonths?: number;
}

export const FIRST_AID: FirstAidGuide[] = [
  { id: 'fa.cpr', title: 'CPR — not breathing', steps: [
    'Shout for help and call 108 / 112 immediately, put the phone on speaker.',
    'Lay the person flat on a firm surface.',
    'Push hard and fast in the centre of the chest — about 100–120 pushes a minute, 5–6 cm deep.',
    'Do not stop until the person breathes, moves, or an ambulance team takes over.',
  ], ageVariants: {
    neonate: { title: 'CPR — newborn baby', steps: [
      'Call 108 / 112 and put the phone on speaker before you start.',
      'Give 5 gentle rescue breaths first: cover mouth and nose with your lips, puff for 1 second each.',
      'Then 2-finger compressions in the centre of the chest (just below the nipple line), about 1.5 inches deep, 100–120 a minute.',
      '5 breaths then 30 compressions (two rescuers: 15 and 2). Stop only when the baby breathes, moves, or help takes over.',
    ] },
    infant: { title: 'CPR — baby under 1 year', steps: [
      'Call 108 / 112 and put the phone on speaker before you start.',
      'Give 5 gentle rescue breaths first: cover mouth and nose, small puffs for 1 second each.',
      'Then 2-finger compressions in the centre of the chest, about 1.5 inches deep, 100–120 a minute.',
      '30 compressions then 2 breaths (two rescuers: 15 and 2). Continue until the baby breathes, moves, or help takes over.',
    ] },
    child: { title: 'CPR — child (1 year to puberty)', steps: [
      'Call 108 / 112 immediately, phone on speaker.',
      'Lay the child flat on a firm surface and give 5 rescue breaths.',
      'Push in the centre of the chest with one or two hands — about one-third of chest depth, 100–120 a minute.',
      '30 compressions then 2 breaths. Do not stop until the child breathes, moves, or help takes over.',
    ] },
  } },
  { id: 'fa.recovery-position', title: 'Unconscious but breathing', steps: [
    'Call 108 / 112. Check the person is breathing by looking, listening and feeling for 10 seconds.',
    'Turn them onto their side, mouth pointing down, so vomit can drain out.',
    'Bend the top knee forward to keep the position stable.',
    'Keep them warm and stay with them until help arrives. Never give food or drink.',
  ] },
  { id: 'fa.seizure', title: 'Seizure (convulsion)', steps: [
    'Stay calm and time the seizure. Call 108 / 112 if it lasts more than 5 minutes or repeats.',
    'Clear hard or sharp objects away and cushion the head.',
    'Do NOT hold the person down and do NOT put anything in the mouth.',
    'After it stops, turn them on their side and keep them warm until fully awake.',
  ] },
  { id: 'fa.stroke', title: 'Stroke — act FAST', steps: [
    'F — Face: ask them to smile; is one side drooping?',
    'A — Arms: can they raise both arms and hold them up?',
    'S — Speech: is it slurred, or are words mixed up?',
    'T — Time: note the exact time symptoms started and call 108 / 112 at once. Do not give food, drink or aspirin.',
  ] },
  { id: 'fa.bleeding', title: 'Severe bleeding', steps: [
    'Press firmly on the wound with a clean cloth or your hand — do not lift to look.',
    'Add more cloth on top if it soaks through; keep pressing for a full 10 minutes.',
    'Raise the injured part above heart level if you can, without moving a broken bone.',
    'Call 108 / 112. If bleeding still spurts, press harder on the pressure point above the wound.',
  ] },
  { id: 'fa.choking', title: 'Choking', steps: [
    'If they can cough, encourage coughing. If they cannot breathe or speak, act now.',
    'Adults and children over 1 year: give 5 firm back blows between the shoulder blades.',
    'Then 5 abdominal thrusts (Heimlich). Repeat 5 and 5 until the object comes out.',
    'Babies under 1 year: 5 back blows, then 5 chest thrusts with two fingers. Call 108 / 112.',
  ], ageVariants: {
    neonate: { title: 'Choking — newborn baby', steps: [
      'If the baby can cough or cry, encourage it — do not slap the back while coughing.',
      'If silent or cannot cry: place face-down along your forearm, head lower than chest.',
      'Give 5 firm back blows between the shoulder blades with the heel of your hand.',
      'Then turn face-up and give 5 chest thrusts with two fingers in the centre of the chest. Call 108 / 112 and repeat.',
    ] },
    infant: { title: 'Choking — baby under 1 year', steps: [
      'If the baby can cough or cry, encourage it — do not hit the back while coughing.',
      'If silent or blue: place face-down along your forearm, head lower than the chest.',
      'Give 5 firm back blows between the shoulder blades.',
      'Turn face-up, give 5 chest thrusts with two fingers. Repeat 5 and 5. Call 108 / 112 — never abdominal thrusts under 1 year.',
    ] },
    child: { title: 'Choking — child over 1 year', steps: [
      'If they can cough, encourage coughing. If silent or cannot speak, act now.',
      'Give 5 firm back blows between the shoulder blades, leaning the child forward.',
      'Then 5 abdominal thrusts (Heimlich) — stand behind, fist above the navel.',
      'Repeat 5 and 5 until the object comes out. Call 108 / 112 if it does not clear quickly.',
    ] },
    teen: { title: 'Choking — adult technique', steps: [
      'If they can cough, encourage coughing. If they cannot breathe or speak, act now.',
      'Give 5 firm back blows between the shoulder blades.',
      'Then 5 abdominal thrusts (Heimlich). Repeat 5 and 5 until the object comes out.',
      'Call 108 / 112 if the object does not clear. If they go limp, start CPR.',
    ] },
    adult: { title: 'Choking — adult technique', steps: [
      'If they can cough, encourage coughing. If they cannot breathe or speak, act now.',
      'Give 5 firm back blows between the shoulder blades.',
      'Then 5 abdominal thrusts (Heimlich). Repeat 5 and 5 until the object comes out.',
      'Call 108 / 112 if the object does not clear. If they go limp, start CPR.',
    ] },
    senior: { title: 'Choking — adult technique', steps: [
      'If they can cough, encourage coughing. If they cannot breathe or speak, act now.',
      'Give 5 firm back blows between the shoulder blades.',
      'Then 5 abdominal thrusts (Heimlich) — use gentler thrusts if frail. Repeat 5 and 5.',
      'Call 108 / 112 if the object does not clear. If they go limp, start CPR.',
    ] },
  } },
  { id: 'fa.anaphylaxis', title: 'Severe allergic reaction', steps: [
    'Call 108 / 112 immediately — this can become fatal within minutes.',
    'If an adrenaline auto-injector is available, use it in the outer thigh.',
    'Lay the person flat with legs raised; let them sit up only if breathing is hard.',
    'If they stop breathing, start CPR. A second dose can be given after 5 minutes if symptoms continue.',
  ] },
  { id: 'fa.heart-attack', title: 'Suspected heart attack', steps: [
    'Call 108 / 112 now and say “chest pain, possible heart attack”.',
    'Sit the person up, leaning slightly forward, and loosen tight clothing.',
    'If not allergic and not bleeding, let them chew one 325 mg aspirin (or 4 × 75 mg).',
    'Do not let them walk or drive. Be ready to start CPR if they collapse.',
  ], ageVariants: {
    child: { title: 'Chest pain — child (rare)', steps: [
      'Call 108 / 112 — severe chest pain in a child always needs urgent assessment.',
      'Sit them upright, calm, and loosen tight clothing around the neck and chest.',
      'Do NOT give aspirin unless a doctor has told you to.',
      'Note any link to sport, injury, fever or breathing difficulty for the doctor.',
    ] },
    teen: { title: 'Chest pain — teenager', steps: [
      'Call 108 / 112 if pain is severe, with sweating, nausea or pain down the arm.',
      'Sit upright and slightly forward; loosen tight clothing.',
      'Do not give aspirin unless sure there is no allergy, bleeding, or a doctor has advised it.',
      'Do not let them walk or drive. Be ready to start CPR if they collapse.',
    ] },
  } },
  { id: 'fa.poisoning', title: 'Swallowed poison or overdose', steps: [
    'Call 108 / 112 or the poison helpline straight away — have the container in your hand.',
    'Do NOT make the person vomit and do not give milk or oil.',
    'If the lips or mouth are burnt, wipe them and give small sips of water or milk.',
    'If the person is drowsy, turn them on their side. Take the container or tablets to hospital.',
  ] },
  { id: 'fa.breathing', title: 'Trouble breathing', steps: [
    'Sit the person upright and slightly forward — never lay them flat.',
    'Loosen clothing at the neck and chest, and open windows for fresh air.',
    'Give their own inhaler if prescribed (2 puffs, repeat after 4 minutes if needed).',
    'Call 108 / 112 if lips turn blue, they cannot speak a full sentence, or they become sleepy.',
  ] },
  { id: 'fa.newborn', title: 'Sick baby under 3 months', maxAgeMonths: 3, steps: [
    'Any fever, poor feeding, or unusual sleepiness in a baby under 3 months is an emergency — go to hospital now.',
    'Keep the baby warm, skin-to-skin, and continue breastfeeding or cup-feeding if able.',
    'Never give paracetamol or other medicines without a doctor’s dose.',
    'Note how many wet nappies and feeds in the last 24 hours to tell the doctor.',
  ] },
  { id: 'fa.mental-health', title: 'Mental health crisis', steps: [
    'Stay with the person and remove access to sharp objects, medicines, ropes or pesticides.',
    'Listen without judging. Ask directly about thoughts of self-harm — it helps, it does not cause harm.',
    'Call Tele-MANAS 14416 (24×7, free) or take them to the nearest hospital/district mental health unit.',
    'If there is an immediate danger to life, call 108 / 112 and do not leave them alone.',
  ] },
  { id: 'fa.head-injury', title: 'Head injury', steps: [
    'Keep the person still and apply a cold pack wrapped in cloth to the swelling.',
    'Watch for vomiting, drowsiness, confusion, unequal pupils, or clear fluid from nose or ear.',
    'Do not give painkillers that thin blood (aspirin) and do not let them sleep without checks.',
    'Any of the warning signs above means hospital now — call 108 / 112.',
  ] },
  { id: 'fa.abdominal', title: 'Severe belly pain', steps: [
    'Stop all food and drink — the person may need surgery.',
    'Do not give painkillers, antacids or laxatives; they hide the signs a doctor needs.',
    'Let them lie still with knees bent, and keep a bowl ready in case of vomiting.',
    'Go to hospital now if the belly is hard, tender all over, or pain is severe.',
  ] },
  { id: 'fa.dehydration', title: 'Dehydration — rehydration', steps: [
    'Give small sips of ORS (oral rehydration solution) every 1–2 minutes; a child should take about 1 teaspoon at a time.',
    'Homemade ORS: 1 litre clean water + 6 level teaspoons sugar + ½ teaspoon salt. Discard after 24 hours.',
    'Keep breastfeeding or feeding normally — continue even if the person vomits; wait 10 minutes and start again slowly.',
    'Go to hospital if there is no urine for 8 hours, sunken eyes, no tears, or the person is drowsy.',
  ], ageVariants: {
    neonate: { title: 'Dehydration — newborn', steps: [
      'Call or go to hospital now — a dehydrated newborn can worsen within hours.',
      'Give expressed breast milk by spoon or cup (not a bottle if very sleepy). Often: 1 small spoon every 5 minutes.',
      'Keep skin-to-skin to maintain warmth and encourage feeding.',
      'Count wet nappies: fewer than 6 in 24 hours, sunken eyes or fontanelle dipping means emergency.',
    ] },
    infant: { title: 'Dehydration — baby under 1 year', steps: [
      'Give ORS by spoon or syringe: 1 teaspoon every 1–2 minutes — do not flood the mouth.',
      'Continue breastfeeding on demand — more frequent, shorter feeds if needed.',
      'Homemade ORS: 1 litre clean water + 6 level teaspoons sugar + ½ teaspoon salt. Discard after 24 hours.',
      'Go to hospital for fewer wet nappies, sunken eyes, no tears, or a baby who is sleepy and not drinking.',
    ] },
    child: { title: 'Dehydration — child', steps: [
      'Give ORS in small sips every 1–2 minutes — about 1 teaspoon at a time for younger children.',
      'Homemade ORS: 1 litre clean water + 6 level teaspoons sugar + ½ teaspoon salt. Discard after 24 hours.',
      'Keep normal feeds; zinc (if advised by your health worker) for 14 days after diarrhoea under 5 years.',
      'Go to hospital for no urine for 8 hours, sunken eyes, no tears, or a child who is drowsy and not drinking.',
    ] },
  } },
  { id: 'fa.burn', title: 'Burn or scald', steps: [
    'Move away from the heat source at once and remove clothing near the burn unless it is stuck to skin.',
    'Cool the burn with cool or lukewarm running water for 20 minutes. Never use ice, butter or toothpaste.',
    'Cover loosely with a clean, non-fluffy cloth or cling film; do not burst blisters.',
    'Go to hospital for burns bigger than the palm, or any burn on the face, hands, feet, joints or genitals.',
  ] },
  { id: 'fa.fracture', title: 'Suspected broken bone', steps: [
    'Keep the limb still in the position you found it. Do not try to straighten it.',
    'Support it with a splint, rolled cloth or magazine, and a sling for arms.',
    'Apply a cold pack wrapped in cloth for 15 minutes to reduce swelling. Do not apply heat.',
    'Go to hospital for an X-ray. Do not give food or drink in case surgery is needed.',
  ] },
  { id: 'fa.eye-chemical', title: 'Chemical or object in the eye', steps: [
    'Rinse the eye immediately with clean, cool running water for 15–20 minutes, holding the eyelid open.',
    'Rinse from the inner corner outward so the chemical does not run into the other eye.',
    'Remove contact lenses if present. Do not rub the eye or pull out an embedded object.',
    'Go to hospital straight away, taking the container or chemical name with you.',
  ] },
  { id: 'fa.snake-bite', title: 'Snake or animal bite', steps: [
    'Keep the person calm and lying still — movement spreads the venom faster.',
    'Keep the bitten limb below heart level and remove rings, bangles and tight clothing.',
    'Do NOT cut, suck, tie a tourniquet, or apply ice. Wash gently and cover with a clean cloth.',
    'Get to hospital immediately. Try to remember the snake’s appearance; do not chase or kill it.',
  ] },
  { id: 'fa.wound', title: 'Cuts, wounds and bites', steps: [
    'Wash your hands, then rinse the wound under clean running water for 5 minutes.',
    'Clean around it with soap; remove only easily reached dirt. Do not dig into the wound.',
    'Cover with a clean dressing and press firmly if it bleeds.',
    'Get a tetanus injection if the wound is dirty, deep, or from an animal bite, and watch for redness, pus or fever.',
  ] },
  { id: 'fa.pregnancy', title: 'Pregnancy warning signs', steps: [
    'Lie on the left side and rest; count baby movements for one hour after a meal.',
    'Drink water and eat something small if you feel faint.',
    'Go to hospital immediately for bleeding, severe belly pain, fit, blurred vision, swelling of face or hands, or reduced baby movement.',
    'Carry your MCP (mother-child protection) card with all check-up dates.',
  ] },
  { id: 'fa.fever', title: 'Fever at home', steps: [
    'Give plenty of fluids — water, ORS, soup, breast milk for babies — in small frequent amounts.',
    'Keep clothing light and sponge the forehead, neck and armpits with lukewarm water.',
    'Paracetamol may be given by weight (10–15 mg/kg per dose, up to 4 times a day) unless a doctor says otherwise.',
    'Never give aspirin to children. See a doctor if fever lasts more than 3 days or comes with a rash, stiff neck or drowsiness.',
  ], ageVariants: {
    neonate: { title: 'Fever — baby under 3 months', steps: [
      'Fever 38°C (100.4°F) or higher under 3 months is an emergency — go to hospital now.',
      'Keep the baby warm, skin-to-skin; undress to one light layer only.',
      'Continue breast or cup feeds in small amounts if alert.',
      'Do not give paracetamol without a doctor’s dose. Note feeds and wet nappies for the doctor.',
    ] },
    infant: { title: 'Fever — baby under 1 year', steps: [
      'Give fluids often — breast milk, ORS or water in small frequent sips.',
      'Keep clothing light; sponge with lukewarm water (never cold water or ice).',
      'Paracetamol by weight only if the doctor or health worker has advised it — never aspirin.',
      'Go to hospital if fever is 38°C+ under 3 months, lasts over 3 days, or baby is drowsy, floppy or not feeding.',
    ] },
    child: { title: 'Fever — child', steps: [
      'Give plenty of fluids — water, ORS, soup; keep meals light.',
      'Light clothing; sponge forehead, neck and armpits with lukewarm water.',
      'Paracetamol by weight (10–15 mg/kg, up to 4 doses/24 h) if advised — never aspirin for children.',
      'See a doctor if fever lasts over 3 days, or comes with rash, stiff neck, fits, or a child who is drowsy or not drinking.',
    ] },
    senior: { title: 'Fever — older adult', steps: [
      'Give fluids in small, frequent amounts; rest in a cool, airy room.',
      'Sponge with lukewarm water and dress in light clothing.',
      'Paracetamol only if not allergic and no kidney problems — check other medicines with a pharmacist.',
      'Fever in an older adult often means infection with few obvious signs — contact a doctor the same day.',
    ] },
  } },
  { id: 'fa.hypoglycemia', title: 'Low blood sugar', steps: [
    'If awake and able to swallow: give 15 g of fast sugar — 3 teaspoons sugar in water, ½ cup fruit juice, or 3 glucose biscuits.',
    'Recheck the blood sugar after 15 minutes; repeat the sugar if still below 70 mg/dL.',
    'Once normal, give a small snack of roti, rice or milk to keep it steady.',
    'If the person is unconscious, give nothing by mouth — put sugar under the tongue and call 108 / 112.',
  ] },
  { id: 'fa.heat', title: 'Heat exhaustion and heat stroke', steps: [
    'Move the person to shade and loosen clothing. Remove extra layers.',
    'Cool rapidly — wet cloths on neck, armpits and groin, fan continuously, sponge with cool water.',
    'Give cool fluids with salt and sugar if fully awake (ORS is ideal).',
    'Heat stroke (hot dry skin, confusion, fainting) is an emergency — call 108 / 112 while cooling.',
  ] },
  { id: 'fa.testicular', title: 'Sudden testicle pain', steps: [
    'Go to hospital immediately — sudden severe pain can mean the testicle has twisted and needs surgery within hours.',
    'Do not give painkillers that hide the pain, and do not apply heat or massage.',
    'Support the scrotum with a folded cloth while travelling.',
    'Do not wait to see if it settles; the window to save the testicle is about 6 hours.',
  ] },
  { id: 'fa.asthma', title: 'Asthma attack', steps: [
    'Sit upright, stay calm and take 2 puffs of a reliever inhaler (salbutamol) with a spacer.',
    'Take 1 puff every 30–60 seconds up to 10 puffs if breathing is still difficult.',
    'Repeat the inhaler every 20 minutes if needed while arranging care.',
    'Call 108 / 112 if there is no relief, lips turn blue, or speaking is difficult.',
  ] },
  { id: 'fa.back', title: 'Back and joint pain', steps: [
    'Keep moving gently — short walks are better than complete bed rest.',
    'Use a cold pack for the first 2 days, then a warm pack, wrapped in cloth for 15 minutes.',
    'Avoid lifting, bending and long sitting. Sleep with a small pillow under the knees.',
    'See a doctor if there is numbness in the groin or legs, weakness, or loss of bladder control.',
  ] },
  { id: 'fa.nosebleed', title: 'Nosebleed', steps: [
    'Sit upright and lean forward — not backwards — so blood does not run down the throat.',
    'Pinch the soft part of the nose firmly for a full 10 minutes without releasing.',
    'Spit out any blood; do not swallow it. Apply a cold pack to the bridge of the nose.',
    'Go to hospital if bleeding lasts over 20 minutes, is very heavy, or follows a head injury.',
  ] },
  { id: 'fa.cough-care', title: 'Cough and cold at home', steps: [
    'Give warm fluids — water, soup, tea with honey (honey only for children over 1 year).',
    'Do steam inhalation twice a day: sit with the face over a bowl of hot water with a cloth over the head.',
    'Saline nose drops or plain salt water rinse help a blocked nose at any age.',
    'Antibiotics are not needed for ordinary colds. See a doctor for fast breathing, chest pain, or a cough over 2 weeks.',
  ] },
  { id: 'fa.diarrhea-care', title: 'Diarrhoea at home', steps: [
    'Start ORS after every loose stool — about ½ cup for a child, 1 cup for an adult.',
    'Zinc supplement for 14 days if the child is under 5 years (as advised by your health worker).',
    'Continue normal food; avoid sugary drinks, tea and very oily food.',
    'Go to hospital for blood in stool, no urine for 8 hours, or a child who is drowsy and not drinking.',
  ] },
  { id: 'fa.vomit-care', title: 'Vomiting at home', steps: [
    'Stop food for 1 hour, then give 1 teaspoon of ORS or water every 5 minutes.',
    'Increase slowly to small sips if it stays down. Breastfeed babies normally.',
    'Avoid fatty, spicy or very sweet food for a day; start with rice, curd, banana, toast.',
    'Go to hospital if there is blood, green vomit, a hard belly, or signs of dehydration.',
  ] },
  { id: 'fa.sprain', title: 'Sprain or strain', steps: [
    'Rest the joint and avoid weight-bearing for the first 24–48 hours.',
    'Apply a cold pack wrapped in cloth for 15 minutes every 2–3 hours.',
    'Wrap with a crepe bandage firmly but not tightly — fingers or toes should stay pink and warm.',
    'Elevate the limb. Get an X-ray if pain is severe, or the joint cannot take any weight.',
  ] },
  { id: 'fa.skin-care', title: 'Itchy, dry or infected skin', steps: [
    'Wash gently with plain water and mild soap; pat dry rather than rubbing.',
    'Apply a thin layer of coconut oil or petroleum jelly for dryness, or the prescribed cream for rash.',
    'Keep nails short and avoid scratching; a cool cloth eases itching.',
    'See a doctor for spreading redness, pus, blistering, fever, or a rash that does not settle in a week.',
  ] },
  { id: 'fa.urine-care', title: 'Burning or frequent urination', steps: [
    'Drink 2–3 litres of water a day unless told to restrict fluids.',
    'Do not hold urine; pass urine every 2–3 hours and after intercourse.',
    'Keep the genital area clean and dry, and wipe from front to back.',
    'See a doctor for fever, back pain, blood in urine, or symptoms lasting more than 2 days.',
  ] },
  { id: 'fa.menstrual', title: 'Period pain and bleeding', steps: [
    'Use a warm water bottle on the lower belly and take rest.',
    'Paracetamol or mefenamic acid after food can ease cramps, if not allergic.',
    'Change sanitary pads every 4–6 hours and keep a record of bleeding days.',
    'See a doctor if bleeding soaks a pad every hour, lasts over 7 days, or pain stops normal activity.',
  ] },
  { id: 'fa.mood-care', title: 'Low mood and stress at home', steps: [
    'Keep a regular sleep and meal routine, and get 20–30 minutes of daylight activity daily.',
    'Share how you feel with one trusted person; speaking about it reduces the load.',
    'Avoid alcohol and tobacco — they make anxiety and sleep worse.',
    'Call Tele-MANAS 14416 (free, 24×7) for counselling support if it continues for 2 weeks or more.',
  ] },
];

export const firstAidById = (id: string): FirstAidGuide | undefined => FIRST_AID.find((f) => f.id === id);

/* Extra questions asked once for the whole assessment. */
export const SECONDARY_QUESTIONS = [
  { id: 'fever', label: 'Fever (38°C / 100.4°F or higher)', redFlag: 'rf.fever-3-days' },
  { id: 'pregnant', label: 'Pregnant or possibly pregnant', redFlag: 'rf.pregnancy-pain' },
  { id: 'diabetes', label: 'Living with diabetes', redFlag: 'rf.sugar-abnormal' },
  { id: 'infant', label: 'Baby under 3 months old', redFlag: 'rf.newborn-ill' },
] as const;

export type SecondaryQuestionId = (typeof SECONDARY_QUESTIONS)[number]['id'];

