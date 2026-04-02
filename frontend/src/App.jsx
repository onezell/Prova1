import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import EmailList from './pages/EmailList'
import EmailDetail from './pages/EmailDetail'
import Stats from './pages/Stats'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/emails" element={<EmailList />} />
          <Route path="/emails/:id" element={<EmailDetail />} />
          <Route path="/stats" element={<Stats />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}
