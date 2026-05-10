// import { StrictMode } from "react";
// import { createRoot } from "react-dom/client";
// import App from "./App";

// createRoot(document.getElementById("root")!).render(
//   <StrictMode>
//     <App />
//   </StrictMode>,
// );

// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css' // или где у тебя стили

// Минимальный мок Telegram WebApp – чтобы не вылетало при обращении
function initTelegramMock() {
  window.Telegram = {
    WebApp: {
      initData: 'mock',
      ready: () => {},
      expand: () => {},
      openLink: (url: string) => window.open(url, '_blank'),
      showAlert: (msg: string) => alert(msg),
    },
  }
}

if (import.meta.env.DEV && import.meta.env.VITE_MOCK_TELEGRAM !== 'false') {
  initTelegramMock()
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)