/**
 * config.js — App-wide constants and configuration
 */

const CONFIG = Object.freeze({
  API_BASE:              'http://localhost:8000/api/v1',
  WA_PHONE:              '+20 100 555 0000',
  TG_BOT:                'YourBotUsername',
  FB_PAGE_ID:            '',          // Facebook Page ID — set in backend .env
  SESSION_KEY:           'demoUser',
  TOAST_DURATION:        2400,
  DEFAULT_APPROVAL_LIMIT: 50000,
  DEFAULT_MAX_DISC:      8,
  VERSION:               '0.2.0',
});

/**
 * Customer segments
 */
const SEG = Object.freeze({
  new:       { n: 'عميل جديد',    c: 1 },
  interested:{ n: 'مهتم',         c: 2 },
  ready:     { n: 'جاهز للشراء',  c: 3 },
  current:   { n: 'عميل حالي',    c: 4 },
  idle:      { n: 'متوقف',        c: 5 },
});

const CONS = Object.freeze({
  in:   ['مشترك',    'st-good'],
  out:  ['منسحب',    'st-bad'],
  none: ['لم يُسأل', 'st-mute'],
});

/**
 * Role → allowed views
 */
const ACCESS = Object.freeze({
  manager: ['overview','chats','alerts','customers','facebook','schedule','insights','settings'],
  staff:   ['overview','chats','customers','schedule'],
});

/**
 * View metadata: key → [title, subtitle]
 */
const VIEWS_META = Object.freeze({
  overview:  ['نظرة عامة',         'ملخص اليوم والوكيل يعمل'],
  chats:     ['المحادثات',         'الوكيل يرد تلقائياً · واتساب · تيليجرام · إيميل'],
  alerts:    ['التنبيهات',         'حالات تحتاج تدخّلك المباشر'],
  customers: ['العملاء',           'سجل كل عميل وتاريخ تواصله'],
  facebook:  ['حملات الفيسبوك',   'إنشاء وجدولة ونشر المنشورات والإعلانات'],
  schedule:  ['المواعيد',          'الوكيل يحجز ويرسل تأكيدات تلقائية'],
  insights:  ['التوصيات',         'اقتراحات الوكيل لهذا الأسبوع'],
  settings:  ['الإعدادات',        'الوكيل وقاعدة المعرفة وربط الحسابات'],
});

/** Days of week in Arabic */
const DAYS_AR = ['السبت','الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة'];

/** Supported channels */
const CHANNELS = Object.freeze({
  whatsapp: { label: 'واتساب',   icon: '💬', color: '#25D366' },
  telegram: { label: 'تيليجرام', icon: '✈️', color: '#2AABEE' },
  email:    { label: 'إيميل',    icon: '📧', color: '#6366f1' },
  facebook: { label: 'فيسبوك',  icon: '👥', color: '#1877F2' },
});

/** Alert severity levels */
const ALERT_LEVELS = Object.freeze({
  high:   { label: 'عاجل',   c: 'st-bad'  },
  medium: { label: 'مهم',    c: 'st-warn' },
  low:    { label: 'للعلم',  c: 'st-acc'  },
});
