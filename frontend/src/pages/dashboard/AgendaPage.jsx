import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../../services/api'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Badge } from '../../components/ui/badge'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'

const statusColors = {
  confirmed: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
  no_show: 'bg-gray-100 text-gray-700',
  pending: 'bg-yellow-100 text-yellow-700',
}

const statusLabels = {
  confirmed: 'Confirmada',
  completed: 'Completada',
  cancelled: 'Cancelada',
  no_show: 'No se presentó',
  pending: 'Pendiente',
}

export default function AgendaPage() {
  const queryClient = useQueryClient()
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['appointments', date],
    queryFn: async () => {
      const res = await api.get(`/appointments/panel/?date=${date}`)
      return res.data
    }
  })

  const updateStatus = useMutation({
    mutationFn: ({ id, status }) => api.put(`/appointments/panel/${id}/`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries(['appointments'])
      toast.success('Estado actualizado')
    },
    onError: () => toast.error('Error al actualizar')
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Agenda</h1>
        <Input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-auto"
        />
      </div>

      {isLoading ? (
        <p className="text-gray-500">Cargando citas...</p>
      ) : appointments.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No hay citas para este día
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {appointments.map((apt) => (
            <Card key={apt.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900">{apt.client_name}</span>
                      <span className="text-gray-400">·</span>
                      <span className="text-gray-600 text-sm">{apt.client_phone}</span>
                    </div>
                    <p className="text-sm text-gray-600">{apt.service_name} con {apt.professional_name}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {new Date(apt.start_datetime).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}
                      {' — '}
                      {new Date(apt.end_datetime).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    {apt.notes && <p className="text-sm text-gray-500 mt-1 italic">{apt.notes}</p>}
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColors[apt.status]}`}>
                      {statusLabels[apt.status]}
                    </span>
                    {apt.status === 'confirmed' && (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-green-600 border-green-200 hover:bg-green-50 text-xs"
                          onClick={() => updateStatus.mutate({ id: apt.id, status: 'completed' })}
                        >
                          Completada
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 border-red-200 hover:bg-red-50 text-xs"
                          onClick={() => updateStatus.mutate({ id: apt.id, status: 'no_show' })}
                        >
                          No llegó
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}