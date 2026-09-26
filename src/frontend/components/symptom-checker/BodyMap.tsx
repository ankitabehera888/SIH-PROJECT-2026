/* WebMD symptom-checker body map with region zoom.
   Exact artwork + hit paths from symptoms.webmd.com (symptom_checker_beta):
   front/back × male/female WebP under transparent SVG region overlays.
   Zoom matches WebMD: half viewBox, SVG width = part.width, scroll to (left, top).
   Click a major area → zoom to it → pick sub-parts (forehead, epigastric…).
   Sub-part pick keeps the parent region selected for the symptom list. */
import { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { RotateCw, ZoomOut } from 'lucide-react';
import { useLanguage } from '../../context/providers';
import { scT, scModelLabel } from '../../i18n/symptomChecker';
import { BODY_REGIONS, regionsForModel } from '../../../mock-data/symptomCheckerBody';
import {
  WEBMD_BODY_PARTS,
  WEBMD_VIEWBOX,
  WEBMD_ZOOM,
  WEBMD_ZOOM_VIEWBOX_F,
  WEBMD_ZOOM_VIEWBOX_M,
  webmdAsset,
  type WebMdPart,
  type WebMdSubPart,
  type WebMdZoomTarget,
} from '../../../mock-data/webmdBodyParts';
import { type BodyType, type ViewSide } from '../../../mock-data/symptomCheckerTriage';

interface BodyMapProps {
  model: BodyType;
  side: ViewSide;
  selectedRegions: string[];
  onSelectRegion: (regionId: string) => void;
  onToggleSide: () => void;
  onSelectSide?: (side: ViewSide) => void;
}

/* WebMD adult bitmaps exist for m/f only — always use that path. */
const genderOf = (model: BodyType): 'm' | 'f' => (model === 'male' ? 'm' : 'f');

/* Later in DOM paints on top. Lower number → earlier → behind.
   Keeps pelvis/legs/bottom under abdomen so navel clicks hit Abdomen. */
const Z_ORDER: Record<string, number> = {
  back: 0,
  bottom: 0,
  pelvis: 0,
  legs: 0,
  abdomen: 1,
  chest: 2,
  arms: 3,
  neck: 4,
  head: 5,
  skin: 6,
  general: 6,
};

const zRank = (part: WebMdPart): number => Z_ORDER[part.region] ?? 1;

export function BodyMap({
  model,
  side,
  selectedRegions,
  onSelectRegion,
  onToggleSide,
  onSelectSide,
}: BodyMapProps) {
  const { language, t } = useLanguage();
  const L = (source: string, params?: Record<string, string | number>) => scT(language, source, params);
  const [hovered, setHovered] =
    useState<{ kind: 'major' | 'sub'; part: WebMdPart | WebMdSubPart } | null>(null);
  const [zoomRegion, setZoomRegion] = useState<string | null>(null);
  const [selectedSubs, setSelectedSubs] = useState<Set<string>>(new Set());
  const scrollRef = useRef<HTMLDivElement>(null);
  const scrollTimer = useRef<number | null>(null);

  const gender = genderOf(model);
  const assetKey = `${side}-${gender}` as const;
  const parts = useMemo(
    () => [...(WEBMD_BODY_PARTS[assetKey] ?? [])].sort((a, b) => zRank(a) - zRank(b)),
    [assetKey],
  );
  const zoomTargets = WEBMD_ZOOM[assetKey] ?? [];
  const regions3d = regionsForModel(model, side);

  const zoomTarget: WebMdZoomTarget | undefined =
    zoomRegion ? zoomTargets.find((z) => z.region === zoomRegion) : undefined;
  const activeSubs = zoomTarget?.subs ?? [];
  const hoveredCaption = hovered
    ? hovered.kind === 'sub'
      ? L((hovered.part as WebMdSubPart).title)
      : L(BODY_REGIONS.find((r) => r.id === (hovered.part as WebMdPart).region)?.caption ?? '')
    : null;
  const hoveredAccent = hovered
    ? BODY_REGIONS.find((r) => r.id === (hovered.part as { region: string }).region)?.accent
    : undefined;

  const src = useMemo(() => webmdAsset(side, gender), [side, gender]);
  const viewbox = zoomTarget
    ? gender === 'f'
      ? WEBMD_ZOOM_VIEWBOX_F
      : WEBMD_ZOOM_VIEWBOX_M
    : WEBMD_VIEWBOX;

  useEffect(
    () => () => {
      if (scrollTimer.current) window.clearTimeout(scrollTimer.current);
    },
    [],
  );

  useEffect(() => {
    setZoomRegion(null);
    setSelectedSubs(new Set());
  }, [assetKey, side]);

  useEffect(() => {
    if (!zoomTarget) return;
    const el = scrollRef.current;
    if (!el) return;
    if (scrollTimer.current) window.clearTimeout(scrollTimer.current);
    /* Width CSS-transition takes ~300ms; scroll after it settles so maxScroll allows left/top. */
    const apply = () => {
      el.scrollTop = zoomTarget.top;
      el.scrollLeft = zoomTarget.left;
    };
    apply();
    scrollTimer.current = window.setTimeout(apply, 380);
  }, [zoomTarget]);

  const spinTo = (target: ViewSide) => {
    if (target === side) return;
    setZoomRegion(null);
    setSelectedSubs(new Set());
    if (onSelectSide) onSelectSide(target);
    else onToggleSide();
  };

  const zoomTo = (region: string) => {
    setHovered(null);
    setZoomRegion(region);
    if (!selectedRegions.includes(region)) onSelectRegion(region);
  };

  const zoomOut = () => {
    setHovered(null);
    setZoomRegion(null);
    setSelectedSubs(new Set());
    const el = scrollRef.current;
    if (el) {
      el.scrollTop = 0;
      el.scrollLeft = 0;
    }
  };

  const subKey = (s: WebMdSubPart) => `${s.region}:${s.name}:${s.id}`;

  const onMajorClick = (part: WebMdPart) => {
    if (zoomRegion) return;
    const target = zoomTargets.find((z) => z.region === part.region || z.name === part.name);
    if (target && target.subs.length > 1) {
      zoomTo(part.region);
      return;
    }
    onSelectRegion(part.region);
  };

  const onSubClick = (sub: WebMdSubPart) => {
    const key = subKey(sub);
    const next = new Set(selectedSubs);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    setSelectedSubs(next);
    if (!selectedRegions.includes(sub.region)) onSelectRegion(sub.region);
  };

  const majorOn = (part: WebMdPart): boolean => {
    if (selectedRegions.includes(part.region)) return true;
    if (part.hoverBoth) {
      const mirror = parts.find((p) => p.class === part.hoverBoth);
      if (mirror && selectedRegions.includes(mirror.region)) return true;
    }
    return false;
  };

  const majorFill = (part: WebMdPart): string | undefined => {
    if (majorOn(part)) return BODY_REGIONS.find((r) => r.id === part.region)?.accent;
    if (
      hovered?.kind === 'major' &&
      (hovered.part === part ||
        ((hovered.part as WebMdPart).hoverBoth && (hovered.part as WebMdPart).hoverBoth === part.class) ||
        (part.hoverBoth && part.hoverBoth === (hovered.part as WebMdPart).class))
    ) {
      return '#83B7D6';
    }
    return undefined;
  };

  const majorOpacity = (part: WebMdPart): number => {
    if (majorOn(part)) return 0.55;
    if (
      hovered?.kind === 'major' &&
      (hovered.part === part ||
        ((hovered.part as WebMdPart).hoverBoth && (hovered.part as WebMdPart).hoverBoth === part.class) ||
        (part.hoverBoth && part.hoverBoth === (hovered.part as WebMdPart).class))
    ) {
      return 0.525;
    }
    return 0;
  };

  const subOn = (sub: WebMdSubPart): boolean => selectedSubs.has(subKey(sub));

  const subFill = (sub: WebMdSubPart): string | undefined => {
    if (subOn(sub)) return BODY_REGIONS.find((r) => r.id === sub.region)?.accent;
    if (hovered?.kind === 'sub' && hovered.part === sub) return '#83B7D6';
    return undefined;
  };

  const subOpacity = (sub: WebMdSubPart): number => {
    if (subOn(sub)) return 0.6;
    if (hovered?.kind === 'sub' && hovered.part === sub) return 0.525;
    if (selectedRegions.includes(sub.region)) return 0.2;
    return 0;
  };

  return (
    <div className="space-y-4">
      <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 shadow-sm dark:border-slate-700/50 dark:bg-slate-900">
        <div className="absolute right-2.5 top-2.5 z-20 flex items-center gap-2">
          {zoomRegion && (
            <button
              onClick={zoomOut}
              className="flex items-center gap-1.5 rounded-full border border-slate-300/70 bg-white/95 px-3 py-1.5 text-xs font-semibold text-ink-700 shadow-md backdrop-blur hover:bg-white dark:border-slate-600/50 dark:bg-slate-900/90 dark:text-slate-200"
              aria-label={t('sc.map.zoomAria')}
            >
              <ZoomOut size={13} />
              {t('sc.map.zoomOut')}
            </button>
          )}
          <div
            className="flex items-center gap-0.5 rounded-full border border-slate-300/70 bg-white/90 p-0.5 shadow-md backdrop-blur dark:border-slate-600/50 dark:bg-slate-900/80"
            role="tablist"
            aria-label={t('sc.map.viewAria')}
          >
            {(['front', 'back'] as ViewSide[]).map((v) => (
              <button
                key={v}
                role="tab"
                aria-selected={side === v}
                onClick={() => spinTo(v)}
                className={`flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-semibold transition-all ${
                  side === v
                    ? 'bg-sahaay-deep text-white shadow'
                    : 'text-ink-500 hover:text-ink-800 dark:text-slate-400 dark:hover:text-white'
                }`}
              >
                {v === 'back' && <RotateCw size={12} />}
                {t(`sc.map.side.${v}`)}
              </button>
            ))}
          </div>
        </div>

        {zoomRegion && (
          <div className="absolute left-2.5 top-2.5 z-20 rounded-full bg-sahaay-deep/90 px-3 py-1.5 text-[11px] font-bold text-white shadow">
            {L(BODY_REGIONS.find((r) => r.id === zoomRegion)?.caption ?? zoomRegion)}
            {t('sc.map.tapPart')}
          </div>
        )}

        <motion.div
          key={`${side}-${model}`}
          initial={{ opacity: 0, rotateY: side === 'back' ? -12 : 12 }}
          animate={{ opacity: 1, rotateY: 0 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          style={{ perspective: 1200 }}
          className="relative flex justify-center"
        >
          <div
            ref={scrollRef}
            className="body-image w-full overflow-auto"
            style={{ height: 'clamp(480px, 70vh, 640px)' }}
          >
            <svg
              viewBox={viewbox}
              className="block max-w-none transition-[width] duration-300"
              style={
                zoomTarget
                  ? { width: `${zoomTarget.width}px`, height: 'auto' }
                  : { width: '100%', height: '100%', maxHeight: '100%' }
              }
              role="img"
              aria-label={`${scModelLabel(language, model)} — ${t(`sc.map.side.${side}`)} · ${zoomRegion ? t('sc.map.tapSpecific') : t('sc.map.clickArea')}`}
            >
              <>
                {src && <image href={src} x="0" y="0" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" />}

              {!zoomRegion &&
                parts.map((part, i) => {
                  const fill = majorFill(part);
                  const opacity = majorOpacity(part);
                  const isZoomable = zoomTargets.some(
                    (z) => z.region === part.region || z.name === part.name,
                  );
                  return (
                    <path
                      key={`${part.name}-${part.id}-${i}`}
                      data-major={part.region}
                      d={part.path}
                      transform={part.transform || undefined}
                      fill={fill ?? '#83B7D6'}
                      fillRule="nonzero"
                      opacity={opacity}
                      style={{ cursor: isZoomable ? 'zoom-in' : 'pointer', transition: 'opacity 120ms ease, fill 120ms ease' }}
                      onMouseEnter={() => setHovered({ kind: 'major', part })}
                      onMouseLeave={() => setHovered((h) => (h?.part === part ? null : h))}
                      onClick={() => onMajorClick(part)}
                    />
                  );
                })}

              {zoomRegion &&
                activeSubs.map((sub, i) => {
                  const fill = subFill(sub);
                  const opacity = subOpacity(sub);
                  const on = subOn(sub);
                  return (
                    <path
                      key={`sub-${sub.name}-${sub.id}-${i}`}
                      data-sub={subKey(sub)}
                      d={sub.path}
                      transform={sub.transform || undefined}
                      fill={fill ?? '#83B7D6'}
                      fillRule="nonzero"
                      stroke={on ? fill ?? 'transparent' : 'transparent'}
                      strokeWidth={on ? 2 : 0}
                      opacity={opacity}
                      style={{ cursor: 'pointer', pointerEvents: 'auto', transition: 'opacity 120ms ease, fill 120ms ease' }}
                      onMouseEnter={() => setHovered({ kind: 'sub', part: sub })}
                      onMouseLeave={() => setHovered((h) => (h?.part === sub ? null : h))}
                      onClick={() => onSubClick(sub)}
                    />
                  );
                })}
              </>
            </svg>
          </div>
        </motion.div>

        <div className="pointer-events-none absolute bottom-2.5 left-0 right-0 z-10 text-center px-3">
          <p className="text-xs font-semibold" style={{ color: hoveredAccent ?? '#64748b' }}>
            {hovered
              ? hovered.kind === 'sub'
                ? t('sc.map.hovSub', {
                  name: hoveredCaption ?? '',
                  action: selectedSubs.has(subKey(hovered.part as WebMdSubPart)) ? t('sc.map.deselect') : t('sc.map.select'),
                })
                : zoomRegion
                  ? hoveredCaption ?? ''
                  : t('sc.map.hovZoom', { name: hoveredCaption ?? '' })
              : zoomRegion
                ? selectedSubs.size
                  ? t('sc.map.pickedParts', {
                    n: selectedSubs.size,
                    s: selectedSubs.size > 1 ? 's' : '',
                    region: L(BODY_REGIONS.find((r) => r.id === zoomRegion)?.caption ?? zoomRegion),
                  })
                  : t('sc.map.tapSpecific')
                : selectedRegions.length
                  ? t('sc.map.nSelected', { n: selectedRegions.length, s: selectedRegions.length > 1 ? 's' : '' })
                  : t('sc.map.clickArea')}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 justify-center">
        {regions3d.map((region) => {
          const isSelected = selectedRegions.includes(region.id);
          return (
            <button
              key={region.id}
              onClick={() => {
                onSelectRegion(region.id);
                if (zoomRegion && zoomRegion !== region.id) {
                  setZoomRegion(null);
                  setSelectedSubs(new Set());
                }
              }}
              aria-pressed={isSelected}
              className={`flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition-all ${
                isSelected
                  ? 'border-transparent text-white shadow-md'
                  : 'border-sahaay-deep/15 bg-white/70 text-ink-600 hover:bg-white dark:border-slate-600/50 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:bg-slate-700'
              }`}
              style={isSelected ? { background: region.accent } : undefined}
            >
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ background: isSelected ? '#ffffff' : region.accent }}
              />
              {L(region.caption)}
            </button>
          );
        })}
      </div>
    </div>
  );
}
