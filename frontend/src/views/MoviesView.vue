<script setup>
import { ref, onMounted, computed } from 'vue'
import { listMovies, updateStatus, deleteStatus, getStats } from '../api/movies'

const movies = ref([])
const stats = ref(null)
const loading = ref(false)
const error = ref('')

const search = ref('')
const filterWatched = ref('')
const sortBy = ref('')
const page = ref(0)
const pageSize = 48

const hasNext = computed(() => movies.value.length === pageSize)
const hasPrev = computed(() => page.value > 0)

const ratingTimers = {}

async function loadMovies() {
  loading.value = true
  error.value = ''
  try {
    const params = { limit: pageSize, skip: page.value * pageSize }
    if (search.value.trim()) params.search = search.value.trim()
    if (filterWatched.value !== '') params.watched = filterWatched.value === 'true'
    if (sortBy.value) params.sort_by = sortBy.value
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

async function handleToggleWatched(movie) {
  const currentWatched = movie.user_status?.watched || false
  const currentRating = movie.user_status?.rating ?? null
  try {
    await updateStatus(movie.id, {
      watched: !currentWatched,
      rating: currentRating,
    })
    await Promise.all([loadMovies(), loadStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to update status.'
  }
}

function handleRatingInput(movie, event) {
  const movieId = movie.id
  const raw = event.target.value

  if (ratingTimers[movieId]) clearTimeout(ratingTimers[movieId])

  ratingTimers[movieId] = setTimeout(async () => {
    const rating = raw === '' ? null : Number(raw)
    if (rating !== null && (rating < 1 || rating > 10)) return

    const watched = movie.user_status?.watched || false
    try {
      await updateStatus(movieId, { watched, rating })
      await Promise.all([loadMovies(), loadStats()])
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to update rating.'
    }
  }, 700)
}

async function handleResetStatus(movie) {
  if (!confirm('Reset your status for this movie?')) return
  try {
    await deleteStatus(movie.id)
    await Promise.all([loadMovies(), loadStats()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to reset status.'
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
      <h1>Movie Catalog</h1>
      <span v-if="loading" class="loading-indicator">Updating…</span>
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
        <span class="stat-label">Your avg</span>
        <span class="stat-value">{{ stats.average_rating.toFixed(1) }}</span>
      </div>
    </div>

    <div class="filters">
      <input
        v-model="search"
        type="text"
        placeholder="Search by title…"
        @keyup.enter="applyFilters"
      />
      <label class="filter-label">
        Status
        <select v-model="filterWatched" @change="applyFilters">
          <option value="">All</option>
          <option value="true">Watched</option>
          <option value="false">Unwatched</option>
        </select>
      </label>
      <label class="filter-label">
        Sort by
        <select v-model="sortBy" @change="applyFilters">
          <option value="">Default</option>
          <option value="title">Title (A–Z)</option>
          <option value="rating">My rating (high → low)</option>
          <option value="external_rating">IMDb rating (high → low)</option>
        </select>
      </label>
      <button class="btn-secondary" @click="applyFilters">Apply</button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <p v-if="!loading && movies.length === 0" class="muted">No movies found.</p>

    <div class="movies-grid" :class="{ 'is-loading': loading }">
      <div v-for="movie in movies" :key="movie.id" class="movie-card">
        <div class="movie-head">
          <h3>{{ movie.title }}</h3>
          <span v-if="movie.external_rating" class="external-rating">
            IMDb {{ movie.external_rating }}
          </span>
        </div>
        <p class="desc">{{ movie.description }}</p>
        <div class="movie-foot">
          <span class="genre">{{ movie.genre }}</span>
          <label class="watched-toggle">
            <input
              type="checkbox"
              :checked="movie.user_status?.watched || false"
              @change="handleToggleWatched(movie)"
            />
            Watched
          </label>
        </div>
        <div class="user-controls">
          <label class="rating-input">
            Your rating:
            <input
              type="number"
              min="1"
              max="10"
              :value="movie.user_status?.rating ?? ''"
              @input="handleRatingInput(movie, $event)"
            />
          </label>
          <button v-if="movie.user_status" class="btn-reset" @click="handleResetStatus(movie)">
            Reset
          </button>
        </div>
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
  max-width: 1200px;
  margin: 0 auto;
}
.header-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
h1 {
  margin: 0;
}
.loading-indicator {
  color: #60a5fa;
  font-size: 0.85rem;
  animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
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
.filters {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  align-items: end;
}
.filter-label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: #94a3b8;
}
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
.filters input {
  flex: 1;
  min-width: 200px;
}
.filters input:focus,
.filters select:focus {
  outline: none;
  border-color: #3b82f6;
}
.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  transition: opacity 0.15s ease;
}
.movies-grid.is-loading {
  opacity: 0.6;
  pointer-events: none;
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
  gap: 0.5rem;
}
.movie-head h3 {
  margin: 0;
  font-size: 1rem;
}
.external-rating {
  color: #fbbf24;
  font-size: 0.8rem;
  white-space: nowrap;
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
.user-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #334155;
}
.rating-input {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #cbd5e1;
}
.rating-input input {
  width: 60px;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.8rem;
}
.rating-input input:focus {
  outline: none;
  border-color: #3b82f6;
}
.btn-reset {
  background: transparent;
  color: #94a3b8;
  border: 1px solid #475569;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
}
.btn-reset:hover {
  color: #f87171;
  border-color: #7f1d1d;
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
