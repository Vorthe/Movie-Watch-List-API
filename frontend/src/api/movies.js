import api from './client'

export async function listMovies(params = {}) {
  const { data } = await api.get('/movies/', { params })
  return data
}

export async function getMovie(id) {
  const { data } = await api.get(`/movies/${id}`)
  return data
}

export async function updateStatus(movieId, { watched, rating }) {
  await api.put(`/movies/${movieId}/status`, { watched, rating })
}

export async function deleteStatus(movieId) {
  await api.delete(`/movies/${movieId}/status`)
}

export async function getStats() {
  const { data } = await api.get('/movies/stats')
  return data
}

export async function getMoviesByGenre() {
  const { data } = await api.get('/movies/group-by-genre')
  return data
}
