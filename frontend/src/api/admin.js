import api from './client'

export async function listCatalog(params = {}) {
  const { data } = await api.get('/admin/movies', { params })
  return data
}

export async function createMovie(movie) {
  const { data } = await api.post('/admin/movies', movie)
  return data
}

export async function updateMovie(id, movie) {
  const { data } = await api.put(`/admin/movies/${id}`, movie)
  return data
}

export async function deleteMovie(id) {
  await api.delete(`/admin/movies/${id}`)
}
