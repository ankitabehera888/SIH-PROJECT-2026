import fs from 'node:fs';

const bp = JSON.parse(fs.readFileSync(process.env.TEMP + '/opencode/webmd-bodyparts.json', 'utf8'));

const mapRegion = (name, id) => {
  if (name === 'head' || id === 9 || id === 905) return 'head';
  if (name === 'neck') return 'head';
  if (name === 'chest') return 'chest';
  if (name === 'abdomen') return 'abdomen';
  if (name === 'pelvis') return 'pelvis';
  if (name && name.startsWith('arm')) return 'arms';
  if (name && name.startsWith('leg')) return 'legs';
  if (name === 'back') return 'back';
  if (name === 'buttock') return 'bottom';
  if (name === 'skin') return 'skin';
  if (name === 'general') return 'general';
  return null;
};

const out = {};
const zoom = {};

for (const key of Object.keys(bp)) {
  if (!/^(front|back)-[mf]$/.test(key)) continue;
  const side = key.startsWith('front') ? 'front' : 'back';

  out[key] = bp[key]
    .filter((p) => p.path && mapRegion(p.name, p.id))
    .map((p) => ({
      name: p.name,
      id: p.id,
      region: mapRegion(p.name, p.id),
      path: p.path,
      transform: p.transform || '',
      class: p.class || '',
      hoverBoth: p.hoverBoth || '',
      width: p.width || 0,
      left: p.left || 0,
      top: p.top || 0,
      depth: p.depth || 0,
      subs: (p.parts || [])
        .filter((s) => s.path)
        .map((s) => ({
          name: s.name,
          id: s.id,
          title: s.title || s.name,
          parentPart: s.parentPart || p.title || p.name,
          region: mapRegion(s.parentPart, s.id) || mapRegion(p.name, p.id),
          path: s.path,
          transform: s.transform || '',
        })),
    }));

  zoom[key] = out[key]
    .filter((p) => p.subs.length > 1 || (p.subs.length === 1 && p.subs[0].name !== p.name))
    .map((p) => ({
      name: p.name,
      id: p.id,
      region: p.region,
      width: p.width,
      left: p.left,
      top: p.top,
      subs: p.subs,
    }));

  console.log(key, 'major', out[key].length, 'zoomable', zoom[key].map((z) => z.name).join(','));
  for (const z of zoom[key]) console.log(' ', z.name, 'subs', z.subs.map((s) => s.title).join(' | '));
}

const ts = `/* WebMD symptom checker body-map hit paths + zoom targets.
   Extracted from symptoms.webmd.com (symptom_checker_beta). */
export interface WebMdSubPart {
  name: string;
  id: number;
  title: string;
  parentPart: string;
  region: string;
  path: string;
  transform: string;
}

export interface WebMdPart {
  name: string;
  id: number;
  region: string;
  path: string;
  transform: string;
  class: string;
  hoverBoth: string;
  width: number;
  left: number;
  top: number;
  depth: number;
  subs: WebMdSubPart[];
}

export interface WebMdZoomTarget {
  name: string;
  id: number;
  region: string;
  width: number;
  left: number;
  top: number;
  subs: WebMdSubPart[];
}

export const WEBMD_VIEWBOX = '0 0 310 385';
export const WEBMD_ZOOM_VIEWBOX_F = '0 0 190 385';
export const WEBMD_ZOOM_VIEWBOX_M = '0 0 190 345';

export const WEBMD_BODY_PARTS: Record<string, WebMdPart[]> = ${JSON.stringify(out, null, 2)};

export const WEBMD_ZOOM: Record<string, WebMdZoomTarget[]> = ${JSON.stringify(zoom, null, 2)};

export const webmdAsset = (side: 'front' | 'back', gender: 'm' | 'f'): string =>
  \`/body/\${side}-\${gender}.webp\`;
`;

fs.writeFileSync('D:/shaay/shaay/src/mock-data/webmdBodyParts.ts', ts);
console.log('written', ts.length);
