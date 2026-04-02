import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Mail, Settings, BarChart3 } from 'lucide-react'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/emails', icon: Mail, label: 'Email' },
  { to: '/stats', icon: BarChart3, label: 'Statistiche' },
  { to: '/settings', icon: Settings, label: 'Impostazioni' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen p-4 flex flex-col">
      <h1 className="text-xl font-bold mb-8 px-2">
        <Mail className="inline mr-2 h-6 w-6" />
        Email AI
      </h1>
      <nav className="flex flex-col gap-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
