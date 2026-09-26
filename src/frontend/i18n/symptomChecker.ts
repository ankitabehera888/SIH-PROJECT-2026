import type { Language } from './translations';
import { scSymptomsHi, scSymptomsMr } from './sc/symptoms';
import { scTriageHi, scTriageMr } from './sc/triage';
import { scBodyHi, scBodyMr } from './sc/body';
import type { AgeBand, BodyType } from '../../mock-data/symptomCheckerTriage';

/* Symptom-checker content i18n.
   Flat dicts keyed by the English source string — English falls back to the
   key itself (empty dict), hi/mr look up the translation. Display-only:
   never feed a translated string back into ranking logic (condition names
   are Map keys in analyzeSymptoms). */

const dicts: Record<Language, Record<string, string>> = {
  en: {},
  hi: { ...scSymptomsHi, ...scTriageHi, ...scBodyHi },
  mr: { ...scSymptomsMr, ...scTriageMr, ...scBodyMr },
};

export const scT = (
  language: Language,
  source: string,
  params?: Record<string, string | number>,
): string => {
  let value = (language !== 'en' && dicts[language]?.[source]) || source;
  if (params) {
    for (const [name, raw] of Object.entries(params)) {
      value = value.split(`{${name}}`).join(String(raw));
    }
  }
  return value;
};

const AGE_BAND_SOURCE: Record<AgeBand, string> = {
  neonate: 'Newborn',
  infant: 'Infant',
  child: 'Child',
  teen: 'Teenager',
  adult: 'Adult',
  senior: 'Older adult',
};

export const scAgeBandLabel = (language: Language, band: AgeBand): string =>
  scT(language, AGE_BAND_SOURCE[band]);

export const scModelLabel = (language: Language, model: BodyType): string =>
  scT(language, model === 'male' ? 'Man' : 'Woman');

/* Mirrors mock-data formatAge but resolves every fragment through scT. */
export const scFormatAge = (language: Language, ageMonths: number): string => {
  if (ageMonths < 1) return scT(language, 'under 1 month');
  if (ageMonths < 12) {
    return scT(language, ageMonths === 1 ? '{n} month' : '{n} months', { n: ageMonths });
  }
  const years = Math.floor(ageMonths / 12);
  const rem = ageMonths % 12;
  if (years < 2 && rem) {
    return scT(language, rem === 1 ? '{y} year {m} month' : '{y} year {m} months', { y: years, m: rem });
  }
  return scT(language, years === 1 ? '{n} year' : '{n} years', { n: years });
};
