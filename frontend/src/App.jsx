import './App.css'
import { Routes, Route, Outlet, Link } from 'react-router-dom';
import { About } from './pages/About';

function App() {
    return (
        <Routes>
            <Route path="/" element={<PrimaryLayout />}>
                <Route index element={<Hello />} />
                <Route path="about" element={<About />} />
            </Route>
        </Routes>
    )
}

function PrimaryLayout() {
    return (
        <div>
            {/* Add primary components here. Such as header bars, etc. */}
            <h1>Layout</h1>
            <Outlet />
        </div>
    )
}

function Hello() {
    return (
        <div>
          <h1>HELLO WORLD (from App.jsx)</h1>
          <Link to="/about">About</Link>
        </div>
    )

}


export default App;
