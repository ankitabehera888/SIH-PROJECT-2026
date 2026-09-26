import { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Paperclip, Search } from 'lucide-react';
import { doctorMessages, messageHandoff, patients } from '../../../mock-data/mockData';
import { Avatar } from '../../components/ui/Avatar';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

/* Open the thread for the patient handoff from My Patients, if any. */
const initialChat = () => {
  const pid = messageHandoff.patientId;
  messageHandoff.patientId = '';
  if (!pid) return doctorMessages[0]!;
  const byId = doctorMessages.find((m) => m.patientId === pid);
  if (byId) return byId;
  const name = patients.find((p) => p.id === pid)?.name;
  return doctorMessages.find((m) => m.contactName === name) ?? doctorMessages[0]!;
};

export function DoctorMessages() {
  const [selectedChat, setSelectedChat] = useState(initialChat);
  const { t } = useLanguage();
  const [newMessage, setNewMessage] = useState('');
  const { showToast } = useToast();

  const contactName = (c: (typeof doctorMessages)[number]) => c.contactName;

  const handleSend = () => {
    if (newMessage.trim()) {
      showToast(t('msg.sent'));
      setNewMessage('');
    }
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-gray-900">{t('dash.messages')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('msg.subtitleDoctor')}</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
        className="glass-card-elevated overflow-hidden flex"
        style={{ height: 'calc(100vh - 200px)', minHeight: 400 }}
      >
        {/* Conversation list */}
        <div className="w-80 border-r border-gray-100 flex flex-col shrink-0 hidden sm:flex">
          <div className="p-3 border-b border-gray-100">
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type="text" placeholder={t('msg.search')} className="sahaay-input pl-9 py-2 text-sm" />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {doctorMessages.map(msg => (
              <button
                key={msg.id}
                onClick={() => setSelectedChat(msg)}
                className={`w-full flex items-start gap-3 p-3 text-left hover:bg-sahaay-surface/50 transition-colors ${selectedChat.id === msg.id ? 'bg-sahaay-surface border-r-2 border-sahaay-deep' : ''}`}
              >
                <Avatar initials={contactName(msg).split(' ').map(n => n[0]).join('').slice(0, 2)} size="md" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-gray-900 truncate">{contactName(msg)}</p>
                    <span className="text-[10px] text-gray-400 shrink-0 ml-2">{msg.time}</span>
                  </div>
                  <p className="text-xs text-gray-500">{t(msg.contactRoleKey)}</p>
                  <p className="text-xs text-gray-400 truncate mt-0.5">{t(msg.lastMessageKey)}</p>
                </div>
                {msg.unread > 0 && (
                  <span className="w-5 h-5 bg-sahaay-deep text-white text-[10px] font-bold rounded-full flex items-center justify-center shrink-0 mt-1">
                    {msg.unread}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <div className="flex items-center gap-3 p-4 border-b border-gray-100">
            <Avatar initials={contactName(selectedChat).split(' ').map(n => n[0]).join('').slice(0, 2)} size="sm" />
            <div className="min-w-0">
              <p className="text-sm font-bold text-gray-900">{contactName(selectedChat)}</p>
              <p className="text-[11px] text-gray-500">{t(selectedChat.contactRoleKey)}</p>
              {selectedChat.treatingForKey && (
                <p className="mt-0.5 flex items-center gap-1 text-[11px] font-medium text-sahaay-deep">
                  <span className="inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-sahaay-deep" />
                  <span className="truncate">
                    {t('msg.treatingFor')}: {t(selectedChat.treatingForKey)}
                  </span>
                </p>
              )}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-sahaay-surface/30">
            {selectedChat.messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.sender === 'doctor' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[75%] px-4 py-2.5 rounded-2xl ${
                  msg.sender === 'doctor'
                    ? 'bg-sahaay-deep text-white rounded-br-md'
                    : 'bg-white text-gray-800 rounded-bl-md shadow-sm border border-gray-100'
                }`}>
                  <p className="text-sm">{t(msg.textKey)}</p>
                  <p className={`text-[10px] mt-1 ${msg.sender === 'doctor' ? 'text-white/60' : 'text-gray-400'}`}>{msg.time}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <button className="w-9 h-9 rounded-xl hover:bg-gray-100 flex items-center justify-center text-gray-400">
                <Paperclip size={18} />
              </button>
              <input
                type="text"
                value={newMessage}
                onChange={e => setNewMessage(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder={t('msg.typePlaceholder')}
                className="sahaay-input flex-1"
              />
              <button onClick={handleSend} className="w-9 h-9 rounded-xl bg-sahaay-deep text-white flex items-center justify-center hover:bg-sahaay-700 transition-colors">
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </motion.div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
