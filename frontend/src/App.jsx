import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import useAuthStore from './store/authStore'

// Auth
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'

// Dashboard
import DashboardLayout from './components/layout/DashboardLayout'
import AgendaPage from './pages/dashboard/AgendaPage'
import ServicesPage from './pages/dashboard/ServicesPage'
import ProfessionalsPage from './pages/dashboard/ProfessionalsPage'
import ReportsPage from './pages/dashboard/ReportsPage'
import SettingsPage from './pages/dashboard/SettingsPage'

// Public
import BookingPage from './pages/public/BookingPage'

const queryClient = new QueryClient()

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? children : <Navigate to="/login" />
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return !isAuthenticated ? children : <Navigate to="/dashboard" />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster position="top-right" />
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
          <Route path="/book/:slug" element={<BookingPage />} />

          {/* Rutas privadas */}
          <Route path="/dashboard" element={<PrivateRoute><DashboardLayout /></PrivateRoute>}>
            <Route index element={<AgendaPage />} />
            <Route path="services" element={<ServicesPage />} />
            <Route path="professionals" element={<ProfessionalsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* Redireccion raiz */}
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}