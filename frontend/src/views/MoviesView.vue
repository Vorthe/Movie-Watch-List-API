<script setup>
import { ref, onMounted, computed } from 'vue'
import { listMovies, createMovie, deleteMovie, getStats, updateMovie } from '../api/movies'

const movies = ref([])
const stats = ref(null)
const loading = ref(false)
const error = ref('')

const search = ref('')
const filterWatched = ref('')
const page = ref(0)
const pageSize = 12

const showForm = ref(false)
const form = ref({
  title: '',
  description: '',
  rating: 5,
  watched: false,
  genre: '',
})

const hasNext = computed(() => movies.value.length === pageSize)
const hasPrev = computed(() => page.value > 0)

function resetForm() {
  form.value = { title: '', description: '', rating: 5, watched: false, genre: '' }
}

async function loadMovies() {
  loading.value = true
  error.value = ''
  try {
    const params = { limit: pageSize, skip: page.value * pageSize }
    if (search.value.trim()) params.search = search.value.trim()
    if (filterWatched.value !== '') params.watched = filterWatched.value === 'true'
    movies.value = await listMovies(params)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load movies.'
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await getStats()
  } catch (e) {
    // stats are optional
  }
}

async function handleCreate() {
  error.value = ''
  try {
    await createMovie({ ...form.value, rating: Number(form.value.rating) })
    showForm.value = false
    resetForm()
    page.value = 0
    await Promise.all([loadMovies(), loadStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create movie.'
  }
}

async function handleDelete(id) {
  if (!confirm('Delete this movie?')) return
  try {
    await deleteMovie(id)
    await Promise.all([loadMovies(), loadStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete movie.'
  }
}

async function toggleWatched(movie) {
  try {
    await updateMovie(movie.id, {
      title: movie.title,
      description: movie.description,
      rating: movie.rating,
      watched: !movie.watched,
      genre: movie.genre,
    })
    await Promise.all([loadMovies(), loadStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to update movie.'
  }
}

function applyFilters() {
  page.value = 0
  loadMovies()
}

function nextPage() {
  page.value++
  loadMovies()
}

function prevPage() {
  page.value--
  loadMovies()
}

onMounted(() => {
  loadMovies()
  loadStats()
})
</script>

<template>
  <div class="movies-view">
    <div class="header-row">
      <h1>My Movies</h1>
      <button class="btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add Movie' }}
      </button>
    </div>

    <div class="stats" v-if="stats">
      <div class="stat-card">
        <span class="stat-label">Total</span>
        <span class="stat-value">{{ stats.total_movies }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Watched</span>
        <span class="stat-value">{{ stats.watched_movies }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Unwatched</span>
        <span class="stat-value">{{ stats.unwatched_movies }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Avg (watched)</span>
        <span class="stat-value">{{ stats.average_rating.toFixed(1) }}</span>
      </div>
    </div>

    <form v-if="showForm" class="movie-form" @submit.prevent="handleCreate">
      <div class="form-row">
        <label>
          Title
          <input v-model="form.title" type="text" required minlength="4" maxlength="20" />
        </label>
        <label>
          Genre
          <input v-model="form.genre" type="text" required minlength="4" maxlength="20" />
        </label>
        <label>
          Rating (1-10)
          <input v-model.number="form.rating" type="number" min="1" max="10" required />
        </label>
        <label class="checkbox-label">
          <input v-model="form.watched" type="checkbox" />
          Watched
        </label>
      </div>
      <label class="full">
        Description
        <textarea
          v-model="form.description"
          rows="2"
          required
          minlength="4"
          maxlength="200"
        ></textarea>
      </label>
      <button type="submit" class="btn-primary">Create</button>
    </form>

    <div class="filters">
      <input
        v-model="search"
        type="text"
        placeholder="Search by title…"
        @keyup.enter="applyFilters"
      />
      <select v-model="filterWatched" @change="applyFilters">
        <option value="">All</option>
        <option value="true">Watched</option>
        <option value="false">Unwatched</option>
      </select>
      <button class="btn-secondary" @click="applyFilters">Apply</button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Loading…</p>
    <p v-else-if="movies.length === 0" class="muted">No movies found.</p>

    <div class="movies-grid">
      <div v-for="movie in movies" :key="movie.id" class="movie-card">
        <div class="movie-head">
          <h3>{{ movie.title }}</h3>
          <span class="rating">⭐ {{ movie.rating }}</span>
        </div>
        <p class="desc">{{ movie.description }}</p>
        <div class="movie-foot">
          <span class="genre">{{ movie.genre }}</span>
          <label class="watched-toggle">
            <input type="checkbox" :checked="movie.watched" @change="toggleWatched(movie)" />
            Watched
          </label>
        </div>
        <button class="btn-delete" @click="handleDelete(movie.id)">Delete</button>
      </div>
    </div>

    <div class="pagination">
      <button class="btn-secondary" :disabled="!hasPrev" @click="prevPage">← Prev</button>
      <span class="muted">Page {{ page + 1 }}</span>
      <button class="btn-secondary" :disabled="!hasNext" @click="nextPage">Next →</button>
    </div>
  </div>
</template>

<style scoped>
.movies-view {
  max-width: 1100px;
  margin: 0 auto;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
h1 {
  margin: 0;
}
.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-primary:hover {
  background: #2563eb;
}
.btn-secondary {
  background: #334155;
  color: #e2e8f0;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-secondary:hover:not(:disabled) {
  background: #475569;
}
.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.stat-card {
  background: #1e293b;
  border: 1px solid #334155;
  padding: 1rem;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.stat-label {
  color: #94a3b8;
  font-size: 0.85rem;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
}
.movie-form {
  background: #1e293b;
  padding: 1.25rem;
  border-radius: 10px;
  border: 1px solid #334155;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.form-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 0.8rem;
  align-items: end;
}
.movie-form label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}
.checkbox-label {
  flex-direction: row !important;
  align-items: center;
  gap: 0.4rem !important;
}
.movie-form input,
.movie-form textarea,
.filters input,
.filters select {
  padding: 0.5rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.9rem;
  font-family: inherit;
}
.movie-form input:focus,
.movie-form textarea:focus,
.filters input:focus,
.filters select:focus {
  outline: none;
  border-color: #3b82f6;
}
.filters {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
}
.filters input {
  flex: 1;
}
.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}
.movie-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.movie-head {
  display: flex;
  justify-content: space-between;
  align-items: start;
}
.movie-head h3 {
  margin: 0;
  font-size: 1rem;
}
.rating {
  color: #fbbf24;
  font-size: 0.85rem;
}
.desc {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0;
  flex: 1;
}
.movie-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.genre {
  background: #1e40af33;
  color: #93c5fd;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}
.watched-toggle {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: #cbd5e1;
  cursor: pointer;
}
.btn-delete {
  background: transparent;
  color: #f87171;
  border: 1px solid #7f1d1d;
  padding: 0.4rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  align-self: start;
}
.btn-delete:hover {
  background: #7f1d1d33;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}
.muted {
  color: #94a3b8;
  text-align: center;
  font-size: 0.9rem;
}
.error {
  color: #f87171;
  padding: 0.6rem;
  background: #7f1d1d33;
  border-radius: 6px;
  font-size: 0.9rem;
}
</style>
