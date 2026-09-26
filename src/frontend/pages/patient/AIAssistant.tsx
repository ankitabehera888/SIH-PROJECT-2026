import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic, MicOff, Bot, Volume2, VolumeX,
  Stethoscope, Info, RotateCcw, ShieldCheck, Waves, Download
} from 'lucide-react';
import { useLanguage } from '../../context/providers';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isVoice?: boolean;
}

interface AssessmentData {
  summary: string;
  urgency: string;
  recommendations: string[];
  suggested_lab_tests: Array<{ name: string; reason: string }>;
}

function generateMedicalResponse(input: string, history: ChatMessage[]): string {
  const lower = input.toLowerCase();
  const previousMessages = history.map(m => m.content.toLowerCase()).join(' ');

  if (lower.includes('chest pain') || lower.includes('heart attack') || lower.includes('can\'t breathe') || lower.includes('difficulty breathing') || lower.includes('stroke') || lower.includes('fainting') || lower.includes('seizure') || lower.includes('severe bleeding')) {
    return "This sounds like a medical emergency. Please call emergency services right away — dial 108 or 112 immediately. While you wait: stay calm, sit in a comfortable position, and if you suspect a heart attack and are not allergic to aspirin, chew one aspirin tablet. Do not drive yourself to the hospital. I'm here to support you, but immediate medical attention is critical.";
  }

  if (lower.includes('headache') || lower.includes('head pain') || lower.includes('migraine')) {
    if (history.length > 1 && previousMessages.includes('headache')) {
      return "Based on what you've told me, your symptoms are consistent with a migraine or tension-type headache. Here's what I recommend: Rest in a dark, quiet room. Stay hydrated — drink plenty of water. You can try over-the-counter pain relief like acetaminophen or ibuprofen. Apply a cold compress to your forehead. If this is the worst headache of your life, or if you have vision changes, weakness, or difficulty speaking, please seek emergency care immediately. I'd suggest scheduling a follow-up with your doctor within a few days.";
    }
    return "I understand you're experiencing a headache. Let me help you assess this. Can you tell me: How would you describe the pain — is it throbbing, pressing, or sharp? On a scale of 1 to 10, how severe is it? Have you noticed any sensitivity to light or sound? And when did this start?";
  }

  if (lower.includes('fever') || lower.includes('temperature') || lower.includes('chills')) {
    if (previousMessages.includes('fever')) {
      return "For managing your fever: Stay well hydrated — drink water, clear broths, or oral rehydration solutions. Rest as much as possible. You may take acetaminophen or ibuprofen to reduce fever — follow the dosage on the package. Use a lukewarm compress on your forehead. Seek medical attention if: your temperature exceeds 103 degrees Fahrenheit, the fever lasts more than 3 days, you develop a severe headache, stiff neck, confusion, or difficulty breathing.";
    }
    return "I see you have a fever. To better understand your condition, I need a few more details: What is your current temperature? How long have you had the fever? Do you have any other symptoms like cough, sore throat, body aches, or nausea? Have you traveled recently or been around anyone who is sick?";
  }

  if (lower.includes('stomach') || lower.includes('abdominal') || lower.includes('belly') || lower.includes('nausea') || lower.includes('vomit') || lower.includes('diarrhea') || lower.includes('constipation')) {
    return "I understand you're having digestive discomfort. Here are some things that may help: For nausea, try sipping ginger tea or clear fluids. Eat small, bland meals — the BRAT diet: bananas, rice, applesauce, and toast. Avoid spicy, fatty, or dairy foods for now. Stay hydrated with small sips of water or oral rehydration salts. Seek immediate care if you experience: blood in vomit or stool, severe abdominal pain, signs of dehydration like dark urine or dizziness, or if symptoms persist beyond 48 hours.";
  }

  if (lower.includes('joint') || lower.includes('knee') || lower.includes('back') || lower.includes('muscle') || lower.includes('pain') || lower.includes('ache')) {
    if (previousMessages.includes('pain') || previousMessages.includes('ache')) {
      return "For managing your pain at home: Apply ice for the first 48 hours if there's swelling, then switch to warm compresses. Rest the affected area but avoid complete immobilization. Over-the-counter anti-inflammatory medications like ibuprofen can help reduce pain and inflammation. Gentle stretching and movement can prevent stiffness. Please see a doctor if: the pain is severe or worsening, you notice swelling, redness, or warmth in the area, you have difficulty moving the joint, or the pain persists beyond a week.";
    }
    return "I understand you're experiencing pain. To help me better understand: Where exactly is the pain located? Did this start after an injury or did it come on gradually? Is the pain constant or does it come and go? On a scale of 1 to 10, how would you rate it? Any swelling, redness, or stiffness in the area?";
  }

  if (lower.includes('rash') || lower.includes('skin') || lower.includes('itch') || lower.includes('pimple') || lower.includes('eczema')) {
    return "For skin concerns, here's what I suggest: Avoid scratching the affected area to prevent infection. Apply a gentle, fragrance-free moisturizer. Over-the-counter hydrocortisone cream may help with itching and inflammation. Keep the area clean and dry. See a dermatologist if: the rash is spreading rapidly, you have a fever along with the rash, there are blisters or open sores, the rash doesn't improve within a week, or you suspect an allergic reaction.";
  }

  if (lower.includes('diabetes') || lower.includes('blood sugar') || lower.includes('sugar level') || lower.includes('insulin')) {
    return "For diabetes management, consistency is key: Monitor your blood sugar levels regularly as advised by your doctor. Take medications or insulin as prescribed — never skip doses. Follow a balanced diet with controlled carbohydrate portions. Exercise regularly — even a 30-minute walk helps. Watch for signs of high blood sugar: excessive thirst, frequent urination, blurred vision, fatigue. For low blood sugar: confusion, shakiness, sweating — eat a quick source of sugar like glucose tablets or fruit juice. Keep regular follow-ups with your endocrinologist.";
  }

  if (lower.includes('cold') || lower.includes('cough') || lower.includes('congestion') || lower.includes('sore throat') || lower.includes('runny nose')) {
    return "For cold and respiratory symptoms: Rest and stay hydrated — warm fluids like tea with honey can soothe a sore throat. Use saline nasal drops or a steam inhaler for congestion. Over-the-counter cold medications can help with symptoms. A warm salt water gargle can help sore throats. Honey is effective for cough in adults. Seek medical care if: symptoms last more than 10 days, you develop a high fever, you have difficulty breathing, chest pain, or your cough produces colored sputum.";
  }

  if (lower.includes('anxious') || lower.includes('anxiety') || lower.includes('depressed') || lower.includes('depression') || lower.includes('stress') || lower.includes('sleep') || lower.includes('insomnia') || lower.includes('mental health')) {
    return "I hear you, and it's important that you're reaching out. Your feelings are valid. Here are some things that may help: Practice deep breathing — inhale for 4 seconds, hold for 4, exhale for 6. Maintain a regular sleep schedule. Physical activity, even a short walk, can significantly improve mood. Limit caffeine and screen time before bed. Talk to someone you trust about how you're feeling. Please consider reaching out to a mental health professional. If you're in crisis, please call the Vandrevala Foundation helpline at 1860-2662-345 or the iCall helpline at 9152987821. You're not alone.";
  }

  if (lower.includes('medication') || lower.includes('medicine') || lower.includes('drug') || lower.includes('side effect') || lower.includes('dosage')) {
    return "Regarding medications: Always take medications as prescribed by your doctor — don't change doses without consulting them. Never share prescription medications with others. If you experience side effects, note them and discuss with your doctor at your next visit. For missed doses, check the medication guide or ask your pharmacist. Keep an updated list of all medications, supplements, and allergies. If you're unsure about any medication, your pharmacist is an excellent resource for quick questions.";
  }

  if (history.length <= 1) {
    return "Hello! I'm your AI health assistant. I'm here to listen to your health concerns and provide general guidance. Please describe what symptoms or health issues you're experiencing, and I'll do my best to help. Remember, I can provide general health information but I'm not a replacement for professional medical advice.";
  }

  return "Thank you for sharing that information. Based on what you've told me, here are my general recommendations: Monitor your symptoms closely and note any changes. Stay hydrated and get adequate rest. Maintain a healthy diet and avoid self-medication unless directed by a healthcare professional. If your symptoms worsen or persist, please schedule an appointment with your doctor. Would you like to tell me more about any specific symptom you're experiencing?";
}

const VOICE_GREETING = 'Hello, I am Sahaay Assistant. How can I help you with your symptoms today?';

export function AIAssistant() {
  const { t } = useLanguage();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isVoiceMode] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(true);
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null);
  const [llmConnected, setLlmConnected] = useState<boolean | null>(null);
  const recognitionRef = useRef<any>(null);
  const listeningRequestedRef = useRef(false);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const voiceSessionRef = useRef<string | null>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    // Single-turn capture lets browser detect speech end and trigger response.
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        }
      }
      if (finalTranscript) {
        listeningRequestedRef.current = false;
        setInputText(prev => prev + finalTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error !== 'no-speech') {
        listeningRequestedRef.current = false;
        setIsListening(false);
      }
    };

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => {
      setIsListening(false);
      if (listeningRequestedRef.current) {
        window.setTimeout(() => {
          try { recognition.start(); } catch (_error) { /* retry on next browser turn */ }
        }, 250);
      }
    };

    recognitionRef.current = recognition;
    synthRef.current = window.speechSynthesis;

    return () => {
      recognition.stop();
      synthRef.current?.cancel();
    };
  }, []);

  useEffect(() => {
    let active = true;
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
    const checkConnection = async () => {
      try {
        const response = await fetch(`${apiBase}/voice/status`);
        const data = await response.json() as { connected?: boolean };
        if (active) setLlmConnected(data.connected === true);
      } catch (_error) {
        if (active) setLlmConnected(false);
      }
    };
    void checkConnection();
    const timer = window.setInterval(checkConnection, 30000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const beginListening = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) return;
    listeningRequestedRef.current = true;
    let attempts = 0;
    const start = () => {
      try {
        recognition.start();
      } catch (_error) {
        attempts += 1;
        if (attempts < 4) window.setTimeout(start, 250);
        else setIsListening(false);
      }
    };
    window.setTimeout(start, 150);
  }, []);

  const speakText = useCallback((text: string, onDone?: () => void) => {
    if (!synthRef.current) {
      onDone?.();
      return;
    }
    synthRef.current.cancel();
    const cleanText = text.replace(/\*\*/g, '').replace(/\*/g, '').replace(/#{1,6}\s/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;
    const voices = synthRef.current.getVoices();
    const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Natural'));
    if (preferredVoice) utterance.voice = preferredVoice;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => {
      setIsSpeaking(false);
      onDone?.();
    };
    utterance.onerror = () => {
      setIsSpeaking(false);
      onDone?.();
    };
    synthRef.current.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    synthRef.current?.cancel();
    audioRef.current?.pause();
    audioRef.current = null;
    setIsSpeaking(false);
  }, []);

  const speakBackendAudio = useCallback((audioBase64: string | null | undefined, fallback: string, onDone?: () => void) => {
    if (!audioBase64) {
      speakText(fallback, onDone);
      return;
    }
    synthRef.current?.cancel();
    audioRef.current?.pause();
    const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
    audioRef.current = audio;
    audio.onplay = () => setIsSpeaking(true);
    audio.onended = () => {
      setIsSpeaking(false);
      onDone?.();
    };
    audio.onerror = () => {
      setIsSpeaking(false);
      speakText(fallback, onDone);
    };
    void audio.play().catch(() => speakText(fallback, onDone));
  }, [speakText]);

  const sendMessage = useCallback(async (text?: string) => {
    const msg = (text || inputText).trim();
    if (!msg || isProcessing) return;
    setInputText('');
    setIsProcessing(true);
    const userMsg: ChatMessage = { role: 'user', content: msg, timestamp: new Date().toLocaleTimeString(), isVoice: isListening };
    setMessages(prev => [...prev, userMsg]);
    if (!isVoiceMode) {
      setTimeout(() => {
        const response = generateMedicalResponse(msg, messages);
        const aiMsg: ChatMessage = { role: 'assistant', content: response, timestamp: new Date().toLocaleTimeString() };
        setMessages(prev => [...prev, aiMsg]);
        setIsProcessing(false);
      }, 1200 + Math.random() * 800);
      return;
    }

    try {
      const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
      if (!voiceSessionRef.current) {
        const start = await fetch(`${apiBase}/voice-symptom/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ language: 'en', voice_preset: 'marin' }),
        });
        if (!start.ok) throw new Error('Voice session could not start');
        const session = await start.json() as { session_id: string };
        voiceSessionRef.current = session.session_id;
      }
      const result = await fetch(`${apiBase}/voice-symptom/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: voiceSessionRef.current, text_message: msg, language: 'en' }),
      });
      if (!result.ok) throw new Error('Voice response failed');
      const data = await result.json() as { doctor_message: string; doctor_audio_base64?: string | null; is_final_assessment?: boolean; assessment_data?: AssessmentData | null };
      if (data.assessment_data) setAssessmentData(data.assessment_data);
      const aiMsg: ChatMessage = { role: 'assistant', content: data.doctor_message, timestamp: new Date().toLocaleTimeString() };
      setMessages(prev => [...prev, aiMsg]);
      speakBackendAudio(data.doctor_audio_base64, data.doctor_message, data.is_final_assessment ? undefined : beginListening);
    } catch (_error) {
      const response = generateMedicalResponse(msg, messages);
      const aiMsg: ChatMessage = { role: 'assistant', content: response, timestamp: new Date().toLocaleTimeString() };
      setMessages(prev => [...prev, aiMsg]);
      speakText(response, beginListening);
    } finally {
      setIsProcessing(false);
    }
  }, [inputText, isProcessing, messages, isListening, isVoiceMode, speakText, speakBackendAudio, beginListening]);

  useEffect(() => {
    if (!isListening && inputText.trim() && isVoiceMode) {
      const timer = setTimeout(() => { if (inputText.trim()) sendMessage(); }, 1500);
      return () => clearTimeout(timer);
    }
  }, [isListening, inputText, isVoiceMode, sendMessage]);

  const startVoiceAssistant = useCallback(async () => {
    if (isListening) {
      listeningRequestedRef.current = false;
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }
    if (isSpeaking || isProcessing) return;

    try {
      const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
      const start = await fetch(`${apiBase}/voice-symptom/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'en', voice_preset: 'marin' }),
      });
      if (!start.ok) throw new Error('Voice session could not start');
      const session = await start.json() as { session_id: string; doctor_message?: string; doctor_audio_base64?: string | null };
      voiceSessionRef.current = session.session_id;
      speakBackendAudio(session.doctor_audio_base64, session.doctor_message || VOICE_GREETING, beginListening);
    } catch (_error) {
      speakText(VOICE_GREETING, beginListening);
    }
  }, [beginListening, isListening, isProcessing, isSpeaking, speakBackendAudio, speakText]);

  const startNewConversation = () => {
    setMessages([]);
    setInputText('');
    setIsListening(false);
    listeningRequestedRef.current = false;
    setIsSpeaking(false);
    setAssessmentData(null);
    voiceSessionRef.current = null;
    recognitionRef.current?.stop();
    synthRef.current?.cancel();
    audioRef.current?.pause();
    audioRef.current = null;
  };

  const downloadReport = useCallback(async () => {
    if (!voiceSessionRef.current) return;
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
    const response = await fetch(`${apiBase}/voice-symptom/${voiceSessionRef.current}/report`);
    if (!response.ok) return;
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'sahaay-symptom-report.pdf';
    link.click();
    URL.revokeObjectURL(url);
  }, []);

  const renderMarkdown = (text: string) =>
    text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="text-gray-500">$1</em>')
      .replace(/\n/g, '<br/>');

  const latestAssistantMessage = [...messages].reverse().find(message => message.role === 'assistant');
  const statusText = isProcessing ? 'Thinking...' : isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Ready when you are';

  return (
    <div className="relative flex h-[calc(100dvh-138px)] min-h-[500px] max-h-[900px] flex-col overflow-hidden rounded-[2rem] border border-cyan-300/15 bg-[#050b16] text-white shadow-[0_24px_90px_rgba(2,12,27,0.35)]">
      <div className="pointer-events-none absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(96,165,250,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(96,165,250,0.06)_1px,transparent_1px)] [background-size:36px_36px]" />
      <div className="pointer-events-none absolute -left-24 top-24 h-72 w-72 rounded-full bg-emerald-400/15 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 bottom-0 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />

      <header className="relative z-10 flex shrink-0 items-center gap-3 border-b border-white/10 bg-white/[0.03] px-4 py-4 sm:px-6">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-300/30 bg-emerald-300/10 text-emerald-200">
          <span className="absolute inset-1 rounded-lg border border-emerald-200/20" />
          <Stethoscope size={19} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[10px] font-bold uppercase tracking-[0.22em] text-cyan-200/70">SAHAAY // VOICE NODE</p>
          <h2 className="truncate text-base font-bold tracking-tight sm:text-lg">{t('ai.title')}</h2>
        </div>
        <div className="flex shrink-0 items-center gap-2 rounded-full border border-white/10 bg-black/20 px-2.5 py-1.5 text-[9px] font-bold uppercase tracking-wider text-white/60 sm:px-3 sm:text-[10px]" title={llmConnected ? 'OpenAI API connected' : 'OpenAI API unavailable; fallback assistant active'}>
          <span className={`h-2 w-2 rounded-full ${llmConnected === true ? 'bg-emerald-300 shadow-[0_0_10px_rgba(110,231,183,0.9)]' : llmConnected === false ? 'bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.7)]' : 'bg-amber-300'}`} />
          <span className="hidden sm:inline">AI Connection</span>
          <span className="sm:hidden">AI</span>
        </div>
        <button onClick={startNewConversation} className="rounded-xl border border-white/10 p-2 text-white/50 transition hover:border-cyan-200/30 hover:bg-cyan-200/10 hover:text-white" title="Start new conversation">
          <RotateCcw size={16} />
        </button>
      </header>

      <main className="relative z-10 flex min-h-0 flex-1 flex-col overflow-y-auto lg:grid lg:grid-cols-[minmax(0,1.08fr)_minmax(300px,0.92fr)] lg:overflow-hidden">
        <section className="flex min-h-0 shrink-0 flex-col items-center justify-center px-4 py-6 text-center sm:px-8 lg:py-8">
          <div className="mb-4 flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.18em] text-white/55">
            <span className={`h-1.5 w-1.5 rounded-full ${isListening ? 'animate-pulse bg-red-400' : isSpeaking ? 'animate-pulse bg-cyan-300' : 'bg-emerald-300'}`} />
            {statusText}
          </div>

          <div className="relative flex h-[clamp(170px,27vh,260px)] w-[clamp(170px,27vh,260px)] shrink-0 items-center justify-center">
            <div className={`absolute inset-0 rounded-full border border-cyan-200/20 ${isListening || isSpeaking ? 'animate-ping' : ''}`} />
            <div className="absolute inset-3 rounded-full border border-emerald-200/20" />
            <div className="absolute inset-8 rounded-full border border-dashed border-cyan-200/20" />
            <div className={`relative flex h-[clamp(108px,17vh,168px)] w-[clamp(108px,17vh,168px)] items-center justify-center rounded-full border border-white/40 bg-gradient-to-br from-emerald-200 via-cyan-300 to-blue-400 text-[#04131e] shadow-[0_0_70px_rgba(45,212,191,0.3)] transition-transform ${isListening ? 'scale-110' : isSpeaking ? 'scale-105' : ''}`}>
              <div className="absolute inset-3 rounded-full border border-white/40" />
              <Waves size={42} strokeWidth={1.25} />
            </div>
          </div>

          <h3 className="mt-5 text-xl font-bold tracking-tight sm:text-2xl">{isListening ? 'Listening channel open' : isSpeaking ? 'Response transmitting' : 'Voice channel ready'}</h3>
          <p className="mt-2 max-w-sm text-xs leading-relaxed text-white/45 sm:text-sm">{isListening ? 'Speak naturally. Silence ends your turn automatically.' : 'Tap once to start. Sahaay listens and responds without typing.'}</p>

          <div className="mt-5 flex items-center gap-4">
            {voiceSupported ? (
              <button onClick={startVoiceAssistant} disabled={isProcessing && !isListening} aria-label={isListening ? 'Stop listening' : 'Start listening'} className={`relative flex h-[68px] w-[68px] items-center justify-center rounded-full border-4 border-[#050b16] ring-1 ring-white/30 transition-all hover:scale-105 sm:h-20 sm:w-20 ${isListening ? 'bg-red-500 shadow-[0_0_38px_rgba(239,68,68,0.55)]' : 'bg-emerald-300 text-[#06202a] shadow-[0_0_38px_rgba(110,231,183,0.4)]'} disabled:cursor-not-allowed disabled:opacity-50`}>
                {isListening ? <MicOff size={24} /> : <Mic size={24} />}
              </button>
            ) : <div className="rounded-xl bg-amber-300/10 px-4 py-3 text-xs text-amber-200">{t('ai.voiceNotSupported')}</div>}
            {latestAssistantMessage && <button onClick={() => isSpeaking ? stopSpeaking() : speakText(latestAssistantMessage.content)} className="flex h-11 w-11 items-center justify-center rounded-full border border-white/15 text-white/60 transition hover:border-cyan-200/40 hover:bg-cyan-200/10 hover:text-white" aria-label={isSpeaking ? 'Stop response' : 'Replay response'}>{isSpeaking ? <VolumeX size={17} /> : <Volume2 size={17} />}</button>}
          </div>
          <p className="mt-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">{isListening ? 'Tap to stop' : 'Tap to speak'}</p>
        </section>

        <section className="min-h-0 border-t border-white/10 bg-black/15 p-4 sm:p-6 lg:overflow-y-auto lg:border-l lg:border-t-0">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-200/60">Live transcript</p>
              <p className="mt-1 text-xs text-white/35">Private voice response channel</p>
            </div>
            <div className="flex gap-1"><span className="h-1.5 w-1.5 rounded-full bg-emerald-300" /><span className="h-1.5 w-1.5 rounded-full bg-cyan-300/60" /><span className="h-1.5 w-1.5 rounded-full bg-blue-300/40" /></div>
          </div>
          <AnimatePresence mode="wait">
            {(inputText || latestAssistantMessage || isProcessing) ? (
              <motion.div key={latestAssistantMessage?.content || inputText || 'processing'} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-left backdrop-blur-sm">
                {inputText && <p className="border-l-2 border-cyan-300/60 pl-3 text-xs italic leading-relaxed text-cyan-100/70">“{inputText}”</p>}
                {isProcessing ? <div className="mt-4 flex items-center gap-2 text-xs text-white/50"><span className="h-2 w-2 animate-bounce rounded-full bg-emerald-300" /><span className="h-2 w-2 animate-bounce rounded-full bg-emerald-300 [animation-delay:120ms]" /><span className="h-2 w-2 animate-bounce rounded-full bg-emerald-300 [animation-delay:240ms]" /> Processing voice signal</div> : latestAssistantMessage && <div className="mt-4 flex gap-3 text-sm leading-relaxed text-white/75"><Bot size={17} className="mt-0.5 shrink-0 text-emerald-300" /><span dangerouslySetInnerHTML={{ __html: renderMarkdown(latestAssistantMessage.content) }} /></div>}
                {assessmentData && <div className="mt-5 border-t border-white/10 pt-4"><p className="text-[10px] font-bold uppercase tracking-[0.16em] text-emerald-300">Suggested lab tests</p><div className="mt-2 space-y-2">{assessmentData.suggested_lab_tests.length ? assessmentData.suggested_lab_tests.map(test => <div key={test.name} className="rounded-xl border border-white/5 bg-black/20 px-3 py-2"><p className="text-xs font-semibold text-white/85">{test.name}</p><p className="mt-0.5 text-[11px] leading-relaxed text-white/45">{test.reason}</p></div>) : <p className="text-xs text-white/45">No lab test suggested by screening.</p>}</div><button onClick={downloadReport} className="mt-4 inline-flex items-center gap-2 rounded-xl bg-emerald-300 px-4 py-2.5 text-xs font-bold text-[#06202a] transition hover:bg-emerald-200"><Download size={14} /> Download report</button></div>}
              </motion.div>
            ) : <div className="rounded-2xl border border-dashed border-white/10 px-4 py-10 text-center text-xs text-white/30">Your spoken response will appear here.</div>}
          </AnimatePresence>
        </section>
      </main>

      <footer className="relative z-10 flex shrink-0 items-center justify-center gap-2 border-t border-white/10 px-4 py-3 text-[9px] text-white/30 sm:text-[10px]"><ShieldCheck size={13} /><span>{t('ai.disclaimer')}</span><Info size={12} /></footer>
    </div>
  );
}
