<script setup>
import { ref, onMounted, computed } from 'vue'
import { listCatalog, createMovie, deleteMovie } from '../api/admin'

const movies = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')

const showForm = ref(false)
const form = ref({
  title: '',
  description: '',
  genre: '',
  external_rating: '',
  external_id: '',
  external_source: '',
})

const filteredMovies = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return movies.value
  return movies.value.filter(
    (m) => m.title.toLowerCase().includes(q) || m.genre.toLowerCase().includes(q)
  )
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    movies.value = await listCatalog({ limit: 300 })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load catalog.'
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    title: '',
    description: '',
    genre: '',
    external_rating: '',
    external_id: '',
    external_source: '',
  }
}

async function handleCreate() {
  error.value = ''
  const payload = {
    title: form.value.title.trim(),
    description: form.value.description.trim(),
    genre: form.value.genre.trim(),
  }
  if (form.value.external_rating !== '') {
    payload.external_rating = Number(form.value.external_rating)
  }
  if (form.value.external_id.trim()) {
    payload.external_id = form.value.external_id.trim()
    payload.external_source = form.value.external_source.trim() || 'tmdb'
  }

  try {
    await createMovie(payload)
    showForm.value = false
    resetForm()
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create movie.'
  }
}

async function handleDelete(movie) {
  if (!confirm(`Delete "${movie.title}"?`)) return
  try {
    await deleteMovie(movie.id)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to delete movie.'
  }
}

onMounted(load)
</script>

<template>
  <div class="admin-view">
    <div class="header-row">
      <h1>Admin — Catalog</h1>
      <button class="btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add Movie' }}
      </button>
    </div>

    <p class="hint">Admin panel: manage the shared movie catalog. Changes affect all users.</p>

    <form v-if="showForm" class="create-form" @submit.prevent="handleCreate">
      <div class="grid-2">
        <label>
          Title
          <input v-model="form.title" type="text" required minlength="1" maxlength="200" />
        </label>
        <label>
          Genre
          <input v-model="form.genre" type="text" required minlength="1" maxlength="50" />
        </label>
      </div>
      <label>
        Description
        <textarea
          v-model="form.description"
          rows="2"
          required
          minlength="1"
          maxlength="200"
        ></textarea>
      </label>
      <div class="grid-3">
        <label>
          External rating (0–10, optional)
          <input v-model="form.external_rating" type="number" min="0" max="10" step="0.1" />
        </label>
        <label>
          External ID (optional)
          <input v-model="form.external_id" type="text" maxlength="50" />
        </label>
        <label>
          External source (default: tmdb)
          <input v-model="form.external_source" type="text" maxlength="20" />
        </label>
      </div>
      <button type="submit" class="btn-primary">Create</button>
    </form>

    <div class="toolbar">
      <input v-model="search" type="text" placeholder="Search by title or genre…" />
      <span class="muted">{{ filteredMovies.length }} movies</span>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Loading…</p>

    <table v-else class="catalog-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Genre</th>
          <th>IMDb</th>
          <th>Source</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="m in filteredMovies" :key="m.id">
          <td class="id-col">{{ m.id }}</td>
          <td class="title-col">{{ m.title }}</td>
          <td>
            <span class="genre">{{ m.genre }}</span>
          </td>
          <td>{{ m.external_rating ?? '—' }}</td>
          <td class="muted">
            {{ m.external_source ? `${m.external_source}:${m.external_id}` : '—' }}
          </td>
          <td>
            <button class="btn-danger" @click="handleDelete(m)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.admin-view {
  max-width: 1100px;
  margin: 0 auto;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
h1 {
  margin: 0;
}
.hint {
  color: #94a3b8;
  font-size: 0.85rem;
  margin: 0 0 1.5rem 0;
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
.btn-danger {
  background: transparent;
  color: #f87171;
  border: 1px solid #7f1d1d;
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}
.btn-danger:hover {
  background: #7f1d1d33;
}
.create-form {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.grid-2 {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 0.8rem;
}
.grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.8rem;
}
.create-form label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}
.create-form input,
.create-form textarea,
.toolbar input {
  padding: 0.5rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.9rem;
  font-family: inherit;
}
.create-form input:focus,
.create-form textarea:focus,
.toolbar input:focus {
  outline: none;
  border-color: #3b82f6;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.toolbar input {
  flex: 1;
  max-width: 400px;
}
.catalog-table {
  width: 100%;
  border-collapse: collapse;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  overflow: hidden;
}
.catalog-table th,
.catalog-table td {
  padding: 0.6rem 0.8rem;
  text-align: left;
  font-size: 0.85rem;
  border-bottom: 1px solid #334155;
}
.catalog-table th {
  background: #0f172a;
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.catalog-table tr:last-child td {
  border-bottom: none;
}
.catalog-table tr:hover td {
  background: #0f172a;
}
.id-col {
  color: #64748b;
  width: 60px;
}
.title-col {
  color: #e2e8f0;
}
.genre {
  background: #1e40af33;
  color: #93c5fd;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}
.muted {
  color: #94a3b8;
  font-size: 0.85rem;
}
.error {
  color: #f87171;
  padding: 0.6rem;
  background: #7f1d1d33;
  border-radius: 6px;
}
</style>
