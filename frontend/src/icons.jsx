import React from 'react';
const paths = {
  expand: <path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>,
  collapse: <path d="M3 8h5V3m13 5h-5V3M8 21v-5H3m13 5v-5h5"/>,
  plus: <path d="M12 5v14M5 12h14"/>,
  close: <path d="m6 6 12 12M6 18 18 6"/>,
  back: <path d="M19 12H5m6-6-6 6 6 6"/>,
  chevron: <path d="m6 9 6 6 6-6"/>,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  logout: <><path d="M9 4H4v16h5m5-13 5 5-5 5M9 12h10"/></>,
  send: <><path d="m3 3 18 9-18 9 4-9zM7 12h14"/></>,
  message: <><path d="M21 15a3 3 0 0 1-3 3H8l-5 4V6a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3z"/><path d="M7 8h10M7 12h7"/></>,
  flag: <><path d="M5 22V3m0 1c5-4 9 4 14 0v10c-5 4-9-4-14 0"/></>,
  grid: <><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/></>,
  users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/><path d="M16 3a4 4 0 0 1 0 8"/></>,
  settings: <><path d="m12 3 2 3 4-1 1 4 3 3-3 2-1 4-4-1-2 4-2-4-4 1-1-4-3-2 3-3 1-4 4 1z"/><circle cx="12" cy="12" r="3"/></>,
  catalog: <><path d="M4 4h7v7H4zm9 0h7v7h-7zM4 13h7v7H4z"/><path d="M13 16h7m-4-3v7"/></>,
  history: <><path d="M3 11a9 9 0 1 1 2.5 7M3 4v7h7"/><path d="M12 7v5l3 2"/></>,
  moon: <path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/>,
  sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-11 12h4"/></>,
  arrow: <path d="M5 12h14m-5-5 5 5-5 5"/>,
  inbox: <><path d="m3 3-2 12v6h22v-6L21 3zM1 15h6l2 3h6l2-3h6"/></>,
  search: <><circle cx="10" cy="10" r="7"/><path d="m16 16 5 5"/></>,
  shield: <><path d="m12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6z"/><path d="m8 12 3 3 5-6"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
};
export function Icon({ name, size = 20, ...props }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.grid}</svg>;
}
