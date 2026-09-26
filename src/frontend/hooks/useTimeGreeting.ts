import { useEffect, useState } from 'react';
import type { ComponentType } from 'react';
import { Sunrise, Sun, Sunset, Moon } from 'lucide-react';
import { useLanguage } from '../context/providers';

export type GreetingBand = 'morning' | 'afternoon' | 'evening' | 'night';

type Band = {
  name: GreetingBand;
  /** Hour the band opens, local time. */
  from: number;
  key: string;
  icon: ComponentType<{ size?: number | string; className?: string }>;
  /** Accent for the greeting glyph — dawn green → noon amber → dusk violet. */
  tint: string;
};

/**
 * The four greetings we move between, in clock order. Anything before 05:00
 * falls through to night: 2am is still "good night", not a new morning.
 */
const BANDS: Band[] = [
  { name: 'morning',   from: 5,  key: 'dash.goodMorning',   icon: Sunrise, tint: '#17B366' },
  { name: 'afternoon', from: 12, key: 'dash.goodAfternoon', icon: Sun,     tint: '#F59E0B' },
  { name: 'evening',   from: 17, key: 'dash.goodEvening',   icon: Sunset,  tint: '#EC6B3F' },
  { name: 'night',     from: 21, key: 'dash.goodNight',     icon: Moon,    tint: '#7C5CFF' },
];

function bandIndex(date: Date): number {
  const h = date.getHours();
  // Walk backwards: the last band whose start we have passed wins.
  for (let i = BANDS.length - 1; i >= 0; i--) {
    if (h >= BANDS[i].from) return i;
  }
  return BANDS.length - 1; // 00:00–04:59 → night
}

/**
 * A greeting that tracks the real clock — morning, afternoon, evening, night —
 * in whichever language is selected.
 *
 * The dashboards previously hardcoded `t('dash.goodMorning')`, so an evening
 * demo greeted the user as if the day were just starting.
 *
 * State holds the band index rather than a timestamp, and the setter is passed
 * the same value when nothing has changed, so React bails out: the minute tick
 * re-renders on the four boundaries of the day, not 1,440 times.
 */
export function useTimeGreeting() {
  const { t } = useLanguage();
  const [index, setIndex] = useState(() => bandIndex(new Date()));

  useEffect(() => {
    const tick = () => setIndex(bandIndex(new Date()));
    // A minute of drift on a greeting is invisible, and it keeps a screen that
    // sits open across 17:00 honest.
    const id = window.setInterval(tick, 60_000);
    tick();
    return () => window.clearInterval(id);
  }, []);

  const band = BANDS[index];

  return {
    /** Localized greeting, e.g. "Good evening" / "शुभ संध्या". */
    greeting: t(band.key),
    /** Which part of the day it is, for callers that want to branch on it. */
    band: band.name,
    /** Matching lucide glyph — a real icon, not an emoji. */
    Icon: band.icon,
    /** Accent colour that shifts with the light outside. */
    tint: band.tint,
  };
}
