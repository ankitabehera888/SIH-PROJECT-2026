import type { Audience, BodyType, Gender, ViewSide } from './symptomCheckerTriage';

/* ---------------------------------------------------------------------------
   Interactive body map.
   The scanned tool draws six bitmaps (male/female/child × front/back) and puts
   transparent rectangles over each body area ("arms": "46 105 233 350", ...).
   SAHAAY ships the same idea as vector shapes instead of bitmaps: crisp at any
   size, theme-aware, zero network requests and no third-party artwork.
   Coordinates live in a 200 × 420 viewBox for every model.
   --------------------------------------------------------------------------- */

export interface BodyRegion {
  id: string;
  label: string;
  caption: string;
  blurb: string;
  keywords: string[];
  /* Areas that only exist on certain models / views — mirrors the scan:
     'pregnant' is female-front only, 'back'/'bottom' are back-view only. */
  models?: BodyType[];
  sides?: ViewSide[];
  accent: string;
}

export const BODY_REGIONS: BodyRegion[] = [
  { id: 'head', label: 'Head, face, eyes, ears & throat', caption: 'Head', accent: '#0EA5C9',
    blurb: 'Headache, eye and ear problems, nose, mouth, throat, teeth, hair', keywords: ['head', 'face', 'eye', 'ear', 'nose', 'throat', 'tooth', 'mouth'] },
  { id: 'chest', label: 'Chest & breathing', caption: 'Chest', accent: '#e11d48',
    blurb: 'Cough, chest pain, breathing trouble, heart, breast, ribs', keywords: ['chest', 'heart', 'breath', 'lung', 'cough', 'breast'] },
  { id: 'abdomen', label: 'Abdomen & digestion', caption: 'Abdomen', accent: '#f59e0b',
    blurb: 'Stomach pain, vomiting, loose motions, constipation, appetite', keywords: ['abdomen', 'stomach', 'digestion', 'vomit', 'diarrhoea'] },
  { id: 'back', label: 'Back & spine', caption: 'Back', accent: '#7C5CFF', sides: ['back'],
    blurb: 'Backache, neck stiffness, spine and muscle pain', keywords: ['back', 'spine', 'neck', 'shoulder blade'] },
  { id: 'pelvis', label: 'Pelvis, urinary & sexual health', caption: 'Pelvis', accent: '#17B366',
    blurb: 'Periods, pregnancy, passing urine, genital problems', keywords: ['pelvis', 'urine', 'period', 'pregnancy', 'genital'] },
  { id: 'bottom', label: 'Bottoms & bowels', caption: 'Bottom', accent: '#446155', sides: ['back'],
    blurb: 'Piles, rectal bleeding, pain on passing stool, itching', keywords: ['bottom', 'rectal', 'piles', 'anus', 'stool'] },
  { id: 'arms', label: 'Arms, hands & shoulders', caption: 'Arms', accent: '#0284c7',
    blurb: 'Shoulder, elbow, wrist, hand, finger injuries and pain', keywords: ['arm', 'hand', 'wrist', 'elbow', 'finger', 'shoulder'] },
  { id: 'legs', label: 'Legs, knees & feet', caption: 'Legs', accent: '#ea580c',
    blurb: 'Hip, knee, ankle, foot, toe pain, swelling and injuries', keywords: ['leg', 'knee', 'foot', 'ankle', 'toe', 'hip'] },
  { id: 'skin', label: 'Skin, hair & nails', caption: 'Skin', accent: '#A9EFC6',
    blurb: 'Rash, itching, wounds, burns, bites, boils, lumps', keywords: ['skin', 'rash', 'itch', 'wound', 'burn', 'bite'] },
  { id: 'general', label: 'Whole body & general symptoms', caption: 'Other Symptoms', accent: '#5533DB',
    blurb: 'Fever, tiredness, sleep, mood, dizziness, weight change', keywords: ['fever', 'tired', 'sleep', 'mood', 'dizzy', 'general'] },
];

export const regionById = (id: string): BodyRegion | undefined => BODY_REGIONS.find((r) => r.id === id);
export const regionsForModel = (model: BodyType, side: ViewSide): BodyRegion[] =>
  BODY_REGIONS.filter((r) => (!r.models || r.models.includes(model)) && (!r.sides || r.sides.includes(side)));

/* ---- Shape primitives -------------------------------------------------- */
export type Shape =
  | { kind: 'rect'; x: number; y: number; w: number; h: number; rx: number }
  | { kind: 'ellipse'; cx: number; cy: number; rx: number; ry: number }
  | { kind: 'poly'; points: string };

export interface ModelView {
  /* Decorative mannequin — drawn once as a single silhouette. */
  silhouette: Shape[];
  /* Clickable areas, mirrored left/right where the body is symmetric.
     `mirror: true` re-draws the same shapes flipped about the centre line. */
  hotspots: Record<string, { shapes: Shape[]; mirror?: boolean }>;
}

const V = { w: 200, h: 420 };

/* Left-side limbs are authored once and mirrored for the right side. */
const mirrorShape = (s: Shape): Shape => {
  if (s.kind === 'rect') return { ...s, x: V.w - s.x - s.w };
  if (s.kind === 'ellipse') return { ...s, cx: V.w - s.cx };
  const flipped = s.points.split(' ').map((pair) => {
    const [x, y] = pair.split(',').map(Number);
    return `${V.w - x},${y}`;
  }).join(' ');
  return { kind: 'poly', points: flipped };
};

export const expandShapes = (shapes: Shape[], mirror?: boolean): Shape[] =>
  mirror ? [...shapes, ...shapes.map(mirrorShape)] : shapes;
const HEAD_FRONT: Shape[] = [{ kind: 'ellipse', cx: 100, cy: 40, rx: 25, ry: 30 }, { kind: 'rect', x: 90, y: 60, w: 20, h: 20, rx: 6 }];
const HEAD_BACK: Shape[] = [{ kind: 'ellipse', cx: 100, cy: 40, rx: 26, ry: 31 }, { kind: 'rect', x: 90, y: 58, w: 20, h: 24, rx: 6 }];
const ARM_L: Shape[] = [{ kind: 'rect', x: 40, y: 84, w: 18, h: 152, rx: 9 }];
const LEG_L: Shape[] = [{ kind: 'rect', x: 78, y: 188, w: 20, h: 200, rx: 10 }];
const MALE_BODY: Shape[] = [
  { kind: 'ellipse', cx: 100, cy: 40, rx: 23, ry: 28 },
  { kind: 'rect', x: 91, y: 60, w: 18, h: 18, rx: 6 },
  { kind: 'rect', x: 64, y: 74, w: 72, h: 120, rx: 28 },
  { kind: 'rect', x: 40, y: 84, w: 18, h: 152, rx: 9 }, { kind: 'rect', x: 142, y: 84, w: 18, h: 152, rx: 9 },
  { kind: 'rect', x: 60, y: 180, w: 80, h: 40, rx: 18 },
  { kind: 'rect', x: 78, y: 188, w: 20, h: 200, rx: 10 }, { kind: 'rect', x: 102, y: 188, w: 20, h: 200, rx: 10 },
  { kind: 'rect', x: 76, y: 386, w: 24, h: 14, rx: 6 }, { kind: 'rect', x: 100, y: 386, w: 24, h: 14, rx: 6 },
];

export const MODEL_VIEWS: Record<BodyType, Record<ViewSide, ModelView>> = {
  male: {
    front: {
      silhouette: MALE_BODY,
      hotspots: {
        head: { shapes: HEAD_FRONT },
        chest: { shapes: [{ kind: 'rect', x: 64, y: 74, w: 72, h: 62, rx: 26 }] },
        abdomen: { shapes: [{ kind: 'rect', x: 64, y: 136, w: 72, h: 52, rx: 24 }] },
        pelvis: { shapes: [{ kind: 'rect', x: 60, y: 178, w: 80, h: 42, rx: 20 }] },
        arms: { shapes: ARM_L, mirror: true },
        legs: { shapes: LEG_L, mirror: true },
      },
    },
    back: {
      silhouette: MALE_BODY,
      hotspots: {
        head: { shapes: HEAD_BACK },
        back: { shapes: [{ kind: 'rect', x: 64, y: 74, w: 72, h: 114, rx: 26 }] },
        bottom: { shapes: [{ kind: 'rect', x: 60, y: 180, w: 80, h: 38, rx: 18 }] },
        arms: { shapes: ARM_L, mirror: true },
        legs: { shapes: LEG_L, mirror: true },
      },
    },
  },
  female: {
    front: {
      silhouette: [
        { kind: 'ellipse', cx: 100, cy: 42, rx: 27, ry: 34 },
        { kind: 'ellipse', cx: 100, cy: 38, rx: 22, ry: 27 },
        { kind: 'rect', x: 93, y: 60, w: 14, h: 18, rx: 5 },
        { kind: 'rect', x: 68, y: 74, w: 64, h: 66, rx: 26 },
        { kind: 'rect', x: 66, y: 132, w: 68, h: 50, rx: 24 },
        { kind: 'rect', x: 42, y: 84, w: 17, h: 150, rx: 8 }, { kind: 'rect', x: 141, y: 84, w: 17, h: 150, rx: 8 },
        { kind: 'rect', x: 58, y: 172, w: 84, h: 46, rx: 22 },
        { kind: 'rect', x: 74, y: 206, w: 22, h: 182, rx: 11 }, { kind: 'rect', x: 104, y: 206, w: 22, h: 182, rx: 11 },
        { kind: 'rect', x: 72, y: 384, w: 26, h: 14, rx: 6 }, { kind: 'rect', x: 102, y: 384, w: 26, h: 14, rx: 6 },
      ],
      hotspots: {
        head: { shapes: [{ kind: 'ellipse', cx: 100, cy: 38, rx: 24, ry: 30 }, { kind: 'rect', x: 91, y: 58, w: 18, h: 20, rx: 6 }] },
        chest: { shapes: [{ kind: 'rect', x: 68, y: 74, w: 64, h: 66, rx: 26 }] },
        abdomen: { shapes: [{ kind: 'rect', x: 66, y: 132, w: 68, h: 48, rx: 22 }] },
        pelvis: { shapes: [{ kind: 'rect', x: 58, y: 172, w: 84, h: 46, rx: 22 }] },
        arms: { shapes: [{ kind: 'rect', x: 42, y: 84, w: 17, h: 150, rx: 8 }], mirror: true },
        legs: { shapes: [{ kind: 'rect', x: 74, y: 206, w: 22, h: 182, rx: 11 }], mirror: true },
      },
    },
    back: {
      silhouette: [
        { kind: 'ellipse', cx: 100, cy: 42, rx: 27, ry: 34 },
        { kind: 'ellipse', cx: 100, cy: 38, rx: 22, ry: 27 },
        { kind: 'rect', x: 93, y: 60, w: 14, h: 18, rx: 5 },
        { kind: 'rect', x: 68, y: 74, w: 64, h: 120, rx: 28 },
        { kind: 'rect', x: 42, y: 84, w: 17, h: 150, rx: 8 }, { kind: 'rect', x: 141, y: 84, w: 17, h: 150, rx: 8 },
        { kind: 'rect', x: 58, y: 172, w: 84, h: 46, rx: 22 },
        { kind: 'rect', x: 74, y: 206, w: 22, h: 182, rx: 11 }, { kind: 'rect', x: 104, y: 206, w: 22, h: 182, rx: 11 },
        { kind: 'rect', x: 72, y: 384, w: 26, h: 14, rx: 6 }, { kind: 'rect', x: 102, y: 384, w: 26, h: 14, rx: 6 },
      ],
      hotspots: {
        head: { shapes: [{ kind: 'ellipse', cx: 100, cy: 38, rx: 25, ry: 31 }, { kind: 'rect', x: 91, y: 56, w: 18, h: 24, rx: 6 }] },
        back: { shapes: [{ kind: 'rect', x: 68, y: 74, w: 64, h: 116, rx: 26 }] },
        bottom: { shapes: [{ kind: 'rect', x: 58, y: 172, w: 84, h: 42, rx: 22 }] },
        arms: { shapes: [{ kind: 'rect', x: 42, y: 84, w: 17, h: 150, rx: 8 }], mirror: true },
        legs: { shapes: [{ kind: 'rect', x: 74, y: 206, w: 22, h: 182, rx: 11 }], mirror: true },
      },
    },
  },
};

export const BODY_CANVAS = { w: V.w, h: V.h };

export const BODY_MODELS: { id: BodyType; label: string; audience: Audience; hint: string; gender: Gender }[] = [
  { id: 'male', label: 'Man', audience: 'both', hint: 'Male — any age', gender: 'M' },
  { id: 'female', label: 'Woman', audience: 'both', hint: 'Female — any age', gender: 'F' },
];
