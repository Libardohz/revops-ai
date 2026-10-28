# Task Manager PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a mobile-friendly Progressive Web App (PWA) for managing tasks and activities using React and localStorage.

**Architecture:** React application initialized with Vite, using functional components and hooks (`useState`, `useEffect`) for state management and local storage syncing. It will use `vite-plugin-pwa` to generate the service worker and manifest for PWA installation.

**Tech Stack:** React, Vite, Vanilla CSS, vite-plugin-pwa

**Spec:** `docs/superpowers/specs/2026-08-24-task-manager-pwa-design.md`

## Global Constraints

- Use Vanilla CSS for styling (no Tailwind).
- Ensure Spanish language is used for the UI.
- Use `localStorage` to save all tasks.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `package.json`, `vite.config.js`, `index.html`, `src/main.jsx`, `src/App.jsx`, `src/index.css`

**Interfaces:**
- Consumes: N/A
- Produces: A running Vite React application.

- [ ] **Step 1: Initialize Vite React App**
Run: `npm create vite@latest . -- --template react` (or `npx -y create-vite@latest ./ --template react`)
Run: `npm install`
Run: `npm install vite-plugin-pwa`

- [ ] **Step 2: Clean up default files**
Replace `src/App.jsx` with a basic functional component:
```jsx
import './index.css'

function App() {
  return (
    <div className="app-container">
      <h1>Gestor de Tareas</h1>
    </div>
  )
}

export default App
```

- [ ] **Step 3: Add basic Vanilla CSS**
Replace `src/index.css` with a basic modern aesthetic (glassmorphism/dark mode):
```css
:root {
  --bg-color: #121212;
  --text-color: #ffffff;
  --primary-color: #3b82f6;
  --card-bg: rgba(255, 255, 255, 0.1);
}
body {
  margin: 0;
  font-family: 'Inter', system-ui, Avenir, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
}
.app-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}
```

- [ ] **Step 4: Commit**
```bash
git add .
git commit -m "chore: initial vite react project scaffolding"
```

---

### Task 2: Task Form Component

**Files:**
- Create: `src/components/TaskForm.jsx`
- Modify: `src/App.jsx`, `src/index.css`

**Interfaces:**
- Consumes: `addTask` function from App
- Produces: Renders form and passes new task object `{ id, name, type, urgency, date, completed }` to `addTask`.

- [ ] **Step 1: Create TaskForm.jsx**
```jsx
import { useState } from 'react';

export default function TaskForm({ onAdd }) {
  const [name, setName] = useState('');
  const [type, setType] = useState('Trabajo');
  const [urgency, setUrgency] = useState('Media');
  const [date, setDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onAdd({
      id: Date.now().toString(),
      name,
      type,
      urgency,
      date,
      completed: false
    });
    setName('');
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <input type="text" placeholder="Nombre de la tarea" value={name} onChange={e => setName(e.target.value)} required />
      <select value={type} onChange={e => setType(e.target.value)}>
        <option value="Trabajo">Trabajo</option>
        <option value="Personal">Personal</option>
        <option value="Estudio">Estudio</option>
        <option value="Otro">Otro</option>
      </select>
      <select value={urgency} onChange={e => setUrgency(e.target.value)}>
        <option value="Alta">Alta</option>
        <option value="Media">Media</option>
        <option value="Baja">Baja</option>
      </select>
      <input type="datetime-local" value={date} onChange={e => setDate(e.target.value)} />
      <button type="submit">Agregar Tarea</button>
    </form>
  );
}
```

- [ ] **Step 2: Add styles in index.css**
```css
.task-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--card-bg);
  padding: 1.5rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  margin-bottom: 2rem;
}
.task-form input, .task-form select, .task-form button {
  padding: 10px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(0,0,0,0.2);
  color: white;
}
.task-form button {
  background: var(--primary-color);
  cursor: pointer;
  border: none;
  font-weight: bold;
}
```

- [ ] **Step 3: Integrate in App.jsx**
```jsx
import { useState, useEffect } from 'react';
import TaskForm from './components/TaskForm';
import './index.css';

function App() {
  const [tasks, setTasks] = useState(() => {
    const saved = localStorage.getItem('tasks');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const addTask = (task) => setTasks([...tasks, task]);

  return (
    <div className="app-container">
      <h1>Gestor de Tareas</h1>
      <TaskForm onAdd={addTask} />
    </div>
  );
}

export default App;
```

- [ ] **Step 4: Commit**
```bash
git add .
git commit -m "feat: add TaskForm and local storage syncing"
```

---

### Task 3: Task List and Item

**Files:**
- Create: `src/components/TaskItem.jsx`, `src/utils/calendar.js`
- Modify: `src/App.jsx`, `src/index.css`

**Interfaces:**
- Consumes: `tasks` array, `toggleTask` function
- Produces: Renders list of tasks and handles calendar export.

- [ ] **Step 1: Create Calendar Util (`src/utils/calendar.js`)**
```javascript
export function exportToGoogleCalendar(task) {
  const text = encodeURIComponent(task.name);
  const details = encodeURIComponent(`Tipo: ${task.type} | Urgencia: ${task.urgency}`);
  const base = "https://calendar.google.com/calendar/render?action=TEMPLATE";
  
  let dates = "";
  if (task.date) {
    const d = new Date(task.date);
    const end = new Date(d.getTime() + 60*60*1000); // +1 hour
    const format = (date) => date.toISOString().replace(/-|:|\.\d\d\d/g, "");
    dates = `&dates=${format(d)}/${format(end)}`;
  }
  
  window.open(`${base}&text=${text}&details=${details}${dates}`, '_blank');
}
```

- [ ] **Step 2: Create TaskItem (`src/components/TaskItem.jsx`)**
```jsx
import { exportToGoogleCalendar } from '../utils/calendar';

export default function TaskItem({ task, onToggle }) {
  return (
    <div className={`task-item ${task.completed ? 'completed' : ''}`}>
      <div className="task-info">
        <input type="checkbox" checked={task.completed} onChange={() => onToggle(task.id)} />
        <div>
          <h3>{task.name}</h3>
          <p>{task.type} - Urgencia: {task.urgency} {task.date && `- ${new Date(task.date).toLocaleString()}`}</p>
        </div>
      </div>
      <button onClick={() => exportToGoogleCalendar(task)}>📅 Google Calendar</button>
    </div>
  );
}
```

- [ ] **Step 3: Integrate in App.jsx**
```jsx
// Add to App.jsx imports
import TaskItem from './components/TaskItem';

// Add function to toggle tasks
const toggleTask = (id) => {
  setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
};

// Add to return statement below TaskForm
<div className="task-list">
  <h2>Pendientes</h2>
  {tasks.filter(t => !t.completed).map(t => (
    <TaskItem key={t.id} task={t} onToggle={toggleTask} />
  ))}
  <h2>Completadas</h2>
  {tasks.filter(t => t.completed).map(t => (
    <TaskItem key={t.id} task={t} onToggle={toggleTask} />
  ))}
</div>
```

- [ ] **Step 4: Add styles**
```css
/* Add to index.css */
.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--card-bg);
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
}
.task-item.completed h3 {
  text-decoration: line-through;
  color: #888;
}
.task-info {
  display: flex;
  align-items: center;
  gap: 15px;
}
.task-info h3 {
  margin: 0 0 5px 0;
}
.task-info p {
  margin: 0;
  font-size: 0.85rem;
  color: #aaa;
}
```

- [ ] **Step 5: Commit**
```bash
git add .
git commit -m "feat: add TaskList, TaskItem and Google Calendar export"
```

---

### Task 4: Configure PWA

**Files:**
- Modify: `vite.config.js`, `index.html`

**Interfaces:**
- Consumes: Vite configuration
- Produces: Service worker and `manifest.json` for installability.

- [ ] **Step 1: Update vite.config.js**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Gestor de Tareas',
        short_name: 'Tareas',
        description: 'Gestiona tus actividades pendientes',
        theme_color: '#121212',
        background_color: '#121212',
        display: 'standalone',
        icons: [
          {
            src: 'https://via.placeholder.com/192x192.png?text=T',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'https://via.placeholder.com/512x512.png?text=T',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
})
```

- [ ] **Step 2: Add theme-color meta tag**
Add `<meta name="theme-color" content="#121212" />` to the `<head>` in `index.html`.

- [ ] **Step 3: Commit**
```bash
git add .
git commit -m "feat: configure PWA manifest and service worker"
```
