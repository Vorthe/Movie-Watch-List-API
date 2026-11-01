import api from './client'

export async function listMovies(params = {}) {
  const { data } = await api.get('/movies/', { params })
  return data
}

export async function getMovie(id) {
  const { data } = await api.get(`/movies/movie/${id}`)
  return data
}

export async function createMovie(movie) {
  const { data } = await api.post('/movies/movie', movie)
  return data
}

export async function updateMovie(id, movie) {
  const { data } = await api.put(`/movies/movie/${id}`, movie)
  return data
}

export async function deleteMovie(id) {
  const { data } = await api.delete(`/movies/movie/${id}`)
  return data
}

export async function getStats() {
  const { data } = await api.get('/movies/stats')
  return data
}

export async function getMoviesByGenre() {
  const { data } = await api.get('/movies/group-by-genre')
  return data
}