import api from './client'

export async function listSchedules(params = {}) {
  const { data } = await api.get('/schedule/', { params })
  return data
}

export async function createSchedule(movieId, scheduledDate) {
  const { data } = await api.post('/schedule/', {
    movie_id: movieId,
    scheduled_date: scheduledDate,
  })
  return data
}

export async function updateScheduleStatus(scheduleId, status) {
  const { data } = await api.patch(`/schedule/${scheduleId}`, { status })
  return data
}

export async function deleteSchedule(scheduleId) {
  await api.delete(`/schedule/${scheduleId}`)
}
