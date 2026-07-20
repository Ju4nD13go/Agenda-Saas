import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Calendar, Scissors, Users, BarChart2, Settings, LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'
import useAuthStore from '../../store/authStore'
import { Button } from '../ui/button'
import { Separator } from '../ui/separator'

const navItems = [
  { to: '/dashboard', label: 'Agenda', icon: Calendar, end: true },
  { to: '/dashboard/services', label: 'Servicios', icon: Scissors },
  { to: '/dashboard/professionals', label: 'Profesionales', icon: Users },
  { to: '/dashboard/reports', label: 'Reportes', icon: BarChart2 },
  { to: '/dashboard/settings', label: 'Configuración', icon: Settings },
]

export default function DashboardLayout() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r flex flex-col
        transform transition-transform duration-200
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0
      `}>
        <div className="p-6">
          <h1 className="text-xl font-semibold text-gray-900">Agenda SaaS</h1>
          <p className="text-sm text-gray-500 mt-1">Panel de gestión</p>
        </div>
        <Separator />
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <Separator />
        <div className="p-4">
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={handleLogout}
          >
            <LogOut size={18} />
            Cerrar sesión
          </Button>
        </div>
      </aside>

      {/* Overlay mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar mobile */}
        <header className="md:hidden flex items-center gap-4 px-4 py-3 bg-white border-b">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
          <h1 className="font-semibold">Agenda SaaS</h1>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}