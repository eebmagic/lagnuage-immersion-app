import './App.css'
import { Routes, Route, Outlet, Link, useNavigate } from 'react-router-dom';

import { Menubar } from 'primereact/menubar';

import { About } from './pages/About';
import { Learn } from './pages/Learn';

import { UserProvider } from './UserContext.jsx';

function App() {
  return (
    <UserProvider>
      <Routes>
        <Route path="/" element={<PrimaryLayout />}>
          <Route index element={<Hello />} />
          <Route path="learn" element={<Learn />} />
          <Route path="about" element={<About />} />
        </Route>
      </Routes>
    </UserProvider>
  )
}

function PrimaryLayout() {
  const navigateTo = useNavigate();

  const items = [
    {
      label: 'Home',
      icon: 'pi pi-fw pi-home',
      command: () => navigateTo('/')
    },
    {
      label: 'Learn',
      icon: 'pi pi-fw pi-book',
      command: () => navigateTo('/learn')
    },
    {
      label: 'About',
      icon: 'pi pi-fw pi-info-circle',
      command: () => navigateTo('/about')
    }
  ];
  return (
    <div>
      <Menubar model={items} />
      <h1>Layout</h1>

      <Outlet />
    </div>
  )
}

function Hello() {
  return (
    <div>
      <h1>HELLO WORLD (from App.jsx)</h1>
      <Link to="/learn">Learn</Link>
      <Link to="/about">About</Link>
    </div>
  )
}

export default App;
