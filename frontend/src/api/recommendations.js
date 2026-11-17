import api from './client'

export async function getRecommendations(limit = 20) {
  const { data } = await api.get('/recommendations/', { params: { limit } })
  return data
}
